# 粗草稿：站点优化空间 × OpenClaw / Hermes 移动发布

> **状态**：粗草稿，供闲暇时间打磨。非实施计划，不绑定排期。  
> **范围**：当前 `xiaolin-life` 可优化点 + 未来通过 Hermes 和微信随时用手机写稿、传图的兼容思路；OpenClaw 与视频仅作远期备忘。  
> **相关已有文档**：[MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)、[MEDIA-OSS.md](MEDIA-OSS.md)、[DESIGN-ANIMATED-BACKGROUND.md](DESIGN-ANIMATED-BACKGROUND.md)

---

## 0. 一句话结论

本站是 **Hugo 静态站 + COS 媒体 + Docker/CI 部署**，内容与发布链路已经可用，但「人在电脑前跑脚本」仍是瓶颈。  
未来想用 **Hermes + 微信随时访问**，核心不是改主题，而是把现有 **media-publish / 文章脚手架** 包成 **Agent 可调用的工具（Skill / MCP）**，并补一条「微信图片 → Hermes@腾讯轻量 VPS → COS → Markdown URL」的路径。

---

## 1. 当前可优化空间（按优先级粗分）

### P0 — 内容与发布体验（直接影响「写得出东西」）

| 项 | 现状 | 可优化方向 |
| --- | --- | --- |
| 内容量 | 约二十篇，首页刻意不展示「最近文章」 | 选题清单 / 草稿看板；内容够了再恢复 `showRecent` |
| 错位草稿 | 仓库根 `life/entertainment/xiangzhiwei.md`（Jekyll 风格，不在 `content/`） | 迁入 Page Bundle 或删除 |
| 写作门槛 | 需本机 Hugo + coscli + 改 shortcode URL | Agent 一键：建文、传图、改写、提交（见第 3 节） |
| 图集改写 | carousel 本地 `gallery/*` → 上线要手改 `carousel-cdn` | 增强 `media-publish --rewrite` 覆盖 carousel / video |

### P1 — 体验与性能

| 项 | 现状 | 可优化方向 |
| --- | --- | --- |
| 首页 Vanta Birds | three.js ~600KB，仅首页加载 | 懒加载、更轻效果、或仅桌面开启 |
| CDN 图片 | 原图画质，未做响应式 | 腾讯云数据万象 `imageMogr2` 按屏宽出图 |
| OG / 分享图 | 统一 `defaultSocialImage` | 文章级 featured / social image |
| 移动端页脚 | 已移除 footer 菜单，顶栏 nav 保留 | 继续压低页脚高度、检查深色模式对比度 |

### P2 — 工程与运维

| 项 | 现状 | 可优化方向 |
| --- | --- | --- |
| CD SSH | `SERVER_PASSWORD` | 改 SSH key / Deploy key |
| CI 本地钩子 | 规则要求 husky/gitleaks，仓库未见 | 按需补最小门禁 |
| Dockerfile / README Hugo 版本 | 已对齐 0.164，文档表述仍「0.158+」 | 文档写死「构建版本 = Dockerfile ARG」 |
| Cursor 规则噪音 | 同步了 H5/小程序等无关规则 | 本仓只保留 Hugo 相关 |
| 监控栈 | Grafana/Loki 配置在仓内 | 文档化是否启用、与站点关系 |

### P3 — SEO / 生态

- 已有：sitemap、RSS、robots、schema、`llms.txt`。  
- 可补：逐篇 OG、结构化 FAQ、站内搜索 Pagefind 体验抽检。

---

## 2. OpenClaw / Hermes 是什么（对本站意味着什么）

