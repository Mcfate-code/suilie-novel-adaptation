---
description: 使用固定的 Hy4 Preview、GLM-5.3-Flash与Kimi K3对一个剧情问题作三模型独立审查
agent: story-editor
---

加载 `story-governance`，只读取当前问题所需资料。先由当前主编辑Hy4 Preview独立检查长上下文连续性、人物弧线和canon冲突；再把同一份最小审查包分别交给`reasoning-reviewer`（GLM-5.3-Flash，逻辑、动机与最大漏洞）和`kimi-story-reviewer`（Kimi K3，人物欲望、故事因果与感染力）。不得让三个模型先看到彼此结论，不得用任何其他模型替代。Kimi只调用一次，不参与最终汇合。

汇总时用通俗中文分别标明“Hy4 Preview”“GLM-5.3-Flash”“Kimi K3”的意见，再说明共同点、分歧和你的综合判断。不得把GLM-5.3-Flash误标成完整GLM-5.3，不要把多模型一致当作批准，不要修改canon。任一模型不可用时明确报告缺席，不得声称完成三模型审查。每次只审查一个核心问题。$ARGUMENTS
