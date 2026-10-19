# Blowfish 与轮播维护

当前 Hugo 版本由 `.hugo-version` 统一锁定，主题固定在 Blowfish v3.9.0。历史 v2.104.0 的版本上限与旧安装路径不再适用。

## 轮播资源与点击处理

主题内置 `carousel`、`timeline` 由主题加载 TW Elements；项目的 `carousel-cdn` 仍通过 `layouts/partials/extend-head-uncached.html` 加载对应 CSS 与脚本。

TW Elements FREE 2.0.0 已包含原生 `Carousel.dataApiClickHandler`。旧记录根据压缩包的字面事件名称判定“没有点击处理”不准确，不能据此重复绑定。

本次回归发现额外的点击桥接会与原生处理冲突，已移除项目桥接脚本及加载入口。鼓楼滨江多图轮播的指示器和前后按钮使用原生处理。

## 升级检查

- Hugo 的主题版本范围警告本身不等于轮播资源一定缺失，应检查生成的资源与实际交互。
- 验证轮播指示器、上一张、下一张，以及文章搜索、栏目目录和深浅色显示。
- Hugo 0.168.0 超出主题声明的最高 0.167.0，项目完成独立回归后采用 0.168.0；保留警告与已验证的 0.167.0 回退版本。
- `carousel` 使用本地 Page Bundle 图片，`carousel-cdn` 使用 CDN 直链；没有多张原图的页面不能用于验证多图切换。
