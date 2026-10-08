---
name: drinkzen
description: |
  DrinkZen 饮品端到端工作流：① Hugo 站点内容创作（品牌页、详情页、模板、命名规范）
  ② 同步到 drinkzen.cn 平台（菜单模板、Logo 核验、用户投稿审阅）。
  触发：新建/更新品牌页、单杯饮品测评、奶茶品牌、茶饮页面、饮品测评、
  同步到平台、审稿、菜单模板变更、Logo 上传、DrinkZen。
metadata:
  version: "1.2.0"
  author: "xiaolin"
  tags: ["drinkzen", "beverage", "tea", "milktea", "brand", "drinks", "admin"]
---

# DrinkZen

饮品从本地 Hugo 站点到 DrinkZen 平台的双侧工作流。

## 子模块

| 子模块 | 路径 | 覆盖场景 |
| --- | --- | --- |
| **内容创作** | [references/content.md](references/content.md) | 品牌页、单杯详情页、模板、命名规范、并行创建、Git 提交 |
| **平台同步** | [references/admin.md](references/admin.md) | `drinkzen-admin` CLI、品牌资料、菜单模板、Logo、用户投稿审阅 |
| **搜索策略** | [references/search-guide.md](references/search-guide.md) | 关键词组合、数据源优先级、热量数据格式 |

## 路径选择

| 用户意图 | 进入 |
| --- | --- |
| 新建/更新品牌页或单杯饮品测评 | [content.md](references/content.md) |
| 同步 Hugo 数据到 drinkzen.cn 平台 | [admin.md](references/admin.md) |
| 审阅用户投稿、变更菜单模板、上传 Logo | [admin.md](references/admin.md) |
| 搜索某品牌/饮品数据 | [search-guide.md](references/search-guide.md) |

## ⚠️ 安全提示

任何 `drinkzen-admin` 写操作（`update` / `set-logo` / `apply` / `resolve`）**必须**先 `--dry-run` + `--json` 输出给用户审阅，确认后再正式执行。详见 [admin.md](references/admin.md) 顶部安全铁律。
