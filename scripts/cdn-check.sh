#!/usr/bin/env bash
# 校验 CDN 域名是否可访问，并与 COS 直链对比状态码。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=lib/cos-config.sh
source "$ROOT/scripts/lib/cos-config.sh"
cos_load_config

CDN="${MEDIA_CDN_BASE:-https://media.xiaolin.fun}"
CDN="${CDN%/}"
COS="${COS_PUBLIC_BASE_URL:-https://media-1300240022.cos.ap-nanjing.myqcloud.com}"
COS="${COS%/}"

SAMPLES=(
  "img-email-thunderbird/thunderbird-lookup.png"
  "life/entertainment/gulou-riverfront/01-nanjing-marathon.jpg"
  "img-table-game-guandan/joker.webp"
)

echo "== CDN 检查 =="
echo "CDN:  $CDN"
echo "COS:  $COS"
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
  # HTTPS 证书未部署时，腾讯云 CDN 常返回 000/514；用 HTTP 二次探测
  if [[ "$url" == https://* ]]; then
    local http_url="${url/https:/http:}"
    local http_code
    http_code=$(curl -s -o /dev/null -w '%{http_code}' -I --max-time 15 "$http_url" 2>/dev/null || echo "000")
    if [[ "$http_code" == "200" || "$http_code" == "206" ]]; then
      echo "△ $label  HTTPS 未就绪（${code:-SSL 错误}），HTTP 已通 200"
      echo "  → 请在 CDN 控制台为 media.xiaolin.fun 部署 HTTPS 证书"
      return 2
    fi
  fi
  echo "✗ $label  ${code:-000}  $url"
  return 1
}

failed=0
https_pending=0

echo "== DNS =="
if cname=$(dig +short "$CDN" CNAME 2>/dev/null | head -1); then
  if [[ -n "$cname" ]]; then
    echo "✓ CNAME ${CDN#https://} → $cname"
  else
    ip=$(dig +short "${CDN#https://}" A 2>/dev/null | head -1 || true)
    if [[ -n "$ip" ]]; then
      echo "△ A 记录 ${CDN#https://} → $ip（非 CNAME，请确认是否经 CDN）"
    else
      echo "✗ 未解析 ${CDN#https://}（请先配置 DNS CNAME）"
      failed=1
    fi
  fi
else
  echo "△ 无法 dig，跳过 DNS 检查"
fi

echo
echo "== 抽样 URL =="
for key in "${SAMPLES[@]}"; do
  check_url "COS" "$COS/$key" || failed=1
  rc=0
  check_url "CDN" "$CDN/$key" || rc=$?
  if [[ $rc -eq 2 ]]; then https_pending=1; elif [[ $rc -ne 0 ]]; then failed=1; fi
  echo
done

if [[ $failed -eq 0 && $https_pending -eq 1 ]]; then
  echo "CDN 回源正常，待部署 HTTPS 后再执行: pnpm run media:cdn-migrate:apply"
  exit 2
fi

if [[ $failed -eq 0 ]]; then
  echo "CDN 就绪。可执行: pnpm run media:cdn-migrate:apply"
else
  echo "存在失败项。请完成 docs/CDN-SETUP.md 中控制台与 DNS 配置后再试。"
  exit 1
fi
