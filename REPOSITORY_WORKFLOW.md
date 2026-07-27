# REPOSITORY_WORKFLOW

本文件定义仓库工作流和 Codex 使用方式。

## 分支策略

保持简单：

```text
main
feature/<single-capability>
```

一个分支只解决一个能力。

## 提交策略

推荐提交粒度：

```text
chore: scaffold agent lab
feat: add deterministic domain models
feat: add reference analyst provider
feat: add minimal knowledge retrieval
feat: add langgraph workflow
feat: add tool calling
test: add eval suite
```

Codex 不自动 commit。用户审核后提交。

## 每轮 Codex 任务流程

```text
1. 填写 Task Contract
2. Codex 读取 AGENTS.md 和相关文件
3. Codex 运行当前测试
4. Codex 实施小范围修改
5. Codex 运行测试和 Golden Case
6. Codex 输出证据报告
7. 用户查看关键 diff、Trace 和输出
8. 用户决定是否提交
```

## 用户重点审查内容

必须认真看：

- Domain Schema
- Prompt
- Workflow State
- Tool Schema
- RAG 检索结果
- SourceUsage 校验
- 数据写入和覆盖逻辑
- 成本限制
- 测试和 Eval

可以少量抽查：

- UI 排版
- 简单映射代码
- 样板配置
- 文档格式

## 每次任务禁止

- 把多个阶段塞进同一任务。
- 一次性搭建 RAG、LangGraph、Tool Calling 和 UI。
- 顺手重构无关代码。
- 删除旧 Trace 或 Golden Case。
- 降低测试断言。
- 自动提交。

## 稳定点

每个 Phase 结束后打一个稳定提交，并填写 `PHASE_EXIT_CHECKLIST.md`。

## 旧项目处理

旧项目只作为业务参考。不得直接复制旧项目复杂治理结构。需要复用概念时，优先复用业务对象和流程，不复用旧的 Mock 文案和大页面结构。
