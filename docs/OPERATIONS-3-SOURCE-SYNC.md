# 3 源同步运营策略

> 本站点（xiaolin-life）/ drinkzen admin / 小红书 + 大众点评 三源保持同步。自动同步不可达时，由本人手动运营。

## 职责边界

| 源 | 数据形态 | 主要消费 | SoT 角色 |
| --- | --- | --- | --- |
| **xiaolin-life 站点** | 深度评测 + Nutri-Grade + 营养表 + 制作流程 + 原料克重 | 长期 SEO + 完整评估 | **饮品评测 SoT** |
| **drinkzen admin** | 菜单 / 定价 / 库存 / 限定档期 / 门店 | 日常运营决策 | **运营数据 SoT** |
| **小红书 / 大众点评** | 标题 + 800 字 body + 标签 + 评论区置顶 + 图片 | 流量获取 + 用户决策 | **流量出口**（衍生） |

## identifier 关联

三源用同一 `slug` 关联：

- xiaolin-life: `content/drinkzen/<brand>/<slug>/index.md`
- drinkzen admin: `<brand>/<slug>`（slug 与站点一致）
- 小红书草稿: `content/social-publish/drafts/<slug>.md`
- 大众点评短评: 嵌入在小红书草稿的「大众点评」段（同文件）

## 同步规则

| 触发 | xiaolin-life | drinkzen admin | social |
| --- | --- | --- | --- |
| origin 数据更新（热量 / 配方 / 克重）| ✅ 编辑 | ⚠️ 同步相关字段 | ⚠️ 重新生成 XHS 草稿 |
| admin 运营数据更新（定价 / 库存 / 档期）| — | ✅ 编辑 | ⚠️ 重算价格段 |
| social 互动数据（评论 / 点赞）| 可选回灌 | 可选回灌 | — |

⚠️ = 手动同步（自动同步不可达）

## 同步 checklist（每次手动同步时）

1. 确认 slug 一致
2. 校对 origin 数据（热量 / 配方 / 评级）
3. 更新 admin 对应字段
4. 重新生成 / 更新 social 草稿
6. 在三个源 commit（xiaolin-life 站点 / drinkzen admin / social-publish 各自独立仓库或分支）

## 不在范围

- 实时自动同步（差值大、风险高、不值得）
- 大众点评自动发布（API 限制）
- 小红书自动发布（API 限制）

## 相关文档

- 内容分发: `.claude/skills/origin-distribute/SKILL.md`
- 媒体上传: `.claude/skills/media-publish/SKILL.md`
- 内容发布: `.claude/skills/article-create/SKILL.md`
- 草稿目录: `content/social-publish/drafts/`