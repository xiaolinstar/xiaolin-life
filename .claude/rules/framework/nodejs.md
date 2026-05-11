---
alwaysApply: true
globs:
  - "package.json"
  - "pnpm-lock.yaml"
  - "yarn.lock"
  - "package-lock.json"
---

# Node.js 项目规则

- **优先使用 pnpm**：React、Vue 等项目默认使用 pnpm
- 安装依赖：`pnpm install`，添加依赖：`pnpm add <package>`（生产）、`pnpm add -D <package>`（开发）
- 运行脚本：`pnpm run <script>` 或 `pnpm <script>`
- 优先使用 `pnpm-lock.yaml`，提交前确保更新
- CI/CD 使用 `pnpm install --frozen-lockfile` 确保一致性
