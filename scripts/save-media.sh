#!/usr/bin/env bash
# 收图入库（Agent 可调用：life.save_media）
#
# 将图片复制进文章 gallery/ 并规范化命名（小写、连字符、递增序号前缀）。
# 仅接受图片白名单扩展名；超过大小上限拒绝（默认 20MB，IMG_MAX_MB 可调）。
#
# 用法：
#   ./scripts/save-media.sh content/life/entertainment/<slug> <图片文件...>
#
# 示例：
#   ./scripts/save-media.sh content/life/entertainment/carbs ~/Downloads/IMG_0123.JPG

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMG_MAX_MB="${IMG_MAX_MB:-20}"

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 content/<section>/<slug> <图片文件...>" >&2
  exit 1
fi

PAGE="$1"
shift

DIR="$ROOT/$PAGE"
GALLERY="$DIR/gallery"

if [[ ! -f "$DIR/index.md" ]]; then
  echo "Error: 文章不存在: $PAGE/index.md（先执行 new-article.sh）" >&2
  exit 1
fi
mkdir -p "$GALLERY"

# 现有最大序号，从其后继续编号
next_seq=1
for f in "$GALLERY"/[0-9][0-9]-*; do
  [[ -e "$f" ]] || continue
  seq="${f##*/}"
  seq="${seq%%-*}"
  if [[ "$seq" =~ ^[0-9]+$ ]] && (( 10#$seq >= next_seq )); then
    next_seq=$((10#$seq + 1))
  fi
done

max_bytes=$((IMG_MAX_MB * 1024 * 1024))
saved=0

for src in "$@"; do
  if [[ ! -f "$src" ]]; then
    echo "✗ 跳过（文件不存在）: $src" >&2
    continue
  fi

  base="$(basename "$src")"
  ext="${base##*.}"
  ext="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
  case "$ext" in
    jpg|jpeg|png|webp|gif) ;;
    *)
      echo "✗ 拒绝（非图片白名单 .jpg/.jpeg/.png/.webp/.gif）: $base" >&2
      continue
      ;;
  esac

  size="$(stat -f%z "$src" 2>/dev/null || stat -c%s "$src")"
  if (( size > max_bytes )); then
    echo "✗ 拒绝（超过 ${IMG_MAX_MB}MB）: $base ($((size / 1024 / 1024))MB)" >&2
    continue
  fi

  # slug 化原文件名：小写、非字母数字转连字符
  stem="${base%.*}"
  slug="$(printf '%s' "$stem" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"
  slug="${slug:-img}"

  dest="$GALLERY/$(printf '%02d' "$next_seq")-${slug}.${ext}"
  cp "$src" "$dest"
  echo "✓ ${dest#"$ROOT"/}"
  next_seq=$((next_seq + 1))
  saved=$((saved + 1))
done

echo
echo "已入库 $saved 张 → $PAGE/gallery/"
echo "下一步: ./scripts/media-publish.sh $PAGE --rewrite"
