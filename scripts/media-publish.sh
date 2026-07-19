#!/usr/bin/env bash
# 本地媒体发布：上传 COS → 校验直链 →（可选）改写 Markdown URL
#
# gallery/ 不进 Git，此脚本必须在持有 gallery 与 COS 凭证的机器上执行
# （当前：作者本机；接入 Hermes 后：腾讯轻量 VPS）。需 coscli + ~/.cos.yaml。
#
# 用法：
#   ./scripts/media-publish.sh content/life/entertainment/gulou-riverfront
#   ./scripts/media-publish.sh content/life/entertainment/gulou-riverfront --rewrite
#   MEDIA_CDN_BASE=https://media-1300240022.cos.ap-nanjing.myqcloud.com ./scripts/media-publish.sh ...
#
# 环境变量：
#   MEDIA_CDN_BASE  改写 URL 时使用；未设则从 cos-config 推导 COS 直链前缀

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"

REWRITE=false
PATHS=()

for arg in "$@"; do
  case "$arg" in
    --rewrite) REWRITE=true ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *) PATHS+=("$arg") ;;
  esac
done

if [[ ${#PATHS[@]} -eq 0 ]]; then
  echo "Usage: $0 <content-page-dir> [--rewrite]" >&2
  echo "Example: $0 content/life/entertainment/gulou-riverfront" >&2
  exit 1
fi

cos_load_config

MEDIA_BASE="${MEDIA_CDN_BASE:-${COS_PUBLIC_BASE_URL:-}}"
if [[ -z "$MEDIA_BASE" ]]; then
  echo "Error: 无法确定 MEDIA_CDN_BASE / COS 直链前缀" >&2
  exit 1
fi

for page in "${PATHS[@]}"; do
  page_abs="$(cd "$ROOT" && realpath "$page")"
  rel="${page_abs#"$ROOT"/}"
  gallery="$page_abs/gallery"

  if [[ ! -d "$gallery" ]]; then
    echo "Skip（无 gallery/）: $rel" >&2
    continue
  fi

  count="$(find "$gallery" -type f ! -name '.gitkeep' | wc -l)"
  if [[ "$count" -eq 0 ]]; then
    echo "Skip（gallery 为空）: $rel" >&2
    continue
  fi

  echo "== 发布: $rel ($count 个文件) =="
  "$ROOT/scripts/upload-media-cos.sh" "$gallery"

  cos_prefix="${rel#content/}"
  sample="$(find "$gallery" -type f ! -name '.gitkeep' | sort | head -1)"
  sample_name="$(basename "$sample")"
  sample_url="${MEDIA_BASE%/}/${cos_prefix}/${sample_name}"

  echo "→ 校验: $sample_url"
  if curl -sfI "$sample_url" | head -1 | grep -q '200'; then
    echo "✓ 直链可访问"
  else
    echo "✗ 直链不可访问，请检查 Bucket 权限与对象键" >&2
    exit 1
  fi

  if [[ "$REWRITE" == true ]]; then
    index="$page_abs/index.md"
    if [[ -f "$index" ]]; then
      echo "→ 改写 Markdown: $index"
      MEDIA_CDN_BASE="$MEDIA_BASE" python3 "$ROOT/scripts/rewrite-media-urls.py" --apply "$index"
    fi
  fi

  echo
  echo "COS 键前缀: ${cos_prefix}/"
  echo "URL 前缀:   ${MEDIA_BASE%/}/${cos_prefix}/"
  echo "下一步:"
  echo "  1. 将 index.md 中 gallery/* / /assets/images/ 改为上述 URL 前缀"
  echo "  2. git add content/.../index.md && git commit"
  echo "  3. push 后 CI 会构建瘦身镜像（HTML 已指向 COS）"
  echo
done
