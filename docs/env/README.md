# xiaolin-life 环境变量

真源分层见 [dev-standards env-management](https://github.com/xiaolinstar/dev-standards/blob/main/playbook/env-management.md)。

## 本仓库特点（内容站 + 媒体脚本）

站点容器 **不读** `.env`；`.env` 供本机 **COS 上传 / CDN 校验脚本** 使用。COS 凭证在 **`~/.cos.yaml`**（方案 A），不进入 `.env`。

| 层 | 放什么 | 路径 |
|----|--------|------|
| L0 模板 | `COS_PREFIX`、`MEDIA_CDN_BASE` 等 | `.env.example` |
| L3 凭证 | SecretId / SecretKey | **`~/.cos.yaml`**（coscli） |
| L3 本机 | 前缀、CDN、可选 bucket 覆盖 | 仓库根 `.env` |
| L3 VPS | 无 | `compose.yaml` 仅 `TZ`，upstream **8081** |

**VPS 上不应存在 `.env`**（已确认无文件即达标）。COS 凭证仅本机 `~/.cos.yaml`。
| L3 备份 | 本机 `.env` 快照 | `~/.config/xiaolinstar/xiaolin-life/local.env` |

**不要**把 `COS_SECRET_ID` / `COS_SECRET_KEY` 写进 `.env` 或 commit。

## 脚本加载顺序

`scripts/lib/cos-config.sh`：

1. `source` 仓库 `.env`（若有）
2. 读取 `~/.cos.yaml` 补全 bucket / endpoint
3. 默认 `COS_PREFIX=life`

验证：

```bash
set -a && source .env && set +a
./scripts/cos-check.sh
pnpm run media:cdn-check   # 若已配置
```

## 键名校验

```bash
~/AgentProjects/dev-standards/scripts/sync.sh env check --project .
~/AgentProjects/dev-standards/scripts/sync.sh env check \
  --project . --local --env local --strict
```

## 备份示例

```bash
cp .env ~/.config/xiaolinstar/xiaolin-life/local.env
chmod 600 ~/.config/xiaolinstar/xiaolin-life/local.env
# COS 凭证仍在 ~/.cos.yaml，需单独备份 coscli 配置
```

## Agent 禁区

禁止 Agent 修改 `.env`、`~/.cos.yaml` 与 `~/.config/xiaolinstar/**`。

注册表：[env-registry.yaml](https://github.com/xiaolinstar/dev-standards/blob/main/playbook/env-registry.yaml) §xiaolin-life。

更多媒体流程见 [docs/MEDIA-NAMESPACE.md](../MEDIA-NAMESPACE.md)。
