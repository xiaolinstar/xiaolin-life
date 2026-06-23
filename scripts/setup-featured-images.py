#!/usr/bin/env python3
"""为内容页复制分类封面或真实图片作为 featured 图，供 Blowfish 卡片与 Hero 使用。"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
COVERS = ROOT / "assets" / "img" / "covers"
PHOTOS = ROOT / "assets" / "img" / "photos"
STATIC_IMAGES = ROOT / "static" / "assets" / "images"

SECTION_COVER = {
    "life/places": "places.svg",
    "life/university": "university.svg",
    "life/table-game": "table-game.svg",
    "life/entertainment": "entertainment.svg",
    "life/thinks": "thinks.svg",
    "office": "office.svg",
    "life": "default.svg",
    "about": "default.svg",
}

# 优先使用本地占位图或真实配图
PHOTO_FEATURED: dict[str, str] = {
    "life/places/nanjing-museum": "museum.jpg",
    "life/places/sun-mausoleum": "mausoleum.jpg",
    "life/places/chaotian-palace": "palace.jpg",
    "life/university/nju": "campus.jpg",
    "life/university/nnu": "campus.jpg",
    "life/entertainment/carbs": "food.jpg",
    "life/table-game/avalon": "boardgame.jpg",
    "life/table-game/undercover": "friends.jpg",
}

REAL_FEATURED: dict[str, str] = {
    "life/entertainment/gulou-riverfront": "img-gulou-riverfront/nanjing-marathon.jpg",
    "life/table-game/guandan": "img-table-game-guandan/joker.webp",
    "life/table-game/upgrade": "img-upgrade/guandan.jpg",
    "life/thinks/blogger": "img-blogger/shenzhen-senior-school.png",
    "life/thinks/ai-dialectic": "ai-dialectic-moon-egg.png",
    "office/email": "img-email-thunderbird/thunderbird-lookup.png",
    "office/mac": "img-mac/mac-sliver.jpg",
    "office/markdown": "img-markdown/deepseek-markdown.jpg",
}

SECTION_INDEX_COVERS = {
    "content/life/_index.md": "cityscape.jpg",
    "content/life/places/_index.md": "cityscape.jpg",
    "content/life/university/_index.md": "campus.jpg",
    "content/life/table-game/_index.md": "boardgame.jpg",
    "content/life/entertainment/_index.md": "food.jpg",
    "content/life/thinks/_index.md": "friends.jpg",
    "content/office/_index.md": "cityscape.jpg",
    "content/_index.md": "home-bg.jpg",
}

GALLERY_COPY: dict[str, str] = {
    "life/places/nanjing-museum": "museum.jpg",
    "life/places/sun-mausoleum": "mausoleum.jpg",
    "life/places/chaotian-palace": "palace.jpg",
    "life/university/nju": "campus.jpg",
    "life/university/nnu": "campus.jpg",
    "life/entertainment/carbs": "food.jpg",
    "life/table-game/avalon": "boardgame.jpg",
    "life/table-game/undercover": "friends.jpg",
}


def rel_from_content(page_dir: Path) -> str:
    return str(page_dir.relative_to(CONTENT)).replace("\\", "/")


def pick_cover(rel: str) -> str:
    for prefix, cover in sorted(SECTION_COVER.items(), key=lambda x: -len(x[0])):
        if rel == prefix or rel.startswith(prefix + "/"):
            return cover
    return "default.svg"


def clear_featured(page_dir: Path) -> None:
    for pattern in ("featured.*", "feature.*", "cover.*", "thumbnail.*"):
        for path in page_dir.glob(pattern):
            if path.is_file():
                path.unlink()


def copy_featured(page_dir: Path, source: Path) -> None:
    clear_featured(page_dir)
    ext = source.suffix or ".jpg"
    dest = page_dir / f"featured{ext}"
    shutil.copy2(source, dest)
    print(f"  featured: {dest.relative_to(ROOT)} <- {source.name}")


def setup_gallery(page_dir: Path, rel: str) -> None:
    photo_name = GALLERY_COPY.get(rel)
    if not photo_name:
        return
    source = PHOTOS / photo_name
    if not source.exists():
        return
    gallery = page_dir / "gallery"
    gallery.mkdir(exist_ok=True)
    dest = gallery / photo_name
    shutil.copy2(source, dest)
    print(f"  gallery: {dest.relative_to(ROOT)}")


def setup_page(page_dir: Path) -> None:
    if not (page_dir / "index.md").exists() and not (page_dir / "_index.md").exists():
        return

    rel = rel_from_content(page_dir)

    if rel in REAL_FEATURED:
        image_path = STATIC_IMAGES / REAL_FEATURED[rel]
        if image_path.exists():
            copy_featured(page_dir, image_path)
            setup_gallery(page_dir, rel)
            return

    if rel in PHOTO_FEATURED:
        photo_path = PHOTOS / PHOTO_FEATURED[rel]
        if photo_path.exists():
            copy_featured(page_dir, photo_path)
            setup_gallery(page_dir, rel)
            return

    cover_name = pick_cover(rel)
    cover_path = COVERS / cover_name
    if cover_path.exists():
        copy_featured(page_dir, cover_path)


def setup_section_indexes() -> None:
    for rel_path, cover_name in SECTION_INDEX_COVERS.items():
        index_path = ROOT / rel_path
        if not index_path.exists():
            continue
        page_dir = index_path.parent
        photo_path = PHOTOS / cover_name
        if photo_path.exists():
            copy_featured(page_dir, photo_path)
            continue
        cover_path = COVERS / cover_name
        if cover_path.exists():
            copy_featured(page_dir, cover_path)


def main() -> None:
    print("Setting up featured images...")
    setup_section_indexes()

    for index_file in sorted(CONTENT.rglob("index.md")):
        page_dir = index_file.parent
        rel = rel_from_content(page_dir)
        setup_page(page_dir)
        setup_gallery(page_dir, rel)

    print("Done.")


if __name__ == "__main__":
    main()
