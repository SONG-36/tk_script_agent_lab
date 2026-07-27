# tk-script-agent-lab

`tk-script-agent-lab` 是一个学习型 TikTok Script Agent Lab。它不是生产级短视频平台，也不是通用 Agent 平台，而是用一个真实业务场景练习 AI 产品经理在 Agentic Engineering 时代的工作方式。

- [System Map](SYSTEM_MAP.md)

## 项目目标

通过「TikTok 商品短视频创意与剧本生成」这条纵向业务链，完整练习：

- 业务建模：`ProductProfile`、`ProductFact`、`SellingPoint`、`ReferenceVideo`、`ReferenceInsight`、`CreativeIdea`、`SourceUsage`、`ScriptDraft`
- Context Engineering：区分权威任务上下文和可检索知识上下文
- Structured Output：让模型输出可校验的结构化对象
- RAG：用小型知识库支撑 Hook、剧本结构、创意模式和平台规则检索
- LangGraph：学习 `State`、`Node`、`Edge`、`Interrupt`、`Resume`、`Checkpoint`
- Tool Calling：学习工具 Schema、权限、副作用和工具调用 Trace
- Human-in-the-loop：人工选择创意、人工审核剧本
- Eval：用 Golden Case 和失败分类证明系统是否真的变好
- Agentic Coding：用任务合同驱动 Codex 开发，而不是逐函数手写

## 真实业务链

```text
商品资料
→ 商品事实
→ 商品卖点
→ 参考视频
→ 参考洞察
→ 知识库检索
→ 创意表 CreativeIdea[]
→ 人工选择一条 CreativeIdea
→ 生成 ScriptDraft
→ 人工审核
→ 导出 JSON / Markdown
→ 保存 Run Trace
```

## 第一阶段范围

第一阶段只支持一个 Golden Case：车载吸尘器。

- 1 个商品
- 5-10 条商品事实
- 3-5 个卖点
- 3 条参考视频文字资料
- 20-30 条知识库记录
- 生成 5 条创意
- 人工选择 1 条
- 生成 1 个完整 TikTok 剧本
- 记录一次完整运行 Trace

## 明确非目标

初期不做：

- 多用户、账号、权限系统
- FastAPI、React、正式后台
- Docker、Redis、消息队列
- 自动抓取 TikTok
- 自动发布 TikTok
- 视频生成
- 多 Agent 群聊
- 通用知识管理后台
- 通用 Agent Memory
- 大规模生产级 RAG 平台
- 复杂多模型路由

## 核心纪律

1. 先跑通纵向闭环，再增加横向复杂度。
2. 知识库可以早建，但 RAG 只能是辅助工具，不是系统中心。
3. LangGraph 是学习 State 和 Human Gate 的工具，不是让模型自由接管业务。
4. 商品事实、人工选择、人工审核、导出和安全限制必须由确定性代码控制。
5. 每一阶段都必须有测试、Golden Case、Run Trace 和个人复盘。

## 推荐初始命令

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
```
