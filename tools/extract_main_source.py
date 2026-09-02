#!/usr/bin/env python3
"""Create a stable, paragraph-numbered text index for the main story DOCX."""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime
from pathlib import Path

from docx import Document


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: extract_main_source.py SOURCE.docx SNAPSHOT.docx OUTPUT.md", file=sys.stderr)
        return 2

    source_path = Path(sys.argv[1]).resolve()
    snapshot_path = Path(sys.argv[2]).resolve()
    output_path = Path(sys.argv[3]).resolve()

    document = Document(source_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    nonempty = [(index, text) for index, text in enumerate(paragraphs, start=1) if text]
    source_stat = source_path.stat()

    lines = [
        "# 《碎月之书》主线源文件登记与段落索引",
        "",
        "> 本文件是只读抽取索引，不是修改稿。`P001` 等编号对应 DOCX 的原始段落位置；空段保留在计数中，但不抄入正文索引。抽取时将段内硬换行与连续空白规范为一个空格，不改变字词顺序。",
        "",
        "## 一、源文件登记",
        "",
        f"- **来源代号：** `SRC-MAIN`",
        f"- **原始文件：** `{source_path}`",
        f"- **工作区快照：** `{snapshot_path}`",
        f"- **SHA-256：** `{sha256(source_path)}`",
        f"- **文件大小：** {source_stat.st_size} bytes",
        f"- **源文件修改时间：** {datetime.fromtimestamp(source_stat.st_mtime).astimezone().isoformat(timespec='seconds')}",
        f"- **段落数量：** {len(paragraphs)}（非空 {len(nonempty)}）",
        "- **资料状态：** `source-candidate`；用户后续明确决定拥有更高权威。",
        "",
        "## 二、引用方法",
        "",
        "- 单段：`SRC-MAIN:P015`",
        "- 连续段：`SRC-MAIN:P015–P023`",
        "- 多段：`SRC-MAIN:P015、P019–P023`",
        "- 若工作区快照与本登记的哈希不一致，应停止写作并重新审计。",
        "",
        "## 三、段落索引",
        "",
    ]

    for index, text in nonempty:
        normalized = " ".join(text.split())
        lines.extend((f"### P{index:03d}", "", normalized, ""))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
