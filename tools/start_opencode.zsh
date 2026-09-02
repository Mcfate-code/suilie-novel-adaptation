#!/bin/zsh
set -eu

script_dir=${0:A:h}
workspace_dir=${script_dir:h}
outer_project_dir=${workspace_dir:h}
claude_env_file="$outer_project_dir/.secrets/tbtk-claude.env"

if ! command -v opencode >/dev/null 2>&1; then
  print -u2 "未在当前 PATH 中找到 opencode。请从已安装的 OpenCode 打开本目录，或修正终端 PATH。"
  exit 127
fi

if [[ -f "$claude_env_file" ]]; then
  set -a
  source "$claude_env_file"
  set +a
  export TBTK_CLAUDE_API_KEY="$TBTK_API_KEY"
  unset TBTK_API_KEY TBTK_BASE_URL TBTK_MODEL TBTK_PROTOCOL TBTK_PURPOSE
fi

cd "$workspace_dir"
exec opencode "$@"
