---
name: origin-distribute
description: 通用 origin → 社媒分发的占位 skill（生活/办公文章场景）。饮品 plog 分发请走 drinkzen skill 的 social 子模块。触发词：同步、分发、适配小红书、xhs 推文、社媒版（仅限生活/办公文章）。
allowed-tools: 
license: MIT
metadata:
  version: "0.1.0"
  author: xiaolin
  tags: ["origin-distribute", "placeholder", "social-media"]
  status: placeholder  # 占位 skill，待生活/办公文章分发需求出现时启用
---

# origin-distribute（占位）

通用 origin → 社媒分发的占位 skill。当前**未启用**——饮品场景已迁到 drinkzen/social，生活/办公文章暂未触达分发需求。

## 何时启用

当出现以下场景时启用本 skill：

- 生活文章（content/life/）需要同步到小红书 / 微博
- 办公文章（content/office/）需要生成推文版
- 任意非饮品类 origin 需要做平台适配

启用步骤：

1. 在本目录创建 `references/` 子目录
2. 编写通用 origin 模板（不同于 plog，不含 Nutri-Grade / 饮品参数）
3. 更新 frontmatter `metadata.status: placeholder` → `active`
4. 移动本 skill 到 drinkzen 同级目录（如必要）

## 当前状态

```yaml
metadata:
  status: placeholder  # 占位
```

**请勿在饮品场景使用本 skill**——所有饮品社媒分发请走 `drinkzen` skill 的 social 子模块（`references/README.md`）。

## 占位原因

1. 饮品场景已独立到 drinkzen（更适合深耕）
2. 生活/办公文章当前未触达分发需求
3. 通用模板未编写（避免过早抽象）