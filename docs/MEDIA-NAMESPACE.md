# 共享 COS / CDN 命名空间规划

`xiaolin-life` 与 `xiaolin-dcos` 共用：

| 资源 | 值 |
|------|-----|
| Bucket | `media-1300240022`（南京） |
| CDN | `https://media.xiaolin.fun` |

通过 **对象键一级前缀** 隔离项目，避免冲突、便于用量统计与清理。

技术部署见 [MEDIA-OSS.md](MEDIA-OSS.md)；本仓库写作规范见 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)。

---

## 目标结构

```
media.xiaolin.fun/
├── life/                          # xiaolin-life（个人生活站）
│   ├── entertainment/gulou-riverfront/   # Page Bundle 图集
│   ├── img-email-thunderbird/            # 历史 static 插图
│   ├── img-mac/
│   └── ai-dialectic-moon-egg.png
│
└── docs/                          # xiaolin-dcos（技术文档站，策略 A：保留现有前缀）
    ├── gitops/
    ├── img-ai-coding/
    └── …
```

**URL 规则**（两项目统一）：

```
https://media.xiaolin.fun/{项目前缀}/{相对路径}/{文件名}
```

| 项目 | 对象键前缀 | 示例 URL |
|------|------------|----------|
| xiaolin-life | `life` | `…/life/img-mac/mac-sliver.jpg` |
| xiaolin-dcos | **`docs`**（策略 A，不改名） | `…/docs/img-ai-coding/foo.png` |

> **已选策略 A**：dcos 继续用 Bucket 内现有 `docs/` 前缀，不迁移为 `dcos/`。

---

## 现状盘点（2026-06）

### Bucket 根目录（待迁入 `life/`）

| 键 | 来源 | 目标 |
|----|------|------|
| `img-email-thunderbird/` … `img-upgrade/` 等 | xiaolin-life static | `life/img-*` |
| `ai-dialectic-moon-egg.png` | xiaolin-life | `life/ai-dialectic-moon-egg.png` |

### 已符合命名空间

| 键 | 项目 | 说明 |
|----|------|------|
| `life/entertainment/gulou-riverfront/*` | xiaolin-life | Page Bundle 上传，**无需改动** |

### xiaolin-dcos（策略 A）

Bucket 中已有 `docs/img-*`、`docs/gitops/` 等，**保持 `docs/` 前缀不变**，无需 COS 搬迁。

---

## 环境变量在哪里设置

脚本**不会自动读取** `.env` 文件，需在运行前 `export`，或在命令前一行内联。凭证与项目前缀分开配置。

| 变量 | 作用 | xiaolin-life | xiaolin-dcos |
|------|------|--------------|--------------|
| `COS_PREFIX` | 上传到 Bucket 的对象键前缀 | `life` | `docs` |
| `MEDIA_CDN_BASE` | Markdown / 校验用的 CDN 根 URL | `https://media.xiaolin.fun` | 同左 |
| `COS_BUCKET_ALIAS` | coscli 桶别名（可选） | `media-1300240022` | 同左 |

coscli **密钥**不在上述变量里，写在 **`~/.cos.yaml`**（`coscli config init`），两项目共用同一文件即可。

### 1. 本地开发（推荐）

各仓库根目录复制模板并编辑（**勿提交** `.env`）：

**xiaolin-life** — 复制 `.env.example` → `.env`：

```bash
MEDIA_CDN_BASE=https://media.xiaolin.fun
COS_PREFIX=life
```

**xiaolin-dcos** — 同结构，改前缀：

```bash
MEDIA_CDN_BASE=https://media.xiaolin.fun
COS_PREFIX=docs
```

使用前加载（可写入 `~/.zshrc` 别名，或每次手动）：

```bash
set -a && source .env && set +a
pnpm run media:upload
```

或单行内联（不依赖 `.env`）：

```bash
COS_PREFIX=life ./scripts/upload-media-cos.sh static/assets/images
COS_PREFIX=docs ./scripts/upload-media-cos.sh static/assets/images   # dcos 仓库
```

### 2. GitHub Actions（CI 校验）

仓库 **Settings → Secrets and variables → Actions → Variables**：

