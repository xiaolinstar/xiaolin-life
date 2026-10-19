#!/usr/bin/env bash
# 安装 .hugo-version 指定的 Extended 版本；HUGO_VERSION 可用于独立兼容验证。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HUGO_VERSION="${HUGO_VERSION:-$(tr -d '[:space:]' < "${ROOT}/.hugo-version")}"
if [[ ! "${HUGO_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "无效 Hugo 版本：${HUGO_VERSION}" >&2
  exit 1
fi
TOOLS_DIR="${ROOT}/.tools"
DEST="${TOOLS_DIR}/hugo-${HUGO_VERSION}"
verify_version() {
  local version
  version="$("$1" version)"
  if [[ "$version" != "hugo v${HUGO_VERSION}-"* && "$version" != "hugo v${HUGO_VERSION}+"* && "$version" != "hugo v${HUGO_VERSION} "* ]]; then
    echo "下载的 Hugo 版本不匹配：$version" >&2
    return 1
  fi
  [[ "$version" == *"+extended"* ]]
}
if [[ "${1:-}" == "--check" ]]; then
  [[ -x "${DEST}" ]] && verify_version "${DEST}" || { echo "请安装 Hugo Extended ${HUGO_VERSION}" >&2; exit 1; }
  "${DEST}" version
  exit 0
fi

if [[ -x "${DEST}" ]] && verify_version "${DEST}"; then
  "${DEST}" version
  exit 0
fi

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "${OS}-${ARCH}" in
  darwin-arm64|darwin-x86_64) PLATFORM="darwin-universal"; EXT="pkg" ;;
  linux-x86_64|linux-amd64) PLATFORM="linux-amd64"; EXT="tar.gz" ;;
  linux-aarch64|linux-arm64) PLATFORM="linux-arm64"; EXT="tar.gz" ;;
  *) echo "不支持的平台：${OS}-${ARCH}" >&2; exit 1 ;;
esac
ASSET="hugo_extended_${HUGO_VERSION}_${PLATFORM}.${EXT}"
BASE="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"
INSTALL_TMP="$(mktemp -d)"
trap 'rm -rf "${INSTALL_TMP}"' EXIT
mkdir -p "${TOOLS_DIR}"
echo "下载 Hugo Extended ${HUGO_VERSION}（${PLATFORM}）…"
curl --retry 2 --connect-timeout 15 --speed-limit 1024 --speed-time 60 -fsSL "${BASE}/${ASSET}" -o "${INSTALL_TMP}/${ASSET}"
curl --retry 2 --connect-timeout 15 --speed-limit 1024 --speed-time 60 -fsSL "${BASE}/hugo_${HUGO_VERSION}_checksums.txt" -o "${INSTALL_TMP}/checksums.txt"
EXPECTED="$(awk -v asset="${ASSET}" '$2 == asset {print $1}' "${INSTALL_TMP}/checksums.txt")"
[[ -n "${EXPECTED}" ]] || { echo "官方校验清单缺少 ${ASSET}" >&2; exit 1; }
if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL="$(sha256sum "${INSTALL_TMP}/${ASSET}" | awk '{print $1}')"
else
  ACTUAL="$(shasum -a 256 "${INSTALL_TMP}/${ASSET}" | awk '{print $1}')"
fi
[[ "${ACTUAL}" == "${EXPECTED}" ]] || { echo "SHA256 校验失败" >&2; exit 1; }
if [[ "${EXT}" == "pkg" ]]; then
  # 只解包至临时目录，不运行系统安装器或申请管理员权限。
  pkgutil --expand-full "${INSTALL_TMP}/${ASSET}" "${INSTALL_TMP}/expanded"
  BINARIES="$(find "${INSTALL_TMP}/expanded" -type f -name hugo)"
  [[ "$(printf '%s\n' "${BINARIES}" | wc -l | tr -d ' ')" == 1 ]] || { echo "安装包中 Hugo 路径不唯一" >&2; exit 1; }
  BINARY="${BINARIES}"
else
  tar -xzf "${INSTALL_TMP}/${ASSET}" -C "${INSTALL_TMP}" hugo
  BINARY="${INSTALL_TMP}/hugo"
fi
chmod +x "${BINARY}"
verify_version "${BINARY}"
# 同目录临时文件保证替换完整，运行中的开发服务仍可继续使用原二进制。
cp "${BINARY}" "${DEST}.new"
chmod +x "${DEST}.new"
mv "${DEST}.new" "${DEST}"
"${DEST}" version
echo "已安装到 ${DEST}"
