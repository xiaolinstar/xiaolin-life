#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if command -v hugo >/dev/null 2>&1; then
  exec hugo "$@"
fi

if [[ -x "${ROOT}/.tools/hugo158" ]]; then
  exec "${ROOT}/.tools/hugo158" "$@"
fi

echo "需要 Hugo 0.158+（extended）。请安装 Hugo 或确保 .tools/hugo158 存在。" >&2
exit 1