| 变量 | xiaolin-life | xiaolin-dcos |
|------|--------------|--------------|
| `MEDIA_CDN_BASE` | `https://media.xiaolin.fun` | 同左 |

CI 只做 URL 可达性校验，**不上传 COS**；`COS_PREFIX` 一般不必配在 GitHub。

### 3. coscli 凭证（两项目共用）

```bash
~/.cos.yaml          # coscli config init 生成
```

### 4. Hugo 站点配置（非 shell 环境变量）

`config/_default/media.toml` 中的 `cdnBaseURL` 与 `MEDIA_CDN_BASE` 保持一致，供主题 / 模板引用；**对象键前缀**仍由上传脚本 `COS_PREFIX` 控制。

---

## 上传规则（迁移后）

### 环境变量（各项目 `.env` 或 export）

```bash
MEDIA_CDN_BASE=https://media.xiaolin.fun
COS_PREFIX=life          # xiaolin-life
# COS_PREFIX=docs        # xiaolin-dcos
```

> 迁移脚本落地后可能增加别名 `COS_PROJECT`，与 `COS_PREFIX` 同义；当前上传脚本已支持 **`COS_PREFIX`**。

### xiaolin-life Markdown URL 现状

| 类型 | 当前 URL 路径 | 目标 |
|------|---------------|------|
| 鼓楼滨江 carousel | `/life/entertainment/gulou-riverfront/` | ✅ 已正确 |
| static 插图 7 篇 | `/img-email-thunderbird/` 等（缺 `life/`） | `/life/img-*` |
| 根级单图 | `/ai-dialectic-moon-egg.png` | `/life/ai-dialectic-moon-egg.png` |

### 对象键推导

| 本地路径 | COS 键 |
|----------|--------|
| `content/life/entertainment/foo/gallery/01.jpg` | `life/entertainment/foo/01.jpg` |
| `content/office/email/gallery/…` | `life/office/email/01.jpg` |
| `static/assets/images/img-mac/…` | `life/img-mac/…`（需 `COS_PREFIX=life`） |
| dcos `static/assets/images/img-ai-coding/…` | `docs/img-ai-coding/…`（需 `COS_PREFIX=docs`） |

**Page Bundle**：键为 `content/` 之后、`gallery/` 之前的路径；life 站路径通常已以 `life/` 开头，与 `COS_PREFIX` 叠加时需注意避免 `life/life/…`（迁移脚本会处理）。

**static**：上传到 `{COS_PREFIX}/img-*`，不再落 Bucket 根目录。

---

## 迁移路线图

### 阶段 0：约定（两仓库）

- [x] 确认 dcos 前缀：策略 A，保留 **`docs`**
- [ ] 本文档同步到 xiaolin-dcos（或链到 life 仓库此文件）

### 阶段 1：xiaolin-life — COS 对象搬迁

在**不删旧对象**前提下复制（便于回滚）：

```bash
# 示例：根目录 static 目录迁入 life/
coscli sync cos://media-1300240022/img-email-thunderbird/ \
  cos://media-1300240022/life/img-email-thunderbird/ -r

# 对其余 img-*、ai-dialectic-moon-egg.png 同理
# 或用 scripts/migrate-cos-prefix.sh life（阶段 1 实施时提供）
```

搬迁清单：

- [ ] `img-blogger/` → `life/img-blogger/`
- [ ] `img-email-thunderbird/` → `life/img-email-thunderbird/`
- [ ] `img-mac/` → `life/img-mac/`
- [ ] `img-markdown/` → `life/img-markdown/`
- [ ] `img-table-game-guandan/` → `life/img-table-game-guandan/`
- [ ] `img-undercover/` → `life/img-undercover/`
- [ ] `img-upgrade/` → `life/img-upgrade/`
- [ ] `ai-dialectic-moon-egg.png` → `life/ai-dialectic-moon-egg.png`
- [ ] `life/entertainment/…` — **跳过**

验证：`pnpm run media:cdn-check` 增加 `life/` 路径抽样。

### 阶段 2：xiaolin-life — Markdown URL

批量将 CDN URL 中「Bucket 根路径」改为 `life/` 前缀（鼓楼滨江已含 `life/` 的跳过）：

