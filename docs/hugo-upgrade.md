# Hugo 与主题升级

2026-10-19：Hugo Extended 0.168.0，Blowfish v3.9.0（`ebe683e9`）。升级前主题为 v2.104.0（`1f144483`）。

## 版本与安装

- `.hugo-version` 是本地、Docker、Pages 的统一版本来源。
- `bash bin/install-hugo.sh` 校验官方 SHA256 后安装到 `.tools/hugo-<版本>`；macOS 只解包 `.pkg`，不执行系统安装器。
- `bin/hugo` 拒绝运行不同版本或非 Extended 二进制；Hugo 工具不进入 Git。
- 主题声明支持 0.164.0–0.167.0；项目对 0.168.0 单独验证，保留兼容范围警告。

## 验证与回退

0.167.0 基线和 0.168.0 生产构建均通过，126 条搜索记录一致，既有页面地址保留。两版本各 7 项搜索测试通过；JS/CSS 本地资源及 SRI 校验通过。图片质量改为按格式配置，保留质量 75。

浏览器检查覆盖栏目抽屉、Esc 与焦点恢复、搜索、主题筛选、多图轮播及深浅色显示。旧轮播桥接与原生处理冲突，已移除；项目搜索补齐新版页头提示的 `⌘K` / `Ctrl K` 快捷键。

Linux ARM64 容器使用官方 Hugo 二进制完成离线生产构建，页面地址与搜索索引和 macOS 一致。完整 Docker 镜像 `xiaolin-life:local`（ARM64）已构建成功。临时证书挂载下，原 nginx 配置检查、5 个 HTTPS 页面、健康检查 204、HTTP 跳转、13 个 JS/CSS 资源与 SRI、126 条搜索记录及 7 项搜索测试通过；草稿未发布。验证容器和临时证书已清理。Pages 已完成本地对应环境构建，未触发远程部署。

如需回退 Hugo，修改 `.hugo-version` 为 `0.167.0`，运行 `bash bin/install-hugo.sh` 并重启预览。保留 Blowfish v3.9.0；Docker 和 Pages 会读取同一版本文件。
