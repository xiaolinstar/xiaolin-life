# 媒体规范

作者写作、本地管理、COS 上传与 Git 协作的统一约定。技术部署见 [MEDIA-OSS.md](MEDIA-OSS.md)。

## 原则

1. **原画质**：COS 存原图 / 原视频，不做有损压缩。
2. **一篇文章一套媒体**：图片、视频、poster 与文章同目录，不散落在 `static/`。
3. **Git 只留文字与轻量资源**：大图 / 视频不进仓库；线上通过 COS（后期 CDN）URL 访问。
4. **作者本地始终保留母本**：上传 COS 不等于删除个人备份（相册、NAS 等）。

---

## 三层存储

| 层级 | 位置 | 作用 | 进 Git |
|------|------|------|--------|
| 作者母本 | 本机 `gallery/` 或归档目录 | 写作、coscli 上传、个人备份 | ❌ |
| 仓库 | `content/**/*.md`、配置、小 SVG | 版本管理、CI 构建 | ✅ |
| 线上 | 腾讯云 COS（后期 CDN） | 读者访问 | — |

```
写作 ──► content/.../gallery/（本地）
              │
              ├── coscli sync ──► COS（线上原文件）
              │
              └── index.md 写 COS/CDN URL ──► Git（仅链接）
```

---

## 目录结构（作者放置位置）

每篇文章使用 **Page Bundle**：

```
content/life/entertainment/gulou-riverfront/
├── index.md                 # 文章正文与 front matter
├── featured.jpg             # 列表 / 分享封面（可选，建议 ≤500KB 或改用 COS URL）
└── gallery/                 # 该文全部原图、原视频（写作期放这里）
    ├── 01-nanjing-marathon.jpg
    ├── 02-bridge-entry.jpg
    ├── walk-along-river.mp4
    └── walk-along-river-poster.jpg
```

**COS 对象键**与 content 路径对齐（去掉 `content/` 与 `gallery/`）：

| 本地 | COS 键 | URL（CDN 未配时用 COS 直链） |
|------|--------|------------------------------|
| `content/life/.../gallery/01-nanjing-marathon.jpg` | `life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg` | `https://<bucket>.cos.<region>.myqcloud.com/life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg` |
| 同上目录下 `walk-along-river.mp4` | `life/entertainment/gulou-riverfront/walk-along-river.mp4` | 同上规则 |

后期 CDN 域名就绪后，仅替换 URL 前缀为 `https://media.xiaolin.fun/`，路径不变。

---

## 命名规范

| 规则 | 说明 | 示例 |
|------|------|------|
| 小写 ASCII + 数字 + 连字符 | 便于 URL、COS、跨平台 | `nanjing-marathon.jpg` |
| 轮播 / 图集可加序号前缀 | 控制展示顺序 | `01-bridge-entry.jpg` |
| 禁止中文、空格、下划线 | 避免 URL 编码与脚本问题 | ❌ `4玩家.png` → ✅ `04-players.png` |
| 扩展名反映真实格式 | 不强制转码 | `.jpg` `.png` `.webp` `.mp4` |
| 视频 poster 与成片同名 | 便于配对 | `walk.mp4` + `walk-poster.jpg` |
| 纠正拼写 | 新建时即规范 | `mac-silver.jpg`（非 sliver） |

---

## 图片

### 用法与引用

| 场景 | 写作期（本地预览） | 上线后（COS/CDN） |
|------|-------------------|-------------------|
| 轮播 | `{{< carousel images="gallery/*" ... >}}` | `{{< carousel-cdn images="{https://.../01.jpg,...}" ... >}}` |
| 正文插图 | `![说明](gallery/02-bridge-entry.jpg)` | `![说明](https://media.xiaolin.fun/life/.../02-bridge-entry.jpg)` |
| 列表封面 | 同目录 `featured.jpg` | 可保留小文件，或 front matter 指定 COS URL |

### 不再使用的路径

