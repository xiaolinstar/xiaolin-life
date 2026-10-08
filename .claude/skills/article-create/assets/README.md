# Assets

Anthropic Claude Code Skills 规范静态资源目录。**不加载到 context**，仅按需引用。

## 当前用途

本 skill 暂未使用。如未来需要：

- 封面图 / 配图占位
- 字体 / 图标
- 预生成的模板资源

## 引用方式

SKILL.md 或脚本中通过相对路径引用：

```markdown
![示例](assets/example.png)
```

```python
asset_path = Path(__file__).parent.parent / "assets" / "example.png"
```
