# Expected Requirements: Car Vacuum Golden Case

## Expected CreativeIdea Output

系统应生成 5 条 `CreativeIdea`。

每条至少包含：

- `idea_id`
- `idea_title`
- `core_concept`
- `target_audience`
- `pain_point`
- `hook`
- `story_structure`
- `selling_point_ids`
- `product_fact_ids`
- `reference_insight_ids`
- `source_usages`
- `required_shots`
- `risk_notes`
- `status`

## Required Behavior

- 每条创意必须引用至少 1 个 `ProductFact`。
- 每条创意必须引用至少 1 个 `SellingPoint`。
- 如果使用参考视频模式，必须引用对应 `ReferenceInsight`。
- `SourceUsage` 必须说明来源如何被用于创意。
- 不允许出现未提供的吸力、续航、认证、防水等级或医学清洁效果。
- 不允许复制参考视频原文或完整镜头顺序。

## Expected ScriptDraft Output

基于人工选中的一条 `CreativeIdea` 生成一个剧本。

剧本至少包含：

- `script_id`
- `idea_id`
- `opening_hook`
- `scene_breakdown`
- `voiceover`
- `on_screen_text`
- `product_demo_notes`
- `cta`
- `source_usages`
- `risk_notes`

## Must Reject Or Flag

- 剧本引用未选择创意之外的卖点。
- 剧本新增不存在的产品功能。
- 剧本自动批准。
- RAG 内容覆盖当前商品事实。
- SourceUsage 只列 ID，不解释使用方式。
