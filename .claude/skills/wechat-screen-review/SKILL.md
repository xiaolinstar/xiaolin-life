---
name: wechat-screen-review
description: |
  仅在用户明确要求「生成微信公众号文章 / 导出公众号 HTML / 出公众号发布包」时启用：
  把 content/screen/ 影评 Markdown 渲染为 docs/wechat/ 可复制发布包（标题/摘要/正文/封面）。
  默认只改站点文章时禁止调用本 skill，也禁止主动跑 wechat_screen_review.py 或手写公众号 HTML。
  触发词示例：生成公众号、导出微信、公众号 HTML、发布包、粘贴到公众号。
  非触发：改影评、改 draft、补图、站点预览、commit——只编辑 content/screen/。
---

# WeChat Screen Review

光影人生影评 → 微信公众号发布包。方法论全文见 [docs/WECHAT-SCREEN-REVIEW.md](../../../docs/WECHAT-SCREEN-REVIEW.md)。

## 硬门禁（必读）

| 用户意图 | 做法 |
| --- | --- |
| 改站点影评 / 预览 / 配图 / 提交 | **不要**读本 skill 流程，**不要**渲染 HTML |
| 明确说生成公众号文章 / 导出 HTML / 出发布包 | 才执行下方流程；**必须重新跑脚本**，禁止复用旧 HTML |

模糊时先问一句：「是要改站点，还是要导出公众号 HTML？」在未确认前不渲染。

## 源与导出同步（防脏包）

失败模式：`A.md` 曾导出 `A.html`，后来 MD 改成 B 内容，却仍提交/粘贴旧 `A.html`。

对策：

1. **生成物不进 Git**：`docs/wechat/<slug>.html` 与 `*-cover.*` 已 gitignore；仓库只留脚本 + 模板 + 方法论。
2. **每次导出都全量重渲**：即使用户说「再用上次的包」，也先跑脚本覆盖 HTML。
3. **粘贴前可审查**：

   ```bash
   python3 scripts/wechat_screen_review.py content/screen/<slug>/index.md --check
   ```

   若 MD（或 `featured.jpg`）比 HTML 新 → exit 1，提示 STALE，必须先重导出。
4. **改完 MD 后若用户接着说发公众号**：提醒「源已变，先重渲再复制」；不要直接打开旧 HTML。
5. **用户若强行 `git add docs/wechat/*.html`**：警告并劝阻；只提交工具链，不提交发布包。

## 工具

```bash
# 导出（总是覆盖）
python3 scripts/wechat_screen_review.py content/screen/<slug>/index.md \
  --title '《片名》：观点句'

# 仅检查是否过期
python3 scripts/wechat_screen_review.py content/screen/<slug>/index.md --check
```

产出（本地，不入库）：

- `docs/wechat/<slug>.html`
- `docs/wechat/<slug>-cover.jpg`

入库白名单：`docs/wechat/screen-review-template.html`、`docs/wechat/.gitkeep`

## 标准流程（仅明确导出时）

1. 确认 `content/screen/<slug>/index.md` 已是要发的版本。
2. 确认公众号标题：**《片名》：观点句**。
3. **重跑**导出命令（不要手改旧 HTML）。
4. 可选再跑 `--check`，确认 `fresh`。
5. 打开 HTML：复制标题 → 摘要 → 正文；封面用同目录 `*-cover.jpg`。
6. 不主动 commit 发布包；用户要求提交时只带 skill / 脚本 / 文档。

## 字段约定

| 公众号字段 | 来源 |
| --- | --- |
| 标题 | `--title`（观点向，含片名） |
| 摘要 | front matter `summary`（缺则 `description`） |
| 封面 | 站点 `featured.jpg` → `docs/wechat/<slug>-cover.jpg` |
| 正文 | 栏目「光影人生」+《站内 title》+ 信息/评分/影评；**不**再贴公众号主标题 |

## 禁止

- 只改影评时生成或更新公众号 HTML
- 复用旧 HTML「省一步」
- 把 `docs/wechat/<slug>.html` / `*-cover.*` 提交进仓库
- 饮品 / 生活 / 办公走本 skill

## 验证

- 导出后 `--check` 为 fresh
- 发布包含「复制标题 / 复制摘要 / 复制正文」
- `git status` 不应把 `<slug>.html` / `*-cover.jpg` 列为待提交（已被 ignore）
