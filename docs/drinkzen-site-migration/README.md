# DrinkZen 内容复制盘点清单

本目录是 [内容复制与产品站建设计划](../DRINKZEN-SITE-MIGRATION-PLAN.md) 的来源附件，采集日期为 2026-10-18。目录名沿用初版方案，任务范围已改为保留原站、复制资料并在目标站产品化加工。

尚未执行内容复制、验证生产地址或写入数据库。本清单不承担重定向、旧页面退役或 SEO 权重迁移。

## 文件

- `inventory.csv`：243 个 Markdown 源条目，包含 220 个单品页、20 个品牌栏目、1 个总入口和 2 个说明/运营页。
- `aliases.csv`：从当前 front matter 提取的 13 条历史别名，仅作为原文来源关系保留。

CSV 为 UTF-8 编码。复制前重新核对工作区、提交号和媒体文件；盘点包含尚未跟踪的 Manner Latte 营养 JSON，不代表它已进入 Git 备份。

## 字段口径

| 字段 | 含义 |
| --- | --- |
| source_row_id | 按原路径生成的清单行标识，不是产品或未来内容 ID |
| candidate_source_url / candidate_alias_url | 按目录及 front matter 推导的原文候选地址，仅供追溯 |
| source_url_verified / alias_url_verified | 本次均为 false，未核对线上地址 |
| hugo_draft / source_date | 原文状态与文章日期，不等于目标站发布状态或上市日期 |
| has_menu_json / has_nutrition_json | 本机存在对应文件，不代表来源可靠或后台已同步 |
| has_plog | 原文包含共用文案，不代表已在任一平台发布 |
| ledger_entry_exists / known_product_id / known_publication_events | 仅来自当前台账；空 ID 或 0 条记录为未登记，不推断线上事实 |
| proposed_action / proposed_batch | 建议复制与加工用途；公开呈现仍需按产品方案复核 |
| target_module | 拟加工的产品模块类型，不是已实现的路由 |
| target_content_id / target_product_id / target_variant_ids / target_url | 保留给实际关联与目标模块，当前留空；不表示旧地址应重定向 |
| copy_status | 初始 planned；后续可用 copied / reviewed / adapted / published / deferred，复制与公开分别处理 |
| notes | 来源状态、资料限制与待核事项 |

## 使用顺序

1. 确认源文件、未跟踪资料与忽略的 gallery 母本，保存源提交和文件摘要。
2. 复制到目标仓库内部来源档案，核对完整性；原站文件、URL、导航和编辑能力保持现状。
3. 按产品方案将内容拆成模块，核对真实产品/规格 ID、资料来源与公开状态。
4. 分配目标 content_id，记录模块、关联 ID、复制时间、源摘要及目标版本。
5. 经审核的目标模块单独发布；原草稿可以只存内部档案，不自动公开。
6. 两站后续独立编辑，源文变化可进入复核队列，不自动覆盖已加工内容。

一篇原文可对应多个目标模块，多篇原文也可支持同一产品。关系表需保留来源行 ID，不能按名称相似自动合并后台产品。复制社媒历史时保留真实事件，不因两站都有内容而重复登记发布。
