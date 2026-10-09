# DrinkZen Skill 三合一 + plog 分发收编 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把饮品社媒分发从 `origin-distribute` 收编到 `drinkzen` 的第 3 子模块；用 plog 术语统一小红书 + 大众点评；7 个旧 draft 平移到对应 origin 文章；按 Anthropic 官方 skill 规范重构 drinkzen frontmatter。饮品类运营只触达 `drinkzen` 一个 skill。

**Architecture:** drinkzen skill 用 `references/`（documentation）+ `assets/`（templates）区分目录；origin-distribute 保留为占位 skill；7 个 draft 通过 Python 迁移脚本一次性转换为 origin 文章末尾的 `<tabs>` 段；frontmatter 字段按 Anthropic 规范（含 `metadata: allowed`）。

**Tech Stack:** Hugo 0.158+ / Blowfish / Python 3（迁移脚本 + pytest）/ pnpm。

**Spec:** [docs/superpowers/specs/2026-10-08-drinkzen-social-redesign-design.md](../specs/2026-10-08-drinkzen-social-redesign-design.md)

## Global Constraints

- **不修改 `themes/blowfish` submodule**（直接禁动）
- **不自动 git 操作**：subagent 阶段**禁止** `git add` / `git commit` / `git status` 之类写 git 状态命令；只允许 `git mv`（任务核心动作，非验证）。`ls` / `head` / `wc` / `cat` 等只读验证 OK。所有变更由用户手动 `git add` + commit。`git status` 也跳过（避免暴露 staged 信息，commit 时再查）
- **不修改 7 个 origin 文章的现有正文**：仅追加 `## plog 分发版` 段 + frontmatter 加 `platforms`
- **不重新创作 7 个 draft 的内容**：忠实迁移，v2.3 知识一字不改
- **plog 术语**：饮品 → 小红书 / 大众点评 的分发版本统一称 plog（photo log）
- **目录语义**：按 Anthropic spec 区分 `references/`（docs）与 `assets/`（templates）
- **Conventional Commits**：commit message 走 `feat` / `refactor` / `chore` / `fix` 等
- **markdownlint**：所有 `*.md` 文件遵守 `.markdownlint-cli2.jsonc` 规则
- **drinkzen admin 安全铁律**：本次 plan 不触发 CLI 写命令（admin skill 安全铁律与本 plan 无关）

---

## Phase 1 · Skill 骨架（5-7 任务）

### Task 1: 迁移 title-formulas.md 到 drinkzen/references/

**Files:**

- Move: `.claude/skills/origin-distribute/references/title-formulas.md` → `.claude/skills/drinkzen/references/title-formulas.md`

**Interfaces:**

- Produces: `.claude/skills/drinkzen/references/title-formulas.md` 路径可用

- [ ] **Step 1: 用 git mv 移动文件（保留历史）**

```bash
git mv .claude/skills/origin-distribute/references/title-formulas.md \
       .claude/skills/drinkzen/references/title-formulas.md
```

- [ ] **Step 2: 验证文件已在新路径**

Run: `ls -la .claude/skills/drinkzen/references/title-formulas.md`  
Expected: 文件存在，原路径不存在

- [ ] **Step 3: 暂存（不 commit）**

```bash
git add -A
git status  # 应显示 rename: origin-distribute/.../title-formulas.md → drinkzen/.../title-formulas.md
```

> ⚠️ 不执行 `git commit`，等用户授权。

---

### Task 2: 创建 assets/plog-template.md（合并小红书 v2.3 + 大众点评短版）

**Files:**

- Create: `.claude/skills/drinkzen/assets/plog-template.md`

**Interfaces:**

- Consumes: xiaohongshu v2.3 知识（来自 `.claude/skills/origin-distribute/references/xiaohongshu-template.md`，将删除）+ 大众点评短评需求
- Produces: 单文件模板，含 plog 长版（≤800 字）+ plog 短版（≤30 字）+ 通用铁律

- [ ] **Step 1: 创建 assets 目录**

Run: `mkdir -p .claude/skills/drinkzen/assets`

- [ ] **Step 2: 写 plog-template.md**

写入 [`.claude/skills/drinkzen/assets/plog-template.md`](.claude/skills/drinkzen/assets/plog-template.md)，内容如下：

