# 121 同机：Gateway + xiaolin-life + ai-todo

> 日期：2026-11-11  
> 目标机：`121.199.175.147`  
> 回退 tag：`deploy/121-direct-tls-pre-gateway`（已 push）

## 建议拓扑

```text
Internet → nginx-gateway :80/:443
              ├─ xiaolin.fun      → host.docker.internal:8080  (life)
              └─ xingxiaolin.cn   → host.docker.internal:8082  (ai-todo)
```

同机反代用 `host.docker.internal`（gateway `extra_hosts: host-gateway`），对应宿主机上的 **`0.0.0.0:8080` / `:8082` 发布**，不是容器内的 `127.0.0.1`。

**不要**写成 `"127.0.0.1:8080:80"`：只监听回环时，从网桥 IP 进来的 gateway 流量到不了。  
**要**写成 `"8080:80"`，并在阿里云安全组**不要对公网放行 8080/8082**（仅 80/443 对外）。

---

## 谁做什么

| 类型 | 谁 | 例子 |
|------|-----|------|
| **模板化 / 可重复** | GitHub Actions CD | life `backend_mode`；gateway `colocate_121`；合入 conf/compose |
| **一次性 / 有密钥或机器状态** | **你手动** | 拷证书、改 Secrets 主机、DNS、切流窗口顺序、备份 |

---

## A. 仓库侧（已落地 / 合入后走 CI·CD）

### A1. xiaolin-life（本仓）

| 产物 | 作用 |
|------|------|
| `compose.yaml` | 回退用：直绑宿主机 80/443（须先停 gateway） |
| `compose.behind-gateway.yaml` | **现网默认**：`8080:80`（供 gateway 经 host.docker.internal 访问），无容器 TLS |
| `volumes/website/default.behind-gateway.conf` | 对 gateway 提供 HTTP |
| CD `backend_mode` | 自动 CD + 手动默认均为 **`behind-gateway`**；`direct-tls` 仅作回退 |

切流完成后勿再把自动 CD 设回 `direct-tls`，否则会与 gateway 抢 80/443 并部署失败/留下旧容器。

### A2. xiaolin-gateway

| 产物 | 作用 |
|------|------|
| `app/xiaolin-life/xiaolin-life.conf` | vhost + upstream `:8080` |
| `app/ai-todo/ai-todo.121.overlay` | 121 上 ai-todo → `:8082` |
| `docker-compose.121.yml` | 挂载 121 overlay |
| `docker-compose.yml` | `extra_hosts` + life 证书 volume |
| `scripts/prepare-certs.sh` | CI / 占位证书含 life |
| CD `colocate_121` | 是否带上 `docker-compose.121.yml` |
| CD `skip_party_helper_precheck` | 新机首次起 gateway 时可跳过 |
| `routing-registry.md` / `uptime.yml` | 注册 life 探活 |

> 合入 gateway 后，**当前 gateway 生产机**（多半是 101）首次 CD 会 `prepare-certs` 占位 life 证书，避免 `nginx -t` 失败。xiaolin.fun DNS 仍指 121 时，101 上的 life vhost 不会接到公网流量。

---

## B. 你手动执行（一次性）

按顺序；标了「CD」的用 Actions，其余 SSH/控制台。

### B0. 回退靠什么（一般不必再「整包备份」）

| 内容 | 是否要额外备份 | 说明 |
|------|----------------|------|
| `compose.yaml` / nginx conf / 镜像 tag | **否** | Git 已管；回退用 tag `deploy/121-direct-tls-pre-gateway` + CD `direct-tls` |
| `volumes/website/certs/` | **仅当**还没拷进 gateway 时建议留一份 | 证书不进 Git；拷到 `xiaolin-gateway/app/xiaolin-life/cert/` 后，回退可从该目录再拷回 |
| 服务器 `.env` / 密钥 | 按需 | 与本次 life 静态站无关则跳过 |

结论：**配置与静态站点内容不需要再做 121 本地备份**；B1 把真证书放进 gateway 仓路径即可。

### B1. 121 准备 gateway 仓与真实证书

```bash
ssh ecs-user@121.199.175.147
mkdir -p ~/AgentProjects && cd ~/AgentProjects
test -d xiaolin-gateway || git clone git@github.com:xiaolinstar/xiaolin-gateway.git
cd xiaolin-gateway && git fetch && git checkout main && git pull --ff-only

# 从现网 life 证书复制（文件名对齐 conf）
mkdir -p app/xiaolin-life/cert
cp ~/AgentProjects/xiaolin-life/volumes/website/certs/xiaolin.fun_bundle.crt app/xiaolin-life/cert/
cp ~/AgentProjects/xiaolin-life/volumes/website/certs/xiaolin.fun.key app/xiaolin-life/cert/
chmod 600 app/xiaolin-life/cert/xiaolin.fun.key

# ai-todo 证书：按 ai-todo 迁 121 文档放到 app/ai-todo/cert/
# 其他业务证书：若本机要承接原 101 全部域名，再从 101 同步 app/*/cert/
```

