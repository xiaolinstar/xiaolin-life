#!/usr/bin/env bash
# 从 coscli 配置文件（默认 ~/.cos.yaml）读取 Bucket 信息；环境变量优先。
# 可选：仓库根目录 .env（COS_PREFIX、MEDIA_CDN_BASE 等）

cos_load_dotenv() {
  local root="${1:-}"
  if [[ -z "$root" ]]; then
    root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  fi
  if [[ -f "$root/.env" ]]; then
    # 只填充未设置的变量，保证「环境变量优先」
    local key value
    while IFS='=' read -r key value; do
      [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
      if [[ -z "${!key:-}" ]]; then
        export "$key=$value"
      fi
    done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$root/.env")
  fi
}

cos_config_path() {
  printf '%s\n' "${COS_CONFIG_PATH:-$HOME/.cos.yaml}"
}

_cos_yaml_bucket_name() {
  awk '/^[[:space:]]+- name:/ { gsub(/"/, "", $3); print $3; exit }' "$1"
}

_cos_yaml_first_field() {
  local field="$1" file="$2"
  awk -v field="$field" '
    BEGIN { inbucket = 0 }
    /^[[:space:]]+- name:/ { inbucket = 1; next }
    inbucket && $1 == (field ":") {
      $1 = ""; sub(/^ /, "")
      gsub(/"/, "")
      print
      exit
    }
  ' "$file"
}

# 加载 COS_BUCKET_ALIAS、COS_BUCKET_NAME、COS_ENDPOINT、COS_REGION、COS_PUBLIC_BASE_URL
cos_load_config() {
  local config
  cos_load_dotenv
  config="$(cos_config_path)"

  if [[ -z "${COS_BUCKET_NAME:-}" || -z "${COS_BUCKET_ALIAS:-}" || -z "${COS_ENDPOINT:-}" ]]; then
    if [[ ! -f "$config" ]]; then
      echo "Error: 未找到 coscli 配置: $config（请先执行 coscli config init）" >&2
      return 1
    fi

    if [[ -z "${COS_BUCKET_NAME:-}" ]]; then
      COS_BUCKET_NAME="$(_cos_yaml_bucket_name "$config")"
    fi
    if [[ -z "${COS_BUCKET_ALIAS:-}" ]]; then
      COS_BUCKET_ALIAS="$(_cos_yaml_first_field alias "$config")"
      COS_BUCKET_ALIAS="${COS_BUCKET_ALIAS:-$COS_BUCKET_NAME}"
    fi
    if [[ -z "${COS_ENDPOINT:-}" ]]; then
      COS_ENDPOINT="$(_cos_yaml_first_field endpoint "$config")"
    fi
    if [[ -z "${COS_REGION:-}" ]]; then
      COS_REGION="$(_cos_yaml_first_field region "$config")"
    fi
  fi

  if [[ -z "${COS_BUCKET_ALIAS:-}" ]]; then
    echo "Error: 无法从 $config 解析 Bucket alias" >&2
    return 1
  fi

  if [[ -z "${COS_PUBLIC_BASE_URL:-}" && -n "${COS_BUCKET_NAME:-}" && -n "${COS_ENDPOINT:-}" ]]; then
    COS_PUBLIC_BASE_URL="https://${COS_BUCKET_NAME}.${COS_ENDPOINT}"
  fi

  # xiaolin-life 默认 life；xiaolin-dcos 在 .env 设 COS_PREFIX=docs
  export COS_PREFIX="${COS_PREFIX:-life}"

  export COS_BUCKET_ALIAS COS_BUCKET_NAME COS_ENDPOINT COS_REGION COS_PUBLIC_BASE_URL COS_PREFIX
}
