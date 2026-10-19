# DrinkZen 三源同步

`drinkzen-site` 将作为 DrinkZen 产品运营站点；本站保留并继续独立运营，饮品资料复制到目标仓库后按产品模块再加工。定位见 [产品方案](DRINKZEN-SITE-PRODUCT-BRIEF.md)，步骤见 [内容复制计划](DRINKZEN-SITE-MIGRATION-PLAN.md)。不执行旧站退役、URL 重定向或自动双向覆盖。以下为本站现有创作流程。

当前工作流维护在 [DrinkZen 运营闭环](../.claude/skills/drinkzen/references/operations.md)，证据规则见 [数据方案](../.claude/skills/drinkzen/references/search-guide.md)。

| 来源 | 职责 | 关联依据 |
| --- | --- | --- |
| 品牌官方小程序 | 饮品身份、选项、默认值与地区菜单事实 | 菜单项 ID、截图与采集日期 |
| xiaolin-life origin | 证据整理、营养依据、作者记录、唯一共用 plog | 稳定的 brand/slug |
| DrinkZen 后台 | 产品与规格的结构化数据 | 实际产品 ID，不由 slug 推定 |
| 小红书 / 大众点评 | 同一文案分别发布 | 两条真实发布链接与版本记录 |

不再维护独立社媒草稿目录或用 ai-todo 作为发布事实来源。台账保存在 `data/drinkzen-operations.json`，历史链接不明时保持未登记。菜单或正文变化后核对后台、共用 plog、配图和两个平台，实际修正完成后再更新台账。

DrinkZen 源码 CLI 0.6.0 已含产品与规格操作，使用前核对实际环境与参数。Hugo draft 默认值和自动发布门禁待定；本站 draft 不决定目标站的公开状态。
