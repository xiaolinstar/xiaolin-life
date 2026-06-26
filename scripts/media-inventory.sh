#!/usr/bin/env bash
# 统计待上传媒体与 Markdown 引用，输出迁移清单。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"
cos_load_config 2>/dev/null || true

CDN="${MEDIA_CDN_BASE:-https://media.xiaolin.fun}"
COS_INFO="${COS_BUCKET_ALIAS:-（未配置 ~/.cos.yaml）}"

echo "# 媒体迁移清单"
echo "生成时间: $(date -Iseconds)"
echo "CDN: $CDN"
echo "COS alias: $COS_INFO"
if [[ -n "${COS_PUBLIC_BASE_URL:-}" ]]; then
  echo "COS 直链: $COS_PUBLIC_BASE_URL"
fi
echo

echo "## static/assets/images"
du -sh "$ROOT/static/assets/images"
find "$ROOT/static/assets/images" -type f | wc -l | xargs echo "文件数:"
find "$ROOT/static/assets/images" -mindepth 1 -maxdepth 1 -type d | while read -r d; do
  du -sh "$d"
done | sort -hr

echo
echo "## Page Bundle gallery"
find "$ROOT/content" -type d -name gallery | while read -r g; do
  du -sh "$g"
  echo "  ${g#"$ROOT"/}"
done | sort -hr

echo
echo "## Markdown 中的 /assets/images/ 引用"
rg -c '/assets/images/' "$ROOT/content" --glob '*.md' 2>/dev/null | sort -t: -k2 -nr || true

echo
echo "## 鼓楼滨江（试点）"
G="$ROOT/content/life/entertainment/gulou-riverfront/gallery"
if [[ -d "$G" ]]; then
  du -sh "$G"
  ls "$G" 2>/dev/null | wc -l | xargs echo "文件数:"
  echo "  COS 键前缀: life/entertainment/gulou-riverfront/"
fi
echo
echo "## 建议上传命令（coscli 配置完成后）"
echo "./scripts/upload-media-cos.sh static/assets/images"
echo "./scripts/upload-media-cos.sh content/life/entertainment/gulou-riverfront/gallery"
