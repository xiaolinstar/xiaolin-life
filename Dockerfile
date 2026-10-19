FROM node:24-bookworm-slim AS build-stage
ARG TARGETARCH
WORKDIR /app
COPY .hugo-version ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash git tzdata python3 python3-pip \
  && HUGO_VERSION="$(cat .hugo-version)" \
  && HUGO_ASSET="hugo_extended_${HUGO_VERSION}_linux-${TARGETARCH}.tar.gz" \
  && HUGO_BASE="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}" \
  && curl -fsSL "$HUGO_BASE/$HUGO_ASSET" -o /tmp/hugo.tar.gz \
  && curl -fsSL "$HUGO_BASE/hugo_${HUGO_VERSION}_checksums.txt" -o /tmp/hugo-checksums.txt \
  && HUGO_SHA="$(awk -v asset="$HUGO_ASSET" '$2 == asset {print $1}' /tmp/hugo-checksums.txt)" \
  && test -n "$HUGO_SHA" \
  && printf '%s  /tmp/hugo.tar.gz\n' "$HUGO_SHA" | sha256sum -c - \
  && tar xzf /tmp/hugo.tar.gz -C /usr/local/bin hugo \
  && rm /tmp/hugo.tar.gz /tmp/hugo-checksums.txt \
  && npm install -g pnpm@9.15.0 \
  && pip install --break-system-packages pillow \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

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
