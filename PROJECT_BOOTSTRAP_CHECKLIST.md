# PROJECT_BOOTSTRAP_CHECKLIST

新建 `tk-script-agent-lab` 前后按此清单执行。

## 1. 仓库创建

- [ ] 创建独立仓库 `tk-script-agent-lab`。
- [ ] 不在旧项目中继续重构。
- [ ] 初始化 Git。
- [ ] 创建 `.gitignore`。
- [ ] 创建 Python 3.12 虚拟环境。
- [ ] 配置 `pyproject.toml`。
- [ ] 确认 `python -m pytest` 可执行。

## 2. 基础文档

- [ ] `README.md`：项目目标、真实业务链、非目标。
- [ ] `AGENTS.md`：Codex 长期规则。
- [ ] `ARCHITECTURE.md`：目标架构和边界。
- [ ] `LEARNING_ROADMAP.md`：六阶段学习路线。
- [ ] `DECISION_LOG.md`：关键决策。
- [ ] `TECHNOLOGY_PURPOSE.md`：技术目的表。

## 3. 任务合同

- [ ] `TASK_CONTRACT_TEMPLATE.md` 存在。
- [ ] `task_contracts/TEMPLATE.md` 存在。
- [ ] 每次 Codex 任务前复制模板。
- [ ] 一个任务只实现一个纵向能力。

## 4. Golden Case

- [ ] `data/golden_cases/car_vacuum_v1/product_profile.json`
- [ ] `data/golden_cases/car_vacuum_v1/product_facts.json`
- [ ] `data/golden_cases/car_vacuum_v1/selling_points.json`
- [ ] `data/golden_cases/car_vacuum_v1/reference_videos.json`
- [ ] `data/golden_cases/car_vacuum_v1/expected_requirements.md`
- [ ] `data/golden_cases/car_vacuum_v1/review_rubric.md`

## 5. Eval 和 Trace

- [ ] `EVAL_PLAN.md` 存在。
- [ ] `FAILURE_TAXONOMY.md` 存在。
- [ ] `RUN_TRACE_SPEC.md` 存在。
- [ ] `evals/` 目录存在。
- [ ] `run_traces/` 目录存在。

## 6. 成本和安全

- [ ] `.env.example` 存在。
- [ ] `COST_AND_SAFETY_LIMITS.md` 存在。
- [ ] 默认关闭真实模型调用。
- [ ] 默认关闭批量运行。
- [ ] 默认关闭外部写入。
- [ ] API Key 不提交。

## 7. 旧项目冻结

- [ ] `OLD_PROJECT_FREEZE_NOTE.md` 存在。
- [ ] 旧项目只作为业务参考。
- [ ] 不复制旧项目复杂治理结构。
- [ ] 不迁移旧 Mock 文案作为真实能力。

## 8. 第一轮开发前确认

- [ ] 我能说清楚项目目标。
- [ ] 我能说清楚第一阶段不做什么。
- [ ] 我有一个真实车载吸尘器样例。
- [ ] 我知道下一次 Codex 任务只做 Phase 1。
- [ ] 我不会第一轮就要求 Codex 同时做 RAG、LangGraph 和 Tool Calling。
