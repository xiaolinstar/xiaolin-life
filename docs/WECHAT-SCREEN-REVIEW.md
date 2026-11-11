# 光影人生：影评写作与微信公众号发布

> 以站点 `content/screen/` 为唯一正文源，再用固定版式导出公众号稿。  
> 已跑通样例：《肖申克的救赎》→ 公众号《肖申克的救赎》：体制之恶，对个人主义的抹杀。  
> Agent Skill：`.claude/skills/wechat-screen-review/` —— **仅当明确要求生成公众号文章时**才渲染 HTML；日常改站点影评不触发。

## 1. 原则

1. **先站内，后公众号**：观点、结构、配图与图注先在 Hugo 页写定并预览；公众号是分发，不另起一版正文。日常只改 Markdown，不要「顺便」导出。
2. **字段拆开**：公众号「标题 / 摘要 / 封面 / 正文」四件事分开准备，避免把观点标题再贴进正文当大标题。
3. **版式固定**：纸页留白（浅底、近黑字、宋体标题、金句左竖线、图下图注），原生编辑器可粘贴。
4. **媒体分工**：正文插图用 CDN URL；封面优先用站点 `featured.jpg` 本地上传（不一定已上 CDN）。

## 2. 写作（站点）

### 2.1 建稿

```bash
bin/hugo new content --kind screen screen/<work-slug>/index.md
```

- 模板：`archetypes/screen.md`
- 栏目约定与搜索说明见 [content-search.md](content-search.md)
- 媒体命名与上传见 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)、[MEDIA-OSS.md](MEDIA-OSS.md)

### 2.2 Front matter 与公众号字段的对应

| 站点字段 | 用途 | 公众号怎么用 |
| --- | --- | --- |
| `title` | 片名 · 年份（站内标题） | 正文里用《片名 · 年份》识别作品；**不是**公众号主标题的全部 |
| `summary` | 40～60 字观点钩子 | **摘要**（列表/转发）；建议总长仍落在约 54～120 字舒适区 |
| `description` | SEO / 导语备选 | `summary` 缺失时导出脚本可回退到它 |
| `featureimage: featured.jpg` | 站内封面 | **公众号封面**：导出时复制为 `docs/wechat/<slug>-cover.jpg` 后本地上传 |
| 正文 CDN 图 | 论证配图 | 粘贴正文时尽量保留；丢失则按同一 URL 补插 |

### 2.3 正文结构（保持可导出）

1. **作品信息**（引用块两行：主创 / 类型片长上映）
2. **评分推荐**（表格五维 + 综合；导出时改成一行文字，避免原生编辑器丢表）
3. **开篇短评**（评分表后第一段，进入公众号正文）
4. **剧情简介** → **影评正文**（小标题按观点写，不必按「主题/表演/视听」填空）
5. **金句**：英文 + 中文译句放在同一引用块
6. **配图**：`![alt](CDN)`，空一行后 `*图注*`（斜体一行）
7. **收束**：个人思考；可加站内文末署名感

写的时候就按这个结构，后面导出几乎不用手工改 HTML。

### 2.4 标题策略（公众号）

- 格式推荐：**《片名》：观点句**  
  例：`《肖申克的救赎》：体制之恶，对个人主义的抹杀`
- 备选：`片名｜观点句`
- 要求：一眼能看出是哪部作品，同时带出本文论点；不要只写片名，也不要只写抽象观点。

## 3. 导出公众号发布包

### 3.1 命令

```bash
# 导出：总是按当前 Markdown 全量重渲（覆盖旧 HTML）
python3 scripts/wechat_screen_review.py content/screen/<slug>/index.md \
  --title '《片名》：观点句'

# 审查：HTML 是否仍新于 MD / featured.jpg（过期则 exit 1）
python3 scripts/wechat_screen_review.py content/screen/<slug>/index.md --check
```

默认输出（**本地产物，已 gitignore，勿入库**）：

- `docs/wechat/<slug>.html` — 发布包（标题 / 摘要 / 正文分区 + 一键复制）
- `docs/wechat/<slug>-cover.jpg` — 从站点 `featured.jpg` 复制的封面

