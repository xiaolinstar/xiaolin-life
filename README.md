<div align="center">

# 小林的生活

[![Stars](https://img.shields.io/github/stars/xiaolinstar/xiaolin-life?style=for-the-badge&logo=github)](https://github.com/xiaolinstar/xiaolin-life/stargazers)
[![Forks](https://img.shields.io/github/forks/xiaolinstar/xiaolin-life?style=for-the-badge&logo=github)](https://github.com/xiaolinstar/xiaolin-life/network/members)
[![Issues](https://img.shields.io/github/issues/xiaolinstar/xiaolin-life?style=for-the-badge&logo=github)](https://github.com/xiaolinstar/xiaolin-life/issues)
[![Last Commit](https://img.shields.io/github/last-commit/xiaolinstar/xiaolin-life?style=for-the-badge&logo=git)](https://github.com/xiaolinstar/xiaolin-life/commits/main)

[![Website](https://img.shields.io/badge/网站-xiaolin.fun-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white)](https://xiaolin.fun/)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-预览-181717?style=for-the-badge&logo=github)](https://xiaolinstar.github.io/xiaolin-life/)

[![CI](https://img.shields.io/github/actions/workflow/status/xiaolinstar/xiaolin-life/ci-ghcr.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/xiaolinstar/xiaolin-life/actions/workflows/ci-ghcr.yml)
[![Pages Deploy](https://img.shields.io/github/actions/workflow/status/xiaolinstar/xiaolin-life/pages.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=Pages)](https://github.com/xiaolinstar/xiaolin-life/actions/workflows/pages.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/xiaolinstar/xiaolin-life/cd-ghcr.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CD)](https://github.com/xiaolinstar/xiaolin-life/actions/workflows/cd-ghcr.yml)

[![Hugo](https://img.shields.io/badge/Hugo-0.158%2B%20extended-FF4088?style=for-the-badge&logo=hugo&logoColor=white)](https://gohugo.io/)
[![Blowfish](https://img.shields.io/badge/Theme-Blowfish-0891B2?style=for-the-badge)](https://blowfish.page/zh-cn/)
[![pnpm](https://img.shields.io/badge/pnpm-9.15+-F69220?style=for-the-badge&logo=pnpm&logoColor=white)](https://pnpm.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**南京生活 · 轻松办公 · 城市探索 · 日常思考**

[🌐 访问站点](https://xiaolin.fun/) · [📖 本地开发](#本地开发) · [🚀 部署说明](#部署) · [💬 提交 Issue](https://github.com/xiaolinstar/xiaolin-life/issues)

</div>

---

`xiaolin-life` 是基于 **Hugo + Blowfish** 构建的个人生活静态站点，记录南京生活、轻松办公、城市探索与日常思考。

## 内容板块

### 南京生活

- 风景名胜：朝天宫、南京博物馆、中山陵等城市地标探索
- 南京高校：南京大学、南京师范大学等高校巡礼
- 桌游聚会：阿瓦隆、掼蛋、谁是卧底、升级等桌游体验
- 生活思考：人人都是博主、内容仓库等生活感悟

### 轻松办公

- Thunderbird 邮件管理：多邮箱统一管理与收件箱整理
- Markdown 写作：易读易写的文档写作工具
- Linux 学习：系统学习路线与经验记录
- Mac 办公体验：Mac 系统下的高效办公配置

## 技术栈

[![Hugo](https://img.shields.io/badge/Hugo-0.158%2B%20extended-FF4088?style=flat-square&logo=hugo&logoColor=white)](https://gohugo.io/)
[![Blowfish](https://img.shields.io/badge/Blowfish-v2.103+-0891B2?style=flat-square)](https://blowfish.page/zh-cn/)
[![Pagefind](https://img.shields.io/badge/Pagefind-搜索索引-6366F1?style=flat-square)](https://pagefind.app/)
[![Nginx](https://img.shields.io/badge/Nginx-Alpine-009639?style=flat-square&logo=nginx&logoColor=white)](https://nginx.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/xiaolinstar/xiaolin-life/actions)

| 类别 | 说明 |
| --- | --- |
| 静态站点 | Hugo 0.158+（extended） |
| 主题 | [Blowfish](https://blowfish.page/zh-cn/)（git submodule） |
| 搜索 | Fuse.js（主题内置）+ Pagefind（构建后索引） |
| LLM | 构建时自动生成 `llms.txt` / `llms-full.txt` |
| 部署 | GitHub Actions · rsync · Docker Compose（nginx） |

## 本地开发

需要 Hugo **0.158+ extended** 和 Node.js 20+、pnpm 9+。

```bash
# 克隆（含 Blowfish 主题 submodule）
git clone --recurse-submodules https://github.com/xiaolinstar/xiaolin-life.git
cd xiaolin-life

# 已有仓库时初始化 submodule
git submodule update --init --recursive

# 安装依赖
pnpm install

# 启动开发服务器（热更新）
pnpm run site:dev
```

若未全局安装 Hugo，项目已提供 `.tools/hugo158` 作为本地 fallback（`scripts/hugo.sh` 会自动选择）。

## 目录结构

```
config/           Hugo 配置（站点、主题、菜单、中文语言）
content/          全部 Markdown 内容
  life/           生活记录
  office/         轻松办公
  about/          关于页面
static/assets/    站点级小资源（SVG 等；大图见 content/.../gallery/）
themes/blowfish/  Blowfish 主题
layouts/          自定义布局（ICP 备案、llms.txt）
assets/img/       Hugo 管道资源（占位图、SVG 封面）
scripts/          构建与迁移脚本
docs/             MEDIA-OSS.md（COS 部署）、MEDIA-STANDARDS.md（作者规范）
```

日常运营：在 `content/` 新建 Page Bundle，**原图 / 原视频放同目录 `gallery/`**，上传 COS 后 Markdown 用 COS/CDN URL；`gallery/` 不进 Git。详见 [docs/MEDIA-STANDARDS.md](docs/MEDIA-STANDARDS.md) 与 [docs/MEDIA-OSS.md](docs/MEDIA-OSS.md)。

### 媒体写法示例（Blowfish shortcodes）

```markdown
<!-- 图片轮播 -->
{{</* carousel images="gallery/*" interval="3000" */>}}

<!-- 图集 -->
{{</* gallery */>}}
  {{</* figure src="gallery/01.jpg" caption="说明" figureClass="grid-w33" */>}}
{{</* /gallery */>}}

<!-- 本地视频 -->
{{</* video src="gallery/walk.mp4" poster="gallery/cover.jpg" caption="沿江散步" */>}}
```

## 构建

```bash
pnpm run build
```

产物输出到 `public/`，包含 Pagefind 搜索索引。

## 部署

### GitHub Actions

- `.github/workflows/ci-ghcr.yml`：Docker 多阶段构建（Hugo → nginx 镜像）并推送到 GHCR
- `.github/workflows/cd-ghcr.yml`：两阶段 CD（config-sync → deploy）
- `.github/workflows/pages.yml`：部署到 GitHub Pages

CD 流程（容器化，无 scp）：

1. **config-sync**：SSH `git pull`，同步 `compose.yaml`、nginx 配置等
2. **deploy**：`docker compose pull && up -d`，从 `ghcr.nju.edu.cn` 拉取镜像并重启

CI 仍推送到官方 `ghcr.io`；服务器通过 [南大 GHCR 镜像](https://ghcr.nju.edu.cn) 加速拉取（见 `compose.yaml`）。

静态站点由 **Dockerfile** 在 CI 中构建并打入镜像，服务器不挂载 `site/` 目录。

GitHub Actions Secrets（自托管 CD）：

- `SERVER_HOST`、`SERVER_USER`、`SERVER_PASSWORD`

### Docker Compose

服务器使用 **GHCR 镜像（南大加速源）+ nginx 配置挂载**：

```yaml
# compose.yaml
image: ghcr.nju.edu.cn/xiaolinstar/xiaolin-life:main
```

```bash
docker compose pull && docker compose up -d
```

网站容器暴露宿主机 `8081` 端口，由 `xiaolin-gateway` 反向代理；HTTPS 证书在网关维护。

CD 默认服务器目录：`~/AgentProjects/xiaolin-life`

## 媒体资源（腾讯云 COS + CDN）

游记大图与视频放 COS + CDN 加速，Git/镜像只保留页面。详见 [docs/MEDIA-OSS.md](docs/MEDIA-OSS.md)。

## 主题升级

`themes/blowfish` 为 [Blowfish](https://github.com/nunocoracao/blowfish) 的 git submodule（跟踪 `main` 分支）。

```bash
git submodule update --remote --merge themes/blowfish
pnpm run build   # 验证构建
git add themes/blowfish && git commit -m "chore: bump blowfish theme"
```

## 从 Jekyll 迁移

已于 2026-06 完成迁移至 Hugo + Blowfish，URL 路径保持不变（如 `/life/places/nanjing-museum/`）。
