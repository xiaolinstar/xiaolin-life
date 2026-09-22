# 腾讯云 CDN 证书续期流程

`media.xiaolin.fun` 当前使用 **腾讯云 CDN 终结 SSL**，证书为 **TrustAsia DV TLS 单域名证书**（90 天免费）。

| 项 | 值 |
| --- | --- |
| 域名 | `media.xiaolin.fun` |
| 厂商 | TrustAsia DV TLS RSA CA 2024 |
| 部署位置 | 腾讯云 CDN 边缘节点 |
| 续期频率 | **每 90 天**（约每年 4 次；免费证书不支持直接续期，必须重新申请） |
| 提前量 | 建议到期前 **15 天** 申请并部署，预留 DNS 验证 + CDN 节点推送时间 |

> 与主站 `xiaolin.fun`（121 服务器 nginx 终结）无关，本流程只影响 CDN。

---

## 前置条件

- [ ] 腾讯云账号已实名，且拥有 SSL 证书 + CDN 控制台权限
- [ ] `xiaolin.fun` 域名 DNS 服务商账号可用（DNSPod / Cloudflare / 注册商）
- [ ] 距离当前证书到期 ≥ 7 天（避免签发失败）

---

## 第一步：申请免费证书

[SSL 证书控制台](https://console.cloud.tencent.com/ssl) → **申请免费证书**

| 项 | 值 |
| --- | --- |
| 证书类型 | **TrustAsia DV TLS 单域名证书** |
| 通用名称 | `media.xiaolin.fun` |
| 验证方式 | **DNS 验证** |

提交后状态为 `待验证`，同时控制台会给出 DNS 解析记录（形如 `_dnsauth.media` CNAME）。

---

## 第二步：DNS 验证

按控制台给出的记录值，到 DNS 服务商添加：

| 主机记录 | 记录类型 | 记录值 |
|----------|----------|--------|
| `_dnsauth.media`（以控制台实际值为准） | **CNAME** | `xxxxxxxx.tcnverify.qq.com` |

- **DNSPod + 已绑腾讯云账号**：控制台有「**一键验证**」按钮，点一下自动添加
- **Cloudflare**：手动添加，**务必关闭代理（DNS only，灰色云朵）**，否则验证会失败
- **其他注册商**：手动添加即可

等待 5–10 分钟，状态变 `已签发`。

---

## 第三步：清理旧验证记录

DNS 服务商上若有 **往年残留的 `_dnsauth.media` CNAME 记录**，删除掉，避免堆积无用解析。

---

## 第四步：部署到 CDN

[CDN 控制台 → 域名管理](https://console.cloud.tencent.com/cdn/domains) → `media.xiaolin.fun` → **HTTPS 配置**

1. 证书来源：**腾讯云托管证书** → 选择刚签发的那张
2. 推荐配置：
   - HTTP/2 ✅
   - **HTTP → HTTPS 自动跳转** ✅
   - TLS 1.2 / 1.3 ✅
3. 保存

CDN 边缘节点推送通常 1–3 分钟生效。

---

## 第五步：校验

```bash
# 1. 看证书是否已切换
echo | openssl s_client -servername media.xiaolin.fun \
  -connect media.xiaolin.fun:443 2>/dev/null \
  | openssl x509 -noout -dates -issuer -subject

# 期望：
#   notAfter: 约 3 个月后（90 天期）
#   subject:  CN = media.xiaolin.fun
#   issuer:   TrustAsia

# 2. 项目内 CDN 健康检查
cd ~/AgentProjects/xiaolin-life
pnpm run media:cdn-check

# 3. 模拟浏览器完整路径
curl -sI -L https://media.xiaolin.fun/life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg
# 期望第一行是 HTTP/2 200
```

---

## 第六步：加到期告警（强烈建议）

两处都开，避免下次再「突然发现快过期」：

1. **SSL 证书控制台** → 右上角 **消息订阅** → 订阅「证书到期提醒」（提前 30 天邮件/短信）
2. **CDN 控制台** → **用量告警** → 证书相关提醒

---

## 自动化与升级（可选）

| 方案 | 说明 | 适用 |
| --- | --- | --- |
| **单域名手动（默认）** | 每 90 天手动走一遍本流程 | 子域少（当前） |
| **Wildcard `*.xiaolin.fun`** | 一次申请覆盖主站 + 所有子域 | 子域 ≥ 3 个 |
| **GitHub Actions 监控** | SSL API 查证书剩余天数，< 15 天发通知 | 不想被邮件淹没 |

---

## 检查清单

- [ ] 新证书状态 `已签发`
- [ ] DNS 验证记录已添加
- [ ] 旧验证记录已删除
- [ ] CDN HTTPS 配置已切换至新证书
- [ ] HTTP→HTTPS 跳转已开启
- [ ] `openssl s_client` 显示新 `notAfter`
- [ ] `pnpm run media:cdn-check` 全部 ✓
- [ ] SSL 控制台到期提醒已订阅

---

## 常见问题

### DNS 验证一直不通过

- 确认记录值复制完整（无空格 / 换行）
- Cloudflare 检查代理是否关掉（橙色云朵 = 走代理，会破坏验证）
- 用 `dig _dnsauth.media.xiaolin.fun CNAME` 在本机验证记录是否生效

### 部署后浏览器仍看旧证书

- 强制刷新（Cmd/Ctrl + Shift + R）
- 浏览器缓存 / HSTS 记录了旧证书指纹，清除站点数据
- CDN 节点推送延迟，等 5 分钟后再测

### 想从单域名升级到 wildcard

`*.xiaolin.fun` 申请流程基本一致，DNS 验证记录的主机记录不同（以控制台提示为准）。注意：

- DNSPod 一键验证对 wildcard 支持有时不稳定，建议手动添加
- 一张 wildcard 证书可同时在 CDN + 121 服务器使用，部署更省事

---

相关文档：[CDN-SETUP.md](CDN-SETUP.md) · [MEDIA-OSS.md](MEDIA-OSS.md)