- ❌ `static/assets/images/img-*`（历史遗留，迁移后删除）
- ❌ 根目录散落如 `static/assets/images/ai-dialectic-moon-egg.png`

---

## 视频

| 类型 | 存放 | 引用 |
|------|------|------|
| 自拍 / 游记短片 | `gallery/*.mp4` | `{{< video src="..." poster="..." caption="..." >}}` |
| B 站 / YouTube | 无本地文件 | `{{< youtubeLite id="..." >}}` |

上线后将 `src` / `poster` 换为 COS/CDN 绝对 URL。视频体积大，**更不应进 Git**；母本仅留作者本机 + COS。

---

## 与 `assets/`、`static/` 的区别

| 路径 | 用途 | 谁维护 | 进 Git |
|------|------|--------|--------|
| **`content/.../gallery/`** | 文章原图 / 原视频 | 作者 | ❌（见下节） |
| **`assets/img/photos/`** | 分类占位小图（~28KB） | 项目脚本 | ✅ |
| **`assets/img/covers/`** | 分类 SVG 封面 | 项目 | ✅ |
| **`static/assets/images/`** | 旧方案正文插图 | 待迁移清空 | ❌（迁移后） |

`assets/`（仓库根下）是 Hugo 管道资源，**不是**游记大图目录。

---

## Git 策略

### 目标状态

`.gitignore` 已配置（迁移完成后以 COS URL 为准，本地 `gallery/` 仅作上传源）：

- `content/**/gallery/**` — 文章媒体母本
- `static/assets/images/**` — 历史 static 大图

保留 `.gitkeep` 以便空目录结构可被作者本地创建。

### 迁移期说明

已被 Git 跟踪的 `gallery/`、`static/assets/images/` 文件**不会**因 `.gitignore` 自动消失，需在上传 COS 并改完 Markdown 后执行：

```bash
git rm -r --cached content/**/gallery static/assets/images
git commit -m "chore: 媒体迁出 Git，改由 COS 分发"
```

### `featured.jpg`

- 过渡期可暂留 Git（体积可控时）。
- 全面 CDN 化后，优先在 front matter 用 `featuredImage` 指向 COS URL，本地不再提交 `featured.*`。

---

## 作者工作流

### 新文章

1. 创建 `content/<分区>/<slug>/index.md`。
2. 原图 / 原视频放入同目录 `gallery/`，按命名规范重命名。
3. 本地预览：`pnpm run site:dev`（写作期 shortcode 读本地 `gallery/`）。
4. 上传 COS：
   ```bash
   ./scripts/media-publish.sh content/<分区>/<slug>
   # 或 pnpm run media:publish -- content/<分区>/<slug>
   ```
5. 将 Markdown / shortcode 中的路径改为 COS（或 CDN）绝对 URL。
6. 确认线上可访问；`git commit` 仅 `index.md`，push 后 CI 校验 URL 并构建。

### 修改已有媒体

1. 替换本地 `gallery/` 中文件（保持文件名或同步改正文 URL）。
2. `coscli sync` 覆盖上传（同键名即覆盖）。
3. 若改名，同步更新 Markdown 中的 URL。

### 备份建议

除仓库与 COS 外，作者本机或 NAS 保留一份母本目录，例如：

```
~/Archive/xiaolin-life-media/
└── life/entertainment/gulou-riverfront/
    └── ...
```

可与 `gallery/` 同步，或使用硬链 / rsync；**COS 不能替代个人冷备份**。

---

## 辅助命令

| 命令 | 说明 |
|------|------|
| `pnpm run media:inventory` | 统计本地媒体与 Markdown 引用 |
| `pnpm run media:check` | 验证 coscli / Bucket |
| `pnpm run media:upload` | 上传 `static/assets/images`（迁移期） |
| `pnpm run media:publish -- content/.../slug` | **本地**上传 COS + 校验直链（见 `.claude/skills/media-publish/`） |
| `pnpm run media:rewrite` | 预览 `/assets/images/` → CDN URL |
| `pnpm run featured:setup` | 生成分类占位 featured（小图，可进 Git） |

