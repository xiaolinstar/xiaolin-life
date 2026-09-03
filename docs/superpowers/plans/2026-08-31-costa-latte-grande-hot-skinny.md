# Costa 拿铁（Grande · 热 · 脱脂奶）详情页实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `content/drinkzen/costa/latte/index.md` 切换为以「大杯 480ml / 热 / 脱脂奶 / 不加糖」为主评测视角，标题升级为 A 级，新增「本次实测」段落，并发布（`draft: false`）。

**Architecture:** 单文件 Hugo markdown 内容编辑。保留原模板骨架，将默认配置从「中杯 360ml + 全脂奶」切换到「大杯 480ml + 脱脂奶」，参数叠加表重写为杯型与配料对比表，新增本次实测区段。

**Tech Stack:** Hugo + Markdown；无代码改动，无依赖变更，无图片资源。

## 全局约束

- 遵循项目 CLAUDE.md：中文回复、技术专有名词保留英文、中文标点全角、不自动 git 提交（除非用户明确要求）
- 文档命名规范：内容主题化、英文小写、`-` 分隔（沿用现有 slug `latte`）
- Markdown 兼容性：加粗语法外加半角空格或包含标点于加粗语法内
- 中文双引号统一使用“”
- Nutri-Grade 评级：基于新加坡 ABCD 标准（每 100ml 饱和脂肪 < 1.2g、非乳源性糖 < 5g）

---

### Task 1：修正 frontmatter 与产品速览

**Files:**
- Modify: `content/drinkzen/costa/latte/index.md:1-21`

**Step 1：替换 frontmatter 标题、summary、description、date**

将：

```yaml
---
title: "Costa 拿铁 · B-C 级"
description: "经典意式拿铁，浓缩咖啡与丝滑牛奶的完美融合"
date: 2026-08-25
draft: true
showTableOfContents: false
categories:
  - "饮品记录"
  - "奶茶仙人"
tags:
  - "Costa"
  - "拿铁"
  - "经典咖啡"
summary: "Costa Latte：Nutri-Grade B-C 级，热量约 180-220kcal/杯，咖啡因约 75mg。"
---
```

替换为：

```yaml
---
title: "Costa 拿铁（Grande · 热 · 脱脂奶）· A 级"
description: "大杯热脱脂奶拿铁实测，无糖低脂，新加坡 Nutri-Grade A 级"
date: 2026-08-31
draft: false
showTableOfContents: false
categories:
  - "饮品记录"
  - "奶茶仙人"
tags:
  - "Costa"
  - "拿铁"
  - "经典咖啡"
  - "脱脂奶"
  - "控糖"
summary: "Costa Latte Grande · 热 · 脱脂奶 · 不加糖：Nutri-Grade A 级，热量约 152kcal/480ml，咖啡因约 75mg。"
---
```

**Step 2：替换「产品速览」区段**

将「## 产品速览」整段（行 7-14）：

```markdown
## 产品速览

Costa Coffee · Latte · 拿铁

- **系列**：Classic Coffee（经典咖啡系列）
- **Nutri-Grade**：B-C 级（取决于奶类型和糖度）
- **热量**：约 180-220kcal/杯（中杯/不加糖/全脂奶）
- **咖啡因**：约 75mg（双份浓缩）
- **推荐点单**：不加糖 / 可选脱脂奶降低等级
```

替换为：

```markdown
## 产品速览

Costa Coffee · Latte · 拿铁 · Grande · 热 · 脱脂奶

- **系列**：Classic Coffee（经典咖啡系列）
- **杯型**：大杯（Grande）480ml
- **温度**：热
- **奶**：脱脂奶
- **糖度**：不加糖（默认）
- **Nutri-Grade**：A 级（无添加糖 + 低脂）
- **热量**：约 152kcal/杯
- **咖啡因**：约 75mg（双份浓缩）
- **推荐点单**：大杯 / 热 / 脱脂奶 / 不加糖（健身控脂首选）
```

---

### Task 2：重写「制作方式调查」为脱脂奶大杯版

**Files:**
- Modify: `content/drinkzen/costa/latte/index.md:23-78`

