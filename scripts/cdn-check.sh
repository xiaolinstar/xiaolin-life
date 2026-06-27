#!/usr/bin/env bash
# 校验 CDN 域名是否可访问，并与 COS 直链对比状态码。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"
cos_load_dotenv "$ROOT"
cos_load_config

CDN="${MEDIA_CDN_BASE:-https://media.xiaolin.fun}"
CDN="${CDN%/}"
COS="${COS_PUBLIC_BASE_URL:-https://media-1300240022.cos.ap-nanjing.myqcloud.com}"
COS="${COS%/}"
P="${COS_PREFIX:-life}"

SAMPLES=(
  "${P}/img-email-thunderbird/thunderbird-lookup.png"
  "${P}/entertainment/gulou-riverfront/01-nanjing-marathon.jpg"
  "${P}/img-table-game-guandan/joker.webp"
)

echo "== CDN 检查 =="
echo "CDN:  $CDN"
echo "COS:  $COS"
echo "前缀: $P"
echo

check_url() {
  local label="$1" url="$2"
  local code err
  err=$(curl -s -o /dev/null -w '%{http_code}' -I --max-time 15 "$url" 2>&1) || true
  code="${err: -3}"
  if [[ "$code" == "200" || "$code" == "206" ]]; then
    echo "✓ $label  $code  $url"
    return 0
  fi
  if [[ "$url" == https://* ]]; then
    local http_url="${url/https:/http:}"
    local http_code
    http_code=$(curl -s -o /dev/null -w '%{http_code}' -I --max-time 15 "$http_url" 2>/dev/null || echo "000")
    if [[ "$http_code" == "200" || "$http_code" == "206" ]]; then
      echo "△ $label  HTTPS 未就绪（${code:-SSL 错误}），HTTP 已通 200"
      return 2
    fi
  fi
  echo "✗ $label  ${code:-000}  $url"
  return 1
}

failed=0
https_pending=0

echo "== 抽样 URL =="
for key in "${SAMPLES[@]}"; do
  check_url "COS" "$COS/$key" || failed=1
  rc=0
  check_url "CDN" "$CDN/$key" || rc=$?
  if [[ $rc -eq 2 ]]; then https_pending=1; elif [[ $rc -ne 0 ]]; then failed=1; fi
  echo
done

if [[ $failed -eq 0 && $https_pending -eq 1 ]]; then
  echo "CDN 回源正常（前缀 ${P}/），HTTPS 待部署。"
  exit 2
fi

if [[ $failed -eq 0 ]]; then
  echo "CDN 就绪（前缀 ${P}/）。"
else
  echo "存在失败项。"
  exit 1
fi