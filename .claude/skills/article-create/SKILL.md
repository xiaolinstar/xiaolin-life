---
name: article-create
description: |
  创作前期辅助：用户描述想法 → 智能归类（content/life|office）→ 创建 Hugo Page Bundle
  + 结构化 front matter + 标记 draft。
  触发：「想写一篇...」「新建一篇文章」「加个草稿」+ 描述主题。
  媒体上传请走 media-publish；饮品页面走 drinkzen；草稿发布（commit/push）由用户手动执行。
---

# Article Create

创作前期脚手架：把"想法"变成可写的 Page Bundle 草稿。

## 工具映射

| 工具 | 命令 | 用途 |
|---|---|---|
| `article.new` | `pnpm run article:create [path] "<title>"` | 创建 Page Bundle（draft: true）|

不指定 path 时走**关键词推荐**——参考 [references/sections.md](references/sections.md)。

## 标准流程

1. **理解意图**：用户说"想写一篇..."
2. **section 归类**：关键词匹配（详见 [references/sections.md](references/sections.md)）
3. **slug 生成**：用户手动指定（小写 + 连字符，**不自动**中文→pinyin）
4. **调用脚本**：

   ```bash
   pnpm run article:create life/thoughts/olympic-night-run "奥体夜跑随笔" \
     --description "夏夜的奥体中心..." \
     --tags 随笔 跑步 南京
   ```

5. **补正文**：编辑 `content/<path>/index.md`
6. **配图**（可选）：`pnpm run media:save content/<path> <img...>`
7. **预览**：`pnpm run site:dev`
8. **发布**：用户手动去掉 `draft: true` → `git commit` → `git push`

## 关键约束

- **草稿默认 draft: true**：避免误上线
- **section 必须有效**：仅 `life/` / `office/`（饮品走 drinkzen；about 手动）
- **slug 格式**：小写字母+数字+连字符，禁用空格/中文
- **不主动 push**：commit/push 由用户显式触发（遵循 `AGENTS.md`）

## 验证点

- 创建后 `index.md` 含完整 front matter（title / date / draft）
- `gallery/` 目录已建
- 路径与 `content/` 现有结构一致
- 默认 `draft: true`（除非 `--no-draft`）

## 配套 skill

| 任务 | skill |
|---|---|
| 配图 COS 上传 + CDN 改写 | [media-publish](../media-publish/SKILL.md) |
| 饮品品牌/详情页 | [drinkzen](../drinkzen/SKILL.md) |
| origin → 小红书分发 | [origin-distribute](../origin-distribute/SKILL.md) |

## 详细参考

- 工作流：[references/workflow.md](references/workflow.md)
- Section 归类：[references/sections.md](references/sections.md)
- Front matter 模板：[templates/frontmatter.template.md](templates/frontmatter.template.md)
- 静态资源说明：[assets/README.md](assets/README.md)