```markdown
# plog 模板 v1

> 合并小红书长版（≤800 字）+ 大众点评短版（≤30 字）于一份模板。
> 源自小红书 v2.3 模板（秋桂米酿拿铁复盘升级）+ operation-plan 大众点评同步短评需求。
> 维护者：运营 + Claude；规则冲突时优先小红书铁律（更长更精细）。

## 标题公式（两平台共享思路，公式各异）

| 平台 | 公式 | 字数 |
| --- | --- | --- |
| 小红书（plog 长版） | `<卡路里>大卡 <评级> <风味钩子>` | ≤ 20 字 |
| 大众点评（plog 短版） | 一句话点单感受 | ≤ 15 字 |

---

## plog 长版（小红书，≤ 800 字）

### 5 段结构（连续编号【1】→【5】，无缺口）

#### 【1】营养参数 ⚠️ <口径>

必含：热量（含口径）+ 糖（总糖 + 非乳源性糖）+ 蛋白质 / 脂肪 / 饱和脂肪 + 咖啡因（含来源：单源/双源）+ 杯量 + 冰块占比。

#### 【2】热量评级：<等级>

必含：饱和脂肪 g/100ml + 等级 + 非乳源性糖 g/100ml + 等级 + 取较差项 → 最终等级 + 克重数据（唯一降级方式）+ 热版对比（如有）+ 同系列对比（如有）。

#### 【3】制作配方 · N 层叠加

必含：完整 N 层原料清单（含最后一步）+ 每原料克重/毫升 + 关键工艺说明（千目级/双窨制/IIAC 金奖/1:8 打发等）+ 制作流程箭头链（杯底→步骤1→…→顶部）。

#### 【4】口感体验（活人感一段话）

必含：连贯主观体验（开盖→饮完）+ 饮用方式提示（先尝/搅拌/大口喝等）+ 关键感官对比（冰 vs 热）+ 工艺让位说明（短萃让位桂香等设计意图）。

#### 【5】健康建议 ⚠️

必含：特殊人群（驾驶员/孕妇/酒精过敏者/控脂/控糖；含米酒/酒精警告作为法规要求保留）+ 饮用方式 + 控糖说明（最低糖度限制/唯一降级方式）。

---

## plog 短版（大众点评，≤ 30 字）

```text
<品牌>·<饮品>：<一句话感受>
味道：<2-5 字>
服务：<2-5 字>
```

- 主图：origin gallery 首图
- 标签：5-8 个（必带 `#奶茶仙人 #DrinkZen`）
- 不写完整营养参数（不在大众点评定位内）

---

## 通用铁律（两平台共享）

| 铁律 | 说明 |
| --- | --- |
| 无内部链接 | 禁止 `[text](/drinkzen/...)` `[text](url)` 等 |
| 无感叹号 | 禁止 `！` `!`（含半角全角） |
| 无 markdown 列表 | 禁止 `-` `*` `+` `1.` `1.` 开头 |
| 无 markdown 加粗 | 禁止 `**text**` |
| 无博主实测 | origin 中的"博主实测"默认不进入 plog（除非有官方背书） |
| 段落尾部无句号 | 每段最后一句结尾不写句号（段中分句句号保留） |
| 不补卖点 | origin 没写的卖点禁止凭空添加 |

**判断原则**：plog 是直接粘贴发布的纯文本。所有站点内部链接 / 标记语法粘过去都会变成字面字符。**粘到平台是否会变成字面字符 / AI 生成感是否强烈** 是核心判断。

---

## Origin 抽取清单（必抽字段）

| 字段 | origin 位置 | 必含原因 |
| --- | --- | --- |
| 上市日期 | frontmatter `date` + 首段 | 头部信息必含 |
| 同日上新产品 | `## 产品速览` 系列段 | 系列上下文 |
| 所属系列 | `## 产品速览` | 横向对比锚点 |
| 默认配置 | `## 产品速览` | 头部信息必含 |
| Nutri-Grade 评级 | `## 产品速览` + `## Nutri-Grade 评级` | 标题 + 评级段 |
| 热量（含口径） | `## 产品速览` + 营养表 | 标题 + 营养段 |
| 咖啡因 + 来源 | `## 产品速览` | 营养段 |
| 工艺认证 | `## 产品速览` + `## 制作方式调查` | 制作配方 / 口感体验段 |
| 原料 + 克重（完整 N 层） | `## 制作方式调查` 步骤 1-N | 制作配方段（不能漏最后一步） |
| 关键工艺说明 | `## 制作方式调查` | 制作配方段 |
| 风味层次 | `## 口感体验` | 口感体验段 |
| 冰 vs 热对比 | `## 饮用建议` | 口感 + 健康建议段 |
| 饮用方式 | `## 饮用建议` | 健康建议段 |
| 标签词 | frontmatter `tags` | 标签段 |

---

## 标签三档（8-10 个）

```text
# 必带 2-3：#奶茶仙人 #DrinkZen [可选 #城市饮品]
# 栏目 2：#每日打卡 / #饮品测评
# 流量 3-5：城市相关 + 通用流量 mix
```

**变量替换规则**（v2.3 升级，2026-10-06）：

- **必带 2-3**：`#奶茶仙人` + `#DrinkZen` 必带；`#南京饮品` 等城市 tag **仅限南京本地饮品**
- **全国连锁饮品**：只用必带 2，不加城市 tag
- **流量词**：南京本地 → `#南京美食 #南京探店 #新街口`；全国连锁 → `#饮品分享 #今日打卡 #咖啡日常`
- **限定首发**：加 `#首发` / `#限定回归`（不超过 1 个）

---

## 评论区置顶（小红书）

发布后立即置顶第一条评论：

```text
🥤 DrinkZen 小程序搜「<产品名>」，看完整评估
📍 门店：<区/路 + 品牌>（origin 中有则用，无则「待补」）
💡 推荐点单：<冰度> / <糖度> / <杯型>
```

涉及过敏原 / 酒精 / 杯型时，加 `⚠️ <警告内容>` 行。

---

## 自检 checklist（生成 plog 后逐项核对）

