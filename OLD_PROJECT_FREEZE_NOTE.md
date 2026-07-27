# OLD_PROJECT_FREEZE_NOTE

## 冻结目的

旧项目已经完成一定业务审计和 WS-0 / WS-1 骨架，但当前目标是学习 AI 产品经理的 Agentic Engineering 工作方式。因此旧项目冻结为参考资料，不继续在旧项目上增量重构。

## 可复用内容

可以参考：

- 真实业务流程分析。
- `ProductProfile`、`ProductFact`、`SellingPoint`、`ReferenceVideo`、`ReferenceInsight`、`CreativeIdea`、`SourceUsage`、`ScriptDraft` 等领域概念。
- 一行一个创意方案的粒度。
- `CreativeIdea → ScriptDraft` 的绑定规则。
- 人工选择和人工审核流程。
- 车载吸尘器样例。

## 不优先复用内容

不优先迁移：

- 旧 Streamlit 大页面。
- 旧 `ws1/service.py` 大服务文件。
- 确定性 Mock 文案。
- 旧兼容 Adapter。
- 旧复杂治理文档体系。
- 旧快照格式。

## 冻结规则

- 不在旧项目中继续添加 Agent、RAG 或 LangGraph。
- 不删除旧项目。
- 不把旧项目当成新项目代码来源直接复制。
- 如需复用规则，先写进新项目文档或 Task Contract，再让 Codex 用新架构实现。

## 未来回看时机

当 `tk-script-agent-lab` 完成 Phase 6，并能稳定解释 RAG、Agent、Trace 和 Eval 后，再评估：

- 是否把 V2 作为生产项目基础。
- 是否迁移旧项目中的有效业务资产。
- 是否完全废弃旧项目。
