# 技能安装指南

## 技能目录结构

本项目统一使用 `.claude/` 目录管理所有技能：

```css
.claude/
├── rules/          # 规则文件
│   └── core.md
└── skills/         # 技能文件
    ├── find-skills/
    ├── gh-cli/
    ├── git/
    ├── markdown-formatter/
    ├── nano-banana-2/
    └── wechat-article-writer/
```

## 技能来源

### 1. GitHub 技能

通过 GitHub 仓库安装的技能，记录在 `skills-lock.json`：

```json
{
  "source": "owner/repo",
  "sourceType": "github",
  "computedHash": "..."
}
```

### 2. SkillHub 技能

通过 SkillHub 安装的技能，记录在 `skills-lock.json`：

```json
{
  "name": "Skill Name",
  "zip_url": "https://lightmake.site/api/v1/download?slug=xxx",
  "source": "skillhub",
  "version": "1.0.0"
}
```

## 安装新技能

### 从 GitHub 安装

1. 下载技能到 `.claude/skills/`
2. 更新 `skills-lock.json`：

```bash
# 示例
cp -r /path/to/skill .claude/skills/skill-name
```

1. 在 `skills-lock.json` 中添加记录：

```json
{
  "skill-name": {
    "source": "owner/repo",
    "sourceType": "github",
    "computedHash": "sha256-hash"
  }
}
```

### 从 SkillHub 安装

1. 下载技能到 `.claude/skills/`
2. 更新 `skills-lock.json`：

```json
{
  "skill-name": {
    "name": "Skill Name",
    "zip_url": "https://lightmake.site/api/v1/download?slug=xxx",
    "source": "skillhub",
    "version": "1.0.0"
  }
}
```

## 技能迁移

`skills-lock.json` 保证了技能的可迁移性：

1. **克隆项目到新环境**
2. **读取 skills-lock.json** 获取所有技能信息
3. **自动下载/安装技能** 到 `.claude/skills/`

## 维护规则

1. **所有技能必须安装在 `.claude/skills/`**
2. **每次安装/更新技能后，必须更新 `skills-lock.json`**
3. **删除技能时，同步从 `skills-lock.json` 中移除**
4. **不要手动修改 `skills-lock.json` 中的 `computedHash`**

## 当前技能列表

| 技能名称 | 来源 | 版本 |
| --------- | ------ | ------ |
| find-skills | GitHub | - |
| gh-cli | GitHub | - |
| markdown-formatter | GitHub | - |
| nano-banana-2 | GitHub | - |
| wechat-article-writer | GitHub | - |
| git | SkillHub | 1.0.8 |
