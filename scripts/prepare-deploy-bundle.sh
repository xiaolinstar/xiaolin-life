#!/usr/bin/env bash
# 打包 Hugo 构建产物供 CD 传输；启用 CDN 时可剔除本地媒体以缩小部署包。
set -euo pipefail

SOURCE="${1:-public}"
OUTPUT="${2:-site.tar.gz}"
CDN_BASE="${MEDIA_CDN_BASE:-}"

if [[ ! -d "$SOURCE" ]]; then
  echo "Error: source directory not found: $SOURCE" >&2
  exit 1
fi

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
cp -a "$SOURCE/." "$STAGE/"

if [[ -n "$CDN_BASE" ]]; then
  echo "MEDIA_CDN_BASE set — stripping local media from deploy bundle"
  rm -rf "$STAGE/assets/images"
  find "$STAGE" -type d -name gallery -print0 | xargs -0 rm -rf 2>/dev/null || true
fi

du -sh "$STAGE"
tar -C "$STAGE" -czf "$OUTPUT" .
ls -lh "$OUTPUT"