入库只保留：`docs/wechat/screen-review-template.html`、`.gitkeep`，以及脚本 / Skill / 本文。

### 3.1.1 为何不入库 HTML（防「改了 MD 却提交旧包」）

| 场景 | 风险 | 做法 |
| --- | --- | --- |
| `A.md` → 导出 `A.html`，再把 MD 改成 B，却提交旧 HTML | 仓库里正文与源不一致 | 生成物不进 Git；要发公众号就再跑导出 |
| 本地还开着旧 HTML 去复制 | 粘贴到公众号的是旧文 | 粘贴前跑 `--check`；不 fresh 则重渲 |
| 改完站点就 commit | 误把 `*.html` / `*-cover.jpg` add 进去 | `.gitignore` 已忽略；Agent 应劝阻 |

**触发时机**：只在你明确要发/导出公众号时渲染；日常改 MD 不自动生成、也不提醒重渲（避免噪音）。一旦进入导出流程，**必须重渲**，不复用磁盘上的旧包。

骨架说明：`docs/wechat/screen-review-template.html`

### 3.2 发布包怎么用

1. 浏览器打开 `docs/wechat/<slug>.html`
2. **复制标题** → 粘贴到公众号「标题」
3. **复制摘要** → 粘贴到公众号「摘要」
4. **复制正文** → 粘贴到正文编辑器（原生编辑器）
5. **封面**：把同目录 `<slug>-cover.jpg` 拖到封面上传  
   - 常见尺寸 1280×720（16:9）可用；若裁切框偏宽，居中微调即可
6. 预览手机效果；若图未带上，用正文里的 CDN 地址按原位补插

### 3.3 版式约定（纸页留白）

| 元素 | 做法 |
| --- | --- |
| 栏目眉 | 「光影人生」小字字距拉开 |
| 作品识别 | 《片名 · 年份》，不用公众号主标题顶正文 |
| 评分 | 浅灰底块 +「综合 x/10」 |
| 金句 | 左竖线 + 浅底；英斜中正 |
| 图注 | 图下居中小字灰色 |
| 文末 | — 光影人生 · 好好生活 — |

针对的是**微信公众号原生编辑器**：只靠内联样式，不用 flex/grid/复杂表格。

## 4. 推荐工作流（清单）

```text
[ ] 1. hugo new 建 Page Bundle，draft 写作
[ ] 2. 截图/剧照上传 COS，Markdown 写 CDN + 图注
[ ] 3. 补 featured.jpg，定 summary 与评分
[ ] 4. pnpm run site:dev 站内预览，改到可发布
[ ] 5. draft: false，提交并部署站点（按你的发布节奏）
[ ] 6. 想好公众号标题：《片名》：观点句
[ ] 7. 跑 wechat_screen_review.py 生成发布包
[ ] 8. 后台粘贴标题 / 摘要 / 正文，上传封面
[ ] 9. 手机预览 → 群发或定时
[ ] 10.（可选）站内文末或关于页补公众号入口；本仓可保留 docs/wechat 发布包备查
```

## 5. 常见问题

| 现象 | 处理 |
| --- | --- |
| 粘贴后丢图 | 原生编辑器常见；按 HTML 中 CDN `src` 重新插入 |
| 封面 CDN 404 | 正常；封面走本地 `featured.jpg` / `*-cover.jpg` 上传 |
| 摘要太长 | 优先改 `summary`，不要靠编辑器硬砍论点 |
| 想改版式 | 先改 `scripts/wechat_screen_review.py` 再重导，避免手改 HTML 漂移 |
| 剧集 vs 电影 | 同一套流程；作品信息行按 archetype 注释调整字段即可 |

## 6. 相关路径

| 路径 | 说明 |
| --- | --- |
| `content/screen/<slug>/` | 影评唯一正文 |
| `archetypes/screen.md` | 建稿骨架 |
| `scripts/wechat_screen_review.py` | Markdown → 公众号发布包 |
| `docs/wechat/` | 模板说明与各篇导出物 |
| `.claude/skills/wechat-screen-review/` | 明确导出时的 Agent 流程 |
| [content-search.md](content-search.md) | 栏目与站内检索 |
