# DrinkZen 运营闭环

## 唯一内容与记录位置

- 菜单事实：品牌官方小程序的具体单品与选项，保留地区/门店、截图和采集日期。
- 内容原稿：`content/drinkzen/<brand>/<slug>/index.md`，含唯一共用 plog。
- 后台关联：DrinkZen 实际产品 ID，不用相同 slug 推定已经关联。
- 运营台账：项目 `data/drinkzen-operations.json`，内部记录，不放进 Hugo content，不记录密钥。
- 状态查看：项目根目录运行 `python3 scripts/drinkzen-operations.py status`。未登记记录显示“未核实”，不能从 `draft: false` 或 `platforms` 推断发布成功。

## 工作流

| 环节 | 产出 | 记录方式 |
| --- | --- | --- |
| 菜单核实 | 单品、默认配置、可选项、地区与采集时间 | origin 数据依据；台账 menu_evidence / menu_checked_at |
| 内容整理 | 有证据的数字、未知项、评级依据、作者体验 | origin；单份共用 plog |
| 后台核对 | 产品 ID、差异、待录入内容 | 台账 product_id / followup；实际写入仍遵循 admin SOP |
| 发布 | 同一文案分别在两平台发布 | 实际链接、时间、origin/plog 版本摘要 |
| 纠错 | 变更原因、影响平台、修正结果 | 内容变化自动列为待同步；修正后重新登记 |
| 复盘 | 平台表现、可归因的小程序行为、下一次实验 | 各条发布记录下的 metrics 和 note |

## 台账操作

台账初始为空，历史发布状态不做推断。命令只维护本地记录，不调用社媒或后台写 API。

```bash
# 查看含 plog 的文章、缺失记录和版本变化
python3 scripts/drinkzen-operations.py status

# 根据真实证据登记关联信息；仅在确已核实时填日期和资料
python3 scripts/drinkzen-operations.py link --article content/drinkzen/manner/latte/index.md --product-id PRODUCT_ID --menu-evidence EVIDENCE_PATH --menu-checked-at YYYY-MM-DD

# 发布或线上修正完成后登记，每个平台各一条；链接与时间必须是真实值
python3 scripts/drinkzen-operations.py record --article content/drinkzen/manner/latte/index.md --platform xiaohongshu --url ACTUAL_URL --published-at ISO_DATETIME --note 实际发布或纠错原因

# 使用观测时间区分累计数据；未知值不填，不能当 0
python3 scripts/drinkzen-operations.py metrics --article content/drinkzen/manner/latte/index.md --platform xiaohongshu --observed-at ISO_DATETIME --views 100 --likes 5 --saves 2 --note 示例数值需替换
```

菜单证据与日期成对登记；`link` 也支持只登记产品 ID 或只登记菜单证据，其他字段保持未知。

```bash
# 外部菜单变化还未反映到正文时，先登记跟进事项
python3 scripts/drinkzen-operations.py note --article content/drinkzen/manner/latte/index.md --text 菜单已变更，待核对正文和后台

# 实际处理完成后清除当前跟进事项，不代替两平台发布记录
python3 scripts/drinkzen-operations.py note --article content/drinkzen/manner/latte/index.md --resolved
```

旧的 `scripts/migrate_drinkzen_plog.py` 仅用于历史内容迁移，不属于当前运营入口，不从它创建新草稿或新平台版本。

`record` 只在用户提供真实链接/时间或明确确认实际发布、线上修改完成后使用；不能在仅生成文案时执行。记录 origin 与 plog 的 SHA-256 摘要、链接和时间，历次发布/纠错记录保留在 history。菜单证据和后台产品 ID 不明时保持 null；“关联产品”不代表已同步后台字段。

`status` 会分别显示未登记、待同步和已登记当前版本；后者仅表示本地版本与记录相符，不代表已抓取线上内容核验。台账须与内容一起备份/提交，不能将发布前文件当作发布成功记录。

## 变更与纠错

1. 官方菜单、营养证据或作者体验变化时，修正 origin、共用 plog、封面及评论；写明变更原因。
2. `status` 检出 origin 或 plog 摘要不同后，两个已发布平台分别待同步。菜单发生变化而文本尚未修改时，也应在台账 followup 明确登记待办，不能仅依赖摘要发现外部变化。
3. 核对后台实际字段；支持的操作先 dry-run，未支持的在后台 UI 人工处理。关联记录不假装已写入成功。
4. 用户在平台完成修正后，再用 `record` 登记链接和实际修正时间；history 保留旧版本记录。
5. 无法修改旧内容时，记录需补充说明/撤回的处理计划；不把待处理项写成已解决。

## 复盘口径

发布后可在约 24 小时、7 天收集数据；这只是比较窗口，不新增定时任务。记录 views、likes、saves、comments、profile_visits、miniapp_visits、product_queries 及观测时间。平台未提供或无法归因的值为 null。

比较收藏/浏览、互动/浏览等同分母指标；仅有点赞数不能推出点击率。小程序访问、搜索和留存需要实际埋点或来源证据，不能由笔记浏览量推算。每轮记录一个假设、实际改动、观察结果和下一步，先比较相近选题和窗口。

## 待定与 CLI 能力缺口

- Hugo 默认 draft、内容完整性是否自动阻断发布：待用户决定，本轮只记录与提示。
- 当前 CLI 可维护品牌、菜单模板、Logo 和审核任务；本机 0.4.0，实际能力以 `--help` 和实现为准。
- 产品查询/规格读取、营养来源录入、稳定产品 ID、菜单版本与差异、批量同步、写后读回：需要在 DrinkZen 项目确认接口后再决定升级。
- review dry-run 是本地提案预览，不等同于服务端校验成功。CLI 升级需另行实施，不编造尚不存在的命令。
