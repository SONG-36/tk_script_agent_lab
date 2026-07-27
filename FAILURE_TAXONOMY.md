# FAILURE_TAXONOMY

失败分类用于把“感觉不好”转成可追踪、可复盘、可优化的问题。

| Code | 名称 | 定义 | 常见修复方向 |
|---|---|---|---|
| F01 | 商品事实幻觉 | 输出出现 ProductFact 中不存在或相冲突的商品功能、参数、效果 | Claim Guard、Prompt 限制、事实引用校验 |
| F02 | 卖点无事实支持 | SellingPoint 或剧本主张没有绑定 ProductFact | 强制 selling_point.fact_ids 校验 |
| F03 | 引用不存在 | SourceUsage、CreativeIdea 或 ScriptDraft 引用不存在的 ID | 引用完整性校验 |
| F04 | SourceUsage 不完整 | 只列 source_id，未说明 used_in、usage_role 或 derived_statement | SourceUsage Schema 收紧 |
| F05 | 创意重复 | 多条 CreativeIdea 核心机制相同，只是换标题 | 去重校验、Prompt 增加差异化要求 |
| F06 | Hook 弱 | 前 3 秒缺少冲突、画面或即时价值 | HookPattern 检索、Hook Rubric |
| F07 | 剧本偏离创意 | ScriptDraft 重新发明方向，没有基于选中 CreativeIdea | Script Writer 输入约束和校验 |
| F08 | 参考视频复制风险 | 过度复刻参考视频文案、镜头或创意 | ReferenceInsight 中区分 borrow vs do_not_copy |
| F09 | RAG 误召回 | 检索到错误品类、平台或场景的知识 | Metadata Filter、Top-K 调整、重排序 |
| F10 | 输出 Schema 错误 | 模型输出无法解析或字段类型不正确 | Structured Output、Retry、Prompt 示例 |
| F11 | 禁用表达 | 输出包含 prohibited_claims 或平台高风险表达 | PlatformRule、禁止词检查 |
| F12 | 成本超限 | 单次运行模型调用、Token 或成本超过限制 | Cost Guard、最大步数、缓存 |
| F13 | 工具越权 | Agent 调用不该调用的写工具或高风险工具 | Tool 权限、Human Gate |
| F14 | 人工闸门绕过 | 未经选择或审核直接进入下一步 | Workflow State 校验 |
| F15 | Trace 不完整 | 运行后无法还原输入、Prompt、模型、检索或输出 | RunTrace 必填字段校验 |

## 使用规则

- 每次人工审核至少记录一个失败分类，除非完全通过。
- 每次 Eval 统计失败分类分布。
- 修复优先级按业务风险排序，不按实现难度排序。
