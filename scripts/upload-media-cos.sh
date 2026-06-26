#!/usr/bin/env bash
# 使用 coscli 将本地媒体同步到腾讯云 COS，供 CDN 加速。
#
# 前置：coscli config init / config add（见 docs/MEDIA-OSS.md）
#
# 环境变量（均可选，未设置时从 ~/.cos.yaml 读取）：
#   COS_BUCKET_ALIAS  coscli bucket alias
#   COS_PREFIX        可选对象键前缀，默认空（与 CDN URL 路径一致）
#
# 用法：
#   ./scripts/upload-media-cos.sh static/assets/images
#   ./scripts/upload-media-cos.sh content/life/entertainment/gulou-riverfront/gallery

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"
cos_load_config

ALIAS="$COS_BUCKET_ALIAS"
PREFIX="${COS_PREFIX:-}"
PREFIX="${PREFIX#/}"
PREFIX="${PREFIX%/}"

if ! command -v coscli >/dev/null 2>&1; then
  echo "Error: coscli 未安装，见 https://cloud.tencent.com/document/product/436/63144" >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <local-path> [local-path ...]" >&2
  exit 1
fi

cos_dest() {
  local key="$1"
  key="${key#/}"
  if [[ -n "$PREFIX" && -n "$key" ]]; then
    echo "cos://${ALIAS}/${PREFIX}/${key}"
  elif [[ -n "$PREFIX" ]]; then
    echo "cos://${ALIAS}/${PREFIX}/"
  elif [[ -n "$key" ]]; then
    echo "cos://${ALIAS}/${key}"
  else
    echo "cos://${ALIAS}/"
  fi
}

upload_static_images() {
  local src="$1"
  local images_root="$ROOT/static/assets/images"
  if [[ "$src" == "$images_root" ]]; then
    echo "→ sync static/assets/images → $(cos_dest "")"
    coscli sync "$src/" "$(cos_dest "")" -r
  else
    local name
    name="$(basename "$src")"
    echo "→ sync ${src#"$ROOT"/} → $(cos_dest "$name")/"
    coscli sync "$src/" "$(cos_dest "$name")/" -r
  fi
}

upload_page_gallery() {
  local src="$1"
  local page_dir
  page_dir="$(dirname "$src")"
  local cos_key="${page_dir#"$ROOT/content/"}"
  echo "→ sync ${src#"$ROOT"/} → $(cos_dest "$cos_key")/"
  coscli sync "$src/" "$(cos_dest "$cos_key")/" -r
}

for arg in "$@"; do
  target="$(cd "$ROOT" && realpath "$arg")"
  if [[ ! -e "$target" ]]; then
    echo "Skip missing: $arg" >&2
    continue
  fi

  rel="${target#"$ROOT"/}"
  case "$rel" in
    static/assets/images|static/assets/images/*)
      if [[ -d "$target" ]]; then
        upload_static_images "$target"
      else
        parent="$(dirname "$target")"
        upload_static_images "$parent"
      fi
      ;;
    */gallery|*/gallery/*)
      if [[ -d "$target" ]]; then
        if [[ "$(basename "$target")" == "gallery" ]]; then
          upload_page_gallery "$target"
        else
          upload_page_gallery "$(dirname "$target")"
        fi
      else
        upload_page_gallery "$(dirname "$(dirname "$target")")"
      fi
      ;;
    *)
      name="$(basename "$target")"
      if [[ -d "$target" ]]; then
        echo "→ sync: ${rel} → $(cos_dest "$name")/"
        coscli sync "$target/" "$(cos_dest "$name")/" -r
      else
        parent="$(dirname "$target")"
        pname="$(basename "$parent")"
        echo "→ cp: ${rel} → $(cos_dest "$pname")/$(basename "$target")"
        coscli cp "$target" "$(cos_dest "$pname")/$(basename "$target")"
      fi
      ;;
  esac
done

echo "Done. Bucket: cos://${ALIAS}/"
if [[ -n "${MEDIA_CDN_BASE:-}" ]]; then
  echo "CDN base: ${MEDIA_CDN_BASE}"
elif [[ -n "${COS_PUBLIC_BASE_URL:-}" ]]; then
  echo "Public base (COS 直链，CDN 未配): ${COS_PUBLIC_BASE_URL}"
fi
