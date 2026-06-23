#!/usr/bin/env python3
"""Migrate Jekyll markdown content to Hugo Blowfish structure."""

from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

CATEGORY_MAP = {
    "life/places": ["生活", "风景名胜"],
    "life/university": ["生活", "知名高校"],
    "life/table-game": ["生活", "桌游时光"],
    "life/entertainment": ["生活", "美食探店"],
    "life/thinks": ["生活", "生活感悟"],
    "office": ["办公"],
}

DEFAULT_DATE = "2025-05-21"

OFFICE_ARTICLES = [
    ("email.md", "Thunderbird 解放收件箱", "/office/email/"),
    ("markdown.md", "Markdown 文本编辑", "/office/markdown/"),
    ("mac.md", "Mac 办公体验", "/office/mac/"),
    ("linux.md", "Linux 学习路线", "/office/linux/"),
]

THINKS_ARTICLES = [
    ("blogger.md", "人人都是博主", "/life/thinks/blogger/"),
    ("content-warehouse.md", "内容仓库", "/life/thinks/content-warehouse/"),
    ("grandma-letter.md", "给阿嬷的情书", "/life/thinks/grandma-letter/"),
    ("letter-to-grandma.md", "给阿嬷的情书", "/life/thinks/letter-to-grandma/"),
    ("ai-dialectic.md", "AI 的辩证思考", "/life/thinks/ai-dialectic/"),
]


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()
    return fm, parts[2].lstrip("\n")


def convert_body(body: str) -> str:
    body = re.sub(
        r'!\[(.*?)\]\(\{\{\s*"(.*?)"\s*\|\s*relative_url\s*\}\}\)',
        r'![\1](\2)',
        body,
    )
    body = re.sub(
        r'!\[(.*?)\]\(\{\{\s*\'(.*?)\'\s*\|\s*relative_url\s*\}\}\)',
        r'![\1](\2)',
        body,
    )
    body = re.sub(r'!\[(.*?)\]\(\.\./assets/(.*?)\)', r'![\1](/assets/\2)', body)
    body = re.sub(r'\{\{\s*site\.baseurl\s*\}\}', "", body)
    body = re.sub(r'\{%.*?%\}', "", body, flags=re.DOTALL)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip() + "\n"


def build_front_matter(
    title: str,
    description: str,
    rel_path: str,
    *,
    is_index: bool = False,
) -> str:
    lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f"date: {DEFAULT_DATE}",
        "draft: false",
    ]
    if is_index:
        lines.append("showTableOfContents: false")
    else:
        lines.append("showTableOfContents: true")
        categories: list[str] | None = None
        for prefix, mapped in CATEGORY_MAP.items():
            if rel_path.startswith(prefix + "/") or rel_path == prefix:
                categories = mapped
                break
        if categories:
            lines.append("categories:")
            for cat in categories:
                lines.append(f'  - "{cat}"')
    lines.append("---")
    return "\n".join(lines) + "\n"


def target_path(rel: str, is_index: bool) -> Path:
    rel = rel.replace("\\", "/")
    if is_index:
        parts = rel.split("/")
        if len(parts) == 1:
            return CONTENT / parts[0] / "_index.md"
        return CONTENT / Path(*parts[:-1]) / "_index.md"
    if rel in ("index", "_index"):
        return CONTENT / "_index.md"
    if rel == "about":
        return CONTENT / "about" / "index.md"
    parts = rel.split("/")
    return CONTENT / Path(*parts) / "index.md"


def migrate_file(src: Path, rel: str, *, is_index: bool = False) -> None:
    raw = src.read_text(encoding="utf-8")
    fm, body = parse_front_matter(raw)
    title = fm.get("title", src.stem)
    description = fm.get("description", "")

    if rel == "office/index":
        body = """提升工作效率，让办公更轻松。

## 文章列表

- [Thunderbird 解放收件箱](/office/email/)
- [Markdown 文本编辑](/office/markdown/)
- [Mac 办公体验](/office/mac/)
- [Linux 学习路线](/office/linux/)
"""
    elif rel == "life/thinks/index":
        body = """记录生活中的思考与成长。

## 文章列表

- [人人都是博主](/life/thinks/blogger/)
- [内容仓库](/life/thinks/content-warehouse/)
- [给阿嬷的情书](/life/thinks/grandma-letter/)
- [AI 的辩证思考](/life/thinks/ai-dialectic/)
"""
    elif rel == "life/places/index":
        body = """南京拥有众多著名的风景名胜，是一座值得深度探索的城市。

## 景点列表

- [中山陵](/life/places/sun-mausoleum/)
- [南京博物院](/life/places/nanjing-museum/)
- [南京朝天宫](/life/places/chaotian-palace/)
"""
    elif rel == "life/university/index":
        body = """## 高校列表

- [南京大学](/life/university/nju/)
- [南京师范大学](/life/university/nnu/)
"""
    elif rel == "life/table-game/index":
        body = """## 桌游列表

- [掼蛋](/life/table-game/guandan/)
- [升级](/life/table-game/upgrade/)
- [谁是卧底](/life/table-game/undercover/)
- [阿瓦隆](/life/table-game/avalon/)
"""
    elif rel == "life/entertainment/index":
        body = """## 美食与休闲

- [在南京吃碳水这一块](/life/entertainment/carbs/)
- [鼓楼滨江步行道](/life/entertainment/gulou-riverfront/)
"""
    elif rel == "index":
        body = """欢迎来到我的生活站点！这里记录着南京生活、轻松办公、城市探索的点点滴滴。

## 生活记录

- [名胜古迹](/life/places/) — 总统府、中山陵、明孝陵等
- [高校巡礼](/life/university/) — 南京大学、南京师范大学等
- [桌游时光](/life/table-game/) — 掼蛋、升级、谁是卧底、阿瓦隆
- [美食探店](/life/entertainment/) — 碳水美食、南京小吃
- [生活感悟](/life/thinks/) — 数字劳动、内容仓库

## 轻松办公

- [Thunderbird 邮件管理](/office/email/)
- [Markdown 文本编辑](/office/markdown/)
- [Mac 办公体验](/office/mac/)
- [Linux 学习路线](/office/linux/)

## 关于我

欢迎了解更多[关于我](/about/)的信息。
"""
    else:
        body = convert_body(body)

    dest = target_path(rel, is_index)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        build_front_matter(title, description, rel, is_index=is_index) + body,
        encoding="utf-8",
    )
    print(f"migrated: {src} -> {dest}")


def main() -> None:
    if CONTENT.exists():
        shutil.rmtree(CONTENT)
    CONTENT.mkdir()

    migrate_file(ROOT / "index.md", "index")
    migrate_file(ROOT / "about.md", "about")

    for section in ("life", "office"):
        section_dir = ROOT / section
        if not section_dir.exists():
            continue
        for path in sorted(section_dir.rglob("*.md")):
            rel = str(path.relative_to(ROOT).with_suffix("")).replace("\\", "/")
            is_index = path.name == "index.md"
            migrate_file(path, rel, is_index=is_index)

    print("Migration complete.")


if __name__ == "__main__":
    main()
