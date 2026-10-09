# drinkzen · social 子模块

饮品 → 社媒 plog 分发的工作流入口。

## 何时使用

- 新建饮品测评后 → 在 origin 文章末尾追加 `## plog 分发版` 段
- 日常 11:30 发布小红书 → 复制 plog 长版 tab 内容到小红书 APP
- 同步大众点评 → 复制 plog 短版 tab 内容到大众点评 APP
- 标题微调 → 参考 [title-formulas.md](title-formulas.md)

## plog 模板

见 [`../assets/plog-template.md`](../assets/plog-template.md)。

模板含 plog 长版（小红书，≤800 字）+ plog 短版（大众点评，≤30 字）+ 通用铁律 + 警告触发条件。

## 文章结构（origin + plog 合一）

饮品页末尾可追加：

````markdown
{{< tabs "plog" >}}
{{< tab "📕 plog 长版（小红书 / 微博，≤800 字）" >}}

[按 plog-template 长版 5 段结构生成]

{{< /tab >}}
{{< tab "📍 plog 短版（大众点评，≤30 字）" >}}

[按 plog-template 短版生成]

{{< /tab >}}
{{< /tabs >}}
````

**灵活性**：若只有小红书内容（如迁移阶段），可用单 tab；若两者都有，用双 tab。

**frontmatter 扩展**（可选）：

```yaml
platforms: [xiaohongshu]      # 实际覆盖哪些平台就填哪些
```

## 工作流

### 1. 新饮品创建后

1. 完成 origin 内容（`## 产品速览` / `## Nutri-Grade 评级` / `## 制作方式调查` / `## 口感体验` / `## 饮用建议`）
2. 读 `assets/plog-template.md`，按 Origin 抽取清单逐项取数据
3. 在 origin 文章末尾追加 `## plog 分发版` 段（tabs 包裹）
4. 更新 origin frontmatter 加 `platforms: [xiaohongshu, dianping]`
5. 写完走 `pnpm run site:dev` 验证 tabs 渲染

### 2. 发布到小红书

1. 打开饮品页 → 展开"📕 plog 长版" tab
2. 复制"小红书 text 代码块"整段 → 粘贴到小红书 APP
3. 上传 4-6 张图（按 plog 模板的"图片清单"章节顺序）
4. 标题 → 按 title-formulas.md 公式
5. 标签 → 按 plog 模板的"标签三档"
6. 发布后立即置顶第一条评论（按 plog 模板的"评论区置顶"）
7. 记录发布链接到 ai-todo（"小红书 11:30 发布《<产品>》"）

### 3. 同步到大众点评

1. 打开饮品页 → 展开"📍 plog 短版" tab
2. 复制整段 → 粘贴到大众点评 APP
3. 上传 1 张主图（origin gallery 首图）
4. 标签 → 简化版（必带 2 + 城市/品牌 tag）
5. 选 3-5 星评分

## 图片生成指引

plog 发布前需准备 4-6 张图（小红书）或 1 张主图（大众点评），全部来自 origin gallery：

| 模板位 | 来源 | 角色 |
| --- | --- | --- |
| 图 1 封面 | origin 首图 | 封面杀手 |
| 图 2 杯身 | origin 杯身图 | 品牌识别 |
| 图 3 配料 | origin 配料表截图 | 信任锚点 |
| 图 4 评估 | origin 评估表/小程序截图 | 数据可视化 |
| 图 5 场景（选） | origin 场景图 | 情绪锚点 |
| 图 6 结尾（选） | origin 结尾图 | CTA 引导 |

**封面文字叠加**（图 1 必备）：

- 左上角：品牌 Logo（直接复用 origin 图）
- 居中：产品名 + ABCD 评级
- 右下角：1 个数字钩子（如「431大卡」）

**图片处理禁忌**：

- 不重压画质
- 不裁剪 logo / 容量标识
- 不用动图（webp / live photo）

## 发布后操作

1. 在小红书 / 大众点评 APP 复制发布链接
2. 记录到 ai-todo（已完成状态）
3. 当周复盘时归档到 [content/social-publish/](../../social-publish/)（如果该目录还在；本 design 实施后该目录会被删除，发布状态追踪改用 ai-todo）
4. 数据异常的饮品 → 标记回 origin（"origin 数据有误需复核"）

## 与 drinkzen admin 子模块的关系

plog 分发是饮品对外的"宣传出口"，drinkzen admin 是饮品在 drinkzen.cn 平台上的"结构化数据入口"。两者独立：

- plog 改了小红书 / 大众点评内容，不影响 drinkzen.cn 后台数据
- drinkzen.cn 后台改了品牌资料 / 菜单模板，不影响 plog 已发布内容
- 唯一联动：origin 文章改了 → plog 需要重新生成（但 plog 已发布的链接不会更新）

## 关联文档

- 主模板：`assets/plog-template.md`
- 标题公式：`references/title-formulas.md`
- drinkzen admin：`references/admin.md`
- drinkzen 创作：`references/content.md`
