---
name: drinkzen
description: 饮品运营三件套：Hugo 品牌页/单杯测评创建、drinkzen.cn 后台维护、小红书/大众点评 plog 分发。触发词：奶茶、品牌页、饮品测评、菜单模板、Logo、DrinkZen、plog、审稿。
allowed-tools: Bash(drinkzen-admin:*)
license: MIT
metadata:
  version: "2.0.0"
  author: xiaolin
  tags: ["drinkzen", "beverage", "tea", "milktea", "brand", "plog"]
---

# DrinkZen

饮品端到端工作流：① Hugo 站点内容创作 ② drinkzen.cn 平台后台 ③ 社媒 plog 分发。

## 子模块

| 子模块 | 路径 | 覆盖场景 |
| --- | --- | --- |
| **content** | [references/content.md](references/content.md) | 品牌页 / 单杯详情页 / 模板 / 命名规范 |
| **admin** | [references/admin.md](references/admin.md) | `drinkzen-admin` CLI / 品牌资料 / 菜单模板 / Logo / 投稿审阅 |
| **social** | [references/README.md](references/README.md) | plog 模板入口 + 工作流 + 标题公式 |

## ⚠️ 安全提示

`drinkzen-admin` 写操作必须先 `--dry-run` + `--json` 输出给用户审阅，确认后再正式执行。详见 [admin 子模块](references/admin.md) 顶部安全铁律。