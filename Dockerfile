FROM alpine:3.20 AS hugo
ARG HUGO_VERSION=0.158.0
RUN apk add --no-cache curl tar \
  && curl -fsSL "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" \
    | tar xz -C /usr/local/bin hugo

FROM hugo AS build-stage
WORKDIR /app

RUN apk add --no-cache nodejs npm git tzdata

COPY package.json package-lock.json ./
RUN npm ci || npm install

COPY . .
RUN npm run build

FROM nginx:alpine3.20-perl

COPY volumes/website/nginx.conf /etc/nginx/nginx.conf
COPY volumes/website/default.conf /etc/nginx/conf.d/default.conf
COPY volumes/website/nginx-stub-status.conf /etc/nginx/conf.d/nginx-stub-status.conf
COPY --from=build-stage /app/public /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
