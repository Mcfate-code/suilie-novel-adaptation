#!/usr/bin/env python3
"""Validate source anchors and basic Markdown-table integrity."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


EXPECTED_HASH = "1966824a403199713ef0fa9aea5a03dc9719e1554d4edd640be6053f69938974"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_tables(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    table: list[tuple[int, str]] = []

    def check(rows: list[tuple[int, str]]) -> None:
        if len(rows) < 2:
            return
        counts = [row.count("|") for _, row in rows]
        if len(set(counts)) != 1:
            detail = ", ".join(f"L{line}:{count}" for (line, _), count in zip(rows, counts))
            errors.append(f"{path.name}: table column mismatch ({detail})")

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("|") and line.endswith("|"):
            table.append((line_number, line))
        else:
            check(table)
            table = []
    check(table)
    return errors


def main() -> int:
    workspace = Path(__file__).resolve().parents[1]
    library = workspace / "资料库"
    snapshot = workspace / "原始资料快照" / "碎月之书_主线基准候选_SHA256-1966824a.docx"
    index = library / "00A_主线源文件登记与段落索引.md"

    errors: list[str] = []
    if file_hash(snapshot) != EXPECTED_HASH:
        errors.append("main-source snapshot hash mismatch")

    index_text = index.read_text(encoding="utf-8")
    indexed_paragraphs = {int(number) for number in re.findall(r"^### P(\d{3})$", index_text, re.MULTILINE)}
    if len(indexed_paragraphs) != 89:
        errors.append(f"expected 89 indexed non-empty paragraphs, got {len(indexed_paragraphs)}")

    markdown_paths = sorted(
        path
        for path in workspace.rglob("*.md")
        if ".opencode/node_modules" not in path.as_posix()
    )

    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        errors.extend(validate_tables(path, text))
        if path == index:
            continue
        for citation in re.findall(r"`SRC-MAIN:([^`]+)`", text):
            for number in map(int, re.findall(r"P(\d{3})", citation)):
                if number not in indexed_paragraphs:
                    errors.append(f"{path.name}: citation P{number:03d} is not a non-empty indexed paragraph")

    joined = "\n".join(path.read_text(encoding="utf-8") for path in markdown_paths)
    stale_phrases = (
        "有限对象、有限条件和有限消耗",
        "不能无限供能、治愈一切或修复所有镜路装置",
        "quarantined / D8-scope-pending",
        "D8 范围确认前临时隔离",
        "D8 究竟只删除某一篇",
        "时间回声机制不进入小说 canon",
        "仍支持辅助层或引导层的居民",
    )
    for phrase in stale_phrases:
        if phrase in joined:
            errors.append(f"stale over-interpretation remains: {phrase}")

    d8_files = (
        "研究院年度试炼监考行为规范",
        "笑话若干",
        "不正经报",
        "不知名研究员的吐槽",
        "莫名其妙的文本之公告栏",
    )
    version_index = (library / "01_版本与资料状态索引.md").read_text(encoding="utf-8")
    ai_allowlist = (library / "09_AI上下文准入清单.md").read_text(encoding="utf-8")
    exclusion_match = re.search(
        r"^## D8 已确认正式排除\s*$([\s\S]*?)(?=^## |\Z)",
        ai_allowlist,
        re.MULTILINE,
    )
    if not exclusion_match:
        errors.append("D8 formal-exclusion section is missing from AI context policy")
        exclusion_section = ""
    else:
        exclusion_section = exclusion_match.group(1)

    allowed_match = re.search(r"^## 可直接提供\s*$([\s\S]*?)(?=^## |\Z)", ai_allowlist, re.MULTILINE)
    if not allowed_match:
        errors.append("directly-allowed section is missing from AI context policy")
        allowed_section = ""
    else:
        allowed_section = allowed_match.group(1)

    project_root = workspace.parent
    for title in d8_files:
        if not re.search(rf"\| 《{re.escape(title)}》 \| excluded \|", version_index):
            errors.append(f"D8 file is not excluded in version index: {title}")
        if f"《{title}》" not in exclusion_section:
            errors.append(f"D8 file missing from AI exclusion list: {title}")
        if f"《{title}》" in allowed_section:
            errors.append(f"D8 file was also placed in the directly-allowed section: {title}")
        original = project_root / "文案组内容" / "新建文件夹 (5)" / f"{title}.docx"
        if not original.is_file():
            errors.append(f"D8 original file is missing: {original}")

    mia_title = "修月亮的米娅"
    if f"《{mia_title}》" in exclusion_section:
        errors.append("D7 folklore was incorrectly included in the D8 exclusion section")
    mia_original = project_root / "文案组内容" / "新建文件夹 (5)" / f"{mia_title}.docx"
    if not mia_original.is_file():
        errors.append(f"D7 folklore original file is missing: {mia_original}")

    initial_audit = (workspace / "00_原剧情资料审计报告.md").read_text(encoding="utf-8")
    for phrase in ("其真实性尚未决定", "很适合成为研究院内部私人证词", "建议暂列非 canon 素材箱"):
        if phrase in initial_audit:
            errors.append(f"stale D7/D8 wording remains in initial audit: {phrase}")

    decision_sheet = (workspace / "01_待批准修改决策单.md").read_text(encoding="utf-8")
    if "唯一生效决定（2026-08-30 二次确认）" not in decision_sheet:
        errors.append("D8 final decision is not clearly marked as the sole effective choice")
    if "当前唯一锁定的 C6 边界是“阿月是普通人；圣火不是万能道具”" not in decision_sheet:
        errors.append("C6 follow-up boundary is missing from the decision sheet")

    usage_rules = (library / "00_资料库使用说明.md").read_text(encoding="utf-8")
    if "时间更新、范围更具体" not in usage_rules:
        errors.append("decision precedence does not specify newer and more specific user decisions")
    if "《09_AI上下文准入清单》为唯一清单" not in usage_rules:
        errors.append("AI context governance does not identify one canonical allowlist")

    if "USR-20260830-D8" not in joined:
        errors.append("D8 confirmation source marker is missing")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDATION OK")
    print(f"- snapshot SHA-256: {EXPECTED_HASH}")
    print(f"- indexed non-empty paragraphs: {len(indexed_paragraphs)}")
    print(f"- markdown files checked: {len(markdown_paths)}")
    print(f"- D8 originals retained and excluded: {len(d8_files)}")
    print("- D7 folklore retained outside D8: 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
