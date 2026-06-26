# 媒体资源：腾讯云 COS + CDN 方案

个人生活站以图片/视频为主，**源文件保持原画质**，通过对象存储 + CDN 加速分发；Git 与 Docker 镜像只保留页面与轻量资源。

**作者写作与目录规范** → [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)

## 架构

```
┌─────────────┐     构建      ┌──────────────┐
│ Git 仓库     │ ──────────► │ Docker 镜像   │  HTML/CSS/JS（无大图）
│ Markdown    │             │ ~10–20MB     │
│ 小 SVG 图标  │             └──────┬───────┘
└─────────────┘                    │
                                   ▼
                            xiaolin.fun（服务器）

┌─────────────┐     CDN 加速   ┌──────────────┐
│ 腾讯云 COS   │ ──────────► │ media.xiaolin.fun │
│ 原图/视频    │             │ 读者浏览器        │
└─────────────┘             └──────────────┘
```

| 存放位置 | 内容 | 进 Git | 进镜像 |
|----------|------|--------|--------|
| Git | Markdown、Hugo 配置、小 SVG / 占位图 | ✅ | — |
| COS | 游记图集、截图、视频 | ❌ | ❌ |
| 镜像 | 构建后的 HTML/CSS/JS | — | ✅ |

## 下一步清单（按顺序执行）

**当前进度**：COS 与 coscli 已就绪；媒体目录规范见 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)。**下一步：整理命名与去重 → 全量上传 COS → Markdown 改 URL → 从 Git 移出 gallery**；CDN 待购服务后再配置。

### 1. 创建 COS 存储桶 ✅

Bucket **`media-1300240022`**，地域 **南京（ap-nanjing）**，公有读私有写。

<details>
<summary>首次创建参考步骤</summary>

