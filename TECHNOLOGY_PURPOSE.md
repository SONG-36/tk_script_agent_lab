# TECHNOLOGY_PURPOSE

本表用于防止技术堆砌。每项技术都必须说明业务是否必需、学习是否需要、何时加入、如何证明有价值。

| 技术 | 业务是否必需 | 学习是否需要 | 加入阶段 | 价值证明 |
|---|---|---|---|---|
| Python 3.12 | 是 | 是 | Phase 0 | 本地测试和应用可运行 |
| Pydantic | 是 | 是 | Phase 1 | Schema 校验阻止无效引用和错误输出 |
| pytest | 是 | 是 | Phase 0 | Golden Case 和回归测试可重复执行 |
| Streamlit | 部分 | 部分 | Phase 1 | 能人工录入、选择和审核，不需要正式前端 |
| Fake Provider | 是 | 是 | Phase 1 | 不依赖 LLM 也能验证业务链 |
| LLM Provider Adapter | 是 | 是 | Phase 2 | 可替换模型，记录模型名、Prompt、Token 和成本 |
| Prompt 文件 | 是 | 是 | Phase 2 | Prompt 可版本化和独立迭代 |
| Structured Output | 是 | 是 | Phase 2 | 模型输出可被 Schema 校验 |
| JSON Run Trace | 是 | 是 | Phase 2 | 可解释一次运行为什么生成该结果 |
| SQLite | 部分 | 是 | Phase 2-4 | Run 可恢复、可查询，复杂度仍可控 |
| RAG | 暂时否 | 是 | Phase 3 | 有 RAG / 无 RAG 对照显示创意质量或规则覆盖提升 |
| 向量索引 | 暂时否 | 是 | Phase 3 | Top-K 检索能找到语义相关 Hook 和结构 |
| Metadata Filter | 是 | 是 | Phase 3 | 防止跨品类、跨平台、跨场景误召回 |
| LangGraph | 暂时否 | 是 | Phase 4 | 能暂停、恢复、返工和记录 Step Trace |
| Tool Calling | 部分 | 是 | Phase 5 | Agent 工具选择有记录且不能越权 |
| Eval | 是 | 是 | Phase 6 | Prompt、RAG、模型变更可以量化比较 |
| 多 Agent 群聊 | 否 | 暂不需要 | Deferred | 无，除非未来出现清晰角色协作收益 |
| FastAPI | 否 | 否 | Deferred | 需要外部系统调用时再加入 |
| React | 否 | 否 | Deferred | 需要正式产品 UI 时再加入 |
| Docker | 否 | 否 | Deferred | 需要部署复现时再加入 |
| 自动发布 TikTok | 否 | 否 | Deferred | 高风险，必须生产阶段另行设计审批 |
