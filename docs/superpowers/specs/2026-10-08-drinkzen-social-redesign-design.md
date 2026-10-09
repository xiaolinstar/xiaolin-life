# DrinkZen Skill 三合一 + 饮品社媒分发收编设计

日期：2026-10-08
状态：待评审
站点：xiaolin-life（Hugo + Blowfish）+ drinkzen.cn 后台

## 背景与目标

`origin-distribute` skill 名义上"通用"，但实际只服务饮品（`content/social-publish/drafts/` 7 个 draft 全是 drinkzen origin）。同时：

- 小红书 v2.3 模板的 8 条铁律、5 段结构、字数控制全是饮品场景踩出来的，套到生活/办公文章会很怪
- 大众点评模板缺失（`operation-plan` 写"同步短评"，但 origin-distribute 没建模板）
- drinkzen 技能包已是 2 模块（content + admin），把 social 收编进来更聚焦

**目标**：让饮品运营的"创作 → 后台 → 分发"三步全部落在 `drinkzen` 一个 skill 下。`origin-distribute` 退为占位，留给未来生活/办公类分发。

成功标准：

- 饮品运营只触达 `drinkzen` 一个 skill（不必跳到 origin-distribute）
- 小红书 v2.3 模板知识不丢（v2.3+ 继续演化为 v3）
- 7 个现有 draft 平移到对应 origin 文章，不丢字段
- 大众点评模板从无到有建立
- `origin-distribute` 仍有占位 description，未来需要时直接启用

## 方案选择（已确认）

采用 **方案 A：收编到 drinkzen 作为第 3 子模块**。

不采用：

- 方案 B：创建独立 `drinkzen-social` skill —— 用户否决（"drinkzen 的技能包含 3 部分，更集中"）
- 方案 C：不拆分、扩展 origin-distribute —— 与用户意图不符（模板不适合通用文章）

**术语统一**：饮品 → 小红书 / 大众点评 的分发版本统一称为 **plog**（photo log，生活类社交媒体常用术语，隐含图文混合形态）。一个饮品页一份 plog，内部用 tabs 区分长版（小红书，≤ 800 字）与短版（大众点评，≤ 30 字）。

