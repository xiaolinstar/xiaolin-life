# 首页 Hero 视觉优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将首页切到 Blowfish `hero` 布局，补齐 logo / Hero 图 / CTA，并接线轻量 CSS。

**Architecture:** 不 fork 主题。只改站点配置、`content/_index.md`、站点级素材与 `assets/css/custom.css`。Hero 图与 logo 放在 `assets/img/`，由 Hugo resource pipeline 加载。

**Tech Stack:** Hugo 0.158+、Blowfish、站点 `assets/`、可选 Python/Pillow 生成 Hero JPG。

## Global Constraints

- 保持 `colorScheme = "blowfish"`，不整站换肤
- 不修改 `themes/blowfish` submodule
- 不改各篇文章正文与图集
- 不自动 git commit（除非用户明确要求）

---

### Task 1: 新增 logo 与 Hero 图素材

**Files:**

- Create: `assets/img/logo.svg`
- Create: `assets/img/photos/home-hero.jpg`
- Optional reference: `assets/img/home-hero.svg`（可作构图参考，不必删除）

**Interfaces:**

- Produces: Hugo 可加载路径 `img/logo.svg`、`img/photos/home-hero.jpg`

- [ ] **Step 1: 创建 Header logo SVG**

简洁线标：圆角方底 + 橙猫剪影或「不上班」二字，浅/深色下均可用（用 `currentColor` 或固定高对比色）。

- [ ] **Step 2: 生成 / 写入 Hero JPG**

优先基于现有 `home-hero.svg` 或南京城市气质构图，导出/生成约 1920×1080 的 `home-hero.jpg`。避免抽象紫渐变。

- [ ] **Step 3: 确认文件可被 Hugo 读取**

Run: `ls -la assets/img/logo.svg assets/img/photos/home-hero.jpg`  
Expected: 两文件存在且非空

---

### Task 2: 切换 homepage 为 hero 并配置 logo

**Files:**

- Modify: `config/_default/params.toml`
- Modify: `config/_default/languages.zh-cn.toml`

**Interfaces:**

- Consumes: Task 1 素材路径
- Produces: `homepage.layout = "hero"`，`params.logo` 生效

- [ ] **Step 1: 修改 `params.toml` 的 `[homepage]`**

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
  layoutBackgroundBlur = true
  disableHeroImageFilter = false
```

- [ ] **Step 2: 在 `languages.zh-cn.toml` 的 `[params]` 增加 logo**

```toml
logo = "img/logo.svg"
```

---

### Task 3: 首页正文改为 alert + 双 CTA

**Files:**

- Modify: `content/_index.md`

- [ ] **Step 1: 按 spec 重写 `_index.md` 正文**

使用 Blowfish `alert` / `button` / `icon` 短代码；图标用主题已有 `circle-info`、`globe`、`code`（或 `mug-hot`）。

---

### Task 4: 接线 custom.css 动效

**Files:**

- Modify: `assets/css/custom.css`

- [ ] **Step 1: 将 `hero-drift` 绑到 Hero 背景图选择器**

Hero 模板内背景图为 `.relative.shadow-xl img`（圆角卡片内 absolute 层）。使用足够具体、不误伤文章页的选择器，例如首页主区域：

```css
/* 首页 Hero 背景微动 */
.relative.shadow-xl.sm\:overflow-hidden > .absolute.inset-0 > img {
  animation: hero-drift 28s ease-in-out infinite;
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .relative.shadow-xl.sm\:overflow-hidden > .absolute.inset-0 > img {
    animation: none;
  }
}
```

注意：Tailwind 转义在纯 CSS 中可能失效；若无效，改用 Hugo 首页可稳定命中的结构选择器（实现时对照渲染 DOM 调整）。

- [ ] **Step 2: 将 `.home-recent-card` 动画接到最近文章卡片**

主题 recent 卡片为 `article.group`。可：

```css
section article.group {
  animation: fade-up 0.6s ease both;
}
```

并保留原有 hover 规则。

---

### Task 5: 本地验证

**Files:** 无代码变更

- [ ] **Step 1: 构建或启动预览**

Run: `hugo server -D` 或 `pnpm run site:dev`  
若本机无 hugo：`pnpm run site:build` 检查构建成功

- [ ] **Step 2: 核对清单**

1. 首屏为圆角 Hero  
2. Header 有 logo  
3. CTA 跳转 `/life/`、`/office/`  
4. 最近文章 12 卡片 + 显示更多  
5. 浅/深色 logo 可读  

- [ ] **Step 3: 更新 spec 状态为「已实现」**（可选）

---

## Spec coverage

| Spec 项 | Task |
| --------- | ------ |
| layout=hero | Task 2 |
| homepageImage | Task 1 + 2 |
| logo | Task 1 + 2 |
| CTA buttons | Task 3 |
| custom.css 动效 | Task 4 |
| 验证 | Task 5 |
| 不改主题 submodule | 全局约束 |