- [ ] 标题 ≤ 20 字，无 `|`，无感叹号，无敏感词（减肥/瘦身/掉秤）
- [ ] plog 长版 ≤ 800 字（红线 1000）
- [ ] plog 长版 5 段连续编号【1】→【5】，无缺口
- [ ] plog 长版无 markdown 内部链接 / 感叹号 / 列表符号 / 加粗
- [ ] plog 短版 ≤ 30 字，含"味道 + 服务 + 一句感受"
- [ ] 标签 8-10 个，三档齐全
- [ ] 所有数字与 origin 完全一致
- [ ] 评论区置顶 3-7 行，含核心引流
- [ ] 警告条件已触发（参见 [警告触发条件]）

### 警告触发条件

| 触发条件 | 警告内容 | 必含位置 |
| --- | --- | --- |
| D 级评级 | "D 级警告 / 控脂慎点" | 标题 + 【2】 + 评论区 |
| 含米酒 / 含醇 | "驾驶员 / 孕妇禁点" | 头部 + 【5】 + 评论区 |
| 控糖期无法降到 B 级 | "最低糖度已无法降级" | 【2】 + 【5】 |
| 没有"不另外加糖"选项 | "最低糖度就是微甜" | 头部 + 评论区 |

---

## v1 → v2 演进位

踩坑后直接增量修订本文件顶部"v1 → v2 关键变化"段落，记录新增/调整的铁律与公式。
```

- [ ] **Step 3: 验证文件写入**

Run: `wc -l .claude/skills/drinkzen/assets/plog-template.md`  
Expected: 非空（>100 行）

- [ ] **Step 4: 暂存**

```bash
git add .claude/skills/drinkzen/assets/plog-template.md
git status  # 应显示 new file: drinkzen/assets/plog-template.md
```

> ⚠️ 不 commit。

---

### Task 3: 创建 references/README.md（social 子模块入口）

**Files:**

- Create: `.claude/skills/drinkzen/references/README.md`

**Interfaces:**

- Consumes: assets/plog-template.md 路径
- Produces: social 子模块入口文档（工作流 + 触发 SOP）

- [ ] **Step 1: 写 references/README.md**

写入 [`.claude/skills/drinkzen/references/README.md`](.claude/skills/drinkzen/references/README.md)，内容：

````markdown
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
````

- [ ] **Step 2: 验证文件**

Run: `wc -l .claude/skills/drinkzen/references/README.md`  
Expected: 非空（>50 行）

- [ ] **Step 3: 暂存**

```bash
git add .claude/skills/drinkzen/references/README.md
git status
```

> ⚠️ 不 commit。

---

### Task 4: 重写 drinkzen/SKILL.md（Anthropic 规范 frontmatter + 3 子模块）

**Files:**

- Modify: `.claude/skills/drinkzen/SKILL.md`（整文件覆盖）

**Interfaces:**

- Consumes: references/{content,admin,README}.md + assets/plog-template.md
- Produces: drinkzen v2.0.0 frontmatter（含 metadata）+ 3 子模块入口

- [ ] **Step 1: 完整覆盖 drinkzen/SKILL.md**

写入 [`.claude/skills/drinkzen/SKILL.md`](.claude/skills/drinkzen/SKILL.md)，内容：

```markdown
---
name: drinkzen
description: 饮品运营三件套：Hugo 品牌页/单杯测评创建、drinkzen.cn 后台维护、小红书/大众点评 plog 分发。触发词：奶茶、品牌页、饮品测评、菜单模板、Logo、DrinkZen、plog、审稿。
allowed-tools: Bash(drinkzen-admin:*)
license: MIT
metadata:
  version: "2.0.0"
  author: xiaolin
  tags: ["drinkzen", "beverage", "tea", "milktea", "brand", "plog"]
---

# DrinkZen

饮品端到端工作流：① Hugo 站点内容创作 ② drinkzen.cn 平台后台 ③ 社媒 plog 分发。

## 子模块

| 子模块 | 路径 | 覆盖场景 |
| --- | --- | --- |
| **content** | [references/content.md](references/content.md) | 品牌页 / 单杯详情页 / 模板 / 命名规范 |
| **admin** | [references/admin.md](references/admin.md) | `drinkzen-admin` CLI / 品牌资料 / 菜单模板 / Logo / 投稿审阅 |
| **social** | [references/README.md](references/README.md) | plog 模板入口 + 工作流 + 标题公式 |

## ⚠️ 安全提示

`drinkzen-admin` 写操作必须先 `--dry-run` + `--json` 输出给用户审阅，确认后再正式执行。详见 [admin 子模块](references/admin.md) 顶部安全铁律。
```

- [ ] **Step 2: 验证 frontmatter 解析**

Run: `head -5 .claude/skills/drinkzen/SKILL.md`  
Expected: `---` 开头，第二行是 `name: drinkzen`

- [ ] **Step 3: 暂存**

```bash
git add .claude/skills/drinkzen/SKILL.md
git status
```

> ⚠️ 不 commit。

---

### Task 5: 更新 origin-distribute/SKILL.md（占位 description）

**Files:**

- Modify: `.claude/skills/origin-distribute/SKILL.md`

- [ ] **Step 1: 重写 SKILL.md 为占位版**

写入 [`.claude/skills/origin-distribute/SKILL.md`](.claude/skills/origin-distribute/SKILL.md)，内容：

```markdown
---
name: origin-distribute
description: 通用 origin → 社媒分发的占位 skill（生活/办公文章场景）。饮品 plog 分发请走 drinkzen skill 的 social 子模块。触发词：同步、分发、适配小红书、xhs 推文、社媒版（仅限生活/办公文章）。
allowed-tools: 
license: MIT
metadata:
  version: "0.1.0"
  author: xiaolin
  tags: ["origin-distribute", "placeholder", "social-media"]
  status: placeholder  # 占位 skill，待生活/办公文章分发需求出现时启用
