---
description: 构建“可对话“的内容仓库：博客的下一个进化方向——让博客同时服务于人类读者和 AI 智能体
---

# 构建“可对话“的内容仓库：博客的下一个进化方向

我们每天都在互联网上发表内容：博客文章、公众号推文、技术笔记。这些内容承载着我们的思考和经验，但它们的价值是否被充分利用了？

当你想让 AI 分析自己写过的东西时，是否遇到过这样的困境：AI 只能读取渲染后的 HTML 页面，无法理解原始的 Markdown 格式，更无法准确提取文章结构。

**是时候审视我们的内容资产了。**

关键词：数字资产、内容仓库、VitePress、LLM、AI 辅助写作、个人知识管理

*特别说明：本文是笔者与 AI“结对编程“式写作的产物。AI 是我的协作者，而我作为主导者，对文章质量负责。*

---

## 同一个内容，两种访问方式

传统模式下，用户访问你的文章看到的是渲染后的 HTML 页面。而对于 AI 智能体，这些 HTML 是“脏“的——充满了 JS 脚本、CSS 样式、无关的导航元素。

**现在，我们可以做得更好。**

以本文为例，你可以用两种方式访问：

- **面向人类**：[https://xiaolinstar.cn/life-nanjing/thinks/content-warehouse.html](https://xiaolinstar.cn/life-nanjing/thinks/content-warehouse.html)
- **面向 AI**：[https://xiaolinstar.cn/life-nanjing/thinks/content-warehouse.md](https://xiaolinstar.cn/life-nanjing/thinks/content-warehouse.md)

只需将 `.html` 改为 `.md`，AI 就能直接读取纯净的 Markdown 源文件。这意味着你的每一篇文章都同时服务于两个对象：人类读者和 AI 智能体。

---

## 解决方案：VitePress + vitepress-plugin-llms

实现这个功能并不复杂，我们使用 VitePress 的插件生态来完成。

### 核心工具

**[vitepress-plugin-llms](https://github.com/okineadev/vitepress-plugin-llms)** 是 VitePress 的一个插件，它可以：

- 为每个页面生成 LLM 友好的 Markdown 版本
- 生成 `llms.txt` 索引文件
- 生成 `llms-full.txt` 完整内容文件

### 适用于其他静态站点

虽然本文以 VitePress 为例，但这个方案同样适用于其他静态站点：

**Docusaurus**
```bash
npm install docusaurus-plugin-llms
```

在 `docusaurus.config.js` 中配置：
```javascript
plugins: ['docusaurus-plugin-llms'],
```

**VitePress（其他主题）**
如果使用自定义主题，只需在 `vite.config.ts` 中添加插件即可：
```typescript
import llms from 'vitepress-plugin-llms'

export default {
  vite: {
    plugins: [llms()],
  },
}
```

### 额外配置

为了让 Markdown 源文件直接在浏览器中显示，我们还需要：

- 一个构建脚本，在打包时复制 Markdown 源文件到输出目录
- Nginx 配置，正确返回 `.md` 文件的 Content-Type

---

## 实战步骤：3 分钟部署完成

### 步骤 1：安装插件

```bash
pnpm add -D vitepress-plugin-llms
```

### 步骤 2：配置 VitePress

在 `.vitepress/config.mts` 中添加插件：

```typescript
import llms from 'vitepress-plugin-llms'

export default {
  vite: {
    plugins: [llms()],
  },
}
```

### 步骤 3：配置构建脚本

创建一个脚本，在 VitePress 构建完成后复制 Markdown 源文件：

```javascript
// scripts/copy-md.js
const fs = require('fs')
const path = require('path')

function copyMdToDist() {
  // 遍历 docs 目录，复制所有 .md 文件到 dist 对应位置
  // 具体实现略
}

copyMdToDist()
```

### 步骤 4：配置 Nginx

在 Nginx 配置中添加 Markdown 文件的 MIME 类型：

```nginx
location ~* \.(md|txt)$ {
    root   /usr/share/nginx/html;
    default_type text/plain;
    charset utf-8;
}
```

### 步骤 5（可选）：页面顶部显示源文件链接

可以自定义主题组件，在每个页面顶部显示 Markdown 源文件地址：

```vue
<template>
  <div class=“markdown-source-link“>
    <span>📄 Markdown 源文件：</span>
    <a :href=“markdownUrl“ target=“_blank“>{{ fullUrl }}</a>
  </div>
</template>
```

---

## 进阶使用：给 AI IDE 的提示词模板

现在你已经完成了配置，只需要告诉 AI 如何访问你的内容仓库。以下是一个通用的提示词模板，可以在任何 AI IDE（Cursor、Trae、OpenCode 等）中使用：

```
我有一个 VitePress 站点，部署在 https://xiaolinstar.cn/
- 站点的所有 Markdown 源文件可以直接用 .md 后缀访问
- 站点索引文件位于 https://xiaolinstar.cn/llms.txt
- 完整内容文件位于 https://xiaolinstar.cn/llms-full.txt

请先了解我的内容库，然后回答我的问题。
```

**使用场景示例**：

1. **让 AI 了解你的知识体系**
   ```
   请阅读 https://xiaolinstar.cn/llms.txt，告诉我博客的主要内容领域分布
   ```

2. **让 AI 基于你的积累回答问题**
   ```
   我想写一篇关于”CI/CD 最佳实践”的文章，请先阅读 https://xiaolinstar.cn/sre/devops/cicd-01.md 等相关内容，然后给我一些建议
   ```

3. **让 AI 做你的内容策划师**
   ```
   请分析 https://xiaolinstar.cn/llms-full.txt，帮我梳理过去一年在”AI”领域写了哪些内容
   ```

**核心思路**：只需告诉 AI 你的站点地址和文件规则，它就能像访问本地文件一样访问你的内容。

---

## 总结：让你的数字资产真正”活”起来

当你把每一篇文章都以 Markdown 源文件的形式暴露给 AI，你的博客就不再只是”给人看”的静态页面，而是一个”可以与 AI 对话”的内容资产库。

你可以：

- 让 AI 基于你过往的积累回答新问题
- 让 AI 分析你的思考模式和知识体系
- 让 AI 在你已有的内容上进行二次创作
- 构建真正的”个人数字花园”，让 AI 成为你的第二大脑

**从今天开始，让你的每一篇文章都”一鱼两吃”。**
