# PHASE_EXIT_CHECKLIST

每个阶段结束前填写。本清单不能让 Codex 全代写，用户必须亲自复盘关键问题。

## 基本信息

```text
Phase:
Date:
Branch:
Commit candidate:
Owner:
```

## 业务能力

- [ ] 本阶段新增的业务能力已经跑通。
- [ ] Golden Case 已运行。
- [ ] 用户能看到可理解的输出。
- [ ] 输出能被人工审核。

## 工程验证

- [ ] `python -m pytest` 通过。
- [ ] 相关 Eval 已运行或说明为什么暂不运行。
- [ ] Run Trace 已保存。
- [ ] 关键错误路径有测试。
- [ ] 没有降低测试断言。

## AI 能力验证

- [ ] 模型输入可追踪。
- [ ] Prompt 版本可追踪。
- [ ] Structured Output 校验生效。
- [ ] 模型失败和业务校验失败可区分。
- [ ] 没有绕过人工闸门。

## RAG 验证

适用于 Phase 3 以后：

- [ ] 检索 query 可查看。
- [ ] Top-K 结果可查看。
- [ ] Metadata Filter 生效。
- [ ] 有 RAG / 无 RAG 对照已记录。
- [ ] 未发现 RAG 覆盖当前商品事实。

## LangGraph 验证

适用于 Phase 4 以后：

- [ ] State 字段清晰。
- [ ] Node 职责清晰。
- [ ] Human Interrupt 生效。
- [ ] Resume 生效。
- [ ] 返工不会重跑不必要节点。

## Tool Calling 验证

适用于 Phase 5 以后：

- [ ] Tool Schema 清晰。
- [ ] Tool Call Trace 已保存。
- [ ] 最大步骤限制生效。
- [ ] Agent 无法调用高风险工具绕过审批。

## 成本和安全

- [ ] 单次运行成本记录完整。
- [ ] 最大调用次数限制生效。
- [ ] 没有提交 API Key。
- [ ] 没有外部写入。
- [ ] 没有自动发布或批量生成。

## 个人复盘

回答以下问题：

1. 本阶段真正学到了什么？
2. 哪些复杂度是业务需要？
3. 哪些复杂度只是学习需要？
4. 哪个失败最常见？
5. 下一阶段是否真的值得进入？
6. 是否应该删掉或简化某些设计？
