# 好好生活 · 橘猫吉祥物

2026-10-20：选定正脸橘猫作为后续精修方向，保存当前概念原图。已确认使用橘猫 SVG、页头字标、头像及修复后的浏览器图标，保留旧版切换配置。

- 原图：[orange-tabby-v1.png](../assets/img/mascot/orange-tabby-v1.png)，1254 × 1254 PNG。
- 生成方式：内置 imagegen，以上一版正脸猫作为参考迭代；原图保留，不覆盖。
- 形象：正脸、圆润脸颊、小微笑、橘色虎斑与奶油色口鼻。
- 建议标准色：焦糖橘 `#C66A36`、奶油白 `#FFF0D8`、深蓝灰 `#344C5A`；虎斑辅助色 `#93492A`。这些是后续矢量定稿的目标色值。
- 矢量主稿：[orange-tabby.svg](../assets/img/mascot/orange-tabby.svg)，20 个路径，无内嵌位图；配色围绕上述 4 个主色色系整理。
- 小图标与兼容资源：`static/brand/orange-tabby/`，包含 SVG、16/32/48px PNG、ICO、Apple 180px 和 Android 192/512px 图标。
- 分享封面：`assets/img/mascot/social-card.png`，1200 × 630 PNG。

## 生成提示要点

保留参考稿的正脸、温柔微笑和可爱表情，改为圆润的家养橘色虎斑猫。脸颊饱满、口鼻短、耳朵较小，使用少量流畅曲线与三道额头虎斑。焦糖橘为主色，奶油白用于口鼻和下脸颊，深蓝灰用于五官。图形独立居中、透明背景，不含文字、边框、身体或场景，适合个人生活站点，后续整理为矢量标志。

## 本地预览与切换

站名暂保留“好好生活”。橘猫用于页头、首页与作者头像；页头文字调整字重、字距和深浅色显示。首页不再使用圆形裁切，避免切掉猫耳。作者署名仍为 xiaolinstar。

```bash
# 橘猫备选方案
bin/hugo server -D --disableFastRender --port 1313

# 旧头像与旧图标对照方案，使用独立输出目录
bin/hugo server -D --disableFastRender --environment brand-legacy --port 1314 --destination /tmp/xiaolin-brand-legacy-live
```

旧头像 `assets/img/avatar.png` 和根目录下原有浏览器图标均保留。`brand-legacy` 环境恢复旧版页头标志、头像和浏览器图标，便于对比；首页显式指定的橘猫分享封面仍保留。

浏览器图标和动态生成的 manifest 均包含当前部署前缀，兼容 `/xiaolin-life/` 的 GitHub Pages。手机桌面图标使用奶油色底并预留边距，未声明为 maskable 图标。

## 浏览器小图标校正

自动简化的初版 favicon 曾丢失眼睛、鼻子等深色路径，已恢复完整猫头路径并重新导出 16/32/48px PNG 和多尺寸 ICO。页面图标链接带有由 SVG 内容生成的版本号，更新文件后能请求新的资源地址。首页与页头主标志保持不变。

另有针对 16px 的极简猫头设计备选，当前仅作对比展示，未切换为站点图标。最终小图标应优先保留耳朵、橘色轮廓、深色眼睛和奶油色口鼻，减少碎毛和细条纹。