---

## 迁移路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 定规范（本文档） | ✅ |
| 2 | 整理命名、去重（如鼓楼滨江 static vs gallery） | ✅ 鼓楼滨江试点完成（COS URL + carousel-cdn） |
| 3 | 全量上传 COS，Markdown 改 COS URL | ✅ 7 篇 static 插图 + 鼓楼滨江 |
| 4 | `git rm --cached` 移出 gallery / static 大图 | ✅ static/assets/images |
| 5 | 购买 CDN，URL 前缀换为 `media.xiaolin.fun` | ✅ |

CDN 未配置前，统一使用 COS 直链前缀（见 [MEDIA-OSS.md](MEDIA-OSS.md)）。

---

## 附录：鼓楼滨江试点（已完成）

路径：`content/life/entertainment/gulou-riverfront/gallery/`

| 原文件名 | 规范文件名 |
|----------|------------|
| `nanjing-marathon.jpg` | `01-nanjing-marathon.jpg` |
| `fangjiaying.jpg` | `02-fangjiaying.jpg` |
| `bridge-entry.jpg` | `03-bridge-entry.jpg` |
| `steel-bridge.jpg` | `04-steel-bridge.jpg` |
| `outway.jpg` | `05-riverside-walk.jpg` |
| `riverfront-scenic-belt.jpg` | `06-riverfront-scenic-belt.jpg` |
| `riverfront-oversee.jpg` | `07-riverfront-overlook.jpg` |
| `wangjiang-pavilion.jpg` | `08-wangjiang-pavilion.jpg` |
| `distant-see.jpg` | `09-distant-view.jpg` |
| `railway.jpg` … `railway-face.jpg` | `10-railway.jpg` … `12-railway-face.jpg` |
| `railway-site-1/2.jpg` | `13-railway-site-01.jpg` / `14-railway-site-02.jpg` |
| `railway-site-gongqijun-1.png` | `15-railway-gongjiqun-01.png` |
| `railway-site-gongjiqun-2.png` | `16-railway-gongjiqun-02.png` |
| `yinghongriver.jpg` | `17-yinghong-river.jpg` |
| `river-stone.jpg` | `18-river-stone.jpg` |
| `skyline-cuisine.jpg` | `19-skyline-cuisine.jpg` |
| `nanjing-beijing.jpg` | `20-nanjing-beijing.jpg` |
| `enjoy-youth.jpg` | `21-enjoy-youth.jpg` |
| `dad-baby.jpg` | `22-dad-and-baby.jpg` |

- 已删除重复目录 `static/assets/images/img-gulou-riverfront/`（22 张，~181MB）。
- COS 上传：`./scripts/upload-media-cos.sh content/life/entertainment/gulou-riverfront/gallery`
- 正文：`carousel-cdn` + COS URL；`build.publishResources: false`
- 构建产物：`public/.../gulou-riverfront/` 仅 ~60KB（无 gallery 副本）

## 附录：static 插图批量迁移（已完成）

已将 `static/assets/images/` 下 7 篇文章共 34 处 `/assets/images/` 引用改为 COS 直链，并自 Git 索引移除 static 大图：

| 文章 | 图片数 | featureimage |
|------|--------|--------------|
| `office/email` | 20 | thunderbird-lookup.png |
| `office/markdown` | 4 | txt-markdown.png（原 deepseek 缺失图已改引用） |
| `office/mac` | 2 | mac-sliver.jpg |
| `life/table-game/guandan` | 4 | joker.webp（中文文件名已规范为 ASCII） |
| `life/table-game/upgrade` | 1 | guandan.jpg |
| `life/thinks/blogger` | 2 | shenzhen-senior-school.png |
| `life/thinks/ai-dialectic` | 1 | ai-dialectic-moon-egg.png |

本地 `static/assets/images/` 仍保留作上传源（已 `.gitignore`），COS 键与目录名一致，如 `img-email-thunderbird/thunderbird-lookup.png`。
