# Task Contract Template

每次让 Codex 开发前，复制本模板并填写。一个任务只解决一个纵向能力。

## Goal

说明本次任务要完成的业务能力。

示例：

```text
将 ReferenceVideo[] 转换为结构化 ReferenceInsight[]，并接入真实 LLM Provider。
```

## Current State

说明当前已有代码、数据、测试和限制。

## Business Behavior

说明用户视角下应该发生什么，而不是只描述代码文件。

## Inputs

列出输入对象、字段和样例路径。

```text
ProductProfile:
ProductFact[]:
SellingPoint[]:
ReferenceVideo[]:
Knowledge records:
```

## Outputs

列出输出对象和必须保留的字段。

```text
ReferenceInsight[]:
CreativeIdea[]:
ScriptDraft:
RunTrace:
```

## Invariants

不可破坏的不变量：

- 商品事实不得由模型修改。
- SellingPoint 必须引用存在的 ProductFact。
- ReferenceInsight 必须引用存在的 ReferenceVideo。
- CreativeIdea 必须引用存在的 Fact、SellingPoint 和 Insight。
- ScriptDraft 必须绑定一个人工选中的 CreativeIdea。
- 人工选择和人工审核不得被自动跳过。

## Allowed Changes

列出允许修改的文件或目录。

## Forbidden Changes

列出禁止事项：

- 不新增无关技术栈。
- 不自动提交 Git。
- 不删除 Golden Case。
- 不降低测试断言。
- 不将 Prompt 写死在业务函数中。

## Acceptance Criteria

用可验证语言写完成标准。

```text
- python -m pytest 通过。
- Golden Case 可运行。
- Run Trace 包含 prompt_version、model、input_snapshot、validated_output。
- 输出通过 Schema 校验。
```

## Test Commands

```bash
python -m pytest
```

如果有 Eval：

```bash
python -m pytest tests/evals
```

## Golden Case

指定必须运行的真实样例：

```text
data/golden_cases/car_vacuum_v1/
```

## Required Final Report

Codex 最终必须报告：

- 修改文件。
- 调用链变化。
- 新增测试。
- 测试结果。
- Golden Case 结果。
- Run Trace 路径。
- 剩余风险。
- 明确没有做什么。