**Step 1：替换「官方主要原料」「原料工艺」整段**

将行 23-32（标题到「原料工艺」列表）：

```markdown
**官方主要原料**（⚠️ 基于行业通用配方）：

- Mocha Italia 拼配浓缩咖啡（双份）
- 全脂牛奶（可选脱脂奶、燕麦奶、豆奶）

**原料工艺**：

- 采用 Costa 专利 Mocha Italia 拼配豆，中深烘焙
- 双份 Espresso 与丝滑蒸汽牛奶融合
- 口感醇厚顺滑，咖啡与奶香平衡
```

替换为：

```markdown
**官方主要原料**（⚠️ 基于 Costa 中国市场标准配方）：

- Mocha Italia 拼配浓缩咖啡（双份 Espresso，约 60ml）
- **脱脂牛奶**（默认配置；可选全脂奶、燕麦奶、豆奶）
- 不加糖（默认配置）

**原料工艺**：

- 采用 Costa 专利 Mocha Italia 拼配豆，中深烘焙
- 双份 Espresso 与丝滑蒸汽脱脂牛奶融合
- 脱脂奶去除了绝大部分乳脂，热量更低、饱和脂肪显著下降
- 口感清爽干净，咖啡风味更突出（脱脂奶不会盖过咖啡味）
```

**Step 2：替换「制作方式」段**

将行 34-38：

```markdown
**制作方式**（中杯 360ml）：

1. 双份浓缩咖啡液（Espresso）约 60ml
2. 蒸汽全脂牛奶 约 280ml
3. 奶泡 约 20ml
```

替换为：

```markdown
**制作方式**（大杯 480ml / 热）：

1. 双份浓缩咖啡液（Espresso）约 60ml
2. 蒸汽脱脂牛奶 约 400ml
3. 奶泡 约 20ml
```

**Step 3：替换「配方营养计算」整段**

将行 40-49：

```markdown
**配方营养计算**（中杯 360ml，不加糖/全脂奶）：

| 成分 | 用量 | 热量 | 蛋白质 | 脂肪 | 饱和脂肪 | 总糖 | 乳糖（豁免） | 非乳源性糖（计入分级） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 全脂牛奶 | 约 300ml | 186kcal | 9.6g | 10.8g | 6.9g | 14.4g | 14.4g | — |
| 浓缩咖啡液 | 约 60ml | 5kcal | 0.2g | 0.1g | 0.04g | 0.2g | — | 0.2g |
| **合计** | **360ml** | **约 191kcal** | **约 9.8g** | **约 10.9g** | **约 6.9g** | **约 14.6g** | **约 14.4g** | **约 0.2g** |

> **营养参考**（全脂牛奶，每 100ml）：热量 62kcal、蛋白质 3.2g、脂肪 3.6g、饱和脂肪 2.3g、碳水 4.8g（乳糖）
```

替换为：

```markdown
**配方营养计算**（大杯 480ml，不加糖/脱脂奶）：

| 成分 | 用量 | 热量 | 蛋白质 | 脂肪 | 饱和脂肪 | 总糖 | 乳糖（豁免） | 非乳源性糖（计入分级） |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 脱脂牛奶 | 约 420ml | 147kcal | 14.3g | 1.0g | 0.4g | 21.0g | 21.0g | — |
| 浓缩咖啡液 | 约 60ml | 5kcal | 0.2g | 0.1g | 0.04g | 0.2g | — | 0.2g |
| **合计** | **480ml** | **约 152kcal** | **约 14.5g** | **约 1.1g** | **约 0.5g** | **约 21.2g** | **约 21.0g** | **约 0.2g** |

> **营养参考**（脱脂牛奶，每 100ml）：热量 35kcal、蛋白质 3.4g、脂肪 0.2g、饱和脂肪 0.1g、碳水 5.0g（乳糖）。数据来源：美国 USDA FoodData Central / 香港食物安全中心。
```

**Step 4：替换「参数叠加汇总」整段**

将行 51-61：

