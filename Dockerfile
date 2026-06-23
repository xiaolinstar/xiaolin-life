FROM alpine:3.20 AS hugo
ARG HUGO_VERSION=0.158.0
RUN apk add --no-cache curl tar \
  && curl -fsSL "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz" \
    | tar xz -C /usr/local/bin hugo

FROM hugo AS build-stage
WORKDIR /app

RUN apk add --no-cache nodejs npm python3 py3-pip git tzdata \
  && npm install -g pnpm@9.15.0 \
  && pip install --break-system-packages pillow

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build

FROM nginx:alpine3.20-perl

COPY volumes/website/nginx.conf /etc/nginx/nginx.conf
COPY volumes/website/default.conf /etc/nginx/conf.d/default.conf
COPY volumes/website/nginx-stub-status.conf /etc/nginx/conf.d/nginx-stub-status.conf
COPY --from=build-stage /app/public /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
