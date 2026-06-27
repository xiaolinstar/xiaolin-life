#!/usr/bin/env bash
# 将 Bucket 根目录 legacy 对象复制到 COS_PREFIX 下（不删除源对象，便于回滚）。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"
cos_load_dotenv "$ROOT"
cos_load_config

ALIAS="$COS_BUCKET_ALIAS"
PREFIX="${COS_PREFIX:-life}"
PREFIX="${PREFIX#/}"
PREFIX="${PREFIX%/}"

if ! command -v coscli >/dev/null 2>&1; then
  echo "Error: coscli 未安装" >&2
  exit 1
fi

echo "== COS 前缀迁移（复制） =="
echo "Bucket: cos://${ALIAS}/"
echo "目标前缀: ${PREFIX}/"
echo

copy_dir() {
  local name="$1"
  local src="cos://${ALIAS}/${name}/"
  local dst="cos://${ALIAS}/${PREFIX}/${name}/"
  if ! coscli ls "cos://${ALIAS}/${name}/" >/dev/null 2>&1; then
    echo "Skip missing dir: ${name}/"
    return 0
  fi
  echo "→ sync ${name}/ → ${PREFIX}/${name}/"
  coscli sync "$src" "$dst" -r
}

copy_file() {
  local name="$1"
  local src="cos://${ALIAS}/${name}"
  local dst="cos://${ALIAS}/${PREFIX}/${name}"
  if ! coscli ls "$src" >/dev/null 2>&1; then
    echo "Skip missing file: ${name}"
    return 0
  fi
  echo "→ cp ${name} → ${PREFIX}/${name}"
  coscli cp "$src" "$dst"
}

for dir in img-blogger img-email-thunderbird img-mac img-markdown \
  img-table-game-guandan img-undercover img-upgrade; do
  copy_dir "$dir"
done

copy_file "ai-dialectic-moon-egg.png"

echo
echo "Done. 验证: COS_PREFIX=${PREFIX} pnpm run media:cdn-check"