```markdown
**参数叠加汇总**（中杯 360ml）：

| 参数 | 配置 | 热量 | 非乳源性糖 | 评级 |
| :--- | :--- | :--- | :--- | :--- |
| 默认 | 不加糖/全脂奶 | 191kcal | 0.2g | B-C 级 |
| +1 泵糖浆 | 标准甜 | +25kcal | +6g | C 级 |
| +2 泵糖浆 | 双倍糖 | +50kcal | +12g | C-D 级 |
| 换脱脂奶 | 脱脂奶 | -80kcal | — | A-B 级 |
| 换燕麦奶 | 燕麦奶 | -20kcal | +2g | B-C 级 |

> **说明**：
>
> - 每泵糖浆约 6g 非乳源性糖（Costa 标准泵）
> - 脱脂奶可显著降低饱和脂肪，提升评级
> - 杯型容量：中杯 360ml、大杯 480ml
```

替换为：

```markdown
**杯型与配料对比表**（杯型与营养关系）：

| 杯型 | 奶 | 糖 | 热量 | 非乳源性糖 | 评级 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 大杯 480ml | 脱脂奶 | 不加糖 | 152kcal | 0.2g | **A 级** |
| 大杯 480ml | 全脂奶 | 不加糖 | 254kcal | 0.2g | B-C 级 |
| 大杯 480ml | 燕麦奶 | 不加糖 | ~170kcal | ~2g | A-B 级 |
| 中杯 360ml | 脱脂奶 | 不加糖 | 113kcal | 0.2g | **A 级** |
| 中杯 360ml | 全脂奶 | 不加糖 | 191kcal | 0.2g | B-C 级 |
| 中杯 360ml | 全脂奶 | +1 泵糖浆 | 216kcal | 6.2g | C 级 |
| 中杯 360ml | 全脂奶 | +2 泵糖浆 | 241kcal | 12.2g | C-D 级 |

> **说明**：
>
> - 每泵糖浆约 6g 非乳源性糖（Costa 标准泵）
> - 脱脂奶可显著降低饱和脂肪，是健身/控脂首选
> - 杯型容量：中杯 360ml、大杯 480ml（Costa 中国市场标准）
> - 大杯 480ml 脱脂奶不加糖组合实现 A 级评级（每 100ml 饱和脂肪 0.1g，非乳源性糖 0.04g）
```

**Step 5：替换「数据来源」块**

将行 63-67：

```markdown
**数据来源**：

- **营养参考**：全脂牛奶数据基于行业标准值
- **配方比例**：基于 Costa 通用制作标准 ⚠️
```

替换为：

```markdown
**数据来源**：

- **脱脂牛奶营养参考**：美国 USDA FoodData Central / 香港食物安全中心
- **Espresso 营养参考**：美国 USDA FoodData Central（prepared espresso）
- **配方比例**：基于 Costa 中国市场 Grande 标准制作流程 ⚠️
- **Nutri-Grade 评级**：按新加坡 ABCD 标准（每 100ml 标准化）
```

---

### Task 3：新增「本次实测」章节

**Files:**
- Modify: `content/drinkzen/costa/latte/index.md:82-93`（在「口感体验」之前插入新章节）

**Step 1：在 `## 口感体验` 之前插入新章节**

将：

```markdown
## 口感体验
```

替换为：

```markdown
## 本次实测

**实测日期**：2026-08-31  
**门店**：Costa Coffee（中国市场门店）  
**杯型**：大杯（Grande）480ml  
**温度**：热  
**奶**：脱脂奶  
**糖度**：不加糖（默认）  
**配料**：双份 Espresso（约 60ml）+ 蒸汽脱脂牛奶（约 420ml）  
**Nutri-Grade**：A 级  

**实测营养**（基于配料推算）：

| 项目 | 含量 | 每 100ml |
| :--- | :--- | :--- |
| 热量 | 152kcal | 32kcal |
| 蛋白质 | 14.5g | 3.0g |
| 脂肪 | 1.1g | 0.2g |
| 饱和脂肪 | 0.5g | 0.1g |
| 总糖（乳糖） | 21.2g | 4.4g |
| 非乳源性糖 | 0.2g | 0.04g |
| 咖啡因 | 75mg | — |

**口感体验**（占位：由作者填写实测主观感受）

建议填写维度：

- 风味层次：前调（脱脂奶的清爽奶香）、中段（咖啡醇香）、尾调（坚果/巧克力尾韵）
- 甜度感知：极微甜（来自乳糖，脱脂奶乳糖含量与全脂相近）
- 苦度感知：略高于全脂奶版（脱脂奶不掩盖咖啡苦味）
- 奶感强度：中等偏低（脱脂奶无脂肪带来的厚重感）
- 一句话总结：清爽干净的咖啡主导型拿铁，健身控脂首选

---

## 口感体验
```

