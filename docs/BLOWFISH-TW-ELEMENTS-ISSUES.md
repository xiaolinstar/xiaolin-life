# Blowfish 主题 & TW Elements 已知问题

> 记录项目对 blowfish 主题与 tw-elements 库的踩坑、workaround 与未解决的局限。
> 适用 Hugo 版本：`0.158.0` – `0.163.3`（blowfish v2.104.0 / `themes/blowfish/config.toml:5` 显式 `max = "0.163.3"`）。

---

## 问题 1：Hugo 版本必须 ≤ 0.163.3

**症状**：本地或 CI 用 `hugo v0.164.0+` 构建时出现：

```
WARN  Module "blowfish" is not compatible with this Hugo version: 0.158.0/0.163.3 extended
```

且吹气式 `{{< carousel >}}` 与 `{{< timeline >}}` 主题内置 `vendor.html` 的 `.Page.HasShortcode` 检测失效，**carousel.css 与 tw-elements 不加载**。

**根因**：

- `themes/blowfish/config.toml:5` 显式声明 `[module.hugoVersion] max = "0.163.3"`
- 当前 blowfish main HEAD `1f144483` (v2.104.0) 仍是此声明
- 后续 commit `88b42601`（把 `max` 改成 `0.164.0`）目前只在 `hugo-new-version` 分支，**未合并 main**

**解决**：

1. **CI**（`.github/workflows/pages.yml`）：固定 `hugo-version: "0.163.3"`
2. **本地**：使用 `./bin/hugo` 包装器，优先调用 `./.tools/hugo158`（v0.158.0 extended，兼容范围内）。首次 clone 后运行 `./bin/install-hugo.sh` 下载 `v0.163.3` 到 `.tools/hugo158`
3. **未来**：等 blowfish 把 `88b42601` 合到 main 后，submodule 升级 + 恢复 `hugo 0.164.0+`

---

## 问题 2：TW Elements FREE 2.0.0 carousel 缺失 click handler

**症状**：吹气式 `{{< carousel >}}` 页面（如 `thai-milk-tea-latte`、`carbs`、`undercover` 等 10 个）：

- ✓ 自动轮播正常（3.5s 间隔自动 next）
- ✗ 点击 prev / next 按钮、底部 indicator **完全无响应**

**根因**：

`themes/blowfish/assets/lib/tw-elements/index.min.js` 是 **TW Elements FREE 2.0.0**（113KB 精简版）。

| 期望能力 | 实际状态 |
|---|---|
| Carousel 类定义 | ✓ 存在（cycle / next / prev / to / getOrCreateInstance） |
| 自动轮播（cycle 定时器）| ✓ 构造函数里 `cycle()` 启动 |
| **click / pointerdown / mousedown 事件监听** | **✗ 0 处** |

```
$ grep -oE 'addEventListener\s*\(\s*["'\'']' themes/blowfish/assets/lib/tw-elements/index.min.js
DOMContentLoaded / scroll / resize / keydown / animationstart / input
（无 click / pointerdown / touchstart 等鼠标/触摸事件）
```

也就是说，FREE 版只放了 Carousel 类骨架 + 构造函数自启定时器，**没有把 button click 桥接到 `_slide`**。这是 TW Elements FREE 版的固有限制，blowfish 主题未修补。

**解决（项目层补桥接）**：

新增 `assets/js/carousel-click.js`：

```js
// 监听 document click → 查找 [data-twe-slide] / [data-twe-slide-to] 按钮
// 从 data-twe-target 找到 carousel 容器
// Carousel.getOrCreateInstance(el) 取实例
// 根据 data-twe-slide 调用 instance.prev() / .next() / .to(parseInt)
```

`layouts/partials/extend-head-uncached.html` 检测 `carousel` / `carousel-cdn` / `timeline` 时加载此脚本（`defer`，与 tw-elements 同 defer 顺序加载，**保证 carousel-click.js 在 tw-elements 之后执行**）。

---

## 问题 4（次要）：blowfish 主题维护性与健壮性评估

| 维度 | 评价 | 证据 |
|---|---|---|
| Hugo 兼容性声明 | ⚠️ 落后 | 声明 max 0.163.3，但 Hugo 已发到 0.164+；兼容性 PR 卡在 `hugo-new-version` 分支未合并 |
| 第三方库选型 | ⚠️ 不一致 | TW Elements FREE 2.0.0 在 2023 末停更，新组件实现不完整；项目实际只用其 carousel 一项 |
| 短代码/Partial 健壮性 | ⚠️ 依赖 shortcode 文本检测 | `vendor.html` 用 `HasShortcode` 决定资源加载，越界 Hugo 版本下可能整体失效，无 fallback |
| 文档/迁移指南 | ⚠️ 缺失 | 无 changelog 注明 tw-elements FREE → FULL 升级路径；Hugo 版本绑定只在 config.toml 隐式声明 |

**结论**：blowfish 主题对 carousel / timeline 短代码的支持建立在「Hugo ≤ 0.163.3 + TW Elements FREE 2.0.0」这一组脆弱组合上。一旦其中一项升级（无论是 Hugo 0.164+ 还是 tw-elements FULL 版）都需要重做集成测试。

**后续可能方向**：

- 等待 blowfish 团队把 `88b42601` 合到 main（升级 Hugo 上限）
- 或 fork tw-elements FREE 自行补 click handler（已通过 `assets/js/carousel-click.js` 实现）
- 或迁移到其他 carousel 库（swiper.js、glide.js），但需重写短代码

---

## 受影响页面清单

使用吹气式 `{{< carousel >}}` 的页面（都依赖 carousel-click.js + Hugo ≤ 0.163.3）：

| 页面 | 类型 |
|---|---|
| `content/drinkzen/luckincoffee/thai-milk-tea-latte/` | drinkzen |
| `content/life/entertainment/carbs/` | life |
| `content/life/table-game/undercover/` | life |
| `content/life/table-game/avalon/` | life |
| `content/life/places/sun-mausoleum/` | life |
| `content/life/places/chaotian-palace/` | life |
| `content/life/places/nanjing-museum/` | life |
| `content/life/university/nju/` | life |
| `content/life/university/nnu/` | life |

使用 `{{< carousel-cdn >}}`（项目层 shortcode）：`content/life/entertainment/gulou-riverfront/` 等。