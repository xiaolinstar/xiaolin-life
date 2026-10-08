# article-create

创作前期辅助：把"想法"变成可写的 Hugo Page Bundle 草稿。

## 快速使用

```bash
# 1. 智能归类（不指定 path）
pnpm run article:create "奥体夜跑随笔"
# → 推荐: life/thoughts/，等你指定 slug

# 2. 手动指定
pnpm run article:create life/thoughts/olympic-night-run "奥体夜跑随笔"

# 3. 完整参数
pnpm run article:create life/thoughts/olympic-night-run "奥体夜跑随笔" \
  --description "夏夜..." \
  --tags 随笔 跑步 南京 \
  --featured
```

## 触发场景

- 「想写一篇...」
- 「新建一篇文章」
- 「加个草稿」+ 描述主题

## 目录结构

按 Anthropic Claude Code Skills 规范：

```text
article-create/
├── SKILL.md                  # 必填
├── pyproject.toml            # uv 依赖
├── README.md
├── scripts/                  # 可执行脚本（不加载到 context）
│   └── new_article.py
├── references/               # 文档参考（按需加载）
│   ├── workflow.md
│   └── sections.md
├── templates/                # 可填充文本模板
│   └── frontmatter.template.md
└── assets/                   # 静态资源
    └── README.md
```

## 详见

- [SKILL.md](SKILL.md)
- [references/workflow.md](references/workflow.md)
- [references/sections.md](references/sections.md)
- [templates/frontmatter.template.md](templates/frontmatter.template.md)
