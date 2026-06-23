---
title: "媒体模板示例"
description: "Blowfish 轮播、图集、视频 shortcode 用法参考"
date: 2025-06-23
draft: false
showTableOfContents: true
categories:
  - "办公"
tags:
  - "模板"
  - "媒体"
---

本文汇总 Blowfish 主题中常用的图片与视频展示方式，可作为新文章写作模板。

## 图片轮播（Carousel）

将图片放入文章目录下的 `gallery/` 文件夹，然后用 shortcode 引用：

```markdown
{{</* carousel images="gallery/*" interval="4000" aspectRatio="21-9" */>}}
```

带 caption 的写法：

```markdown
{{</* carousel images="gallery/*" captions="{01.jpg:第一张,02.jpg:第二张}" */>}}
```

参考示例：[鼓楼滨江步行道](/life/entertainment/gulou-riverfront/)

## 响应式图集（Gallery）

```markdown
{{</* gallery */>}}
  {{</* figure src="gallery/01.jpg" caption="说明文字" figureClass="grid-w33" */>}}
  {{</* figure src="gallery/02.jpg" caption="说明文字" figureClass="grid-w33" */>}}
  {{</* figure src="gallery/03.jpg" caption="说明文字" figureClass="grid-w33" */>}}
{{</* /gallery */>}}
```

## 本地视频

```markdown
{{</* video src="gallery/walk.mp4" poster="gallery/cover.jpg" caption="视频说明" */>}}
```

## B 站 / YouTube 嵌入

```markdown
{{</* youtubeLite id="BVxxxxxx" label="视频标题" */>}}
```

## 封面图（Featured Image）

在文章目录放置 `featured.jpg` 或 `featured.svg`，会自动用于：

- 首页 / 列表页卡片缩略图
- 文章顶部 Hero 背景
- 社交分享预览图

也可运行 `pnpm run featured:setup` 批量生成分类占位封面。

## 分类占位封面

| 分类 | 占位图 |
|------|--------|
| 风景名胜 | `assets/img/covers/places.svg` |
| 知名高校 | `assets/img/covers/university.svg` |
| 桌游时光 | `assets/img/covers/table-game.svg` |
| 美食探店 | `assets/img/covers/entertainment.svg` |
| 生活感悟 | `assets/img/covers/thinks.svg` |
| 轻松办公 | `assets/img/covers/office.svg` |
