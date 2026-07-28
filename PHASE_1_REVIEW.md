# Phase 1 Review

## 1. 阶段目标

Phase 1 的目标是建立一个没有真实 LLM 的最小可审计闭环：从固定 Golden Case 读取商品、事实、卖点和参考视频，通过固定 output fixture 与 Fake Provider 走完整 Provider 契约，保留人工创意选择，并用确定性代码验证和导出结果。

这个阶段不是证明模型质量，而是证明业务对象、边界、校验和测试方法已经足够清晰，后续接入真实模型时不会绕过人工闸门或 Schema 校验。

## 2. 已完成能力

- Golden Case JSON 加载为 Pydantic 领域对象。
- 商品版本、ID 唯一性和基础引用关系由确定性代码校验。
- 固定 ReferenceInsight、CreativeIdea 和 ScriptDraft fixture 可以加载并校验。
- Provider Protocol 已定义，pipeline 依赖协议而不是具体 Fake 类。
- Fake Provider 返回 fixture deep copy，不使用网络、随机数、时间或 API Key。
- 人工 `selected_idea_id` 必须显式传入，系统不会自动选择创意。
- ScriptDraft 必须匹配人工选择、所选创意、Scene 卖点、fact 支持关系和 SourceUsage。
- Phase 1 结果可以稳定导出为 `phase1_result.json`。

## 3. 当前完整数据流

```text
Golden Case JSON
→ load_golden_case
→ GoldenCase
→ Output Fixture JSON
→ load_output_fixtures
→ OutputFixtureSet
→ Fake Provider
→ Provider Protocol
→ prepare_creative_options
→ CreativeOptions
→ 人工 selected_idea_id
→ generate_selected_script
→ ScriptDraft
→ export_phase1_result
→ Schema 重校验
→ 跨对象校验
→ phase1_result.json
→ 重新读取验证
```

## 4. AI 产品经理六问

### 4.1 数据从哪里进来

当前数据只来自三处：

- Golden Case JSON；
- 固定 Output Fixture JSON；
- 人工 `selected_idea_id`。

Golden Case 提供商品资料、商品事实、卖点和参考视频。固定 Output Fixture 提供 ReferenceInsight、CreativeIdea 和 ScriptDraft。人工选择决定哪条 CreativeIdea 进入剧本生成。

### 4.2 中间经过哪些转换

```text
JSON
→ Pydantic 模型
→ GoldenCase / OutputFixtureSet
→ Fake Provider
→ Provider Protocol
→ CreativeOptions
→ 人工选择
→ ScriptDraft
→ Schema 重校验
→ 跨对象校验
→ phase1_result.json
```

每一步都保留明确对象边界。fixture 不是直接写入导出文件，而是经过 Provider 契约、pipeline 和 shared validators。

### 4.3 哪一步由模型完成

Phase 1 没有真实 LLM。

Fake Provider 不是模型生成，也不模拟智能能力。它只在未来模型节点的位置返回固定 fixture，用于验证接口、校验和调用链。

### 4.4 哪一步必须由确定性代码完成

以下职责必须由代码完成：

- Schema；
- ID 唯一；
- 引用存在；
- 商品版本；
- 人工选择；
- Scene 卖点边界；
- fact 支持关系；
- SourceUsage；
- Provider 输出重校验；
- 稳定 JSON 导出。

这些规则不能交给模型自行判断，因为它们是合同、引用和安全边界，不是文案生成问题。

### 4.5 系统可能在哪里说谎

当前系统仍可能在这些位置说谎：

- 商品事实可能不真实；
- ReferenceInsight 文字可能不忠实；
- 合法 CreativeIdea 不代表创意优秀；
- 合法 ScriptDraft 不代表 TikTok 转化好；
- SourceUsage 合法不代表自由文本完全忠实；
- fixture 结果不代表真实模型能力；
- Golden Case 成功不代表生产数据全部成功。

Phase 1 的测试只能证明结构、引用和调用链，不证明内容事实和商业效果。

### 4.6 如何证明它做对了

当前证据来自自动测试、Golden Case E2E 和人工运行：

- 无 LLM 确定性闭环；
- Provider 可替换；
- 人工选择不能被绕过；
- 非法输出被拒绝；
- 相同输入导出一致；
- Golden Case E2E 可落盘并重新读取。

这些证据覆盖了 Phase 1 的工程合同，但不覆盖真实模型质量。

## 5. 当前已证明

- Golden Case 和 output fixture 能加载为明确 Schema。
- shared validators 能拒绝重复 ID、缺失引用、版本错配和 Schema 漂移。
- Fake Provider 可通过协议接入 pipeline。
- 人工选择是显式输入，剧本不能绕过所选 CreativeIdea。
- ScriptScene 的 selling point 和 fact 引用受到所选创意与卖点支持关系限制。
- SourceUsage 必须对应实际可引用来源。
- `phase1_result.json` 对相同输入字节级一致。
- 当前完整闭环不需要网络、API Key、随机数、当前时间或真实 LLM。

## 6. 当前尚未证明

- 商品真实性；
- 真实 LLM 质量；
- Prompt 效果；
- Token 和成本；
- 模型失败恢复；
- TikTok 业务效果；
- 生产级多案例稳定性。

这些能力属于后续阶段，不能从 Phase 1 closeout 的成功中推导出来。

## 7. Phase 1 结论

Phase 1 已证明：在没有真实 LLM 的情况下，商品资料、固定参考洞察、固定创意候选、人工创意选择、固定剧本、确定性校验和 JSON 导出可以形成一个可测试、可重复、可审计的最小闭环。

Phase 1 没有证明：真实模型可以稳定地产生高质量洞察、创意和剧本。

## 8. 进入 Phase 2 前的边界

进入 Phase 2 前仍需保持以下边界：

- 不让模型决定商品事实是否真实；
- 不让模型自动选择最终创意；
- 不让模型批准剧本；
- 不让模型绕过 Pydantic 或 shared validators；
- 不把 Prompt、Token、成本、Trace、RAG 或 LangGraph 伪装成当前已实现能力；
- 接入真实模型前必须保留 Fake Provider 测试作为回归基线。
