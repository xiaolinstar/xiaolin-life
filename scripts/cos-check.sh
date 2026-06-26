#!/usr/bin/env bash
# 检查 coscli 与腾讯云 COS 连通性（需已完成 coscli config init）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"

CONFIG="$(cos_config_path)"

echo "== coscli =="
if ! command -v coscli >/dev/null 2>&1; then
  echo "✗ coscli 未安装"
  exit 1
fi
coscli --version

echo
echo "== 配置文件 =="
if [[ ! -f "$CONFIG" ]]; then
  echo "✗ 未找到 $CONFIG"
  echo "  请执行: coscli config init"
  exit 1
fi
echo "✓ $CONFIG 存在"

cos_load_config
echo "  Bucket: ${COS_BUCKET_NAME} (alias: ${COS_BUCKET_ALIAS})"
echo "  Endpoint: ${COS_ENDPOINT}"
if [[ -n "${COS_PUBLIC_BASE_URL:-}" ]]; then
  echo "  直链前缀: ${COS_PUBLIC_BASE_URL}"
fi

echo
echo "== Bucket 连通 =="
if coscli ls "cos://${COS_BUCKET_ALIAS}/" 2>/dev/null; then
  echo "✓ cos://${COS_BUCKET_ALIAS}/ 可访问"
else
  echo "✗ 无法列出 cos://${COS_BUCKET_ALIAS}/"
  echo "  检查 alias、密钥权限与 Bucket 地域"
  exit 1
fi

echo
echo "== 本地媒体体量 =="
du -sh "$ROOT/static/assets/images" 2>/dev/null || true
find "$ROOT/content" -type d -name gallery -exec du -sh {} \; 2>/dev/null | sort -hr | head -5

echo
echo "就绪。上传: ./scripts/upload-media-cos.sh static/assets/images"