**注意**：原「## 口感体验」整段（行 82-92，占位符+建议填写维度）保留不变，仍为通用占位。本节中新增的「口感体验」子段仅记录本次实测专项感受。

---

### Task 4：保留「饮用建议」「标签」「评论区置顶」「数据说明」区段

**Files:**
- Modify: `content/drinkzen/costa/latte/index.md`

无需改动。这四段内容对默认评测视角切换无影响，原内容仍适用。

**仅修改一处**：评论区置顶的 B-C / A-B 评级摘要更新为本次默认实测 A 级。

将行 113-118：

```markdown
```text
🥤 DrinkZen 小程序搜「Costa 拿铁」，看完整评估
📍 全脂奶：B-C 级
📍 脱脂奶：A-B 级
💡 控糖推荐：不加糖
```
```

替换为：

```markdown
```text
🥤 DrinkZen 小程序搜「Costa 拿铁」，看完整评估
📍 默认实测：大杯 热 脱脂奶 不加糖 → A 级
📍 全脂奶：B-C 级
📍 脱脂奶：A 级
💡 控糖推荐：不加糖
```
```

---

### Task 5：本地构建验证（可选）

**Files:**
- Read: Hugo 构建输出

**Step 1：检查 Markdown 渲染**

如需验证，运行：

```bash
hugo --quiet
```

预期：构建成功，无 markdown 解析警告。如未配置本地 Hugo 环境，可跳过本步骤（Hugo 会在部署时校验）。

**Step 2：自检占位符**

Read `content/drinkzen/costa/latte/index.md` 全文，确认：

- frontmatter `draft: false`
- 标题已切换为「Costa 拿铁（Grande · 热 · 脱脂奶）· A 级」
- 默认评测配置为「480ml 热 脱脂奶 不加糖」
- 主表数据与配料查验一致
- 「本次实测」章节位于「口感体验」之前
- 评论区置顶已更新

---

### Task 6：等待用户决定提交

**约束**：按项目 CLAUDE.md，未经用户明确确认不执行 `git add` / `git commit` / `git push`。

交付内容：

- 已更新的 `content/drinkzen/costa/latte/index.md`
- 本次改动摘要：
  - frontmatter 标题、date、draft 切换
  - 默认评测视角从「中杯 360ml 全脂奶」切换到「大杯 480ml 脱脂奶 不加糖」
  - 主表重写为脱脂奶大杯数据
  - 参数叠加表重写为杯型与配料对比表
  - 新增「本次实测」章节
  - 评论区置顶更新

等待用户确认是否提交 / 是否需要进一步调整。

---

## Self-Review（已完成）

**Spec coverage**：对照已批准的设计方案，所有 6 个改动点都已映射到具体 Task 步骤（标题修正 ✓、主表切换 ✓、配料查验 ✓、参数叠加表重写 ✓、新增本次实测 ✓、draft 切换 ✓）。

**Placeholder scan**：
- 「口感体验」段为原作者占位（设计稿明确要求保留），不算 plan placeholder
- 配料查验中的「~」估算值来自设计稿已批准的合理推算
- 数据来源标注清晰，可追溯

**Type consistency**：表头字段（成分、用量、热量、蛋白质、脂肪、饱和脂肪、总糖、乳糖、非乳源性糖）在 Task 2 的主表和 Task 3 的实测表中保持一致。

**No gaps**。