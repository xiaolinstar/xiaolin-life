---
name: media-publish
description: >-
  Publish xiaolin-life article media to Tencent COS from the author's machine:
  upload gallery via coscli, verify public URLs, optionally rewrite Markdown.
  Use when adding or updating gallery images, publishing to COS, or migrating
  local gallery/* to remote URLs. Gallery is gitignored — upload must run locally.
---

# 媒体发布（本地 + CI 校验）

`content/**/gallery/` **不进 Git**，GitHub Actions **无法**读取母本文件，因此 **COS 上传必须在作者本机**执行。CI 只负责校验已写入 Markdown 的远程 URL、以及构建部署。

## 架构

```
作者本机                          GitHub
────────                          ──────
gallery/（gitignore）
    │
    ├─ media-publish.sh ──► COS
    │
    ├─ 改 index.md 为 COS URL
    │
    └─ git commit index.md ──► push ──► media-verify.yml（curl 校验 URL）
                                    └─► ci-ghcr.yml（构建瘦身镜像）
```

## 何时触发本 Skill

- 新增 / 更新文章 `gallery/` 图片或视频
- 问「怎么上传 COS」「怎么发布媒体」「gallery 怎么上线」
- 完成规范化命名后同步到 COS

## 前置条件

- 已 `coscli config init`（`~/.cos.yaml`）
- 项目根目录执行
- 文章目录符合 Page Bundle：`content/<path>/index.md` + `gallery/`

## 发布流程

### 1. 上传并校验（必做，本地）

```bash
# 单篇文章
./scripts/media-publish.sh content/life/entertainment/gulou-riverfront

# 上传 + 改写 index.md 中的 /assets/images/ 路径（不含 carousel gallery/*）
./scripts/media-publish.sh content/life/entertainment/gulou-riverfront --rewrite
```

或 `pnpm run media:publish -- content/life/entertainment/gulou-riverfront`

脚本会：

1. `upload-media-cos.sh` 同步到 `life/entertainment/gulou-riverfront/`
2. `curl` 校验至少一个直链 200
3. `--rewrite` 时调用 `rewrite-media-urls.py`（仅 `/assets/images/`）

### 2. 替换正文引用（手动或 agent 协助）

| 引用类型 | 替换时机 | 方式 |
|----------|----------|------|
| Markdown `![](/assets/images/...)` | 上传后 | `--rewrite` 或 `pnpm run media:rewrite:apply` |
| `{{< carousel images="gallery/*" >}}` | 上传后 | 改 `carousel-cdn` + COS URL；front matter 加 `build.publishResources: false` |
| `featured.jpg` | 可选 | front matter 指定 COS URL，或保留小文件 |

**COS URL 格式**（CDN 未配时用直链）：

```
https://media-1300240022.cos.ap-nanjing.myqcloud.com/life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg
```

CDN 购买后只换域名前缀为 `https://media.xiaolin.fun/`，路径不变。

### 3. 提交并推送（仅 Markdown）

```bash
git add content/life/entertainment/gulou-riverfront/index.md
git commit -m "content: 鼓楼滨江媒体改 COS 链接"
git push
```

**不要** `git add gallery/`（已 gitignore）。

### 4. CI 自动执行

- `media-verify.yml`：校验 content 里 `https://...jpg|png|mp4` 返回 200
- `ci-ghcr.yml`：Hugo 构建；若 Markdown 已是 COS URL，`public/` 不含大图，镜像 ~10–20MB

## 为何不用「上传 + 替换」一条 GHA？

| 方案 | 可行？ | 原因 |
|------|--------|------|
| GHA 上传 gallery | ❌ 默认不可行 | gallery 已 gitignore，runner 无文件 |
| GHA 上传 + 若 gallery 进 Git | ⚠️ 临时可行 | 与「媒体不进 Git」目标冲突 |
| GHA `workflow_dispatch` + artifact | ⚠️ 可行但繁琐 | 本地打包 zip 再手动触发 |
| **本地 publish + GHA verify/build** | ✅ 推荐 | 简单、符合 gitignore 策略 |

若未来需要 CI 上传，只能二选一：

1. 迁移完成前暂时把 `gallery/` 提交进 Git；或
2. 本地 `media-publish.sh` 上传后，CI 只做 URL 校验与构建（当前方案）。

## 相关文件

- `docs/MEDIA-STANDARDS.md` — 命名与目录规范
- `docs/MEDIA-OSS.md` — COS/CDN 部署
- `scripts/media-publish.sh` — 本地发布入口
- `scripts/upload-media-cos.sh` — coscli sync
- `scripts/rewrite-media-urls.py` — `/assets/images/` → URL
- `.github/workflows/media-verify.yml` — 远程 URL 校验

## Agent 执行清单

用户说「发布媒体」「上传 COS」时：

1. 确认 `coscli` 与 `~/.cos.yaml`
2. 运行 `media-publish.sh` 对目标文章目录
3. 协助改 `index.md`：`carousel-cdn` + COS URL + `publishResources: false`
4. 仅 commit `index.md`，不 commit gallery
5. 提醒 push 后 CI 会 verify + build
