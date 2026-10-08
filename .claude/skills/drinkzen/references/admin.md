# DrinkZen 平台同步

通过 `drinkzen-admin` CLI 把 Hugo 数据同步到 drinkzen.cn 后台，覆盖：品牌资料维护、菜单模板治理、Logo 核验、用户投稿审阅。

> ⚠️ **核心安全铁律（Safety Principles）**：
>
> 1. **默认使用 `--dry-run`**：在执行任何修改性操作（`update`, `set-logo`, `apply`, `resolve`）之前，**必须先执行带 `--dry-run` 和 `--json` 的命令**。
> 2. **人工确认防线 (Human-in-the-loop)**：Agent **不得在未获得用户显式确认前**真正执行写操作。Agent 应输出拟调用的 `drinkzen-admin` 命令及变更对比，等待用户审核批准。
> 3. **命令区别**：`drinkzen-admin` 是管理员与运营专属 CLI；普通用户侧 CLI 保留为未来扩展，**当前项目不混用**。

---

## 依赖条件与环境准备

确保系统已安装 `drinkzen-admin-cli`，并已通过配置文件或环境变量完成凭据设置：

```bash
# 方式 A：一次性持久化保存配置（推荐，文件权限自动设为 0600）
drinkzen-admin config set --set-url "https://api.drinkzen.cn" --set-token "your-admin-token"

# 方式 B：通过环境变量注入
export DRINKZEN_API_BASE_URL="https://api.drinkzen.cn"
export DRINKZEN_ADMIN_TOKEN="your-admin-token"

# 验证配置与连接
drinkzen-admin config show --json
drinkzen-admin brand list --json
```

---

## 核心命令速查表

| 领域     | 操作       | 命令格式                                               | 必备/常用参数                                                                                 |
| -------- | ---------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **配置** | 保存配置   | `drinkzen-admin config set`                            | `--set-url <url>`, `--set-token <token>`, `--json`                                            |
| **配置** | 查看状态   | `drinkzen-admin config show`                           | `--json` (脱敏展示 Token)                                                                     |
| **配置** | 路径查询   | `drinkzen-admin config path`                           | `--json`                                                                                      |
| -------- | ---------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| **品牌** | 查询列表   | `drinkzen-admin brand list`                            | `--search <keyword>`, `--active-only`, `--json`                                               |
| **品牌** | 查询详情   | `drinkzen-admin brand show <brand>`                    | `--json`                                                                                      |
| **品牌** | 更新信息   | `drinkzen-admin brand update <brand>`                  | `--name <name>`, `--alias <alias>`, `--dry-run`, `--json`                                     |
| **品牌** | 上传 Logo  | `drinkzen-admin brand set-logo <brand> <file>`         | `--confidence <verified\|high\|medium\|low>`, `--source-name`, `--source-url`, `--dry-run`    |
| **模板** | 导出模板   | `drinkzen-admin menu-template export <brand>`          | `--out <file>`, `--json`                                                                      |
| **模板** | 校验模板   | `drinkzen-admin menu-template validate <file_or_json>` | `--json`                                                                                      |
| **模板** | 应用模板   | `drinkzen-admin menu-template apply <brand> <file>`    | `--dry-run`, `--json`                                                                         |
| **审核** | 查询任务   | `drinkzen-admin review list`                           | `--status <pending\|approved\|rejected\|merged>`, `--limit <N>`, `--json`                     |
| **审核** | 查看上下文 | `drinkzen-admin review show <task_id>`                 | `--json`                                                                                      |
| **审核** | 决议任务   | `drinkzen-admin review resolve <task_id> <action>`     | `<action>: create\|merge\|supplement\|reject`, `--target-product-id`, `--reason`, `--dry-run` |

---

## Agent 操作 SOP 指南

### 剧本 1：审阅用户贡献饮品 (User Contribution Review)

当用户请求辅助处理审核中心积压的任务时，遵循以下步骤：

1. **拉取任务**：

   ```bash
   drinkzen-admin review list --status pending --json
   ```

2. **获取上下文与比对数据**：

   ```bash
   drinkzen-admin review show <task_id> --json
   ```

3. **查重与判重**：
   使用 `drinkzen-admin brand show <brand_name> --json` 检查该品牌现有饮品库，判断：
   - 若数据库中已存在同名且规格完整饮品 → 建议 `merge` 到现有饮品。
   - 若数据库中已存在该饮品但缺少当前用户提交的新规格/热量 → 建议 `supplement` 补充规格。
   - 若为品牌新上架的真实饮品 → 建议 `create` 创建新饮品。
   - 若提交信息为测试乱码、虚假饮品或违反规定 → 建议 `reject` 驳回。
4. **生成 Dry-Run 拟执行命令并提示用户**：

   ```bash
   drinkzen-admin review resolve <task_id> create --reason "经过官方菜单核实，该饮品为新增有效饮品" --dry-run --json
   ```

   **向用户展示**：
   - 任务详情与提交饮品名称。
   - 提案操作（如新建/合并）及推荐原因。
   - `dry_run` 返回的变更 JSON 结构。
   - **请求用户确认是否真正执行**。
5. **用户确认后真正执行**（去掉 `--dry-run`）：

   ```bash
   drinkzen-admin review resolve <task_id> create --reason "经过官方菜单核实，该饮品为新增有效饮品" --json
   ```

---

### 剧本 2：品牌菜单模板维护 (Menu Template Governance)

当需要为某个品牌定义或修改可选杯型、温度、甜度与小料选项时：

1. **导出当前模板**：

   ```bash
   drinkzen-admin menu-template export 霸王茶姬 --out chagee_template.json
   ```

2. **校验新模板合法性**：

   ```bash
   drinkzen-admin menu-template validate chagee_template.json --json
   ```

   _注意检查_：`optionGroups` 中每个组需具备 `key`, `label`, `values`, `selectionType` (`single` | `multiple`) 及合法 `defaultValues`。
3. **Dry-Run 变更预览**：

   ```bash
   drinkzen-admin menu-template apply 霸王茶姬 chagee_template.json --dry-run --json
   ```

4. **提交用户确认**：展示当前模板与新模板的 Diff，获得批准后再进行正式 `apply`。

---

### 剧本 3：品牌 Logo 与权属核验 (Logo Provenance)

当为品牌设置官方 Logo 资源时：

1. **核验文件格式**：确保 Logo 图像为正方形 PNG/JPEG，且具备明确的官方来源（如官方小程序、品牌官网、微信公众号）。
2. **预览上传**：

   ```bash
   drinkzen-admin brand set-logo 霸王茶姬 ./chagee.png --source-name "霸王茶姬官方小程序" --source-url "https://chagee.com" --confidence verified --dry-run --json
   ```

3. **提交用户确认后正式上传**。

---

## 营养评级与数据置信度参考

在协助用户评估数据准确性时，遵循 DrinkZen 的统一营养评级标准：

| 评级        | 热量 (Calories) | 糖分 (Sugar) | 脂肪 (Fat) |
| ----------- | --------------- | ------------ | ---------- |
| **Grade A** | < 150 kcal      | < 5 g        | < 3 g      |
| **Grade B** | < 250 kcal      | < 10 g       | < 5 g      |
| **Grade C** | < 350 kcal      | < 20 g       | < 8 g      |
| **Grade D** | ≥ 350 kcal      | ≥ 20 g       | ≥ 8 g      |

数据来源置信度标注规则：

- `verified`：品牌官方公开计算器、成分表或检验报告。
- `high`：官方菜单明确标注、官方客服提供。
- `medium`：知名第三方媒体、测评机构公开检测。
- `low` / `pending`：用户自行预估或民间草案。
