# 内容分发（distribute）

origin 内容的小红书/微博/大众点评等社媒版本。**由 [`origin-distribute`](../../.claude/skills/origin-distribute/SKILL.md) skill 生成。**

## 目录

```html
content/social-publish/
├── README.md           本文件
├── drafts/             分发草稿（staging）
│   └── <slug>-<platform>.md
└── published/          （v2 预留）已发布追踪
```

## 状态机

```html
origin（content/.../index.md）
  ↓ origin-distribute skill
drafts/<slug>-xhs.md（草稿）
  ↓ 人工发布到小红书 APP
（已发布，不进 git）
  ↓ （v2 评估）
published/<slug>-xhs.md（发布记录）
```

**v1 只到 `drafts/`**——发布动作在小红书 APP 完成，发布后的数据（点赞/评论/收藏）由人工维护，不进 git。

## 命名规范

`<origin-slug>.md`（一份 origin 一个文件，按平台分章节）

示例：

- `coconut-latte.md`（瑞幸生椰拿铁 → 小红书）
- `thai-milk-tea-latte.md`（泰奶鸳鸯拿铁 → 小红书 + 大众点评）
- `costa-latte.md`（Costa 拿铁 → 小红书 + 大众点评，门店向）
- `manner-latte.md`（Manner 拿铁 → 微博，v2）

`platforms` 字段在 frontmatter 里声明覆盖的平台，文档内按平台分章节（如 `## 小红书` / `## 大众点评`）。

## Git 策略

- `drafts/*.md` **入仓**——可追溯「哪天打算发什么」
- `published/*` **暂不入仓**——含发布 ID/链接等敏感元数据
- `gallery/*` 与 origin 共享（已在 `.gitignore` 中排除）

## 与 origin 的关系

| 维度 | origin | 分发版 |
| --- | --- | --- |
| 内容 | 完整长文 | 压缩 ≤80 字 |
| 媒介 | Hugo 站点 | 社媒 APP |
| 更新责任 | 一次发布，长期 SEO | 一次性发布，无历史 |
| 修改权限 | git | 不可修改（已发即终） |
| 数据一致性 | Source of Truth | **必须 1:1 同步** |

**重叠是常态**：origin 与小红书大量文字重叠是正常的，不是 bug。SEO 视角下 origin 是 canonical URL。

## 平台定位差异（重要）

| 平台 | 评价对象 | 主战场 | 内容重心 |
| :--- | :--- | :--- | :--- |
| 小红书 | 单品饮品 / 选题内容 | 推流算法 | 数据钩子 + 个人体验 + 知识科普 |
| 大众点评 | **门店** | 评分 + 短评 | 空间氛围 + 服务 + 适合场景（饮品数据仅作佐证） |

**核心原则**：

- 小红书笔记 = 内容分享（drink-first）
- 大众点评笔记 = 门店评价（store-first），饮品数据最多一段带过
- 一份 origin 可能生成 1 份小红书 + 1 份大众点评，但**两边的正文结构、图片位、文风完全不同**