1. [COS 控制台](https://console.cloud.tencent.com/cos) → **创建存储桶**
2. **地域**：`南京（ap-nanjing）` 或 `上海（ap-shanghai）`
3. **名称**：全局唯一，例 `xiaolin-life-media-<appid>`
4. **访问权限**：个人站推荐 **公有读私有写**
5. 记录 **Bucket 名称** 与 **地域简称**

</details>

### 2. 配置 coscli ✅

`~/.cos.yaml` 已配置；脚本通过 `scripts/lib/cos-config.sh` 自动读取 alias，无需手动 export。

```bash
pnpm run media:check   # 应显示 media-1300240022 可访问
```

<details>
<summary>首次配置参考命令</summary>

```bash
coscli config init
# 或
coscli config add -b media-1300240022 -r ap-nanjing -a media-1300240022
```

</details>

### 3. 绑定 CDN 加速域名 ⬜（待购服务后配置）

1. [CDN 控制台](https://console.cloud.tencent.com/cdn) → **域名管理** → **添加域名**
2. **加速域名**：`media.xiaolin.fun`
3. **加速区域**：中国境内（与已购资源包一致）
4. **源站类型**：COS 源 → 选择上一步 Bucket
5. **回源 HOST**：默认 Bucket 域名即可
6. **HTTPS**：申请免费证书或上传已有证书（与主站一致体验更好）
7. 控制台给出 **CNAME**（如 `media.xiaolin.fun.cdn.dnsv1.com`）
8. 在 DNS（`xiaolin.fun`）添加：`media` → CNAME 指向上述地址

**路径约定（与 Markdown 一致）**

- 本地：`static/assets/images/img-gulou-riverfront/foo.jpg`
- COS 对象键：`img-gulou-riverfront/foo.jpg`（相对 `images/` 目录，**无** `/assets/images` 前缀）
- CDN URL：`https://media.xiaolin.fun/img-gulou-riverfront/foo.jpg`

CDN 源站路径留空即可；对象直接放在 Bucket 根目录对应键下。

### 4. 试点上传 🟡 部分完成

COS 直链已验证（CDN 未配前可用 `https://media-1300240022.cos.ap-nanjing.myqcloud.com/...`）：

| 已上传 | 说明 |
|--------|------|
| `img-table-game-guandan/` | 4 文件，~10.5MB |
| `tmp/cos-verify.txt` | 连通性测试 |

待上传（CDN 就绪后建议全量 sync）：

```bash
./scripts/upload-media-cos.sh static/assets/images
# 鼓楼滨江与 static 重复，二选一即可，不必重复传 gallery
```

<details>
<summary>单目录试点命令</summary>

```bash
./scripts/upload-media-cos.sh static/assets/images/img-gulou-riverfront
# 验证直链（CDN 前）：
# https://media-1300240022.cos.ap-nanjing.myqcloud.com/img-gulou-riverfront/<文件名>
```

</details>

### 5. 改 1 篇文章验证 ⬜

CDN 绑定并解析生效后再做；未配 CDN 前可临时用 COS 直链本地预览。

**改造前（同源，进镜像）：**

```markdown
![说明](/assets/images/img-gulou-riverfront/nanjing-marathon.jpg)
```

**改造后（CDN，不进镜像）：**

```markdown
![说明](https://media.xiaolin.fun/img-gulou-riverfront/nanjing-marathon.jpg)
```

本地 `pnpm build` + 预览，确认图片加载正常。

### 6. 批量迁移与瘦身 ⬜

1. 全量上传 `static/assets/images`（~218MB，64 文件）
2. `pnpm run media:rewrite:apply`（7 篇文章、34 处引用，已预览）
3. 设置 GitHub **Variables**：`MEDIA_CDN_BASE=https://media.xiaolin.fun`
4. ~~`config/_default/media.toml` 填写 `cdnBaseURL`~~ ✅ 已填
5. `.gitignore` 已迁 COS 的目录，从 Git 移除大文件（历史 blob 可选 `git filter-repo`）
6. Docker 镜像不再含大图，`docker pull` 恢复 ~10–20MB 量级

### 7. （可选）CI 自动同步

媒体变更频率低，**推荐本地手动 sync**；若需 CI：

- GitHub **Secrets**：`COS_SECRET_ID`、`COS_SECRET_KEY`
- Workflow 中安装 coscli 并 `coscli sync`（与本地相同命令）
- 仅在有 `static/assets/images/**` 变更时触发，避免每次 build 全量上传

---

## 环境变量

```bash
# coscli 凭证在 ~/.cos.yaml；脚本自动读取 Bucket alias / endpoint
export MEDIA_CDN_BASE=https://media.xiaolin.fun

# 可选：覆盖自动读取的配置
# export COS_BUCKET_ALIAS=media-1300240022
# export COS_CONFIG_PATH=~/.cos.yaml

# CI 无 ~/.cos.yaml 时使用
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_BUCKET=media-1300240022
export COS_REGION=ap-nanjing
```

| 变量 | 用途 |
|------|------|
| `~/.cos.yaml` | 本地默认配置源（`scripts/lib/cos-config.sh` 解析） |
| `COS_BUCKET_ALIAS` | 可选覆盖；未设时从配置文件读取 |
| `MEDIA_CDN_BASE` | Markdown/CDN 根 URL |
| `COS_SECRET_ID` / `COS_SECRET_KEY` | 仅 CI 或 `coscli config init` 用 |

配置占位：`config/_default/media.toml`

---

## 辅助脚本

| 命令 | 说明 |
|------|------|
| `pnpm run media:inventory` | 统计待上传体量与 Markdown 引用 |
| `pnpm run media:check` | 验证 coscli 配置与 Bucket 连通 |
| `pnpm run media:upload` | 同步 `static/assets/images` 到 COS |
| `pnpm run media:rewrite` | 预览 Markdown CDN URL 替换 |
| `pnpm run media:rewrite:apply` | 写入 CDN URL（**上传并验证 CDN 后再执行**） |

本地凭证模板：复制 `.env.example` 为 `.env`（已 gitignore）。

---

## 上传脚本

```bash
# 同步 static 下全部历史图片
./scripts/upload-media-cos.sh static/assets/images

# 同步 Page Bundle 图集（键前缀为 gallery/<文章名>/）
./scripts/upload-media-cos.sh content/life/entertainment/gulou-riverfront/gallery
```

`coscli sync` 默认增量上传，支持断点续传；大目录可加 `--rate-limiting 10` 限速。

---

## Blowfish 图集说明

**轮播** `gallery/*` shortcode 仅读本地目录。迁 COS 后可选：

- 改用 Markdown 图集 + CDN 绝对 URL；或
- 后续增加 `carousel-cdn` shortcode（待实现）

视频同理：上传 COS 后，用 Blowfish `video` shortcode 引用 CDN URL。

---

## 构建与部署（启用 CDN 后）

1. 设置 `MEDIA_CDN_BASE` 后，可用 `scripts/prepare-deploy-bundle.sh` 在打包前剔除本地媒体（容器化场景下更理想的是 Markdown 已用 CDN URL，Hugo 构建产物天然不含大图）。
2. Docker 镜像只含 HTML/CSS/JS，部署时 `docker compose pull && up -d` 快速完成。

---

## 迁移进度

| 步骤 | 状态 | 备注 |
|------|------|------|
| 停止构建时 lossy 压缩 | ✅ | |
| 恢复原图 | ✅ | static ~218MB |
| 购买 COS + CDN、安装 coscli | ✅ | coscli v1.0.8 |
| coscli config + 创建 Bucket | ✅ | `media-1300240022` / ap-nanjing |
| 迁移脚本与工具链 | ✅ | upload / rewrite / check / cos-config |
| `media.toml` `cdnBaseURL` | ✅ | `https://media.xiaolin.fun` |
| CDN 绑定 + DNS CNAME | ⬜ | 待购 CDN 服务 |
| 媒体目录规范 | ✅ | [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md) |
| gallery / static 大图 gitignore | ✅ | 已写入；已跟踪文件待迁移后 `git rm --cached` |
| COS 试点上传 | 🟡 | 已传 `img-table-game-guandan`；COS 直链 200 OK |
| 全量上传 static | ⬜ | 64 文件 / ~218MB |
| 单篇 Markdown + CDN 验证 | ⬜ | 依赖 CDN |
| 批量替换 Markdown | ⬜ | 7 篇 34 处，脚本已就绪 |
| GitHub `MEDIA_CDN_BASE` | ⬜ | |
| 从 Git 移除大图 | ⬜ | 含鼓楼滨江 gallery 去重（22 个同名） |

**COS 直链前缀**（CDN 未配前）：`https://media-1300240022.cos.ap-nanjing.myqcloud.com`

---

## 画质与图片处理

- **源文件**：COS 存原图/原视频，不做有损压缩
- **传输**：靠 CDN 边缘节点，不靠压低质量
- **按需缩放**（可选）：腾讯云数据万象 CI，URL 参数示例  
  `?imageMogr2/thumbnail/1920x`  
  源文件仍为原图，仅响应时缩放

---

## 配额参考

已购资源包示例：**COS 50GB/12 月** + **CDN 500GB/12 月（境内）**。当前仓库媒体约 **~220MB**（static）+ 图集重复部分，远低于 COS 容量；流量取决于访问量，个人站通常足够。控制台可开 **用量告警**。
