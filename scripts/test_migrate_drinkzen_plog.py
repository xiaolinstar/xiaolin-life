from migrate_drinkzen_plog import extract_origin_path, extract_xhs_section


def test_extract_origin_path():
    sample = """---
title: foo
origin: content/drinkzen/luckincoffee/foo/index.md
platforms: [xiaohongshu]
generated: 2026-09-30
status: draft
---

# 标题

## 小红书

```text
content
```
"""
    assert extract_origin_path(sample) == "content/drinkzen/luckincoffee/foo/index.md"


def test_extract_xhs_section():
    """Real draft structure has ```text``` fences around all 4 sections."""
    sample = """## 小红书

```text
📍 今日饮品：XX
内容
```

- 字数：约 750 字符

### 标签

```text
#奶茶仙人 #DrinkZen
#每日打卡
```

- 共 9 个

### 评论区置顶

```text
🥤 DrinkZen 小程序搜「XX」
💡 推荐点单：冰 / 少甜
```

- 6 行结构化

## 图片清单

| 位 | 角色 | 来源 |
| --- | --- | --- |
| 图 1 | 封面 | gallery/01.jpg |

## 📸 图片生成指引

（跳过此段）
"""
    sections = extract_xhs_section(sample)
    # 小红书正文: only the code block content, no 注释行
    assert "今日饮品" in sections["text"]
    assert "内容" in sections["text"]
    assert "字数" not in sections["text"], "should NOT capture 注释行 below code block"
    assert "图片生成指引" not in sections["text"]

    # 标签: only the ```text``` block
    assert "#奶茶仙人" in sections["tags"]
    assert "共 9 个" not in sections["tags"], "should NOT capture 注释行 below code block"
    assert "图片生成指引" not in sections["tags"]

    # 评论区置顶: only the ```text``` block
    assert "DrinkZen 小程序搜" in sections["pinned"]
    assert "6 行结构化" not in sections["pinned"]

    # 图片清单: markdown table until next ## heading
    assert "图 1" in sections["images"]
    assert "封面" in sections["images"]
    assert "图片生成指引" not in sections["images"]


import tempfile
from pathlib import Path

from migrate_drinkzen_plog import build_tabs_section, update_origin_frontmatter


def test_build_tabs_section():
    sections = {
        "text": "📍 今日饮品",
        "tags": "#tag1",
        "pinned": "🥤 line",
        "images": "- 图 1",
    }
    output = build_tabs_section(sections, draft_origin="content/foo.md")
    assert "## plog 分发版" in output
    assert "{{< tabs \"plog\" >}}" in output
    assert "📕 plog 长版" in output
    assert "📍 今日饮品" in output
    assert "#tag1" in output
    assert "🥤 line" in output
    assert "<!-- generated" in output  # 包含生成元数据注释
    # NEW: 验证 ```text``` fences 包裹 tags 和 pinned（避免被 markdownlint 误判为 H1）
    assert "### 标签\n\n```text\n#tag1\n```" in output, f"tags 应被 ```text``` fence 包裹:\n{output}"
    assert "### 评论区置顶\n\n```text\n🥤 line\n```" in output, f"pinned 应被 ```text``` fence 包裹:\n{output}"


def test_update_origin_frontmatter():
    original = """---
title: 秋桂米酿拿铁
date: 2026-09-30
draft: false
categories: [饮品记录, 奶茶仙人]
tags: [luckincoffee, autumn]
---

[正文]
"""
    updated = update_origin_frontmatter(original, platforms=["xiaohongshu"])
    assert "platforms: [xiaohongshu]" in updated
    assert "categories: [饮品记录, 奶茶仙人]" in updated  # 保留原字段
    assert "[正文]" in updated  # 保留正文


def test_migrate_draft_dry_run(tmp_path, monkeypatch):
    # 创建临时 draft
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    origin_dir = tmp_path / "origin"
    origin_dir.mkdir()
    (origin_dir / "index.md").write_text(
        "---\ntitle: foo\ndate: 2026-01-01\n---\n\n正文\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    (drafts / "foo.md").write_text(
        "---\ntitle: foo\norigin: origin/index.md\nplatforms: [xiaohongshu]\ngenerated: 2026-01-01\nstatus: draft\n---\n\n## 小红书\n\n```text\n📍 今日饮品\n```\n\n### 标签\n\n#tag\n\n### 评论区置顶\n\n🥤 line\n\n## 图片清单\n\n- 图 1\n",
        encoding="utf-8",
    )

    from migrate_drinkzen_plog import migrate_draft
    result = migrate_draft(drafts / "foo.md", dry_run=True)
    assert result["ok"]

    # dry_run 不应修改文件
    assert (origin_dir / "index.md").read_text(encoding="utf-8") == "---\ntitle: foo\ndate: 2026-01-01\n---\n\n正文\n"