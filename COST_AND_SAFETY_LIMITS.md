# COST_AND_SAFETY_LIMITS

学习项目也必须有成本和安全边界。没有上限的 Agent 是低级风险。

## 环境变量

真实密钥只放本地 `.env`，不得提交。

`.env.example` 只声明变量名和说明。

## 初始限制

建议默认值：

```text
MAX_MODEL_CALLS_PER_RUN=8
MAX_AGENT_STEPS_PER_RUN=12
MAX_RETRIES_PER_STEP=2
MAX_INPUT_TOKENS_PER_CALL=20000
MAX_OUTPUT_TOKENS_PER_CALL=4000
MAX_COST_USD_PER_RUN=1.00
ENABLE_REAL_MODEL_CALLS=false
ENABLE_BATCH_RUNS=false
ENABLE_EXTERNAL_WRITES=false
```

## 禁止行为

- 不允许后台循环调用模型。
- 不允许自动批量生成大量剧本。
- 不允许 Agent 自动批准剧本。
- 不允许 Agent 自动发布或写入 TikTok。
- 不允许 Agent 修改权威商品事实。
- 不允许跳过 SourceUsage 校验。
- 不允许把其他商品的事实当成本商品事实。

## 高风险操作必须人工确认

- 批量生成。
- 重新运行所有 Eval。
- 使用昂贵模型。
- 写入外部平台。
- 覆盖已有导出。
- 删除 Run Trace。

## 成本记录

每次 Run Trace 必须记录：

```text
model_name
input_tokens
output_tokens
total_tokens
estimated_cost_usd
model_call_count
retry_count
```

## 超限处理

如果接近或超过限制：

1. 当前 run 标记为 `failed_cost_limit`。
2. 停止后续模型调用。
3. 保存已完成 Trace。
4. 在 UI 显示明确错误。
5. 不自动重试。

## 安全检查

每次 ScriptDraft 导出前必须检查：

- 是否绑定选中 CreativeIdea。
- 是否使用不存在的 ProductFact。
- 是否包含 prohibited_claims。
- 是否包含未支持的功效承诺。
- 是否通过人工审核。
