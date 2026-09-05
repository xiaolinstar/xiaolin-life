---
description: Claude Code 专有规则（Git 提交策略）
globs:
alwaysApply: true
---

@AGENTS.md

# Claude 专有规则

> 中文输出与排版规范由 `.claude/rules/core.md` 自动加载（alwaysApply: true），不在此重复。

## Git 提交规则

> 所有的文件更新、创建、删除操作都要触发该规则

- **禁止自动提交 git**：除非用户明确要求提交，否则不要执行 git commit、git add 等操作。
- 如果需要提交，先询问用户是否确认提交，提供变更摘要供用户确认。
