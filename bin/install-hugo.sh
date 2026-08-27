#!/usr/bin/env bash
# bin/install-hugo.sh — 下载项目锁定的 Hugo v0.163.3 到 ./.tools/hugo158
#
# 用法：
#   ./bin/install-hugo.sh           # 自动检测平台下载
#   ./bin/install-hugo.sh --check   # 仅检查 ./.tools/hugo158 是否就绪

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS_DIR="$ROOT/.tools"
DEST="$TOOLS_DIR/hugo158"

HUGO_VERSION="0.163.3"

if [[ "${1:-}" == "--check" ]]; then
  if [[ -x "$DEST" ]]; then
    VER=$("$DEST" version 2>/dev/null | head -1 || echo "unknown")
    echo "✓ .tools/hugo158 已就绪 ($VER)"
    exit 0
  else
    echo "✗ .tools/hugo158 未安装"
    exit 1
  fi
fi

mkdir -p "$TOOLS_DIR"

# 检测平台
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "$OS-$ARCH" in
  linux-x86_64|linux-amd64) PLATFORM="linux-amd64" ;;
  linux-aarch64|linux-arm64) PLATFORM="linux-arm64" ;;
  darwin-x86_64|darwin-amd64) PLATFORM="darwin-universal" ;;
  darwin-arm64) PLATFORM="darwin-universal" ;;
  *)
    echo "❌ 不支持的平台: $OS-$ARCH" >&2
    echo "   请手动从 https://github.com/gohugoio/hugo/releases/tag/v${HUGO_VERSION} 下载 hugo_extended_${HUGO_VERSION}_${PLATFORM}.tar.gz" >&2
    exit 1
    ;;
esac

TARBALL="hugo_extended_${HUGO_VERSION}_${PLATFORM}.tar.gz"
URL="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${TARBALL}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ 下载 Hugo v${HUGO_VERSION} ($PLATFORM)..."
curl -fsSL "$URL" -o "$TMP/$TARBALL"

echo "→ 解压到 .tools/hugo158..."
tar -xzf "$TMP/$TARBALL" -C "$TMP"
mv "$TMP/hugo" "$DEST"
chmod +x "$DEST"

VER=$("$DEST" version | head -1)
echo "✓ 已安装：$VER"
echo "  路径：$DEST"