# 创作前期工作流

## 触发场景

- 用户描述"想写一篇..."、"加个草稿"、"新建文章"
- Agent 识别意图，调用 article-create

## 流程

### 1. 理解意图

从用户描述中提取：

- **主题**：要写什么
- **风格**：随笔 / 教程 / 评测
- **大致分类**：生活 / 办公 / 饮品

### 2. Section 归类

见 [sections.md](sections.md)。Agent 根据关键词推荐，或用户直接指定。

### 3. Slug 生成

- 用户手动指定（小写 + 连字符）
- **不自动**中文→pinyin（避免歧义，由用户决定）

### 4. 调用脚本

```bash
# 智能归类（不指定 path）
pnpm run article:create "奥体夜跑随笔"
# → 推荐 section，等用户补 slug

# 手动指定完整路径
pnpm run article:create life/thoughts/olympic-night-run "奥体夜跑随笔"

# 完整参数
pnpm run article:create life/thoughts/olympic-night-run "奥体夜跑随笔" \
  --description "夏夜的奥体中心..." \
  --tags 随笔 跑步 南京 \
  --categories 生活记录 \
  --featured
```

### 5. 结构化 Front Matter

脚本自动生成（[templates/frontmatter.template.md](../templates/frontmatter.template.md)），含：

- title（必填）
- date（今天）
- draft: true（默认）
- description / tags / categories（用户传则填）

### 6. 用户补正文

编辑 `content/<path>/index.md`，完成草稿。

### 7. 配图（可选）

```bash
pnpm run media:save content/<path> <图片1> <图片2>...
```

### 8. 预览

```bash
pnpm run site:dev   # http://localhost:1313
```

### 9. 发布

**手动**（按 `AGENTS.md` 规则，Agent 不主动 push）：

1. 编辑 `index.md` 把 `draft: true` 改为 `false`
2. `git add content/<path>/index.md`
3. `git commit -m "feat: ..."`
4. `git push`

## 边界

| 场景 | 用哪个 skill |
|---|---|
| 新建生活/办公文章 | **article-create**（本 skill）|
| 新建饮品页 | **[drinkzen](../drinkzen/SKILL.md)** skill |
| 已建文章配图 | **[media-publish](../media-publish/SKILL.md)** skill |
| 改 CDN URL | **[media-publish](../media-publish/SKILL.md)** skill |
| origin → 小红书 | **[origin-distribute](../origin-distribute/SKILL.md)** skill |
