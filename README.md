# 小林的生活

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

- 静态站点引擎：Hugo 0.158+（extended）
- 主题：[Blowfish](https://blowfish.page/zh-cn/)
- 搜索：Fuse.js（主题内置）+ Pagefind（构建后索引）
- LLM 访问：构建时自动生成 `llms.txt` / `llms-full.txt`
- 服务端：Nginx
- 部署：GitHub Actions、GitHub Container Registry、Docker Compose

## 本地开发

需要 Hugo **0.158+ extended** 和 Node.js 20+。

```bash
# 安装 Node 依赖
npm install

# 启动开发服务器（热更新）
npm run site:dev
```

若未全局安装 Hugo，项目已提供 `.tools/hugo158` 作为本地 fallback（`scripts/hugo.sh` 会自动选择）。

## 目录结构

```
config/           Hugo 配置（站点、主题、菜单、中文语言）
content/          全部 Markdown 内容
  life/           生活记录
  office/         轻松办公
  about/          关于页面
static/assets/    图片等静态资源（保持 /assets/images/ URL 不变）
themes/blowfish/  Blowfish 主题
layouts/          自定义布局（ICP 备案、llms.txt）
assets/img/       Hugo 管道资源（头像等）
scripts/          构建与迁移脚本
```

日常运营：在 `content/` 对应目录新增 `index.md`（或 Page Bundle 目录），图片放入 `static/assets/images/` 或文章同目录 `gallery/`。

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
npm run build
```

产物输出到 `public/`，包含 Pagefind 搜索索引。

## 部署

### GitHub Actions

- `.github/workflows/ci-ghcr.yml`：构建 Docker 镜像并推送到 GHCR
- `.github/workflows/cd-ghcr.yml`：SSH 部署到自托管服务器
- `.github/workflows/pages.yml`：部署到 GitHub Pages

GitHub Actions Secrets（自托管 CD）：

- `SERVER_HOST`、`SERVER_USER`、`SERVER_PASSWORD`

### Docker Compose

```bash
docker compose up -d
```

网站容器暴露宿主机 `8081` 端口，由 `xiaolin-gateway` 反向代理；HTTPS 证书在网关维护。

CD 默认服务器目录：`~/AgentProjects/xiaolin-life`

## 主题升级

当前 `themes/blowfish` 为 vendored 副本。网络可用时建议改为 git submodule：

```bash
rm -rf themes/blowfish
git submodule add -b main https://github.com/nunocoracao/blowfish.git themes/blowfish
```

## 从 Jekyll 迁移

已完成全面迁移（2026-06）。旧 Jekyll 源文件已移除，历史迁移脚本保留在 `scripts/migrate_jekyll_to_hugo.py`。

URL 路径保持不变（如 `/life/places/nanjing-museum/`）。
