# 小林的生活

`xiaolin-life` 是一个基于 Jekyll 构建的个人生活静态站点，用来记录南京生活、轻松办公、城市探索与日常思考。

## 内容板块

### 南京生活

- 风景名胜：朝天宫、南京博物馆、中山陵等城市地标探索。
- 南京高校：南京大学、南京师范大学等高校巡礼。
- 桌游聚会：阿瓦隆、掼蛋、谁是卧底、升级等桌游体验。
- 生活思考：人人都是博主、内容仓库等生活感悟。

### 轻松办公

- Thunderbird 邮件管理：多邮箱统一管理与收件箱整理。
- Markdown 写作：易读易写的文档写作工具。
- Linux 学习：系统学习路线与经验记录。
- Mac 办公体验：Mac 系统下的高效办公配置。

## 技术栈

- 静态站点引擎：Jekyll。
- Markdown 渲染：Kramdown。
- 代码高亮：Rouge。
- SEO、订阅与 LLM 访问：`jekyll-seo-tag`、`jekyll-sitemap`、`jekyll-feed`、`jekyll-aeo`。
- 服务端：Nginx。
- 部署：GitHub Actions、GitHub Container Registry、Docker Compose。

## 本地开发

先安装 Ruby 3.0+ 和 Bundler，然后执行：

```bash
bundle install
bundle exec jekyll serve --livereload
```

也可以使用 npm 脚本转发：

```bash
npm run site:dev
```

## 目录结构

- `index.md`、`about.md`：站点入口页面。
- `life/`：南京生活、城市探索、桌游、思考等内容。
- `office/`：轻松办公、工具使用、系统学习等内容。
- `_layouts/`、`_includes/`、`_data/`：Jekyll 模板、公共片段和导航数据。
- `assets/`：站点样式、脚本和图片资源。
- `compose.yaml`：独立网站容器部署。
- `k8s/`、`volumes/`、`docker-compose.yaml`、`nginx.conf`：完整自托管部署与运维配置。

日常运营只需要维护 Markdown 页面和 `assets/images/` 中的图片；新增页面时，在对应目录创建 `.md` 文件并补充 YAML Front Matter。

## 构建

```bash
npm run site:build
```

## 部署

### GitHub Actions

项目使用两条流水线完成容器化部署：

- `.github/workflows/ci-ghcr.yml`：构建 Docker 镜像并推送到 GitHub Container Registry。
- `.github/workflows/cd-ghcr.yml`：登录目标服务器，拉取最新代码，并通过 `docker compose up -d` 部署。

需要配置以下 GitHub Actions Secrets：

- `SERVER_HOST`：服务器地址。
- `SERVER_USER`：SSH 登录用户。
- `SERVER_PASSWORD`：SSH 登录密码。

`GITHUB_TOKEN` 由 GitHub Actions 自动注入，用于推送镜像到 GitHub Container Registry，无需手动配置。

### Docker Compose

在服务器上使用 `compose.yaml` 只运行网站容器：

```bash
docker compose up -d
```

独立网站容器会将站点服务暴露到宿主机 `8081` 端口，供 `xiaolin-gateway` 反向代理访问；`xiaolin.fun`、`www.xiaolin.fun` 的 HTTPS 证书与公网入口统一在 `xiaolin-gateway` 中维护，本项目不提交证书文件。

CD 默认服务器目录为：

```text
~/AgentProjects/xiaolin-life
```

如需完整自托管环境，也可以使用 `docker-compose.yaml` 运行 Nginx 网关、静态站点容器与监控组件。静态站点容器默认读取：

```text
./volumes/jekyll/site
```

## 迁移说明

- Jekyll 正式内容位于根目录、`life/`、`office/`、`_layouts/`、`_includes/`、`_data/` 和 `assets/`。
- 旧 VitePress 内容已移除，仓库只保留 Jekyll 站点与部署配置。
- 新页面图片统一放在 `assets/images/`，Markdown 中使用 `relative_url` 以兼容不同部署路径。
- `package.json` 只保留 Jekyll 相关脚本，不再承担 VitePress 构建。

## LLM 访问

站点使用 `jekyll-aeo` 在构建阶段自动生成面向 agent 的访问文件，无需手动维护：

- `llms.txt`：站点内容索引。
- `llms-full.txt`：站点完整内容聚合。
- 页面 Markdown 副本：方便 agent 读取干净的源内容。

## 可选扩展

- 搜索：接入 Pagefind，适合文章数量增加后做本地静态搜索。
- 评论：接入 Giscus，使用 GitHub Discussions 承载评论。
- 图片优化：增加构建前图片压缩脚本，降低首屏加载体积。
- 文章集合：把生活文章迁移为 Jekyll `_posts` 或自定义 collection，便于归档、标签和 RSS。
- 站点统计：接入 Umami 或 Plausible，比传统统计更轻量。
- Markdown 增强：按需接入 Mermaid 或 MathJax，仅在确实有图表、公式内容时启用。
