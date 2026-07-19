#!/usr/bin/env bash
# 新建文章 Page Bundle 脚手架（Agent 可调用：life.draft_article）
#
# 用法：
#   ./scripts/new-article.sh content/life/entertainment/<slug> "文章标题"
#   ./scripts/new-article.sh content/office/<slug> "标题" --description "一句话描述"
#
# 生成：
#   content/<path>/index.md   draft: true 草稿
#   content/<path>/gallery/   媒体目录（gitignore，仅本机/VPS 持有）

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

PAGE=""
TITLE=""
DESCRIPTION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --description)
      DESCRIPTION="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,11p' "$0"
      exit 0
      ;;
    *)
      if [[ -z "$PAGE" ]]; then
        PAGE="$1"
      elif [[ -z "$TITLE" ]]; then
        TITLE="$1"
      else
        echo "Error: 未识别的参数: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$PAGE" || -z "$TITLE" ]]; then
  echo "Usage: $0 content/<section>/<slug> \"标题\" [--description \"...\"]" >&2
  exit 1
fi

case "$PAGE" in
  content/*) ;;
  *)
    echo "Error: 路径必须以 content/ 开头: $PAGE" >&2
    exit 1
    ;;
esac

DIR="$ROOT/$PAGE"
INDEX="$DIR/index.md"

if [[ -f "$INDEX" ]]; then
  echo "Error: 已存在 $PAGE/index.md，拒绝覆盖" >&2
  exit 1
fi

# 按区推断默认分类
category="生活"
case "$PAGE" in
  content/office/*) category="办公" ;;
esac

mkdir -p "$DIR/gallery"
touch "$DIR/gallery/.gitkeep"

cat > "$INDEX" <<EOF
---
title: "$TITLE"
description: "${DESCRIPTION:-$TITLE}"
date: $(date +%Y-%m-%d)
draft: true
showTableOfContents: true
categories:
  - "$category"
tags:
  - "南京"
---

正文待补充。

<!-- 图片放本目录 gallery/（不进 Git），然后执行：
  ./scripts/media-publish.sh $PAGE --rewrite
  即上传 COS 并把 carousel/assets 引用改写为 CDN URL -->
EOF

echo "已创建: $PAGE/index.md（draft: true）"
echo "媒体目录: $PAGE/gallery/"
echo "下一步:"
echo "  1. 补正文；图片放 gallery/（./scripts/save-media.sh $PAGE <图片...>）"
echo "  2. ./scripts/media-publish.sh $PAGE --rewrite"
echo "  3. 确认后去掉 draft: true，提交 index.md"
