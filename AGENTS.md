# AGENTS.md

本文件是 Codex 每次进入本仓库时必须遵守的长期工作规则。它不是产品愿景文档，而是 Agentic Coding 的执行合同。

## 项目定位

本仓库是学习型 `TikTok Script Agent Lab`。目标是通过一个真实业务案例学习 AI 应用、RAG、LangGraph、Tool Calling、Trace 和 Eval 的完整流程。

本项目允许一定学习性复杂度，但所有复杂度必须在 `DECISION_LOG.md` 或 `TECHNOLOGY_PURPOSE.md` 中说明原因。

## 工作原则

- 一次只实施一个纵向能力。
- 修改前先读取相关代码、测试、Prompt 和数据样例。
- 修改前运行当前测试，确认基线。
- 不擅自新增技术栈。
- 不把确定性规则交给 LLM。
- 不把 Prompt 写死在业务函数里。
- 不允许模型输出绕过 Pydantic 或等价 Schema 校验。
- 不允许 Agent 自动批准、自动发布、自动调用付费批量服务。
- 不允许为了让测试通过而降低断言、删除测试或跳过核心测试。
- 不顺手重构无关模块。
- 不自动提交 Git commit。

## 固定边界

初期固定：

- 一个 Streamlit UI。
- 一个 LangGraph Workflow。
- 一个共享 Workflow State。
- 一个 LLM Provider Adapter。
- 一个轻量向量库或本地向量索引。
- 一个 Golden Case 起步。
- 人工选择创意必须保留。
- 人工审核剧本必须保留。

## 不允许模型决定的事项

- 商品事实是否真实。
- 卖点是否经过事实支撑。
- 最终选择哪条创意。
- 剧本是否批准。
- 是否忽略禁用表达。
- 是否自动发布或调用外部平台。
- 是否修改权威商品上下文。

## 允许模型辅助的事项

- 从参考视频文字中提取 `ReferenceInsight`。
- 根据商品、卖点、参考洞察和检索知识生成 `CreativeIdea[]`。
- 生成 Hook、故事结构、分镜和口播。
- 根据人工审核意见重写剧本。
- 为 RAG 检索生成查询词。

## 每次任务必须输出的证据

最终报告必须包含：

- 修改文件列表。
- 调用链变化。
- 新增或修改的 Schema。
- Prompt 变更。
- 测试命令和结果。
- Golden Case 运行结果。
- Run Trace 或样例 Trace 路径。
- 未解决问题。
- 明确没有做什么。

## 默认测试命令

```bash
python -m pytest
```

如果任务涉及格式、类型、文档或 Eval，应补充对应命令，但不得临时引入大型检查框架。

## Codex 固定工作法

每一轮开发遵循：

```text
任务合同
→ 当前状态审计
→ 小范围实现
→ 自动测试
→ Golden Case 运行
→ Trace 检查
→ 风险报告
→ 用户验收
```

不要把「搭建整个 Agent 系统」作为单次任务。
