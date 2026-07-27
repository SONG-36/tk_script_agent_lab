# LEARNING_ROADMAP

本路线用于练习 AI 产品经理在 Agentic Engineering 时代的工作方式。每阶段都要留下代码、测试、Golden Case、Run Trace 和个人复盘。

## Phase 0：冻结旧项目，建立实验规则

### 学习目标

- 区分旧项目参考价值与新实验项目范围。
- 学会为 Codex 建立项目级工作边界。
- 准备可重复运行的 Golden Case。

### 业务结果

- 新仓库 `tk-script-agent-lab` 创建完成。
- 车载吸尘器 Golden Case 准备完成。
- 项目目标、非目标、技术边界写清楚。

### 工程验收

- `python -m pytest` 可执行。
- `README.md`、`AGENTS.md`、`TECHNOLOGY_PURPOSE.md` 存在。
- `data/golden_cases/car_vacuum_v1/` 存在并含必要输入模板。

### 禁止事项

- 不接 LLM。
- 不做 RAG。
- 不写 LangGraph。
- 不复制旧项目复杂治理体系。

### 个人复盘问题

- 我能否一句话说清项目目标和非目标？
- Golden Case 是否足以代表真实业务？
- 哪些旧项目内容只作为参考，不迁移？

## Phase 1：业务模型和确定性闭环

### 学习目标

- 学会用 Pydantic 或等价结构表达业务对象。
- 理解确定性校验和模型生成的边界。
- 学会用 Fake Provider 建立可测试闭环。

### 业务结果

```text
商品资料
→ 固定参考洞察
→ 固定创意表
→ 人工选一条
→ 固定剧本
→ 导出
```

### 工程验收

- `ProductProfile`、`ProductFact`、`SellingPoint`、`ReferenceVideo`、`ReferenceInsight`、`CreativeIdea`、`SourceUsage`、`ScriptDraft` 定义完成。
- 校验规则覆盖引用存在性。
- Golden Case 端到端测试通过。

### 个人复盘问题

- 哪些字段必须结构化？
- 哪些字段可以保留自由文本？
- 这条链在没有 LLM 时是否可验证？

## Phase 2：接入真实 LLM

### 学习目标

- 理解 Provider Adapter、Prompt 版本和 Structured Output。
- 区分模型失败、Prompt 失败、Schema 失败和业务校验失败。

### 业务结果

- Reference Analyst 真实生成 `ReferenceInsight[]`。
- Creative Planner 真实生成 5 条 `CreativeIdea`。
- Script Writer 根据选中创意生成完整 `ScriptDraft`。

### 工程验收

- Prompt 文件放在 `prompts/`。
- Prompt 版本、模型名、原始响应、Token、成本进入 Run Trace。
- 模型输出必须经过 Schema 校验。
- Golden Case 至少能完成一次真实运行。

### 个人复盘问题

- 哪一步模型最容易失败？
- 模型有没有编造商品事实？
- Prompt V1 的主要缺陷是什么？

## Phase 3：加入最小 RAG

### 学习目标

- 理解知识条目、Embedding、Metadata Filter、Top-K 和检索评估。
- 学会区分权威上下文和检索上下文。

### 业务结果

- Creative Planner 可以使用 Hook、结构、创意模式和平台规则。
- 能做有 RAG / 无 RAG 对照实验。

### 工程验收

- 知识库含 20-30 条结构化记录。
- 检索记录保存到 Run Trace。
- 每条检索结果包含 `knowledge_id`、score、metadata、source。
- 对照实验记录在 `evals/results/`。

### 个人复盘问题

- RAG 是否真的提高创意质量？
- 哪些结果是误召回？
- Metadata Filter 和向量搜索分别解决了什么？

## Phase 4：加入 LangGraph 工作流

### 学习目标

- 学习 `State`、`Node`、`Edge`、`Conditional Edge`、`Interrupt`、`Resume` 和 `Checkpoint`。
- 理解 Workflow 和 Agent 的区别。

### 业务结果

- 创意生成后暂停等待人工选择。
- 剧本生成后暂停等待人工审核。
- 返工时只重跑必要节点。

### 工程验收

- 只有一个 Graph。
- 只有一个共享 State。
- 页面刷新后可以恢复运行。
- Step Trace 可查看。

### 个人复盘问题

- LangGraph 在本项目中解决了什么？
- 哪些节点可以安全重跑？
- State 里是否塞了不该塞的内容？

## Phase 5：Tool Calling 和有限 Agent 决策

### 学习目标

- 学习 Tool Schema、只读工具、有副作用工具、工具权限和 Tool Call Trace。
- 理解有限 Agent 决策，而不是自由自治 Agent。

### 业务结果

- Creative Planner 可以决定是否检索 Hook、ScriptPattern、PlatformRule。
- Agent 可以改写检索查询，但不能越过人工闸门。

### 工程验收

- 工具调用可记录。
- 最大工具调用步数受限。
- Agent 无法修改权威商品事实。
- Agent 无法自动批准或发布。

### 个人复盘问题

- Tool 与普通函数的差别是什么？
- 哪些工具应该只读？
- 哪些工具必须人工确认？

## Phase 6：Eval 和产品迭代

### 学习目标

- 学会用固定案例、失败分类和指标比较 Prompt、RAG 和模型变化。
- 从“感觉不错”切换到“可验证变好”。

### 业务结果

- 形成 10-20 个 Eval Case。
- 能比较不同 Prompt、不同模型、有无 RAG 的效果。

### 工程验收

- `evals/failure_taxonomy.md` 存在。
- 每次重要变更都有 Eval 结果。
- 指标至少包含 Schema 通过率、来源完整率、事实幻觉率、RAG 有效率、人工返工率、成本和耗时。

### 个人复盘问题

- 哪类失败最影响业务？
- RAG、Prompt、Workflow 分别该怎么改？
- 哪些学习性复杂度应该删掉？
