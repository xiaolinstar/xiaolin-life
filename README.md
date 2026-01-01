# 持续运维｜基于VitePress搭建个人网站

> 运维相关工作经验分享

## 代办TODO

* [X]  搭建 Jenkins docker in docker 平台
* [X]  Jenkins 持续集成、持续部署
* [X]  使用 https 访问，端口号443
* [X]  变更时区为 Asia/Shanghai，自适应黑白主题
* [X]  在 Jenkins 容器中使用 docker compose 启动
* [X]  完善项目 README
* [X]  Nginx 支持 stub-status 模块
* [X]  增加 Prometheus 监控，监控 Linux 宿主机和 Nginx
* [X]  增加 Loki 日志系统
* [X]  实现 GitHub Actions CI/CD 流水线
* [X]  配置 SSH 方式 CD 部署
* [X]  nginx.conf URL 匹配，域名访问 grafana
* [X]  Markdown 语法支持脚注
* [ ]  Jenkinsfile 只将 main 分支执行流水线 
* [ ]  文章支持三级标签索引
* [ ]  数据库执行，使用传统的 shell 执行，编排到 Pipeline 中
* [ ]  数据库执行，使用专门的数据库执行工具，Bytebase、Liquibase

## 问题记录
- VitePress 中图片等静态文件 build
- Dockerfile 中使用国内镜像安装
- 时区问题
- 阿里云「HTTPS加速网关」配置，不需要修改原项目任何配置信息，包括 80 端口

## 配置

本项目依赖以下技术：

- VitePress: VitePress 是一个静态站点生成器 (SSG)，专为构建快速、以内容为中心的站点而设计。简而言之，VitePress 获取用 Markdown 编写的内容，对其应用主题，并生成可以轻松部署到任何地方的静态 HTML 页面。
- Jenkins: 一款开源 CI&CD 软件，用于自动化各种任务，包括构建、测试和部署软件。
- Docker 和 Docker Compose: 容器，环境隔离
- Nginx: Web服务器，代理静态资源，负载均衡
- npm & pnpm: 前端包管理器，安装第三方库，项目编译、打包等 

## 更新日志

2024-09-13：支持 `Dockerfile` 构建镜像，添加 `Jenkinsfile` 
2025-01-25：Jenkins容器支持 Docker Compose 能力
2025-01-25：添加 Prometheus 监控，包括 node-exporter 监控宿主机，nginx-prometheus-exporter 监控 nginx
2025-09-01：使用 Kubernetes 部署服务，外部流量→ NodePort (在节点上) → port (在Service上) → targetPort (在Pod上)
2025-12-10：添加 GitHub Actions CI/CD 流水线，支持自动构建和部署

## 介绍
本项目基于 VitePress 构建静态资源站点，访问域名：https://xiaolin.fun 

在提供基本的博客服务能力外，增加运维能力建设：

- docker 容器化，docker compose 多容器编排启动
- Jenkins 编排开发、测试、集成、部署，实现 CI/CD
- Grafana + Prometheus 支持指标监控，包括 Linux 宿主机，Nginx 服务器
- 高可用，部署多个服务，使用 Nginx 作负载均衡
- Grafana Loki 支持日志管理

## 单点容器编排 Docker Compose



## 分布式容器编排 Kubernetes

文件目录 `k8s`

Kubernetes 一键启动所有服务
```shell
kubectl apply -f k8s
```

逐个启动服务，观察运行情况
```shell
kubectl apply -f k8s/vitepress-website.yaml
kubectl apply -f k8s/nginx-gateway-config.yaml
kubectl apply -f k8s/nginx-gateway.yaml
```

启动完成后检查：

```shell
kubectl get pods
kubectl get services
kubectl describe deploy nginx-gateway-deploy
```

访问服务，外部流量→ NodePort (在节点上) → port (在Service上) → targetPort (在Pod上)

[http://localhost:32108](http://localhost:32108)


## Jenkins 与 CI/CD

### GitHub Actions CI/CD 流水线

本项目提供了两套 CI/CD 解决方案：

1. **Jenkins 流水线** - 传统的 CI/CD 方案
2. **GitHub Actions 流水线** - 现代化的 CI/CD 方案

GitHub Actions 配置文件位于 `.github/workflows/` 目录下：

- `release-package.yml` - CI 流水线，负责构建 Docker 镜像并推送到 GitHub Container Registry
- `deploy.yml` - CD 流水线，通过 SSH 部署到目标服务器（使用 Docker Compose）
- `deploy-k8s.yml.disabled` - CD 流水线，部署到 Kubernetes 集群（当前已禁用）
#### 配置说明

为了使 GitHub Actions 正常工作，您需要在仓库的 Secrets 中配置以下环境变量：

##### SSH 部署所需 Secrets：
- `SERVER_PASSWORD` - 目标服务器密码（用于密码认证）
- `SERVER_USER` - 目标服务器用户名
- `SERVER_HOST` - 目标服务器 IP 地址或域名

> 注意：确保目标服务器已正确配置 Docker 和 Docker Compose 环境，并且允许通过 SSH 连接。当前部署使用密码认证方式连接到腾讯云服务器。
##### Kubernetes 部署所需 Secrets：
- `KUBECONFIG_DATA` - Kubernetes 配置文件内容（base64 编码）

> 注意：Kubernetes 集群的连接信息（API 服务器地址、认证令牌等）都包含在 kubeconfig 文件中，因此不需要单独配置服务器地址等环境变量。

##### 邮件通知所需 Secrets：
- `MAIL_USERNAME` - QQ 邮箱账号
- `MAIL_PASSWORD` - QQ 邮箱授权码

#### 部署流程

1. 当代码推送到 `release` 分支时，会自动触发 CI 流水线
2. CI 流水线构建 Docker 镜像并推送到 GHCR
3. SSH CD 流水线会自动部署最新的镜像到目标服务器（Kubernetes部署已禁用）

您也可以手动触发部署流程：
1. 在 GitHub 仓库页面点击 "Actions" 标签
2. 选择 `CD Pipeline, Deploy to Target Server` 工作流
3. 点击 "Run workflow" 按钮

## Prometheus 与指标监控
## 多服务部署高可用

## Grafana Loki 日志管理


## 参考

1. Compose build https://docs.docker.com/reference/compose-file/build/#using-build-and-image
2. Nginx-Prometheus-Exporter https://github.com/nginx/nginx-prometheus-exporter
