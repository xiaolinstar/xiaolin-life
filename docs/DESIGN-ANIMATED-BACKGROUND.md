# 首页动画背景：方案与参考

> 记录首页背景动画的选型参考与当前实现，后期内容丰富后可按需切换。

## 当前实现

- **底层**：纯 CSS「极光流动」渐变（`assets/css/custom.css` 中 `home-aurora` 系列规则），零依赖，支持深色模式与 `prefers-reduced-motion`。
- **上层**：[Vanta.js](https://www.vantajs.com/) **Birds** 效果，透明画布叠加在极光之上，鸟群颜色蓝紫渐变（`0x3b82f6` → `0x8b5cf6`），支持鼠标/触摸交互。
- **降级策略**：用户开启「减少动态效果」或 JS 加载失败时，自动回退为纯 CSS 极光背景。

### 相关文件

| 文件 | 作用 |
|---|---|
| `layouts/partials/home/background.html` | 首页全屏 hero 覆写模板，挂载 `#home-vanta` 容器与脚本 |
| `assets/js/home-vanta.js` | Vanta Birds 初始化参数 |
| `assets/js/vendor/three.min.js` | three.js r134（Vanta 依赖，自托管） |
| `assets/js/vendor/vanta.birds.min.js` | Vanta Birds v0.5.24（自托管） |
| `assets/css/custom.css` | 极光渐变、全屏 hero、画布层级 |

### 许可证

Vanta.js 与 three.js 均为 **MIT 协议**，个人与商业站点免费使用，无需授权。

## 参考网站（后期选型）

| 网站 | 看什么 |
|---|---|
| [Awwwards](https://www.awwwards.com/) | 获奖站点，整体设计感标杆 |
| [Codrops](https://tympanus.net/codrops/) | 前端动效教程 + 可直接用的 Demo |
| [Vanta.js](https://www.vantajs.com/) | 开箱即用的 WebGL 背景：BIRDS、WAVES（流动感）、FOG、CLOUDS |
| [tsParticles](https://particles.js.org/) | 粒子引擎，现成的雨滴、雪花、星空预设 |
| [ShaderGradient](https://www.shadergradient.co/) | 高级流动渐变生成器，Stripe 风格 |
| [unicorn.studio](https://unicorn.studio/) | 无代码 WebGL 交互效果 |
| [linear.app](https://linear.app/) / [stripe.com](https://stripe.com/) | 渐变 + 微动效的商业设计标杆 |

## 备选方案对比

| 方案 | 体积 | 风格 | 适用场景 |
|---|---|---|---|
| 纯 CSS 极光（保底） | 0 KB | 流动渐变，克制高级 | 任何页面，性能敏感场景 |
| Vanta Birds（当前） | ~630 KB（three.js 601K + birds 28K） | 灵动鸟群，有生命力 | 内容较少的展示型主页 |
| Vanta Waves / Fog | 同上 | 流动感 / 雾气弥漫 | 想换氛围时一行参数切换 |
| tsParticles 雨滴 | ~100 KB | 雨滴感、粒子 | 想要天气类氛围时 |
| ShaderGradient | ~200 KB | Stripe 式高饱和流动渐变 | 品牌感更强的落地页 |

## 切换 / 调参指南

- 换 Vanta 其它效果：下载对应 `vanta.xxx.min.js` 到 `assets/js/vendor/`，改 `home-vanta.js` 中 `VANTA.BIRDS` 为对应效果并调参（部分效果依赖 p5.js 而非 three.js，注意替换）。
- 调鸟群参数：`quantity`（数量）、`birdSize`（体型）、`speedLimit`（速度）、`color1/color2`（渐变色）。
- 彻底关闭动画背景：删除 `background.html` 末尾三个 `<script>` 标签即可，极光 CSS 背景仍在。
