# drinkzen-admin product 命令需求

## 背景

当前 drinkzen-admin CLI (v0.4.0) 支持品牌和菜单模板管理，但缺少产品（饮品）管理能力。

**设计原则**：

- CLI 是纯软件工程工具，不涉及 AI/Agent
- 输入来自结构化 JSON 文件，不解析 markdown
- 提供基本 CRUD 操作，简单直接

---

## 核心命令设计

### 1. product list — 查询产品列表

```bash
drinkzen-admin product list --brand MannerCoffee --json
drinkzen-admin product list --brand MannerCoffee --search "拿铁" --json
drinkzen-admin product list --brand MannerCoffee --active-only --json
```

**API**：`GET /api/admin/products?brand_id={}&search={}&active_only={}`

---

### 2. product show — 查询产品详情

```bash
drinkzen-admin product show product-xxx --json
```

**API**：`GET /api/admin/products/{id}`

---

### 3. product create — 创建产品

从 JSON 文件创建产品。

```bash
drinkzen-admin product create --from product-data.json --dry-run --json
drinkzen-admin product create --from product-data.json
```

**product-data.json 格式**：

```json
{
  "brand_id": "brand-aefb9db3c355",
  "name": "拿铁",
  "english_name": "Latte",
  "default_price": 20,
  "menu_options": {
    "source": "official-miniapp",
    "collected_at": "2026-10-11",
    "option_groups": [
      {
        "key": "size",
        "label": "规格",
        "values": ["大热杯 355ml", "小热杯 237ml"],
        "selectionType": "single",
        "defaultValues": ["大热杯 355ml"]
      }
    ]
  }
}
```

**API**：`POST /api/admin/products`

---

### 4. product update — 更新产品

```bash
# 从 JSON 文件更新
drinkzen-admin product update product-xxx --from product-data.json --dry-run --json

# 直接传参数更新
drinkzen-admin product update product-xxx --name "经典拿铁" --price 22 --dry-run --json
```

**API**：`PATCH /api/admin/products/{id}`

---

### 5. product delete — 删除产品

```bash
drinkzen-admin product delete product-xxx --dry-run --json
drinkzen-admin product delete product-xxx
```

**API**：`DELETE /api/admin/products/{id}`

---

## 安全约束

1. **默认 dry-run**：写入操作先 `--dry-run --json` 预览
2. **变更确认**：展示变更后，用户确认才执行
3. **删除保护**：删除操作需二次确认

---

## 实现优先级

| 优先级 | 命令 | 理由 |
|---|---|---|
| P0 | product list | 基础查询 |
| P0 | product show | 查看详情 |
| P1 | product create | 创建产品 |
| P1 | product update | 更新产品 |
| P2 | product delete | 删除产品（低频） |

---

## 后端 API 需求

| 方法 | 端点 | 说明 |
|---|---|---|
| GET | `/api/admin/products` | 产品列表 |
| GET | `/api/admin/products/{id}` | 产品详情 |
| POST | `/api/admin/products` | 创建产品 |
| PATCH | `/api/admin/products/{id}` | 更新产品 |
| DELETE | `/api/admin/products/{id}` | 删除产品 |

---

## 工作流集成

CLI 只负责基本 CRUD。数据准备（从 Hugo 页面提取营养数据等）由 Agent 或人工完成，生成 JSON 后交给 CLI。

```bash
# 1. Agent 或人工准备 product-data.json
# 2. CLI 创建产品
drinkzen-admin product create --from product-data.json --dry-run
drinkzen-admin product create --from product-data.json

# 3. 营养数据由后台 UI 录入，或后续扩展 nutrition.json 支持
```
