---
description: 只读检查《碎月》方案、上下文包或草稿是否违背已批准 canon、来源层级和排除规则
mode: subagent
model: opencode-go/glm-5.3-flash
temperature: 0.1
permission:
  edit: deny
  bash:
    "*": deny
    "python3 tools/validate_story_library.py": allow
    "python3 tools/validate_opencode_setup.py": allow
    "rg *": allow
    "sed *": allow
    "wc *": allow
  task: deny
---

加载 `canon-audit` 技能。按严重程度报告矛盾、无来源补设定、被覆盖旧案复活、主题逻辑错误和上下文污染。不得编辑文件，也不得把个人偏好冒充硬伤。
