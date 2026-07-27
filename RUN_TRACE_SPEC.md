# RUN_TRACE_SPEC

Run Trace 用来回答：一次输出为什么会这样生成，模型看到了什么，RAG 召回了什么，人工如何选择，成本是多少，哪里失败。

## 最小 RunTrace 字段

```json
{
  "run_id": "run_20260726_0001",
  "created_at": "2026-07-26T00:00:00Z",
  "phase": "creative_generation",
  "status": "completed",
  "model_provider": "openai",
  "model_name": "example-model",
  "prompt_versions": {
    "reference_analyst": "v1",
    "creative_planner": "v1",
    "script_writer": "v1"
  },
  "input_snapshot": {},
  "retrieved_knowledge": [],
  "model_calls": [],
  "validated_outputs": {},
  "human_selection": null,
  "human_review": null,
  "token_usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0
  },
  "estimated_cost_usd": 0.0,
  "errors": []
}
```

## ModelCall 记录

每次模型调用至少保存：

```text
call_id
step_name
model_provider
model_name
prompt_version
input_snapshot
raw_output
parsed_output
schema_validation_result
started_at
finished_at
duration_ms
token_usage
estimated_cost_usd
error
```

## RetrievedKnowledge 记录

每次检索至少保存：

```text
retrieval_id
query
metadata_filter
top_k
results[]
```

每条结果：

```text
knowledge_id
knowledge_type
title
score
metadata
source
used_by_step
```

## Human Selection 记录

```text
selected_idea_id
rejected_idea_ids
selection_reason
selected_at
operator
```

## Human Review 记录

```text
review_status: approved | rework | hold | rejected
review_notes
failure_codes
reviewed_at
operator
```

## Trace 保存规则

- Trace 中不得保存真实 API Key。
- 原始模型输出可以保存，但后续需要支持脱敏。
- 每个导出文件应能反查 `run_id`。
- 每个 `CreativeIdea` 和 `ScriptDraft` 应能反查生成它的 Step。

## Trace 检查问题

- 模型使用了哪个 Prompt？
- RAG 召回了哪些知识？
- CreativeIdea 为什么引用这些来源？
- ScriptDraft 是否只使用选中创意？
- 成本是否超限？
- 失败发生在模型、Schema、RAG、校验还是人工审核？
