# 《碎月》OpenCode 迁移说明

## 打开位置

在 OpenCode 中只打开本目录：

`小说改编工作区`

不要把外层“钟·漠项目文件”作为项目根目录。外层包含美术、视频、游戏策划、旧文案和敏感配置，会增加上下文污染与索引负担。

## 第一次连接模型

1. 在 OpenCode 中运行 `/connect`，选择 **OpenCode Go**，粘贴当前准备使用的 Go 密钥。
2. Go模型标识已经写入配置：默认Hy4 Preview，轻量任务与逻辑反审使用GLM-5.3-Flash，Kimi K3只在三模型审查中承担故事与人物意见。
3. 正文 Claude 有两种连接方式：
   - 终端启动：在本目录运行 `./tools/start_opencode.zsh`，脚本会从外层 `.secrets/tbtk-claude.env` 注入环境变量，但不会把密钥复制进项目文件；
   - OpenCode 图形界面：运行 `/connect`，选择 **Other**，provider id 填 `tbtk-claude`，再粘贴 Claude 密钥。项目中的 provider 定义会负责 endpoint 和模型名。

OpenCode Go 当前一次只保存一份该 provider 的凭据。需要更换三把 Go 密钥时，重新执行 `/connect` 覆盖即可；本项目不把密钥写入 `opencode.json`，也不自行实现不透明的自动轮换。

## 已配置代理

- `story-editor`：默认主代理，Hy4 Preview；整理资料、讨论情节、长上下文连续性与主编辑汇合。
- `novel-writer`：Claude oplus5；只写已经批准的小说正文。
- `canon-auditor`：GLM-5.3-Flash；只读canon审查。
- `long-context-auditor`：Hy4 Preview；只读长上下文和跨章节检查，供单独长审查使用。
- `reasoning-reviewer`：GLM-5.3-Flash；只读逻辑与反方审查。
- `kimi-story-reviewer`：Kimi K3；只在三模型审查中调用一次，检查人物欲望、故事因果和感染力。

可以用 Tab 切换主代理，或在输入中 `@` 指定只读审查代理。

## 常用命令

- `/status`：查看当前批准状态和资料健康度。
- `/next`：只提出一个最应继续讨论的问题。
- `/audit 文件或方案`：检查 canon 与因果矛盾。
- `/long-audit 人物线或多个章节`：检查连续性。
- `/draft 上下文包/某场景.md`：调用 Claude 写正文。
- `/validate`：运行资料库和迁移配置验证。

## 推荐工作流

先用 `story-editor` 一条一条讨论情节。用户批准后更新资料库，再为单个场景建立 `上下文包/` 文件。用 `/audit` 检查该上下文包，通过后再执行 `/draft`。正文进入 `草稿/`，之后仍需审查，不能反向覆盖 canon。

## 安全边界

- 会话分享已禁用。
- OpenCode 不允许读取项目外目录，因此不会直接扫描原项目与 `.secrets`。
- 资料库和配置文件的修改默认要求确认；`草稿/` 与 `上下文包/` 可以直接写入。
- D8 五份文本继续永久排除。

配置依据为 OpenCode 2026-08-30 官方文档：项目规则使用 `AGENTS.md`，代理、命令与技能位于 `.opencode/`，模型使用 `provider/model-id`，OpenCode Go 模型使用 `opencode-go/<model-id>`。
