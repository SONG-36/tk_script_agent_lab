# GOLDEN_CASE_GUIDE

Golden Case 是本项目最重要的学习资产。它不是测试数据的附属品，而是每次判断系统是否真的可用的固定业务样例。

## Golden Case 目标

第一版 Golden Case 使用车载吸尘器，验证系统是否能完成：

```text
商品资料
→ 商品事实
→ 卖点
→ 参考视频
→ 参考洞察
→ 知识库检索
→ 5 条 CreativeIdea
→ 人工选择
→ ScriptDraft
→ 人工审核
→ 导出和 Trace
```

## 目录结构

```text
data/golden_cases/car_vacuum_v1/
├── product_profile.json
├── product_facts.json
├── selling_points.json
├── reference_videos.json
├── expected_requirements.md
└── review_rubric.md
```

## 编写原则

### ProductProfile

记录当前商品的权威资料。模型不得改写。

必须包含：

- 商品名称
- 品类
- 目标市场
- 目标用户
- 使用场景
- 禁止表达
- 语气偏好

### ProductFacts

记录事实，不写营销夸张。

示例：

```text
包含缝隙吸嘴
Type-C 充电
适合清理车内缝隙和座椅表面碎屑
```

### SellingPoints

每个卖点必须引用一个或多个 `ProductFact`。

错误示例：

```text
清洁力行业第一
```

除非有事实或证据支撑，否则不能写成卖点。

### ReferenceVideos

第一版可以人工输入摘要，不需要自动抓取 TikTok。

必须包含：

- URL 或来源
- 标题
- 平台
- 人工摘要
- 可借鉴点
- 不能复制的内容

## 每次运行后的检查

- 创意是否真的关联商品事实？
- 创意是否使用了卖点？
- 创意是否借鉴参考视频模式，而不是复制？
- 剧本是否只基于选中创意？
- 是否有不存在的产品功能？
- SourceUsage 是否能解释来源如何被使用？
- 导出是否保留来源链？

## Golden Case 不等于 Eval 全集

Golden Case 是第一条固定主案例。后续 Eval 需要增加更多异常情况和边界情况。
