# 首页 Hero 视觉优化设计

日期：2026-07-16  
状态：已实现  
站点：xiaolin-life（Hugo + Blowfish）

## 背景与目标

当前首页使用 `background` 布局 + 脚本生成的占位背景图 + 极简正文（alert + 文字链），品牌感弱。目标是参考 Blowfish 示例站的 Hero 视觉强度，在**不重写主题、不大改内容文**的前提下，提升首页第一屏设计感。

成功标准：

- 首屏一眼能识别「今天不上班」品牌（logo + Hero + 头像）
- 生活 / 办公有明确 CTA，不再只有纯文字链接
- 背景/图标等站点级素材可替换为更有质感的资产
- 仍走 Blowfish 原生布局，维护成本低

## 方案选择（已确认）

采用 **方案 1：`hero` 布局 + 强化素材与入口**。

不采用：`card` 左文右图、`custom` 多区块自定义首页。

## 整体结构

```text
Header（新增 logo）
└─ Hero 圆角卡片
   ├─ homepageImage + 主题色渐变滤镜
   ├─ 作者头像（保留橙猫）
   ├─ 姓名 / headline「今天不上班」
   └─ GitHub / Email
正文区
├─ alert 公告（精简保留）
├─ button × 2：生活记录 / 轻松办公
└─ 一句导语
最近文章（主题自动：12 卡片 + 显示更多 → /life/）
```

## 视觉方向

| 项 | 决策 |
| ---- | ------ |
| 配色 | 保持 `colorScheme = "blowfish"`，不整站换肤 |
| 氛围 | 南京城市气质（天际线 / 江景感），避免抽象紫渐变 |
| 头像 | 保留 `img/orange-cat.svg` |
| Header logo | 新增简洁 SVG（橙猫简标或「不上班」二字线标） |
| 动效 | Hero 图轻量 drift；卡片悬停；不堆动画 |

## 配置改动

文件：`config/_default/params.toml`

```toml
[homepage]
  layout = "hero"
  homepageImage = "img/photos/home-hero.jpg"
  showRecent = true
  showRecentItems = 12
  showMoreLink = true
  showMoreLinkDest = "/life/"
  cardView = true
  cardViewScreenWidth = false
  disableHeroImageFilter = false
```

说明：从 `background` 切到 `hero` 后，`layoutBackgroundBlur` 对首页不再适用，可保留字段无害。

文件：`config/_default/languages.zh-cn.toml`

```toml
[params]
  logo = "img/logo.svg"
  # …其余不变
```

## 素材清单

| 资产 | 动作 | 说明 |
| ------ | ------ | ------ |
| `assets/img/photos/home-hero.jpg`（或复用/升级现有图） | 新增或替换 | Hero 宽图；可用现有摄影气质图、`home-hero.svg` 导出、或 Nano Banana / 脚本生成城市插画 JPG |
| `assets/img/logo.svg` | 新增 | Header 品牌标，浅/深色可读 |
| `assets/icons/*.svg` | 按需 | 若主题缺语义图标再补；优先用内置 `globe` / `code` / `file-lines` 等 |
| `assets/img/orange-cat.svg` | 保留 | 作者头像 |
| `assets/css/custom.css` | 接线 | `hero-drift` 绑到 Hero 背景图；`.home-recent-card` 接到最近文章卡片选择器（若主题 DOM 允许，用合理 CSS 选择器，避免 fork 主题模板） |

范围边界：

- **做**：布局、logo、Hero 图、首页 CTA、轻量 CSS
- **不做**：整站换配色、`custom` 布局、改各篇文章正文与图集、sponsors/contributors 演示区

## 首页文案结构（`content/_index.md`）

```markdown
{{< alert icon="circle-info" >}}
**生活频道已上线。** 南京的风景、美食、桌游与办公技巧 —— 图文为主，持续更新。
{{< /alert >}}

{{< button href="/life/" >}}
{{< icon "globe" >}} 生活记录
{{< /button >}}
{{< button href="/office/" >}}
{{< icon "code" >}} 轻松办公
{{< /button >}}

南京生活 · 轻松办公 · 城市探索。从下方最近文章开始逛，或进入频道翻阅。
```

图标名以实现时主题 `assets/icons/` 实际存在的为准；若需更贴切语义可新增自定义 icon。

## 验证

1. `hugo server -D` 或 `pnpm run site:dev`，首页首屏为圆角 Hero
2. Header 显示 logo，点击回首页
3. 两个 button 跳转 `/life/`、`/office/`
4. 最近文章卡片与「显示更多」正常
5. 浅色 / 深色外观下 logo 与 Hero 文字可读
6. 移动端 Hero 与按钮不挤爆、可点

## 非目标（明确排除）

- 复制示例站的 layout 切换演示、sponsors、contributors
- 修改 Blowfish submodule 源码
- 强制默认 dark mode
