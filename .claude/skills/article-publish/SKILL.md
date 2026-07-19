---
name: article-publish
description: >-
  End-to-end article publishing workflow for xiaolin-life: scaffold a Page
  Bundle draft, save images into gallery with whitelist and naming rules,
  upload to Tencent COS, rewrite Markdown to CDN URLs, then commit and push
  to main. Use when creating a new article, adding images to an article,
  publishing an article, or when a mobile/agent channel (Hermes) delivers
  images and text to publish. Images only — video is not supported yet.
---

# 文章发布（Layer A 工具链）

一条龙：建稿 → 收图 → 上传 COS → 改写 CDN → 提交推送。
设计目标：同一套命令在作者 Mac（Cursor）与 Hermes@腾讯轻量 VPS 上均可执行。
背景与决策见 `docs/DRAFT-OPENCLAW-HERMES-MOBILE.md`。

## 工具映射（Agent 视角）

| 工具（草案名） | 命令 | 说明 |
|---|---|---|
| `life.draft_article` | `./scripts/new-article.sh content/<区>/<slug> "标题" [--description "..."]` | 创建 Page Bundle（`draft: true`）+ `gallery/` |
| `life.save_media` | `./scripts/save-media.sh content/<区>/<slug> <图片...>` | 白名单校验 + 规范化命名入库 `gallery/` |
| `life.publish_media` | `./scripts/media-publish.sh content/<区>/<slug> --rewrite` | coscli 上传 COS + 校验直链 + carousel/assets 改写为 CDN URL |
| `life.commit_push` | `git add <文章>/index.md && git commit && git push` | **必须用户明确说「提交/推送」后执行**；目标 `main` |
| `life.status` | `git status -sb` + `gh run list --limit 3` | 工作区与最近 CI/CD 状态 |

## 约束（必须遵守）

- **只收图片**：`.jpg/.jpeg/.png/.webp/.gif`；视频一律拒绝并告知「暂不支持」。
- **单文件上限**：默认 20MB（`IMG_MAX_MB` 可调）；超限拒绝。
- **gallery/ 不进 Git**：只 commit `index.md`（及小体积 `featured.jpg`）。
- **上传在持有 `~/.cos.yaml` 的机器执行**（作者 Mac 或 Hermes VPS），凭证不外传。
- **push 前必须有用户明确指令**；push 后 CI 会跑 `media-verify`（URL 200 校验）与镜像构建。
- 命名、目录、front matter 细节遵循 `docs/MEDIA-STANDARDS.md`。

## 标准流程

```bash
# 1. 建稿（draft: true）
./scripts/new-article.sh content/life/entertainment/xinjiekou-food "新街口觅食记" \
  --description "新街口小巷的三家宝藏小店"

# 2. 收图（可多张；来自微信/相册的临时文件路径）
./scripts/save-media.sh content/life/entertainment/xinjiekou-food \
  /tmp/IMG_0101.jpg /tmp/IMG_0102.jpg

# 3. 补正文（Agent 起草，包含 {{< carousel images="gallery/*" ... >}} 即可）

# 4. 上传 + 改写（carousel → carousel-cdn，/assets/images/ → CDN）
./scripts/media-publish.sh content/life/entertainment/xinjiekou-food --rewrite

# 5. 本地预览（可选）
pnpm run site:dev   # http://localhost:1313

# 6. 用户确认后：去掉 draft: true → commit index.md → push main
```

## 验证点

- `media-publish.sh` 输出 `✓ 直链可访问`（CDN `https://media.xiaolin.fun/...` 返回 200）。
- 改写后 `index.md` 内不应再有 `gallery/*` 或 `/assets/images/` 引用（`rg 'gallery/\*|/assets/images/' <index.md>` 无输出）。
- push 后 `media-verify` workflow 绿色。

## Hermes / VPS 部署备忘

- VPS 需要：本仓 clone、`coscli` + `~/.cos.yaml`、仓库根 `.env`（`MEDIA_CDN_BASE`、`COS_PREFIX`）、GitHub 推送凭证。
- 微信图片先落 VPS 临时目录，再交给 `save-media.sh`；入库成功后可删临时文件，避免磁盘占满。
- 本 Skill 文本即 Hermes 的操作手册：工具名可注册为上表草案名，命令保持不变。