**Skill frontmatter 规范**：按 Anthropic 官方 skill 规范（[agentskills.io/specification](https://agentskills.io/specification.md) + [github.com/anthropics/skills](https://github.com/anthropics/skills)）：
- `name` ≤ 64 字符，小写字母数字连字符
- `description` ≤ 1024 字符（非空，含触发词）
- `metadata` 允许任意 key-value（**官方允许**，本设计不删）
- `allowed-tools` 可选（Experimental）
- `license` / `compatibility` 可选
- 多行 YAML description 用 `>-` 折叠语法（项目惯例，单行过长时）

**目录组织**：按 spec 区分 `references/`（documentation）与 `assets/`（templates, resources）——这是用户提醒后核实的结果，本项目当前混用 `references/`，新结构按 spec 区分。

## 整体结构

### Skill 树（drinkzen v2.0.0）

```text
.claude/skills/drinkzen/
├── SKILL.md                          （更新：Anthropic 规范 frontmatter + 3 子模块入口）
├── references/                       （文档类：spec "documentation"）
│   ├── content.md                    （保留：饮品 Hugo 创作）
│   ├── admin.md                      （保留：drinkzen.cn 后台）
│   ├── README.md                     （新增：social 子模块入口与工作流）
│   └── title-formulas.md             （迁入：标题公式）
└── assets/                           （模板类：spec "templates, resources"）
    └── plog-template.md              （合并：原 xhs v2.3 + 大众点评短评模板）
```

`drinkzen/SKILL.md` 改为（Anthropic 规范 frontmatter）：

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
| **content** | [content.md](references/content.md) | 品牌页 / 单杯详情页 / 模板 / 命名规范 |
| **admin** | [admin.md](references/admin.md) | `drinkzen-admin` CLI / 品牌资料 / 菜单模板 / Logo / 投稿审阅 |
| **social** | [README.md](references/README.md) | plog 模板入口 + 工作流 + 标题公式 |

## ⚠️ 安全提示

`drinkzen-admin` 写操作必须先 `--dry-run`，详见 admin 子模块。
```

### 文章结构（origin + distribution 合一）

饮品页可包含以下可选 H2 段（位置：放在饮用建议/标签之后，作为最末段）：

```markdown
{{< tabs "plog" >}}
{{< tab "📕 plog 长版（小红书 / 微博，≤800 字）" >}}

[完整可粘贴内容 — v2.3 模板套用]

{{< /tab >}}
{{< tab "📍 plog 短版（大众点评，≤30 字）" >}}

[完整可粘贴内容 — 短评模板套用]

{{< /tab >}}
{{< /tabs >}}
```

**frontmatter 扩展**（可选，仅当存在分发版时）：

```yaml
platforms: [xiaohongshu]          # 实际覆盖哪些平台就填哪些；缺哪个 tab 哪个
```

**tabs 灵活性**：

- 若 origin 已有小红书长版 + 大众点评短版 → 2 tabs（长版 + 短版）
- 若只有小红书长版（迁移阶段） → 单 tab（仅长版）
- 若两者都缺 → 不写 `## plog 分发版` 段

**为什么用 `{{< tabs >}}` 收起**：

- 默认不打扰正常阅读（饮品测评的主体仍是配料/口感/营养）
- 可手动展开查看（运营需要复制粘贴时方便）
- Hugo 仍会渲染进 HTML，搜索引擎可索引
- 不依赖主题外 shortcode（Blowfish 原生支持）

## skill 文件改动清单

| 动作 | 源 | 目标 |
| --- | --- | --- |
| 新写 | — | `.claude/skills/drinkzen/references/README.md`（social 子模块入口） |
| 新写 | — | `.claude/skills/drinkzen/assets/plog-template.md`（合并自 xiaohongshu v2.3 + 大众点评短评） |
| 移动 | `.claude/skills/origin-distribute/references/title-formulas.md` | `.claude/skills/drinkzen/references/title-formulas.md` |
| 重写 | `.claude/skills/drinkzen/SKILL.md` | Anthropic 规范 frontmatter + 3 子模块入口（**保留** `metadata:` 块，spec 允许） |
| 删除 | `.claude/skills/origin-distribute/references/xiaohongshu-template.md` | — |
| 删除 | `.claude/skills/origin-distribute/references/title-formulas.md` | — |
| 更新 | `.claude/skills/origin-distribute/SKILL.md` description | 改为"通用 origin → 社媒分发占位 skill；饮品场景请走 drinkzen" |

> **目录语义**（按 Anthropic spec）：
> - `references/` = documentation（README、title-formulas、content.md、admin.md）
> - `assets/` = templates, resources（plog-template.md）
>
> 当前项目惯例是把所有子模块文件放在 `references/`，新结构首次区分 `assets/`。

## draft → article 迁移清单

7 个 draft 都在 `content/social-publish/drafts/*.md`，每个 frontmatter 都有 `origin:` 字段指向源文章。

| draft 文件 | 目标 origin | 迁入 tab | 状态 |
| --- | --- | --- | --- |
| `autumn-osmanthus-fermented-rice-latte.md` | `content/drinkzen/luckincoffee/autumn-osmanthus-fermented-rice-latte/index.md` | plog 长版 | slug 已确认 |
| `mo-cha-nai-lao-na-tie.md` | `content/drinkzen/luckincoffee/mo-cha-nai-lao-na-tie/index.md` | plog 长版 | slug 已确认 |
| `liu-xin-zhi-shi-na-tie.md` | `content/drinkzen/luckincoffee/liu-xin-zhi-shi-na-tie/index.md` | plog 长版 | slug 已确认 |
| `costa-latte.md` | 实施时按 frontmatter `origin:` 字段精确取值 | plog 长版 | 实施时核对 |
| `coconut-latte.md` | 实施时按 frontmatter `origin:` 字段精确取值 | plog 长版 | 实施时核对 |
| `fei-se-yue-guang.md` | 实施时按 frontmatter `origin:` 字段精确取值 | plog 长版 | 实施时核对 |
| `thai-milk-tea-latte.md` | 实施时按 frontmatter `origin:` 字段精确取值 | plog 长版 | 实施时核对 |

> 7 个 draft 都是小红书长版，迁入后只填 plog 长版 tab。plog 短版（大众点评）将在日常运营中按需补充，不在本次迁移范围。

**实施前必做**：写一个验证脚本（`bash` + `grep` 即可），遍历 7 个 draft 的 `origin:` 字段，确认每个路径都存在且唯一。失败即停。

**字段映射**（draft → origin article 内嵌段）：

| draft 字段 | origin 处理 |
| --- | --- |
| `## 标题` 内容 | 保留为 plog 长版 tab 的子标题或段首 |
| `## 小红书` text 代码块 | 保留，作为 plog 长版 tab 的核心可粘贴内容 |
| `### 标签` 内容 | 保留 |
| `### 评论区置顶` 内容 | 保留 |
| `## 图片清单` | 保留（运营对照发布用） |
| `## 📸 图片生成指引` | 不嵌入文章；迁移到 `references/README.md` 作为通用指引 |
| `## 自检清单` | 不嵌入文章；迁移到 `assets/plog-template.md` 作为模板自检项 |
| `## 发布后操作` | 不嵌入文章；迁移到 `references/README.md` 作为发布后 SOP |
| frontmatter `origin` | 不需要（已经是 origin 自身） |
| frontmatter `platforms` | 写入 origin frontmatter 顶层（值 `[xiaohongshu]`） |
| frontmatter `generated` | 写入 social 段顶部 HTML 注释 `<!-- generated: 2026-XX-XX by drinkzen-social v2.x -->` |
| frontmatter `status` | 隐含（段存在 = draft/ready；运营用 draft→published 心智） |

**draft 文件迁移后删除**；`content/social-publish/` 整个目录删除（含 `README.md`）。

## plog 模板设计（合并小红书 + 大众点评）

文件：`.claude/skills/drinkzen/assets/plog-template.md`

**模板结构**：

```markdown
# plog 模板 v1

> 合并小红书长版（≤800 字）+ 大众点评短版（≤30 字）于一份模板。
> 源自秋桂米酿拿铁复盘升级（小红书 v2.3）+ operation-plan 大众点评同步短评需求。

## 标题公式（两个平台共享）

| 平台 | 公式 | 字数 |
| --- | --- | --- |
| 小红书 | `<卡路里>大卡 <评级> <风味钩子>` | ≤ 20 字 |
| 大众点评 | 一句话点单感受 | ≤ 15 字 |

## plog 长版（小红书，≤ 800 字）

[5 段结构：营养参数 / 热量评级 / 制作配方 / 口感体验 / 健康建议]

## plog 短版（大众点评，≤ 30 字）

[3 行结构：味道 + 服务 + 一句感受]

## 通用铁律（两个平台共享）

- 无内部链接
- 无感叹号
- 无 markdown 列表符号
- 无 markdown 加粗
- 段落尾部无句号
```

**触发条件**：每篇饮品 origin 至少做一份 plog（包含长版 + 短版）。运营可手动跳过（`<tabs>` 段缺失）。

**标签规则**（继承 operation-plan v2.3）：

- 必带 2：`#奶茶仙人 #DrinkZen`
- 城市饮品 tag 仅限南京本地饮品（独立门店 / 南京限定产品）
- 流量词根据门店类型选（南京本地 / 全国连锁）

## origin-distribute 调整

保留 skill（不删除），做最小调整：

| 文件 | 改动 |
| --- | --- |
| `origin-distribute/SKILL.md` description | 改为："通用 origin → 社媒分发的占位 skill（生活/办公文章场景）。饮品 plog 分发请走 `drinkzen` skill 的 social 子模块。" |
| `origin-distribute/references/` 目录 | 删除 `xiaohongshu-template.md`、`title-formulas.md`（已迁走）；目录留空时整目录删除 |
| `origin-distribute/SKILL.md` 正文 | 删掉"饮品测评"示例描述；改为通用 origin 分发的占位说明 |
| `origin-distribute/SKILL.md` frontmatter | 按 Anthropic 规范重构（description 单行 ≤ 200 字符、含触发词；如使用多行 description 需符合 `>-` 折叠语法） |

`skills-lock.json`：

```json
"origin-distribute": {
  "path": ".claude/skills/origin-distribute",
  "sourceType": "project-local"
}
```

保留 entries，无需修改 version。

## skills-lock.json 调整

`drinkzen` 项 version `"1.2.0"` → `"2.0.0"`，path 不变：

```json
"drinkzen": {
  "path": ".claude/skills/drinkzen",
  "version": "2.0.0",
  "sourceType": "project-local"
}
```

其他 entries 不动。

## 验证

1. **skill 路径**：`.claude/skills/drinkzen/{references/README.md, references/title-formulas.md, assets/plog-template.md}` 3 个新文件存在
2. **Anthropic 规范 frontmatter**：`drinkzen/SKILL.md` 字段齐全（`name` / `description` ≤ 1024 / `license` / `allowed-tools` / `metadata`）；description 含触发词
3. **目录组织**：`references/` 装文档，`assets/` 装模板（按 spec 区分）
4. **skill 描述**：`drinkzen/SKILL.md` 提到 3 个子模块；`origin-distribute/SKILL.md` 不再提饮品测评
5. **7 个 draft 已迁移**：每篇对应 origin 文章末尾有 `{{< tabs >}}` 包裹的 plog 段
6. **`content/social-publish/` 已删除**
7. **Hugo 构建**：`pnpm run site:build` 成功，无 shortcode 报错
8. **plog preview**：本地 `pnpm run site:dev`，访问任一已迁移饮品页，tabs 短code 渲染正常，展开/收起符合预期
9. **skills-lock.json 一致**：`drinkzen.version` 为 `2.0.0`
10. **回流检查**：git log 中 7 个 draft 的删除与 7 篇文章的修改对应

## 非目标（明确排除）

- 不实现自动发布（小红书/大众点评 API 封闭）
- 不实现已发布追踪（manifest.json / 状态看板）
- 不重新创作 7 个 draft 的内容（**忠实迁移**，v2.3 知识不变）
- 不修改饮品 origin 文章正文（除追加 social 段）
- 不创建独立的 drinkzen-social skill
- 不重构 origin-distribute 为新模板（保留占位）
- 不引入新依赖（短code 全用 Blowfish 原生）

## 风险与回滚

### 风险

| 风险 | 概率 | 影响 | 缓解 |
| --- | --- | --- | --- |
| `<tabs>` 短code 在某些 Hugo 渲染场景失效 | 低 | 中 | fallback：可改为 `<details>` HTML 短code 或裸 H2 |
| draft 迁移中字段遗漏（如图片清单） | 中 | 中 | 用 `git diff` 在迁移前/后对比每个 origin 文章的完整性 |
| 大众点评模板不准确（首版可能踩坑） | 中 | 低 | 模板附带 v1 → v2 演进位，运营踩坑后直接增量修订 |
| skills-lock 误改破坏 skill 注册 | 低 | 高 | version bump 前先 dry-run 比对 |

### 回滚

- 整体回滚：`git revert` 提交链
- 单文件回滚：`git checkout HEAD~1 -- <path>`
- 7 个 draft 文件如需恢复：`git checkout HEAD~1 -- content/social-publish/`

## 落地步骤（高层）

**执行顺序**：先建 skill 骨架（步骤 1-7），再迁移 draft（步骤 8-10），最后验证（步骤 11-12）。中间任何一步失败可停在对应位置，不污染后续。

1. 移动 `title-formulas.md` 到 `references/`
2. 写 `references/README.md`（social 子模块入口，含图片生成指引、发布后 SOP）
3. 写 `assets/plog-template.md`（合并小红书 v2.3 + 大众点评短版）
4. 更新 `drinkzen/SKILL.md`（Anthropic 规范 frontmatter + 3 子模块入口 + 保留 `metadata:` 块）
5. 更新 `origin-distribute/SKILL.md`（description + 删引用文件）
6. 删 `origin-distribute/references/` 残余
7. **核对前置**：写脚本遍历 7 个 draft 的 `origin:` 字段，确认路径存在且唯一
8. 逐个迁移 7 个 draft（origin 文章追加单 tab 的 plog 长版段 + 更新 frontmatter `platforms: [xiaohongshu]`）
9. 删 `content/social-publish/`
10. `pnpm run site:build` 验证
11. 提交 git，commit message 走 Conventional Commits：`refactor(drinkzen): 收编 plog 分发为第 3 子模块 + 7 draft 迁移`

---

**评审通过后**进入 `writing-plans` 阶段，生成详细实施计划。