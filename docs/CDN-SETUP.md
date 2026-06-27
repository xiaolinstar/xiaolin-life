# 腾讯云 CDN 配置指南（media.xiaolin.fun）

将已有 COS 桶 `media-1300240022`（南京）接入 CDN，加速域名 **`media.xiaolin.fun`**。对象键与路径不变，仅替换 URL 前缀。

| 阶段 | COS 直链（当前） | CDN（目标） |
|------|------------------|-------------|
| 前缀 | `https://media-1300240022.cos.ap-nanjing.myqcloud.com` | `https://media.xiaolin.fun` |
| 示例 | `.../img-email-thunderbird/thunderbird-lookup.png` | `https://media.xiaolin.fun/img-email-thunderbird/thunderbird-lookup.png` |

---

## 前置条件

- [x] COS 桶 `media-1300240022` / `ap-nanjing`，公有读私有写
- [x] 媒体已上传 COS（鼓楼滨江 + static 插图等）
- [ ] 已购买 / 开通 **CDN 境内流量包**（控制台 → [CDN 概览](https://console.cloud.tencent.com/cdn)）
- [ ] 域名 `xiaolin.fun` 的 DNS 管理权限（添加 CNAME）

---

## 第一步：添加加速域名

1. 打开 [CDN 控制台 → 域名管理](https://console.cloud.tencent.com/cdn/domains)
2. **添加域名**
3. 填写：

| 项 | 值 |
|----|-----|
| 加速域名 | `media.xiaolin.fun` |
| 加速区域 | **中国境内**（与资源包一致） |
| 加速类型 | **CDN 网页小文件**（或「静态加速」） |
| 源站类型 | **COS 源** |
| 源站 | 选择 `media-1300240022`（南京） |
| 回源协议 | **HTTPS**（推荐）或协议跟随 |
| 回源 HOST | `media-1300240022.cos.ap-nanjing.myqcloud.com`（默认即可） |

4. **源站路径**：留空（对象在 Bucket 根目录，与 Markdown 路径一致）
5. 提交后，记录控制台分配的 **CNAME**，形如：  
   `media.xiaolin.fun.cdn.dnsv1.com`

> 勿在 COS 控制台单独再绑一次自定义域名，避免与 CDN 控制台配置冲突；统一在 **CDN 域名管理** 完成。

---

## 第二步：DNS 解析

在 `xiaolin.fun` 的 DNS 服务商（DNSPod / Cloudflare / 域名注册商）添加：

| 主机记录 | 记录类型 | 记录值 |
|----------|----------|--------|
| `media` | **CNAME** | 上一步 CDN 控制台给出的 CNAME |

- 仅添加 `media` 子域，不影响主站 `xiaolin.fun` A 记录
- 解析生效通常 5–30 分钟，最长 48 小时

本地检查：

```bash
dig +short media.xiaolin.fun CNAME
pnpm run media:cdn-check
```

---

## 第三步：HTTPS 证书

1. CDN 控制台 → 域名 `media.xiaolin.fun` → **HTTPS 配置**
2. 开启 **HTTPS 加速**
3. 证书来源（任选其一）：
   - **腾讯云托管证书**：免费 DV 证书，DNS 验证（域名在 DNSPod 时可一键）
   - **上传已有证书**：与主站共用 wildcard `*.xiaolin.fun` 亦可
4. 建议开启 **HTTP 自动跳转 HTTPS**
5. TLS 版本：TLS 1.2+

证书部署完成后，浏览器访问应无 mixed content 警告。

---

## 第四步：缓存与回源（推荐）

进入域名 **缓存配置**：

| 类型 | 缓存时间 | 说明 |
|------|----------|------|
| `.jpg` `.jpeg` `.png` `.webp` `.gif` | 30 天 | 图片文件名带版本号或换图后可在控制台刷新 URL |
| `.mp4` `.mov` | 7–30 天 | 视频可按访问量调整 |
| 默认 | 遵循源站 | 兜底 |

**回源配置**建议：

- 分片回源：开启（大文件）
- 回源超时：10–30s
- **忽略参数**：图片 URL 无查询参数时可开启「忽略 URL 参数」，提高命中率

**跨域（可选）**：若未来前端直连 CDN 资源，在 CDN **HTTP 响应头** 添加：

```
Access-Control-Allow-Origin: https://xiaolin.fun
```

个人站 Hugo 页面 `<img src="CDN">` 不需要 CORS；仅 JS fetch 媒体时需要。

---

## 第五步：验证 CDN 可用

```bash
# 项目内一键检查（对比 COS 直链与 CDN 状态码）
pnpm run media:cdn-check

# 手动抽查
curl -sI "https://media.xiaolin.fun/img-email-thunderbird/thunderbird-lookup.png"
curl -sI "https://media.xiaolin.fun/life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg"
```

期望：`HTTP/1.1 200 OK`，响应头含 `X-Cache-Lookup` 或 `X-NWS-LOG-UUID` 等 CDN 标识。

---

## 第六步：项目内切换 URL 前缀

CDN 验证通过后，将 Markdown 中 COS 直链批量换为 CDN 域名：

```bash
# 预览
pnpm run media:cdn-migrate

# 写入
pnpm run media:cdn-migrate:apply

# 本地构建验证
pnpm run build
```

脚本仅替换域名前缀，**路径不变**。`config/_default/media.toml` 中 `cdnBaseURL` 已为 `https://media.xiaolin.fun`，无需再改。

### GitHub Actions

仓库 **Settings → Secrets and variables → Actions → Variables** 添加：

| 名称 | 值 |
|------|-----|
| `MEDIA_CDN_BASE` | `https://media.xiaolin.fun` |

`media-verify` workflow 会在 push 后校验 content 内远程媒体 URL 可访问。

### 本地 `.env`

```bash
cp .env.example .env
# MEDIA_CDN_BASE=https://media.xiaolin.fun
```

---

## 第七步：提交并部署

```bash
git add content/ docs/
git commit -m "chore: 媒体 URL 切换至 CDN 域名"
git push
```

服务器 CD 拉取后重建镜像即可；读者侧图片走 CDN 边缘节点。

---

## 常见问题

### CNAME 已配但 404

- 确认 COS 对象键与 URL 路径一致（无 `/assets/images` 前缀）
- 检查 CDN 源站是否选对 Bucket、回源 HOST 是否为 Bucket 域名
- 新域名配置后等待 5–10 分钟再测

### HTTPS 证书申请失败

- 确认 `media.xiaolin.fun` CNAME 已生效
- DNS 验证记录是否添加到正确 DNS 服务商

### 换图后仍看到旧图

- CDN 缓存未过期：控制台 **刷新预热** → 提交 URL 刷新
- 或文件名加版本后缀（规范见 [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)）

### 流量与费用

- 控制台 → [用量统计](https://console.cloud.tencent.com/cdn/stat) 查看流量
- 建议设置 **用量告警**（如月度 80% 阈值）

---

## 检查清单

- [ ] CDN 域名 `media.xiaolin.fun` 已添加，源站为 COS `media-1300240022`
- [ ] DNS CNAME 已配置并生效
- [ ] HTTPS 已开启，HTTP 跳转 HTTPS
- [ ] `pnpm run media:cdn-check` 全部 ✓
- [ ] `pnpm run media:cdn-migrate:apply` 已执行
- [ ] `pnpm run build` 通过
- [ ] GitHub Variable `MEDIA_CDN_BASE` 已设置
- [ ] push 后 `Media URL Verify` workflow 绿色

相关文档：[MEDIA-OSS.md](MEDIA-OSS.md) · [MEDIA-STANDARDS.md](MEDIA-STANDARDS.md)