- [ ] B1 life 证书已在 gateway 仓路径  
- [ ] B1 ai-todo 证书就绪（若本窗口同时切 ai-todo）  

### B2. 合入并确认 CI

- [ ] B2.1 push / merge **xiaolin-life**（behind-gateway 文件 + CD 输入）→ CI 绿  
- [ ] B2.2 push / merge **xiaolin-gateway**（life vhost 等）→ CI `nginx -t` 绿  
- [ ] B2.3 （可选）在 **现网 gateway 主机** 跑一次 gateway CD（`colocate_121=false`），确认占位证书后 reload 成功  

### B3. 切流窗口（121）— 短中断

**3.1 CD：life → behind-gateway**

GitHub → `xiaolin-life` → Actions → **CD Pipeline** → Run workflow：

- `backend_mode`: **`behind-gateway`**  
- branch: `main`  

验收：

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/healthz   # 204（宿主机访问）
# 从 gateway 网络视角也应通（可选）：
docker exec nginx-gateway wget -qO- http://host.docker.internal:8080/healthz || true
ss -ltnp | grep -E ':80 |:443 |:8080'   # life 占 8080；80/443 留给 gateway
```

- [ ] B3.1 life 发布为 `0.0.0.0:8080`（不是 127.0.0.1-only）  

**3.2 手动：启动 / 切换 gateway 占 443**

若 gateway **第一次**在 121 起：

```bash
cd ~/AgentProjects/xiaolin-gateway
# 准备 .env / .env.production（可从 101 拷模板，改端口相关）
cp -n .env.example .env
touch .env.production
# 建议：
# COMPOSE_FILE=docker-compose.yml:docker-compose.121.yml:observability-compose.yml

docker compose --env-file .env --env-file .env.production \
  -f docker-compose.yml -f docker-compose.121.yml up -d
docker exec nginx-gateway nginx -t
curl -fsS -o /dev/null -w '%{http_code}\n' \
  --resolve xiaolin.fun:443:127.0.0.1 https://xiaolin.fun/healthz
```

若以后 gateway CD 的 `SERVER_HOST` 已改成 121，则改用 Actions：

- `colocate_121`: **true**  
- 首次可 `skip_party_helper_precheck`: **true**（若本机尚未同步 party 证书）  

- [ ] B3.2 `https://xiaolin.fun/healthz` 本机 resolve 通过  

**3.3 ai-todo**（按 ai-todo 迁 121 文档）

- [ ] B3.3.1 API `8082` 健康  
- [ ] B3.3.2 gateway 已用 121 overlay  
- [ ] B3.3.3 DNS `xingxiaolin.cn` → 121（控制台，一次性）  
- [ ] B3.3.4 跑 cutover-verify 脚本  

**3.4 公网总验收**

- [ ] `https://xiaolin.fun/`、`/healthz`  
- [ ] `https://www.xiaolin.fun/healthz`（若解析存在）  
- [ ] ai-todo 探活  

### B4. 可选收尾（模板化）

- [ ] B4.1 将 gateway 仓库 GitHub Secret `SERVER_HOST` 改为 `121.199.175.147`（若整体迁 gateway）— **Secrets 控制台，手动**  
- [ ] B4.2 之后 gateway 发版只用 CD；`colocate_121=true` 写进 `.env.production` 的 `COMPOSE_FILE` 后，自动 CD 也会带 overlay  
- [ ] B4.3 腾讯 101 旧 gateway：验收稳定后再停（手动）  

---

## C. 回退

```bash
# 121：停 gateway，恢复 life 直绑
cd ~/AgentProjects/xiaolin-gateway && docker compose down

cd ~/AgentProjects/xiaolin-life
git fetch origin tag deploy/121-direct-tls-pre-gateway
git checkout deploy/121-direct-tls-pre-gateway
# 或 CD：backend_mode=direct-tls + 对应 SHA
export WEBSITE_IMAGE_TAG=main   # 或当时 sha-
docker compose -f compose.yaml up -d
bash scripts/wait-healthy.sh
```

---

## D. 推荐执行节奏

```text
1) 合入两仓（A）→ CI 绿
2) 你做 B1（121 上 gateway + 真证书；配置回退靠 Git tag）
3) 切流日：B3.1 CD behind-gateway → B3.2 起 gateway → B3.3 ai-todo/DNS
4) B4 视情况改 Secrets / 下线 101
```
