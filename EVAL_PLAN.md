# EVAL_PLAN

Eval 的目标不是让模型“看起来不错”，而是证明系统变更是否真的改善了业务结果。

## Eval 类型

### 1. Schema Eval

检查模型输出是否能通过结构化校验。

指标：

- Schema 通过率
- 缺失字段率
- 无效 ID 引用率
- JSON 解析失败率

### 2. Source Trace Eval

检查来源链是否完整。

指标：

- `CreativeIdea.source_usages` 完整率
- 不存在来源引用数
- `ScriptDraft` 超出选中创意来源的次数
- 事实主张可追溯率

### 3. Claim Guard Eval

检查是否编造商品事实或夸大卖点。

指标：

- 商品事实幻觉率
- 禁用表达命中数
- 未支撑卖点数
- 与 ProductFact 冲突数

### 4. RAG Eval

检查检索是否有帮助。

指标：

- Top-K 有效率
- 误召回率
- 知识使用率
- 有 RAG / 无 RAG 创意评分差异
- RAG 是否引入错误事实

### 5. Creative Quality Eval

人工评分创意质量。

指标：

- Hook 平均分
- 可拍摄性平均分
- 创意重复率
- 人工选择率
- 参考借鉴质量

### 6. Script Quality Eval

人工评分剧本质量。

指标：

- 剧本完整度
- TikTok 节奏适配
- 返工率
- 审核通过率
- 可拍摄性

## 初始 Eval Cases

至少准备：

1. 标准车载吸尘器案例。
2. 没有参考视频的案例。
3. 卖点缺少事实支撑的案例。
4. 参考视频与商品不匹配的案例。
5. RAG 检索出错误品类的案例。
6. 商品存在禁止表达的案例。
7. 创意重复风险案例。
8. 剧本偏离选中创意的案例。
9. 模型引用不存在来源的案例。
10. 审核返工案例。

## A/B 对照

Phase 3 开始必须支持：

```text
A: 不使用 RAG
B: 使用 RAG
```

比较：

- 创意丰富度
- 来源完整性
- 事实准确性
- Hook 质量
- RAG 误召回
- 成本和耗时

## 每次重要变更必须记录

```text
evals/results/YYYY-MM-DD-change-name.md
```

包含：

- 变更内容
- 使用模型
- Prompt 版本
- Case 列表
- 指标结果
- 人工观察
- 是否接受变更
