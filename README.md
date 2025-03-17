# 持续运维｜基于VitePress搭建个人网站

> 运维相关工作经验分享

## 代办TODO

* [X]  搭建 Jenkins docker in docker 平台
* [X]  Jenkins 持续集成、持续部署
* [X]  使用 https 访问，端口号443
* [X]  变更时区为 Asia/Shanghai，自适应黑白主题
* [X]  在 Jenkins 容器中使用 docker compose 启动
* [ ]  完善项目 README
* [ ]  GitHub Pages 文件标签显示
* [X]  Nginx 支持 stub-status 模块
* [X]  增加 Prometheus 监控，监控 Linux 宿主机和 Nginx
* [X]  增加 Loki 日志系统
* [ ]  nginx.conf URL 匹配，域名访问 grafana
* [ ]  Markdown 语法支持脚注
* [ ]  Jenkinsfile 只将 main 分支执行流水线 


## 问题记录
- VitePress 中图片等静态文件 build
- Dockerfile 中使用国内镜像安装
- 时区问题
- 阿里云「HTTPS加速网关」配置，不需要修改原项目任何配置信息，包括 80 端口

脚注：https://bddxg.top/article/note/vitepress%E4%BC%98%E5%8C%96/%E6%B7%BB%E5%8A%A0markdown%E8%84%9A%E6%B3%A8%E5%8A%9F%E8%83%BD.html

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


## 介绍

本项目基于 VitePress 构建静态资源站点，访问域名：https://xiaolin.fun 

在提供基本的博客服务能力外，增加运维能力建设：

- docker 容器化，docker compose 多容器编排启动
- Jenkins 编排开发、测试、集成、部署，实现 CI/CD
- Grafana + Prometheus 支持指标监控，包括 Linux 宿主机，Nginx 服务器
- 高可用，部署多个服务，使用 Nginx 作负载均衡
- Grafana Loki 支持日志管理

## 容器化

## Jenkins 与 CI/CD

## Prometheus 与指标监控


## 多服务部署高可用

## Grafana Loki 日志管理


## 参考

1. Compose build https://docs.docker.com/reference/compose-file/build/#using-build-and-image
2. Nginx-Prometheus-Exporter https://github.com/nginx/nginx-prometheus-exporter
