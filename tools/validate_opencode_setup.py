#!/usr/bin/env python3
"""Validate the local OpenCode migration scaffold without reading secrets."""

from __future__ import annotations

import json
import re
from pathlib import Path


def main() -> int:
    workspace = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    required = (
        "AGENTS.md",
        "opencode.json",
        ".opencode/agents/story-editor.md",
        ".opencode/agents/novel-writer.md",
        ".opencode/agents/canon-auditor.md",
        ".opencode/agents/long-context-auditor.md",
        ".opencode/agents/reasoning-reviewer.md",
        ".opencode/skills/story-governance/SKILL.md",
        ".opencode/skills/novel-drafting/SKILL.md",
        ".opencode/skills/canon-audit/SKILL.md",
        ".opencode/commands/status.md",
        ".opencode/commands/next.md",
        ".opencode/commands/audit.md",
        ".opencode/commands/long-audit.md",
        ".opencode/commands/draft.md",
        ".opencode/commands/validate.md",
        "上下文包/README.md",
        "草稿/README.md",
    )
    for relative in required:
        if not (workspace / relative).is_file():
            errors.append(f"missing: {relative}")

    config_path = workspace / "opencode.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append(f"invalid opencode.json: {error}")
        config = {}

    if config.get("default_agent") != "story-editor":
        errors.append("default agent must be story-editor")
    if config.get("model") != "opencode-go/hy4-preview":
        errors.append("default planning model must be opencode-go/hy4-preview")
    if config.get("share") != "disabled":
        errors.append("session sharing must remain disabled")

    prose_model = (
        workspace / ".opencode/agents/novel-writer.md"
    ).read_text(encoding="utf-8")
    if "model: tbtk-claude/oplus5" not in prose_model:
        errors.append("novel-writer is not locked to TBTK Claude oplus5")

    agent_models = {
        "story-editor": "opencode-go/hy4-preview",
        "reasoning-reviewer": "opencode-go/glm-5.3-flash",
        "canon-auditor": "opencode-go/glm-5.3-flash",
        "kimi-story-reviewer": "opencode-go/kimi-k3",
        "long-context-auditor": "opencode-go/hy4-preview",
    }
    for agent_name, expected_model in agent_models.items():
        agent_text = (workspace / f".opencode/agents/{agent_name}.md").read_text(
            encoding="utf-8"
        )
        if f"model: {expected_model}" not in agent_text:
            errors.append(f"{agent_name} must use {expected_model}")

    tri_review = (workspace / ".opencode/commands/tri-review.md").read_text(
        encoding="utf-8"
    )
    for required_name in ("Hy4 Preview", "GLM-5.3-Flash", "Kimi K3"):
        if required_name not in tri_review:
            errors.append(f"tri-review is missing model label: {required_name}")

    for skill_dir in (workspace / ".opencode/skills").iterdir():
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            continue
        text = skill_file.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
        description_match = re.search(r"^description:\s*([^\n]+)$", text, re.MULTILINE)
        if not name_match or name_match.group(1).strip() != skill_dir.name:
            errors.append(f"skill name mismatch: {skill_dir.name}")
        if not description_match or not description_match.group(1).strip():
            errors.append(f"skill description missing: {skill_dir.name}")

    scanned_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            workspace / "AGENTS.md",
            workspace / "opencode.json",
            *sorted((workspace / ".opencode").rglob("*.md")),
            workspace / "tools/start_opencode.zsh",
        )
    )
    if re.search(r"sk-[A-Za-z0-9]{16,}", scanned_text):
        errors.append("credential-like literal found in OpenCode scaffold")

    if errors:
        print("OPENCODE SETUP VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OPENCODE SETUP VALIDATION OK")
    print(f"- required files: {len(required)}")
    print("- default agent: story-editor / Hy4 Preview")
    print("- prose agent: novel-writer / TBTK Claude oplus5")
    print("- credentials embedded: no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
