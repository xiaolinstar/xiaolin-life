# Section 归类参考

`content/` 下的有效 section（按现有项目结构）：

| Section | 适用场景 | 关键词（推荐命中）|
|---|---|---|
| `life/entertainment` | 电影、剧、演出、夜跑、KTV | 电影 / 剧 / 夜跑 / 演唱会 / 密室 |
| `life/thoughts` | 随笔、感悟、日记、心情 | 随笔 / 感悟 / 思考 / 心情 / 回忆 |
| `life/media` | 书、影评、乐评、读书笔记 | 书 / 读书 / 影评 / 乐评 / 看完 |
| `life/notes` | 摘录、清单、学习笔记 | 笔记 / 摘录 / 清单 / 学习 |
| `office/tools` | 工具、效率软件、插件 | 工具 / 效率 / 软件 / App / 插件 |
| `office/workflow` | 工作流、流程、方法 | 流程 / 工作流 / SOP / 技巧 |
| `office/experience` | 远程、会议、团队、SRE、运维 | 办公 / 远程 / 会议 / SRE / 部署 |

## 关键词推荐规则

`scripts/new_article.py` 启动时如果用户**没指定** `path`：

1. 扫描 title 命中关键词
2. 命中多个时按命中数排序，取最高
3. 无命中默认推荐 `life/thoughts`

## 决策边界

- **饮品相关** → 走 [drinkzen](../drinkzen/SKILL.md) skill（**不归** article-create 管）
- **关于页** → 手动维护（`content/about/`）
- **其它** → article-create 处理

## 实际目录示例

```text
content/
├── drinkzen/        # 饮品（drinkzen skill）
├── life/
│   ├── entertainment/
│   ├── thoughts/
│   ├── media/
│   └── notes/
├── office/
│   ├── tools/
│   ├── workflow/
│   └── experience/
└── about/           # 关于页（手动）
```