---

# origin-distribute（占位）

通用 origin → 社媒分发的占位 skill。当前**未启用**——饮品场景已迁到 drinkzen/social，生活/办公文章暂未触达分发需求。

## 何时启用

当出现以下场景时启用本 skill：

- 生活文章（content/life/）需要同步到小红书 / 微博
- 办公文章（content/office/）需要生成推文版
- 任意非饮品类 origin 需要做平台适配

启用步骤：

1. 在本目录创建 `references/` 子目录
2. 编写通用 origin 模板（不同于 plog，不含 Nutri-Grade / 饮品参数）
3. 更新 frontmatter `metadata.status: placeholder` → `active`
4. 移动本 skill 到 drinkzen 同级目录（如必要）

## 当前状态

```yaml
metadata:
  status: placeholder  # 占位
```

**请勿在饮品场景使用本 skill**——所有饮品社媒分发请走 `drinkzen` skill 的 social 子模块（`references/README.md`）。

## 占位原因

1. 饮品场景已独立到 drinkzen（更适合深耕）
2. 生活/办公文章当前未触达分发需求
3. 通用模板未编写（避免过早抽象）
```

- [ ] **Step 2: 验证文件**

Run: `head -10 .claude/skills/origin-distribute/SKILL.md`  
Expected: frontmatter 含 `metadata.status: placeholder`

- [ ] **Step 3: 暂存**

```bash
git add .claude/skills/origin-distribute/SKILL.md
git status
```

> ⚠️ 不 commit。

---

### Task 6: 删除 origin-distribute/references/ 残余文件

**Files:**

- Delete: `.claude/skills/origin-distribute/references/xiaohongshu-template.md`
- Delete: `.claude/skills/origin-distribute/references/title-formulas.md`（如仍在）

> 注：title-formulas.md 已在 Task 1 移到 drinkzen/references/，本 Task 6 主要是兜底删除。

- [ ] **Step 1: 删除 xiaohongshu-template.md**

```bash
git rm .claude/skills/origin-distribute/references/xiaohongshu-template.md
```

- [ ] **Step 2: 检查 title-formulas 是否还在原位**

Run: `ls -la .claude/skills/origin-distribute/references/title-formulas.md 2>&1`  
Expected: `No such file or directory`（Task 1 已移走）

若仍存在（异常情况），删除：

```bash
git rm .claude/skills/origin-distribute/references/title-formulas.md
```

- [ ] **Step 3: 检查 references 目录是否为空**

Run: `ls -la .claude/skills/origin-distribute/references/ 2>&1`  
Expected: 仅 `.` 和 `..`（目录为空）

- [ ] **Step 4: 删除空目录**

```bash
git rm -r .claude/skills/origin-distribute/references/ 2>&1
# 若 git 报 "did not have any entries to remove"，跳过此步，目录已被 .gitignore 或空处理
```

或手动：

```bash
rmdir .claude/skills/origin-distribute/references/
```

- [ ] **Step 5: 验证 origin-distribute 目录最终状态**

Run: `ls -la .claude/skills/origin-distribute/`  
Expected: 仅 `SKILL.md` 一个文件

- [ ] **Step 6: 暂存**

```bash
git add -A
git status
```

> ⚠️ 不 commit。

---

### Task 7: 更新 skills-lock.json（drinkzen version 1.2.0 → 2.0.0）

**Files:**

- Modify: `skills-lock.json`

- [ ] **Step 1: 编辑 drinkzen 的 version 字段**

Read current `skills-lock.json`：

```bash
grep -A 3 '"drinkzen"' skills-lock.json
```

Expected: 当前 `"version": "1.2.0"`。

修改：

```bash
# 用 sed 或 Edit 工具替换 "1.2.0" → "2.0.0"（仅 drinkzen 段）
# 推荐用 Edit 工具，避免误改其他 version
```

精确修改（Edit 工具）：

- old_string: `"drinkzen": {\n      "path": ".claude/skills/drinkzen",\n      "version": "1.2.0",\n      "sourceType": "project-local"\n    }`
- new_string: `"drinkzen": {\n      "path": ".claude/skills/drinkzen",\n      "version": "2.0.0",\n      "sourceType": "project-local"\n    }`

- [ ] **Step 2: 验证 JSON 合法**

Run: `python3 -c "import json; json.load(open('skills-lock.json')); print('valid')"`  
Expected: `valid`

- [ ] **Step 3: 验证 drinkzen version 已更新**

Run: `grep -A 3 '"drinkzen"' skills-lock.json`  
Expected: `"version": "2.0.0"`

- [ ] **Step 4: 暂存**

```bash
git add skills-lock.json
git status
```

> ⚠️ 不 commit。

---

## Phase 2 · 迁移脚本与执行（3 任务）

### Task 8: 写迁移脚本 + 单元测试（TDD）

**Files:**

- Create: `scripts/migrate_drinkzen_plog.py`
- Create: `scripts/test_migrate_drinkzen_plog.py`

**Interfaces:**

- Consumes: `content/social-publish/drafts/*.md`（7 个 draft）
- Produces: 每个 draft 对应 origin 文章末尾追加 `## plog 分发版` 段 + frontmatter 加 `platforms: [xiaohongshu]`

- [ ] **Step 1: 写失败测试 1（frontmatter 解析）**

```python
# scripts/test_migrate_drinkzen_plog.py
from migrate_drinkzen_plog import extract_origin_path, extract_xhs_section

def test_extract_origin_path():
    sample = """---
title: foo
origin: content/drinkzen/luckincoffee/foo/index.md
platforms: [xiaohongshu]
generated: 2026-09-30
status: draft
---

# 标题

## 小红书

```text
content
```
"""
    assert extract_origin_path(sample) == "content/drinkzen/luckincoffee/foo/index.md"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_extract_origin_path -v`  
Expected: `FAILED` (function not defined)

- [ ] **Step 3: 实现 `extract_origin_path`**

```python
# scripts/migrate_drinkzen_plog.py
import re

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ORIGIN_RE = re.compile(r"^origin:\s*(.+)$", re.MULTILINE)

def extract_origin_path(content: str) -> str | None:
    """从 draft frontmatter 提取 origin 路径"""
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return None
    origin_match = ORIGIN_RE.search(fm_match.group(1))
    return origin_match.group(1).strip() if origin_match else None
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_extract_origin_path -v`  
Expected: `PASSED`

- [ ] **Step 5: 写失败测试 2（xhs section 提取）**

```python
def test_extract_xhs_section():
    sample = """## 标题

**xxx**

## 小红书

```text
📍 今日饮品
内容
```

### 标签

#tag1

### 评论区置顶

🥤 line1

## 图片清单

- 图 1

## 📸 图片生成指引
（跳过此段）

## 自检清单
（跳过）

## 发布后操作
（跳过）
"""
    sections = extract_xhs_section(sample)
    assert "今日饮品" in sections["text"]
    assert "#tag1" in sections["tags"]
    assert "line1" in sections["pinned"]
    assert "图 1" in sections["images"]
    assert "图片生成指引" not in sections["text"]
```

- [ ] **Step 6: 跑测试确认失败**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_extract_xhs_section -v`  
Expected: `FAILED`

- [ ] **Step 7: 实现 `extract_xhs_section`**

```python
XHS_SECTION_RE = re.compile(
    r"## 小红书\s*\n(.*?)(?=\n## |\Z)",
    re.DOTALL,
)

def extract_xhs_section(content: str) -> dict:
    """从 draft 提取 xhs 文本块 + 标签 + 评论区置顶 + 图片清单"""
    # 找到 ## 小红书 段
    xhs_match = XHS_SECTION_RE.search(content)
    xhs_text = xhs_match.group(1).strip() if xhs_match else ""
    
    # 找到 ## 小红书 之后到下一个 ## 之前的 ### 标签 + ### 评论区置顶
    tags_match = re.search(r"### 标签\s*\n(.*?)(?=\n### |\n## |\Z)", content, re.DOTALL)
    tags = tags_match.group(1).strip() if tags_match else ""
    
    pinned_match = re.search(r"### 评论区置顶\s*\n(.*?)(?=\n### |\n## |\Z)", content, re.DOTALL)
    pinned = pinned_match.group(1).strip() if pinned_match else ""
    
    images_match = re.search(r"## 图片清单\s*\n(.*?)(?=\n## 📸|\n## 自检|\n## 发布后|\Z)", content, re.DOTALL)
    images = images_match.group(1).strip() if images_match else ""
    
    return {"text": xhs_text, "tags": tags, "pinned": pinned, "images": images}
```

- [ ] **Step 8: 跑测试确认通过**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_extract_xhs_section -v`  
Expected: `PASSED`

- [ ] **Step 9: 写失败测试 3（tabs 段组装）**

```python
def test_build_tabs_section():
    sections = {
        "text": "📍 今日饮品",
        "tags": "#tag1",
        "pinned": "🥤 line",
        "images": "- 图 1",
    }
    output = build_tabs_section(sections, draft_origin="content/foo.md")
    assert "## plog 分发版" in output
    assert "{{< tabs \"plog\" >}}" in output
    assert "📕 plog 长版" in output
    assert "📍 今日饮品" in output
    assert "#tag1" in output
    assert "🥤 line" in output
    assert "<!-- generated" in output  # 包含生成元数据注释
```

- [ ] **Step 10: 跑测试确认失败**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_build_tabs_section -v`  
Expected: `FAILED`

- [ ] **Step 11: 实现 `build_tabs_section`**

```python
def build_tabs_section(sections: dict, draft_origin: str) -> str:
    """组装 plog tabs Markdown 段"""
    return f'''## plog 分发版

<!-- generated from {draft_origin} by migrate_drinkzen_plog.py on $(date +%Y-%m-%d) -->

{{< tabs "plog" >}}
{{< tab "📕 plog 长版（小红书 / 微博，≤800 字）" >}}

{sections["text"]}

### 标签

{sections["tags"]}

### 评论区置顶

{sections["pinned"]}

## 图片清单

{sections["images"]}

{{< /tab >}}
{{< /tabs >}}
'''
```

- [ ] **Step 12: 跑测试确认通过**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_build_tabs_section -v`  
Expected: `PASSED`

- [ ] **Step 13: 写失败测试 4（origin frontmatter 更新）**

```python
def test_update_origin_frontmatter():
    original = """---
title: 秋桂米酿拿铁
date: 2026-09-30
draft: false
categories: [饮品记录, 奶茶仙人]
tags: [luckincoffee, autumn]
---

[正文]
"""
    updated = update_origin_frontmatter(original, platforms=["xiaohongshu"])
    assert "platforms: [xiaohongshu]" in updated
    assert "categories: [饮品记录, 奶茶仙人]" in updated  # 保留原字段
    assert "[正文]" in updated  # 保留正文
```

- [ ] **Step 14: 跑测试确认失败**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_update_origin_frontmatter -v`  
Expected: `FAILED`

- [ ] **Step 15: 实现 `update_origin_frontmatter`**

```python
def update_origin_frontmatter(content: str, platforms: list[str]) -> str:
    """在 origin frontmatter 添加或更新 platforms 字段"""
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return content
    frontmatter = fm_match.group(1)
    body = content[fm_match.end():]
    
    platforms_str = ", ".join(platforms)
    platforms_line = f"platforms: [{platforms_str}]"
    
    if re.search(r"^platforms:\s*\[", frontmatter, re.MULTILINE):
        # 已存在则替换
        frontmatter = re.sub(
            r"^platforms:\s*\[.*$",
            platforms_line,
            frontmatter,
            flags=re.MULTILINE,
        )
    else:
        # 不存在则加到 frontmatter 末尾
        frontmatter = frontmatter.rstrip() + "\n" + platforms_line + "\n"
    
    return f"---\n{frontmatter}---\n{body}"
```

- [ ] **Step 16: 跑测试确认通过**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py::test_update_origin_frontmatter -v`  
Expected: `PASSED`

- [ ] **Step 17: 写主入口函数 `migrate_draft`**

```python
# scripts/migrate_drinkzen_plog.py（追加）

def migrate_draft(draft_path: Path, dry_run: bool = True) -> dict:
    """迁移单个 draft 到 origin 文章"""
    content = draft_path.read_text(encoding="utf-8")
    origin_path = extract_origin_path(content)
    if not origin_path:
        return {"ok": False, "error": "no origin path"}
    
    origin_full = Path(origin_path)
    if not origin_full.exists():
        return {"ok": False, "error": f"origin not found: {origin_path}"}
    
    sections = extract_xhs_section(content)
    tabs_md = build_tabs_section(sections, str(draft_path))
    
    origin_content = origin_full.read_text(encoding="utf-8")
    updated = update_origin_frontmatter(origin_content, platforms=["xiaohongshu"])
    # 在正文末尾追加 tabs 段
    updated = updated.rstrip() + "\n\n" + tabs_md
    
    if not dry_run:
        origin_full.write_text(updated, encoding="utf-8")
    
    return {
        "ok": True,
        "draft": str(draft_path),
        "origin": str(origin_full),
        "preview": updated[-500:] if dry_run else None,
    }


def migrate_all(drafts_dir: Path, dry_run: bool = True) -> list[dict]:
    """迁移所有 draft"""
    return [migrate_draft(p, dry_run=dry_run) for p in sorted(drafts_dir.glob("*.md"))]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="actually write changes")
    parser.add_argument("--drafts-dir", default="content/social-publish/drafts")
    args = parser.parse_args()
    
    dry_run = not args.write
    results = migrate_all(Path(args.drafts_dir), dry_run=dry_run)
    
    for r in results:
        if r["ok"]:
            print(f"✓ {r['draft']} → {r['origin']}")
        else:
            print(f"✗ {r['draft']}: {r['error']}")
    
    print(f"\n{len([r for r in results if r['ok']])}/{len(results)} ok")
    print(f"mode: {'dry-run' if dry_run else 'WRITE'}")
```

- [ ] **Step 18: 写主入口测试**

```python
# scripts/test_migrate_drinkzen_plog.py（追加）
import tempfile
from pathlib import Path

def test_migrate_draft_dry_run(tmp_path):
    # 创建临时 draft
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    origin_dir = tmp_path / "origin"
    origin_dir.mkdir()
    (origin_dir / "index.md").write_text(
        "---\ntitle: foo\ndate: 2026-01-01\n---\n\n正文\n",
        encoding="utf-8",
    )
    (drafts / "foo.md").write_text(
        "---\ntitle: foo\norigin: origin/index.md\nplatforms: [xiaohongshu]\ngenerated: 2026-01-01\nstatus: draft\n---\n\n## 小红书\n\n```text\n📍 今日饮品\n```\n\n### 标签\n\n#tag\n\n### 评论区置顶\n\n🥤 line\n\n## 图片清单\n\n- 图 1\n",
        encoding="utf-8",
    )
    
    from migrate_drinkzen_plog import migrate_draft
    result = migrate_draft(drafts / "foo.md", dry_run=True)
    assert result["ok"]
    
    # dry_run 不应修改文件
    assert (origin_dir / "index.md").read_text(encoding="utf-8") == "---\ntitle: foo\ndate: 2026-01-01\n---\n\n正文\n"
```

- [ ] **Step 19: 跑全部测试**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py -v`  
Expected: 全部 `PASSED`（5 个测试：extract_origin_path / extract_xhs_section / build_tabs_section / update_origin_frontmatter / migrate_draft_dry_run）

- [ ] **Step 20: 暂存**

```bash
git add scripts/migrate_drinkzen_plog.py scripts/test_migrate_drinkzen_plog.py
git status
```

> ⚠️ 不 commit。

---

### Task 9: 跑迁移脚本（dry-run + 写模式）

**Files:**

- (No file changes in this task; uses script from Task 8)

- [ ] **Step 1: dry-run 预览**

```bash
python3 scripts/migrate_drinkzen_plog.py --dry-run
```

Expected: 输出 `7/7 ok`，列出每个 draft 的目标 origin 路径

- [ ] **Step 2: 检查每个 origin 路径都存在**

```bash
python3 -c "
import json, re
from pathlib import Path
DRAFTS = Path('content/social-publish/drafts')
for d in sorted(DRAFTS.glob('*.md')):
    content = d.read_text(encoding='utf-8')
    m = re.search(r'^origin:\s*(.+)$', content, re.MULTILINE)
    if not m:
        print(f'MISSING origin: {d}')
        continue
    origin = Path(m.group(1).strip())
    if not origin.exists():
        print(f'NOT FOUND: {d} -> {origin}')
    else:
        print(f'OK: {d.name} -> {origin}')
"
```

Expected: 全部 `OK`，无 `NOT FOUND` / `MISSING`

- [ ] **Step 3: 实际写入**

```bash
python3 scripts/migrate_drinkzen_plog.py --write
```

Expected: `7/7 ok`，mode: `WRITE`

- [ ] **Step 4: 验证 7 个 origin 文章都已更新**

```bash
for f in content/drinkzen/luckincoffee/autumn-osmanthus-fermented-rice-latte/index.md \
         content/drinkzen/luckincoffee/mo-cha-nai-lao-na-tie/index.md \
         content/drinkzen/luckincoffee/liu-xin-zhi-shi-na-tie/index.md; do
    echo "=== $f ==="
    grep -c "## plog 分发版" "$f"
    grep "platforms:" "$f" | head -1
done
```

Expected: 每篇 `## plog 分发版` 出现 1 次，frontmatter 有 `platforms: [xiaohongshu]`

> 对其他 4 篇（costa-latte / coconut-latte / fei-se-yue-guang / thai-milk-tea-latte），slug 按实际路径验证：

```bash
grep -A 1 "^origin:" content/social-publish/drafts/costa-latte.md content/social-publish/drafts/coconut-latte.md content/social-publish/drafts/fei-se-yue-guang.md content/social-publish/drafts/thai-milk-tea-latte.md
```

- [ ] **Step 5: 跑单元测试确认未破坏**

Run: `python3 -m pytest scripts/test_migrate_drinkzen_plog.py -v`  
Expected: 全部 `PASSED`

- [ ] **Step 6: 暂存 7 个 origin 文件修改**

```bash
git add content/drinkzen/
git status
```

> ⚠️ 不 commit。

---

### Task 10: 人工核对每篇 origin 文章的 plog 段

**Files:**

- Verify: 7 个 origin 文章的 plog 段完整性

- [ ] **Step 1: 抽检第 1 篇（autumn）**

```bash
# 找到对应 origin 路径
ORIGIN=$(grep "^origin:" content/social-publish/drafts/autumn-osmanthus-fermented-rice-latte.md | awk '{print $2}')
echo "Origin: $ORIGIN"
echo "==="
tail -100 "$ORIGIN"
```

按 Step 1 的 5 项 checklist 核对本文档的 plog 段：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 2: 抽检第 2 篇（mocha）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/mo-cha-nai-lao-na-tie.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 3: 抽检第 3 篇（liu-xin）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/liu-xin-zhi-shi-na-tie.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 4: 抽检第 4 篇（costa）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/costa-latte.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 5: 抽检第 5 篇（coconut）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/coconut-latte.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 6: 抽检第 6 篇（fei-se-yue-guang）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/fei-se-yue-guang.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 7: 抽检第 7 篇（thai-milk-tea-latte）**

```bash
ORIGIN=$(grep "^origin:" content/social-publish/drafts/thai-milk-tea-latte.md | awk '{print $2}')
tail -100 "$ORIGIN"
```

按 5 项 checklist 核对：

- [ ] 末尾 `## plog 分发版` 段存在
- [ ] tabs 短code 包裹（`{{< tabs "plog" >}}` + `{{< /tabs >}}`）
- [ ] 至少 1 个 `<tab>` 标签，长版文案完整
- [ ] 标签段、评论区置顶段、图片清单段都已包含
- [ ] frontmatter `platforms: [xiaohongshu]` 已添加

- [ ] **Step 8: 修复任何不一致（若有）**

若发现 plog 段缺失关键字段、图片清单为空、tabs 语法错误等问题：

1. 直接 Edit 对应 origin 文章
2. 再次跑 Task 9 Step 1-3 验证（dry-run → write）
3. 记录修复内容到 PR description

- [ ] **Step 9: 暂存任何修复**

```bash
git add content/drinkzen/
git status
```

> ⚠️ 不 commit。

---

## Phase 3 · 清理与验证（3 任务）

### Task 11: 删除 content/social-publish/ 整个目录

**Files:**

- Delete: `content/social-publish/`（含 `drafts/`、`drafts/*.md` 7 个文件、`README.md`）

- [ ] **Step 1: 确认所有 7 个 draft 已迁移**

```bash
ls content/social-publish/drafts/*.md | wc -l
```

Expected: `7`

- [ ] **Step 2: 删除目录**

```bash
git rm -r content/social-publish/
```

- [ ] **Step 3: 验证删除**

```bash
ls content/social-publish/ 2>&1
```

Expected: `No such file or directory`

- [ ] **Step 4: 暂存**

```bash
git status
```

> ⚠️ 不 commit。

---

### Task 12: Hugo 构建 + dev server 验证

**Files:**

- (No file changes; verification only)

- [ ] **Step 1: Hugo 静态构建**

Run: `pnpm run site:build`  
Expected: 构建成功，exit code 0，无 shortcode 报错

- [ ] **Step 2: 检查构建产物**

Run: `ls -la public/drinkzen/luckincoffee/autumn-osmanthus-fermented-rice-latte/ 2>&1 | head -10`  
Expected: 目录存在（含 `index.html`）

- [ ] **Step 3: 验证 tabs 渲染**

Run: `grep -c "plog 分发版\|tabs.*plog" public/drinkzen/luckincoffee/autumn-osmanthus-fermented-rice-latte/index.html`  
Expected: > 0（HTML 中含 tabs 相关标记）

- [ ] **Step 4: 启动 dev server（手动）**

Run: `pnpm run site:dev`（后台运行，浏览器访问 `http://localhost:1313/drinkzen/luckincoffee/autumn-osmanthus-fermented-rice-latte/`）

Expected:

- 页面正常加载
- 文末"plog 分发版" tab 可见
- 展开 tab 后看到 plog 长版文案
- 无 shortcode 渲染错误

- [ ] **Step 5: 停 dev server**

在终端 Ctrl+C 终止 dev server。

- [ ] **Step 6: 记录任何渲染问题（若有）**

若发现 shortcode 报错或 tabs 不显示，记录问题描述，等 plan 完成后修复。

> ⚠️ 不在此步 commit（无文件改动）。

---

### Task 13: 最终 commit + summary

**Files:**

- (No file changes; git commit only)

- [ ] **Step 1: 确认所有改动已暂存**

```bash
git status
```

Expected: 仅 Phase 1-3 修改的文件（无未跟踪的 stray 文件）

- [ ] **Step 2: 列出待 commit 的变更摘要**

```bash
git diff --staged --stat
```

向用户汇报变更摘要（含文件数、行数），请求 commit 授权。

- [ ] **Step 3: 等待用户授权 commit**

> ⚠️ 项目 CLAUDE.md 规则：禁止自动 git commit。需用户明确授权。

用户授权后，建议 commit message：

```text
refactor(drinkzen): 收编 plog 分发为第 3 子模块 + 7 draft 迁移

- drinkzen skill 升级到 v2.0.0，按 Anthropic 规范重构 frontmatter（保留 metadata）
- 新增 social 子模块（references/README.md 入口 + assets/plog-template.md 模板）
- 用 plog 术语统一小红书长版（≤800 字）+ 大众点评短版（≤30 字）
- 7 个 social-publish draft 平移到对应 origin 文章末尾（tabs 短code 包裹）
- origin-distribute 退为占位 skill（description 重写）
- skills-lock.json drinkzen version 1.2.0 → 2.0.0
- 新增迁移脚本 scripts/migrate_drinkzen_plog.py（含 pytest 5 个测试）

Co-Authored-By: Claude Code <noreply@anthropic.com>
```

- [ ] **Step 4: 报告完成**

向用户发送最终 summary：

- 实施的 spec：[docs/superpowers/specs/2026-10-08-drinkzen-social-redesign-design.md](../specs/2026-10-08-drinkzen-social-redesign-design.md)
- 实施计划（本文件）
- 改动文件数（用 `git diff --stat HEAD`）
- 测试结果（5 passed）
- Hugo 构建结果
- 后续观察：下次饮品 origin 创建时按新 social 子模块 SOP 执行

---

## Self-Review Checklist（plan 完成后自检）

- [x] Spec 章节覆盖：架构 / 迁移 / 模板 / 文档更新 / 验证 / 风险 — 全部映射到任务
- [x] 没有 "TBD" / "implement later" / "类似 Task N"
- [x] 每个代码步骤有实际代码块（不是 "写测试" / "实现" 的占位）
- [x] 文件路径精确（不是 "path/to/file"）
- [x] 命令有 expected 输出
- [x] DRY：测试用例与脚本共用同套函数
- [x] YAGNI：未引入 spec 外的功能
- [x] TDD：Task 8 完整 TDD 循环（test → fail → implement → pass）
- [x] 频繁 commit：每 Task 末尾有"暂存"步骤，commit 集中在 Task 13

---

**计划完成，待用户授权执行。**