| 产品 | 角色（粗理解） | 对本站的价值 |
| --- | --- | --- |
| [OpenClaw](https://github.com/openclaw/openclaw) | 自托管个人助手 Gateway；多通道（Telegram/微信等）+ iOS/Android Node（相机、推送） | 手机聊天下指令；Companion App 可直接拍照/选图交给 Agent |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | 另一套个人 Agent（记忆、工具、技能）；可跑本机或 Termux | 与 OpenClaw 类似：执行「写稿 / 传媒体」工具链；可双开 |
| [Clawket](https://github.com/p697/clawket) 等客户端 | 手机端统一管理 OpenClaw / Hermes | 「随时用手机访问」的 UI 入口之一 |

**兼容原则（建议写死）**：

1. **站点继续是静态站** — Agent 不直接改线上容器里的 HTML；只改 VPS 上的仓库副本 + 触发既有 CI/CD。  
2. **媒体继续走 COS** — 图片永不进 Git（与 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md) 一致）；视频暂不接收。  
3. **OpenClaw 与 Hermes 共用同一套「站点 Skill」** — 工具接口稳定（CLI / MCP），两边各自挂载即可，避免两套发布逻辑。  
4. **手机随时访问 ≠ 手机上跑 Hugo** — 手机只负责微信对话与传图；Hermes、COS 上传和 Git 操作在 VPS，构建在既有 CI。

---

## 3. 目标工作流（微信随时发图文）

```text
手机微信
  │  聊天：「发一篇鼓楼滨江，配这几张图」
  │  附件：相册图片 / 拍摄
  ▼
Hermes@腾讯轻量 VPS（常开）
  │  1. 收到媒体 → 落到 content/.../gallery/
  │  2. 按 MEDIA-STANDARDS 重命名
  │  3. 起草 / 补全 index.md
  │  4. media-publish.sh → COS + 校验 URL
  │  5. 改写 shortcode 为 CDN
  │  6. git commit + push（触发 CI/CD）
  ▼
线上 xiaolin.fun（读者只看到静态页 + CDN 媒体）
```

### 3.1 图片（必须支持）

| 步骤 | 做法草案 |
| --- | --- |
| 入站 | 微信图片 → Hermes 保存到 VPS 临时目录 → 复制进目标文章 `gallery/` |
| 命名 | 小写 ASCII + 连字符 + 序号（复用现有规范） |
| 上传 | 调用现有 `./scripts/media-publish.sh content/<path>` |
| 正文 | Agent 写 `carousel-cdn` / `figure`，URL 前缀 `https://media.xiaolin.fun/life/...` |
| 校验 | 现有 `media-verify.yml` 在 push 后 curl 200/206 |

#### 执行机器边界

- **手机 / 微信**：只负责发送指令与图片。
- **Hermes VPS**：接收图片、写入 `gallery/`、执行 `media-publish.sh`、调用 `coscli` 上传 COS、改写 Markdown、提交并推送。
- **GitHub Actions**：校验媒体 URL、构建镜像并触发现有 CD。
- **线上站点服务器**：只运行部署后的静态站，不承担媒体上传。

已有媒体文档中的「作者本机上传」应理解为「持有 `gallery/` 与 COS 凭证的受信任执行机」。接入 Hermes 后，这台执行机由作者 Mac 改为 Hermes VPS；CI 仍不负责上传 COS。

### 3.2 视频（延后，暂不排期）

当前决策：**暂时不做视频**。下文 V1～V3 仅备忘，实施阶段直接跳过；入站收到视频文件时拒绝并提示。

| 阶段 | 能力 | 说明 |
| --- | --- | --- |
| V1 | 短视频直传 COS + `{{< video src poster >}}` CDN URL | 以后再说 |
| V2 | 自动截帧生成 poster | 以后再说 |
| V3 | 可选转码 | 以后再说 |

### 3.3 手机端交互示例（自然语言）

- 「新建生活文章：奥体夜跑，草稿」  
- 「把刚才三张图挂到这篇的 gallery，上传 COS，正文用轮播」  
- 「把这段话润色成文章，提交并推送」  

---

## 4. 如何支持和兼容 OpenClaw / Hermes（实施分层）

### Layer A — 不改架构，先可调用（最快）

把现有脚本封成 **Skill**（两边都能读）：

| 工具名（草案） | 输入 | 动作 |
| --- | --- | --- |
| `life.draft_article` | section, slug, title | 创建 Page Bundle 脚手架 |
| `life.save_media` | slug, 文件路径列表 | 落入 `gallery/` + 规范化命名 |
| `life.publish_media` | slug, `--rewrite?` | 调 `media-publish.sh` |
| `life.commit_push` | message | Conventional Commit + push（需显式确认） |
| `life.status` | — | git status、最近部署、COS 抽检 |

OpenClaw：放到 workspace skills / tool 配置。  
Hermes：挂同一套 CLI 或 MCP。  
**关键：COS 上传由 VPS 上的 Hermes 执行**。`coscli` 与 `~/.cos.yaml` 只放 VPS，不进入 Git、不经微信回传；手机端不接触任何 COS 或 Git 凭证。

### Layer B — MCP 标准化（推荐中期）

做一个薄 MCP Server（VPS 内部监听，不直接暴露公网）：

- Tools = 上表  
- Resources = `content/**/*.md` 只读列表、媒体规范文档  
- 手机 App / Clawket 只连 Gateway，Gateway 调 MCP  

这样 OpenClaw、Hermes、Cursor 都能共用同一工具面。

### Layer C — 手机原生能力（体验拉满）

| 能力 | OpenClaw | Hermes |
| --- | --- | --- |
| 聊天下指令 | 通道（Telegram 等）或 Companion | 客户端 / Termux / 通道 |
| 相册选图 / 拍照 | Android/iOS Node 能力 | Termux API / 附件上传 |
| 推送部署结果 | Node 推送 | 通道消息 |
| 双开 | Gateway 路由到同一 MCP | 同左 |

### Layer D — 安全与边界（草稿必写）

- Agent 可以直接 push `main`，但必须在用户明确说「提交/推送」后执行。  
- 媒体入站只允许图片：`.jpg/.jpeg/.png/.webp/.gif`；视频直接拒绝。  
- 设置图片单文件大小上限和单日上传总量，避免误传占满 VPS 磁盘或 COS 流量。  
- 禁止 Agent 读取或回传 COS 密钥 / Server 密码。  
- 可选：仅 Tailscale / 家庭局域网可达 Gateway。

---

## 5. 与现有仓库的落点（将来改哪里）

| 区域 | 现状 | Agent 化时动刀点 |
| --- | --- | --- |
| `.claude/skills/media-publish/` | 已有作者机器发布 Skill | 扩展输入输出并部署到 Hermes VPS |
| `scripts/media-publish.sh` 等 | CLI 已结构化 | 保持稳定 CLI；Agent 只调脚本不重写逻辑 |
| `docs/MEDIA-*.md` | 人读规范 | 同时作为 Agent 的 Resource / 系统提示摘要 |
| `layouts/shortcodes/carousel-cdn.html` | CDN 轮播 | 作为当前图片展示的线上 shortcode |
| `content/` | Page Bundle | `life.draft_article` 脚手架模板 |
| CI `media-verify.yml` | URL 校验 | 保持；Agent push 后自动兜底 |

**本仓当前没有** OpenClaw / Hermes / MCP 集成代码 —— 从零加，不破坏现有 CD。

---

## 6. 建议的打磨顺序（闲暇 checklist）

- [x] 清掉 / 迁入根目录 `life/` 错位草稿（已迁入 `content/life/entertainment/xiangzhiwei/`，`draft: true`）  
- [x] 写一页「微信发一篇图文」人工剧本，验证现有脚本无缺口（**仅图片**）——本地 `media-publish.sh` 已验证：上传 COS + CDN `media.xiaolin.fun` 校验 200  
- [x] 增强 `media-publish --rewrite` 覆盖 carousel → `carousel-cdn`（按 gallery 实际文件展开 CDN URL；不做 video）  
- [x] 封装 Layer A Skill（`.claude/skills/article-publish/`：new-article / save-media / media-publish / commit-push 工具链，Cursor 可用，可原样搬 Hermes）  
- [ ] VPS 安装 Hermes + 仓 clone + coscli + **微信通道**  
- [ ] 约定图片白名单与单文件上限；微信试传 3 张图端到端（push `main`）  
- [ ] （可选）MCP Server；以后再考虑 OpenClaw / 视频  
- [ ] CD 改 SSH key；文档同步 Hugo 版本表述  

---

## 7. 决策记录

### 已拍板（2026-07-18）

| # | 问题 | 决定 |
| --- | --- | --- |
| 1 | Gateway 跑哪 | **腾讯轻量应用服务器（VPS）**，常开，保证手机随时可达 |
| 2 | 手机通道 | **微信**（Hermes 接微信；具体接入方式实施时再定） |
| 3 | 推送策略 | **允许 Agent 直接 push `main`**（仍建议对话里二次确认文案后再 push） |
| 4 | 视频 | **暂时不做**（只做图片：gallery → COS → CDN） |
| 5 | Agent 选型 | **先只用 Hermes**；OpenClaw 暂不双活 |

### 明确延后

- 视频上传 / poster / 转码 / `video` shortcode 自动化 —— **整条不进当前排期**（文中「视频 V1～V3」仅备忘）。  
- OpenClaw 双活 —— 延后。

### 决策带来的约束（实施时注意）

- **VPS 上要有**：Hermes、本仓 git 工作区、`coscli` + `~/.cos.yaml`、GitHub 推送权限、微信通道凭证（只放 VPS，不进仓）。  
- **媒体范围**：入站白名单先只管图片（`.jpg/.jpeg/.png/.webp/.gif`）；收到视频直接拒绝并提示「暂不支持」。  
- **大图不落 VPS 久留**：`gallery/` 上传 COS 后可清理临时文件，避免轻量盘打满。  
- **push main**：Skill 默认目标 `main`；仍保留「用户明确说提交/推送」才执行。  
- **与现网 CD**：Hermes push → 既有 `ci-ghcr` / `cd-ghcr`；部署机与 Hermes VPS 可以不是同一台。

---

## 8. 参考链接

- OpenClaw：<https://github.com/openclaw/openclaw> · <https://docs.openclaw.ai/>  
- Hermes Agent：<https://github.com/NousResearch/hermes-agent>  
- Clawket（移动客户端）：<https://github.com/p697/clawket>  
- 本站媒体规范：`docs/MEDIA-STANDARDS.md`、`docs/MEDIA-OSS.md`  
- 本站媒体 Skill：`.claude/skills/media-publish/SKILL.md`
