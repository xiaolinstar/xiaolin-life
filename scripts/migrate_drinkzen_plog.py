import re

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
ORIGIN_RE = re.compile(r"^origin:\s*(.+)$", re.MULTILINE)


def extract_origin_path(content: str) -> str | None:
    """从 draft frontmatter 提取 origin 路径"""
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return None
    origin_match = ORIGIN_RE.search(fm_match.group(1))
    return origin_match.group(1).strip() if origin_match else None


XHS_SECTION_RE = re.compile(
    r"## 小红书\s*\n(.*?)(?=\n## |\Z)",
    re.DOTALL,
)


def extract_xhs_section(content: str) -> dict:
    """Extract 小红书 code block, 标签, 评论区置顶, 图片清单 sections — each precisely."""
    # 1. 小红书正文 (```text``` block right after ## 小红书)
    text_match = re.search(
        r"## 小红书\s*\n+```text\n(.*?)\n```",
        content,
        re.DOTALL,
    )
    xhs_text = text_match.group(1).strip() if text_match else ""

    # 2. 标签 (```text``` block right after ### 标签)
    tags_match = re.search(
        r"### 标签\s*\n+```text\n(.*?)\n```",
        content,
        re.DOTALL,
    )
    tags = tags_match.group(1).strip() if tags_match else ""

    # 3. 评论区置顶 (```text``` block right after ### 评论区置顶)
    pinned_match = re.search(
        r"### 评论区置顶\s*\n+```text\n(.*?)\n```",
        content,
        re.DOTALL,
    )
    pinned = pinned_match.group(1).strip() if pinned_match else ""

    # 4. 图片清单 (markdown table from ## 图片清单 until ## 📸)
    images_match = re.search(
        r"## 图片清单\s*\n(.*?)(?=\n## 📸|\n## 自检|\n## 发布后|\Z)",
        content,
        re.DOTALL,
    )
    images = images_match.group(1).strip() if images_match else ""

    return {"text": xhs_text, "tags": tags, "pinned": pinned, "images": images}


from pathlib import Path
from datetime import date


def build_tabs_section(sections: dict, draft_origin: str) -> str:
    """组装 plog tabs Markdown 段"""
    return f'''## plog 分发版

<!-- generated from {draft_origin} by migrate_drinkzen_plog.py on {date.today().isoformat()} -->

{{{{< tabs "plog" >}}}}
{{{{< tab "📕 plog 长版（小红书 / 微博，≤800 字）" >}}}}

{sections["text"]}

### 标签

```text
{sections["tags"]}
```

### 评论区置顶

```text
{sections["pinned"]}
```

### 图片清单

{sections["images"]}

{{{{< /tab >}}}}
{{{{< /tabs >}}}}
'''


def update_origin_frontmatter(content: str, platforms: list[str]) -> str:
    """在 origin frontmatter 添加或更新 platforms 字段"""
    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        return content
    frontmatter = fm_match.group(1)
    body = content[fm_match.end():]

    platforms_str = ", ".join(platforms)
    platforms_line = f"platforms: [{platforms_str}]"

    if re.search(r"^platforms:\s*\[", frontmatter, re.MULTILINE):
        # 已存在则替换
        frontmatter = re.sub(
            r"^platforms:\s*\[.*$",
            platforms_line,
            frontmatter,
            flags=re.MULTILINE,
        )
    else:
        # 不存在则加到 frontmatter 末尾
        frontmatter = frontmatter.rstrip() + "\n" + platforms_line + "\n"

    return f"---\n{frontmatter}---\n{body}"


def migrate_draft(draft_path: Path, dry_run: bool = True) -> dict:
    """迁移单个 draft 到 origin 文章"""
    content = draft_path.read_text(encoding="utf-8")
    origin_path = extract_origin_path(content)
    if not origin_path:
        return {"ok": False, "error": "no origin path"}

    origin_full = Path(origin_path)
    # 相对 origin 路径相对于当前工作目录解析（CLI 从项目根目录运行）
    if not origin_full.is_absolute():
        origin_full = (Path.cwd() / origin_full).resolve()
    if not origin_full.exists():
        return {"ok": False, "error": f"origin not found: {origin_path}"}

    origin_content = origin_full.read_text(encoding="utf-8")
    if "## plog 分发版" in origin_content:
        return {
            "ok": True,
            "skipped": True,
            "reason": "already migrated (## plog 分发版 exists)",
            "draft": str(draft_path),
            "origin": str(origin_full),
        }

    sections = extract_xhs_section(content)
    tabs_md = build_tabs_section(sections, str(draft_path))

    updated = update_origin_frontmatter(origin_content, platforms=["xiaohongshu"])
    # 在正文末尾追加 tabs 段
    updated = updated.rstrip() + "\n\n" + tabs_md

    if not dry_run:
        origin_full.write_text(updated, encoding="utf-8")

    return {
        "ok": True,
        "draft": str(draft_path),
        "origin": str(origin_full),
        "preview": updated[-500:] if dry_run else None,
    }


def migrate_all(drafts_dir: Path, dry_run: bool = True) -> list[dict]:
    """迁移所有 draft"""
    return [migrate_draft(p, dry_run=dry_run) for p in sorted(drafts_dir.glob("*.md"))]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="actually write changes")
    parser.add_argument("--drafts-dir", default="content/social-publish/drafts")
    args = parser.parse_args()

    dry_run = not args.write
    results = migrate_all(Path(args.drafts_dir), dry_run=dry_run)

    for r in results:
        if r["ok"]:
            print(f"✓ {r['draft']} → {r['origin']}")
        else:
            print(f"✗ {r['draft']}: {r['error']}")

    print(f"\n{len([r for r in results if r['ok']])}/{len(results)} ok")
    print(f"mode: {'dry-run' if dry_run else 'WRITE'}")