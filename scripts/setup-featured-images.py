#!/usr/bin/env python3
"""为内容页复制分类封面或真实图片作为 featured 图，供 Blowfish 卡片与 Hero 使用。"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PHOTOS = ROOT / "assets" / "img" / "photos"
STATIC_IMAGES = ROOT / "static" / "assets" / "images"

DEFAULT_PHOTO = "article-default.jpg"

# 分区列表页优先使用的占位图
SECTION_INDEX_PHOTOS = {
    "content/life/_index.md": "cityscape.jpg",
    "content/life/places/_index.md": "cityscape.jpg",
    "content/life/university/_index.md": "campus.jpg",
    "content/life/table-game/_index.md": "boardgame.jpg",
    "content/life/entertainment/_index.md": "food.jpg",
    "content/life/thinks/_index.md": "friends.jpg",
    "content/office/_index.md": "cityscape.jpg",
    "content/_index.md": "home-bg.jpg",
    "content/about/index.md": DEFAULT_PHOTO,
}

# 分区文章默认占位图（无专属配图时使用）
SECTION_PHOTO = {
    "life/places": "cityscape.jpg",
    "life/university": "campus.jpg",
    "life/table-game": "boardgame.jpg",
    "life/entertainment": "food.jpg",
    "life/thinks": "friends.jpg",
    "office": "cityscape.jpg",
    "life": "cityscape.jpg",
    "about": DEFAULT_PHOTO,
}

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
    "life/table-game/guandan": "img-table-game-guandan/joker.webp",
    "life/table-game/upgrade": "img-upgrade/guandan.jpg",
    "life/thinks/blogger": "img-blogger/shenzhen-senior-school.png",
    "life/thinks/ai-dialectic": "ai-dialectic-moon-egg.png",
    "office/email": "img-email-thunderbird/thunderbird-lookup.jpg",
    "office/mac": "img-mac/mac-sliver.jpg",
    "office/markdown": "img-markdown/deepseek-markdown.jpg",
}

GALLERY_COPY: dict[str, str] = {
    "life/entertainment/gulou-riverfront": "nanjing-marathon.jpg",
    "life/places/nanjing-museum": "museum.jpg",
    "life/places/sun-mausoleum": "mausoleum.jpg",
    "life/places/chaotian-palace": "palace.jpg",
    "life/university/nju": "campus.jpg",
    "life/university/nnu": "campus.jpg",
    "life/entertainment/carbs": "food.jpg",
    "life/table-game/avalon": "boardgame.jpg",
    "life/table-game/undercover": "friends.jpg",
}


BUNDLE_FEATURED: dict[str, str] = {
    "life/entertainment/gulou-riverfront": "gallery/nanjing-marathon.jpg",
}


def rel_from_content(page_dir: Path) -> str:
    return str(page_dir.relative_to(CONTENT)).replace("\\", "/")


def photo_path(name: str) -> Path | None:
    path = PHOTOS / name
    return path if path.exists() else None


def pick_section_photo(rel: str) -> Path:
    for prefix, photo_name in sorted(SECTION_PHOTO.items(), key=lambda x: -len(x[0])):
        if rel == prefix or rel.startswith(prefix + "/"):
            found = photo_path(photo_name)
            if found:
                return found
    default = photo_path(DEFAULT_PHOTO)
    if default:
        return default
    raise FileNotFoundError(f"Default photo not found: {PHOTOS / DEFAULT_PHOTO}")


def resolve_featured_source(rel: str, index_file: Path) -> Path:
    index_key = str(index_file.relative_to(ROOT))
    if index_key in SECTION_INDEX_PHOTOS:
        found = photo_path(SECTION_INDEX_PHOTOS[index_key])
        if found:
            return found

    if rel in BUNDLE_FEATURED:
        bundle_path = CONTENT / rel / BUNDLE_FEATURED[rel]
        if bundle_path.exists():
            return bundle_path

    if rel in REAL_FEATURED:
        image_path = STATIC_IMAGES / REAL_FEATURED[rel]
        if image_path.exists():
            return image_path

    if rel in PHOTO_FEATURED:
        found = photo_path(PHOTO_FEATURED[rel])
        if found:
            return found

    return pick_section_photo(rel)


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
    rel_key = rel
    gallery = page_dir / "gallery"
    if gallery.is_dir() and any(gallery.iterdir()):
        return

    photo_name = GALLERY_COPY.get(rel_key)
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


def setup_page(page_dir: Path, index_file: Path) -> None:
    rel = rel_from_content(page_dir)
    source = resolve_featured_source(rel, index_file)
    copy_featured(page_dir, source)
    setup_gallery(page_dir, rel)


def main() -> None:
    print("Setting up featured images...")
    index_files = sorted(
        path for path in CONTENT.rglob("*.md") if path.name in {"index.md", "_index.md"}
    )
    for index_file in index_files:
        setup_page(index_file.parent, index_file)
    print("Done.")


if __name__ == "__main__":
    main()