```bash
# 预览 / 写入（实施时提供脚本）
pnpm run media:prefix-migrate
pnpm run media:prefix-migrate:apply
```

规则：

```
https://media.xiaolin.fun/img-*     → https://media.xiaolin.fun/life/img-*
https://media.xiaolin.fun/ai-*      → https://media.xiaolin.fun/life/ai-*
# 已是 …/life/entertainment/… 的不改
```

- [ ] 8 篇文章 featureimage + 正文 + carousel-cdn
- [ ] `pnpm run build` + `media-verify` CI 通过
- [ ] 浏览器抽查 + 百度统计 / CDN 控制台无 404 激增

### 阶段 3：xiaolin-life — 脚本与配置

- [ ] `COS_PROJECT=life` 写入 `.env.example`、`upload-media-cos.sh` 默认逻辑
- [ ] `static` 上传目标改为 `life/img-*`
- [ ] Page Bundle 上传保持 `life/<content路径去 content/ 和 gallery/>`
- [ ] 更新 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md) COS 键示例

### 阶段 4：xiaolin-dcos — 无需搬迁（策略 A）

- [x] 继续使用 `docs/` 前缀与现有 URL
- [ ] dcos 仓库 `.env` 设置 `COS_PREFIX=docs`
- [ ] 新上传勿写入 Bucket 根目录或 `life/`

### 阶段 5：清理与监控

- [ ] CDN 控制台：对旧 URL 路径做 **404 监控**（可选告警）
- [ ] 删除 Bucket 根目录遗留 `img-*`（**确认无引用后**）
- [ ] 两项目文档注明：新资源**禁止**上传到无前缀的 Bucket 根目录

---

## 脚本改造要点（xiaolin-life）

| 文件 | 改动 |
|------|------|
| `scripts/upload-media-cos.sh` | 读 `COS_PREFIX`；static → `{prefix}/`；gallery 去重前缀 |
| `scripts/lib/cos-config.sh` | 可选：本仓库默认 `COS_PREFIX=life` |
| `scripts/cdn-check.sh` | 抽样 URL 改用 `life/` 路径 |
| `scripts/rewrite-media-prefix.py` | 新增：根路径 URL → `life/` 前缀 |
| `.env.example` | `COS_PREFIX=life` |
| `config/_default/media.toml` | 可选 `projectPrefix = "life"` 供模板引用 |

xiaolin-dcos 复制同一套脚本，`.env` 中设 **`COS_PREFIX=docs`**。

---

## xiaolin-dcos 接入清单

1. 仓库根目录 `.env`：`COS_PREFIX=docs`，`MEDIA_CDN_BASE=https://media.xiaolin.fun`
2. 复制 `scripts/upload-media-cos.sh`、`cos-config.sh`、`cdn-check.sh`
3. Markdown 媒体 URL 保持 `https://media.xiaolin.fun/docs/…`
4. GitHub Variable：`MEDIA_CDN_BASE`（与 life 相同）

---

## 风险与回滚

| 风险 | 缓解 |
|------|------|
| 旧 URL 404（书签、搜索引擎） | 阶段 1 保留旧对象；CDN 可配置 **回源路径重写** 或短期双写 |
| `life/life/` 双前缀 | gallery 上传逻辑检测首段是否已等于 `COS_PROJECT` |
| 两项目误传同一键 | 代码 review + `COS_PROJECT` 必填 |
| dcos 误传到 `life/` 或根目录 | dcos 仓库固定 `COS_PREFIX=docs` |

回滚：Markdown 改回旧 URL；COS 旧对象未删则零停机。

---

## 检查清单（life 迁移完成标准）

- [ ] 所有 life 媒体 URL 以 `https://media.xiaolin.fun/life/` 开头
- [ ] Bucket 根目录无 `img-*`（仅 `life/`、`docs/`、`.gitkeep` 等）
- [ ] xiaolin-dcos 新上传仅写 `docs/`

---

## 下一步

**xiaolin-life 阶段 1–3 已完成。** 可选：确认无 404 后删除 Bucket 根目录遗留 `img-*` 与 `ai-dialectic-moon-egg.png`。
