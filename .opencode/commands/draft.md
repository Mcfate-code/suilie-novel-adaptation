---
description: 使用 Claude 根据已批准上下文包撰写小说正文
agent: novel-writer
---

加载 `novel-drafting`。根据 $ARGUMENTS 指定的上下文包和场景卡写作。若没有明确文件，或内容仍含未批准待决项，停止并列出缺口。正文只写入 `草稿/`。
