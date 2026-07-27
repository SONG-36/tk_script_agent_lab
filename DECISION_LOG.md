# DECISION_LOG

本文件只记录真正的架构、产品和学习路径决策。不要记录日常修改流水账。

## 记录格式

```text
Date:
Decision:
Context:
Reason:
Tradeoff:
Revisit when:
Status:
```

## Decision 001：新建独立学习仓库

Date: TBD

Decision:
新建 `tk-script-agent-lab`，旧项目冻结为业务参考，不继续在旧仓库增量重构。

Context:
旧项目已有 WS-0、WS-1、确定性 Mock、审计和文档，但尚未接入真实 LLM、RAG、LangGraph 或完整 Agent 运行闭环。当前目标是学习 AI 产品经理如何管理 Agentic Engineering，而不是把旧项目生产化。

Reason:
新仓库可以减少兼容旧接口、旧测试和旧治理体系的成本，更快走完真实模型调用、RAG、Trace、Human Gate 和 Eval。

Tradeoff:
会放弃旧代码的部分工程资产，但保留其业务分析和领域对象作为参考。

Revisit when:
学习型 V2 的核心闭环稳定后，再评估是否迁移回生产项目或重建生产版。

Status: Proposed

## Decision 002：早期使用 RAG 的定位

Date: TBD

Decision:
Phase 3 加入最小 RAG，但明确它一部分服务学习目标，不代表当前业务规模必须使用 RAG。

Context:
当前数据量小，普通结构化过滤即可满足业务 MVP。但用户希望学习知识库、索引、Embedding、检索和 Agent 框架流程。

Reason:
用小型结构化知识库学习 RAG 的数据流、检索流和评估方法，可以帮助建立 AI 产品经理对 RAG 的真实判断力。

Tradeoff:
增加学习性复杂度。必须通过有 RAG / 无 RAG 对照实验验证价值。

Revisit when:
如果 RAG 误召回多、无法提高创意质量，优先改知识结构和检索策略，而不是继续堆工具。

Status: Proposed

## Decision 003：使用 LangGraph 的定位

Date: TBD

Decision:
Phase 4 使用一个 LangGraph Workflow，限制为一个 Graph、一个 State、三类模型节点和两个人工闸门。

Context:
当前业务流程基本固定，普通 Python Workflow 足够实现业务 MVP。但学习目标包括 State、Checkpoint、Interrupt 和 Resume。

Reason:
LangGraph 可以作为学习 Agent Workflow 的载体，帮助理解 Human-in-the-loop 和可恢复执行。

Tradeoff:
业务上不一定必须。必须避免多 Agent 群聊和自由规划。

Revisit when:
如果 Graph 长期只是线性调用且没有暂停恢复价值，考虑退回普通 Python Workflow。

Status: Proposed
