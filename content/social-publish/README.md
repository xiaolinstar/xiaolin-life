# 内容分发（distribute）

origin 内容的小红书/微博/大众点评等社媒版本。**由 [`origin-distribute`](../../.claude/skills/origin-distribute/SKILL.md) skill 生成。**

## 目录

```
content/social-publish/
├── README.md           本文件
├── drafts/             分发草稿（staging）
│   └── <slug>-<platform>.md
└── published/          （v2 预留）已发布追踪
```

## 状态机

```
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

`<origin-slug>-<platform>.md`

示例：

- `coconut-latte-xhs.md`（瑞幸生椰拿铁 → 小红书）
- `thai-milk-tea-latte-xhs.md`（泰奶鸳鸯拿铁 → 小红书）
- `manner-latte-weibo.md`（Manner 拿铁 → 微博，v2）

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
