# ARCHITECTURE

## 架构原则

本项目采用「受控 Agentic Workflow」，不是自由自治 Agent。

```text
80% 确定性 Workflow
20% 模型辅助决策
```

核心思想：

- 确定性代码管理状态、校验、权限、保存、导出、人工闸门。
- LLM 负责非结构化理解、创意生成、语言生成和可解释草稿。
- RAG 只负责提供可复用知识，不允许覆盖当前商品事实。
- LangGraph 用于学习状态图、暂停恢复和条件分支，不用于制造多 Agent 群聊。

## 目标架构

```text
Streamlit UI
    ↓
Application Layer
    ↓
LangGraph Workflow
    ├── validate_input
    ├── analyze_reference_videos
    ├── build_retrieval_query
    ├── retrieve_knowledge
    ├── compose_context
    ├── generate_creative_ideas
    ├── validate_source_usage
    ├── human_select_idea
    ├── generate_script
    ├── validate_script_claims
    ├── human_review
    └── export
    ↓
Domain Models / Validators
    ↓
Providers / Tools / Storage
```

## 三类上下文

### Authoritative Context

权威任务上下文，直接进入模型，不通过模糊检索：

- `ProductProfile`
- `ProductFact[]`
- `SellingPoint[]`
- 用户输入的禁止表达
- 当前任务目标
- 当前人工选择

规则：RAG 和模型不得修改或覆盖这些内容。

### Reference Context

本次任务参考视频上下文：

- `ReferenceVideo[]`
- `ReferenceInsight[]`

规则：参考视频用于借鉴模式，不能复制原视频，也不能引入未经商品事实支撑的产品功能。

### Retrieved Context

可复用知识上下文：

- `HookPattern`
- `ScriptPattern`
- `CreativePattern`
- `PlatformRule`
- `ScriptExample`

规则：只能辅助创意和结构，不是当前商品事实来源。

## 核心领域对象

```text
ProductProfile
ProductFact
SellingPoint
ReferenceVideo
ReferenceInsight
CreativeIdea
SourceUsage
ScriptDraft
ReviewDecision
ProductionExport
RunTrace
```

## 模型步骤

### Reference Analyst

输入：`ReferenceVideo[]`

输出：`ReferenceInsight[]`

职责：提取 Hook、结构、镜头、节奏、产品展示方式、CTA、可借鉴点和复制风险。

### Creative Planner

输入：`ProductProfile`、`ProductFact[]`、`SellingPoint[]`、`ReferenceInsight[]`、`RetrievedKnowledge[]`

输出：`CreativeIdea[]`

职责：生成一行一个可独立生成剧本的创意方案，并提供 `SourceUsage[]`。

### Script Writer

输入：一个人工选中的 `CreativeIdea` 与权威商品上下文

输出：`ScriptDraft`

职责：在选中创意约束下生成完整 TikTok 剧本，不得重新发明创意或新增无依据功能。

## RAG 位置

RAG 负责：

```text
从通用知识库中检索对当前创意有帮助的模式、结构、规则和案例。
```

RAG 不负责：

```text
决定当前商品有哪些功能、参数或真实卖点。
```

## Human Gates

必须保留两个人工闸门：

1. `human_select_idea`：用户从 `CreativeIdea[]` 中选择一条。
2. `human_review`：用户审核 `ScriptDraft`，结果为 `approved`、`rework`、`hold` 或 `rejected`。

## 数据保存

第一版可用 JSON 文件或 SQLite。必须保存：

- 输入快照
- 模型请求和响应
- 检索结果
- 校验结果
- 人工选择
- 人工审核
- 导出结果
- 错误和成本

## 复杂度边界

暂不引入：

- 多 Agent 群聊
- 长期记忆
- 自动规划器
- 自动发布工具
- 大规模知识图谱
- 多租户权限系统
