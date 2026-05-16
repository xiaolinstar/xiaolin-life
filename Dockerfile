FROM ruby:3.2-alpine AS build-stage
# 作者信息
LABEL authors="xing.xiaolin@foxmail.com"

# 设置工作目录
WORKDIR /app

# 安装 Jekyll 构建依赖
RUN apk add --no-cache build-base git tzdata

# 复制所有文件到工作目录
COPY . .

# 安装依赖并构建 Jekyll 静态站点
RUN bundle config set path vendor/bundle \
    && bundle install \
    && JEKYLL_ENV=production bundle exec jekyll build --trace --config _config.yml,_config.self-hosted.yml



FROM nginx:alpine3.20-perl

COPY volumes/website/nginx.conf /etc/nginx/nginx.conf
COPY volumes/website/default.conf /etc/nginx/conf.d/default.conf
COPY volumes/website/nginx-stub-status.conf /etc/nginx/conf.d/nginx-stub-status.conf

COPY --from=build-stage /app/_site /usr/share/nginx/html

# 启动Nginx服务
CMD ["nginx", "-g", "daemon off;"]
