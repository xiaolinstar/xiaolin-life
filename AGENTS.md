# AGENTS.md — xiaolin-life

> 跨 Agent 通用说明（Cursor / Codex / Copilot / Claude Code 等都读这份）。
> Claude 专有规则在 [CLAUDE.md](CLAUDE.md)。

## 项目概述

基于 **Hugo + Blowfish** 的个人生活静态站点（南京生活、轻松办公、城市探索、日常思考）。站点镜像通过 GHCR 部署到 `124.222.98.227:8081`，由 `xiaolin-gateway` 反向代理。

**项目类型**：content 类静态站（详见 [dev-standards env-registry](https://github.com/xiaolinstar/dev-standards/blob/main/playbook/env-registry.yaml)）。

## 技术栈

| 类别 | 技术 |
|------|------|
| 静态站点 | Hugo 0.158+ extended |
| 主题 | Blowfish（`themes/blowfish/`，git submodule，跟踪 `main`） |
| 包管理 | pnpm 9.15 |
| 媒体 | 腾讯云 COS + CDN（凭证在 `~/.cos.yaml`，不进仓库） |
| 部署 | Docker 多阶段构建 + GHCR + rsync CD |
| Lint | markdownlint-cli2（`.markdownlint-cli2.jsonc`） |
| Hooks | Husky 9 + commitlint + lint-staged |

## 目录结构

```text
config/           Hugo 配置
content/          全部 Markdown 内容（page bundle 模式）
  drinkzen/       饮品测评（多品牌）
  life/           生活记录
  office/         轻松办公
  about/          关于页面
static/assets/    站点级小资源
themes/blowfish/  主题（git submodule，勿直接编辑）
layouts/          自定义布局（ICP 备案、llms.txt）
assets/img/       Hugo 管道资源
scripts/          构建与媒体脚本（Python + Bash）
docs/             文档（MEDIA-OSS / MEDIA-STANDARDS / env / superpowers）
.claude/          Claude Code 配置（rules / skills / settings）
.github/workflows/ CI / CD / Pages / media-verify
```

## 常用命令

```bash
# 开发
pnpm install
pnpm run site:dev              # Hugo dev server（热更新）
pnpm run site:build            # 生产构建
pnpm run site:build:github     # GitHub Pages 构建

# Lint
pnpm run lint                  # markdownlint-cli2（CI 必跑）
pnpm run lint:fix              # 自动修复

# 媒体
pnpm run media:save            # 保存本地媒体
pnpm run media:upload          # 上传到 COS
pnpm run media:cdn-check       # CDN URL 校验
pnpm run media:rewrite         # 本地路径 → CDN URL 改写

# 文章
pnpm run article:new           # 新建文章骨架

# Git hooks（首次克隆后）
pnpm install                   # 自动触发 husky prepare
# gitleaks 必须本机安装：brew install gitleaks / Linux 见 https://github.com/gitleaks/gitleaks
```

## 内容写作约定

- **Page Bundle 模式**：每个文章一个目录，附 `index.md`
- **媒体文件**：原图/原视频放同目录 `gallery/`（gitignore），上传 COS 后 Markdown 用 CDN URL
- **详见**：[docs/MEDIA-STANDARDS.md](docs/MEDIA-STANDARDS.md) 与 [docs/MEDIA-OSS.md](docs/MEDIA-OSS.md)
- **图片写法**：用 Blowfish shortcode（`{{< carousel >}}`、`{{< gallery >}}`、`{{< video >}}`）

## 开发约束

- **不引入新风格**：命名、缩进、错误处理、文档风格沿用项目既有约定
- **不直接编辑 `themes/blowfish/`**（submodule）：升级用 `git submodule update --remote --merge`
- **密钥不进仓库**：COS 凭证在 `~/.cos.yaml`；`.env` 不入 Git；CI/CD 用 GitHub Secrets
- **Conventional Commits**：`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `build` / `ci` / `chore` / `revert`，subject ≤ 100 字符
- **markdownlint 范围**：默认对所有 `*.md` 跑；`docs/superpowers/**`（归档计划）与 `docs/research/**`（调研素材）已忽略

## 文档入口

| 主题 | 文档 |
|------|------|
| 媒体上传与 COS | [docs/MEDIA-OSS.md](docs/MEDIA-OSS.md) |
| 媒体命名规范 | [docs/MEDIA-NAMESPACE.md](docs/MEDIA-NAMESPACE.md) |
| 作者写作规范 | [docs/MEDIA-STANDARDS.md](docs/MEDIA-STANDARDS.md) |
| CDN 配置 | [docs/CDN-SETUP.md](docs/CDN-SETUP.md) |
| 环境变量 | [docs/env/README.md](docs/env/README.md) |
| 主题问题 | [docs/BLOWFISH-TW-ELEMENTS-ISSUES.md](docs/BLOWFISH-TW-ELEMENTS-ISSUES.md) |
| 首页动效设计 | [docs/DESIGN-ANIMATED-BACKGROUND.md](docs/DESIGN-ANIMATED-BACKGROUND.md) |
| 移动端 Hermes | [docs/DRAFT-OPENCLAW-HERMES-MOBILE.md](docs/DRAFT-OPENCLAW-HERMES-MOBILE.md) |

## 部署

- **CI**：`.github/workflows/ci-ghcr.yml`（gitleaks + lint + Docker 构建推送）
- **CD**：`.github/workflows/cd-ghcr.yml`（config-sync → deploy 两阶段）
- **Pages**：`.github/workflows/pages.yml`（GitHub Pages 预览）
- **媒体校验**：`.github/workflows/media-verify.yml`（内容变更触发 CDN URL 健康检查）

详见 [README.md](README.md)。

## Skills / Rules

- 项目级 Skill：`/article-publish`、`/drinkzen`、`/media-publish`、`/origin-distribute` 等（见 `.claude/skills/`）
- 项目级 Rule：`.claude/rules/core.md`（通用）+ `.claude/rules/framework/nodejs.md`（Node.js）
- 外部 Skill 注册表：`skills-lock.json`
