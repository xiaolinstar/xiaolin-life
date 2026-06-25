#!/usr/bin/env python3
"""压缩 static/assets/images 下的图片：限制宽度、降低 JPEG/WebP 质量、优化 PNG。"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIRS = [
    ROOT / "static" / "assets" / "images",
    ROOT / "content",
]

MAX_WIDTH = 1920
JPEG_QUALITY = 82
WEBP_QUALITY = 82
PNG_COMPRESS = 6
MIN_BYTES = 200_000  # 小于 200KB 跳过

SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def compress_image(path: Path) -> tuple[int, int]:
    before = path.stat().st_size
    if before < MIN_BYTES:
        return before, before

    with Image.open(path) as img:
        img.load()
        original_size = before
        needs_resize = img.width > MAX_WIDTH
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )

        if path.suffix.lower() in {".jpg", ".jpeg"}:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            if needs_resize:
                ratio = MAX_WIDTH / img.width
                img = img.resize(
                    (MAX_WIDTH, int(img.height * ratio)), Image.Resampling.LANCZOS
                )
            img.save(
                path,
                format="JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )
        elif path.suffix.lower() == ".webp":
            if needs_resize:
                ratio = MAX_WIDTH / img.width
                img = img.resize(
                    (MAX_WIDTH, int(img.height * ratio)), Image.Resampling.LANCZOS
                )
            img.save(path, format="WEBP", quality=WEBP_QUALITY, method=6)
        elif path.suffix.lower() == ".png":
            if needs_resize:
                ratio = MAX_WIDTH / img.width
                img = img.resize(
                    (MAX_WIDTH, int(img.height * ratio)), Image.Resampling.LANCZOS
                )
            img.save(path, format="PNG", optimize=True, compress_level=PNG_COMPRESS)

    after = path.stat().st_size
    if after != original_size:
        print(
            f"  {path.relative_to(ROOT)}: {original_size // 1024}KB -> {after // 1024}KB"
        )
    return original_size, after


def iter_images() -> list[Path]:
    found: list[Path] = []
    static_root = IMAGE_DIRS[0]
    if static_root.is_dir():
        found.extend(
            p
            for p in sorted(static_root.rglob("*"))
            if p.is_file() and p.suffix.lower() in SUFFIXES
        )
    content_root = IMAGE_DIRS[1]
    if content_root.is_dir():
        found.extend(
            p
            for p in sorted(content_root.rglob("gallery/*"))
            if p.is_file() and p.suffix.lower() in SUFFIXES
        )
        found.extend(
            p
            for p in sorted(content_root.rglob("featured.*"))
            if p.is_file() and p.suffix.lower() in SUFFIXES
        )
    return found


def main() -> None:
    paths = iter_images()
    if not paths:
        print("No images found")
        return

    total_before = 0
    total_after = 0

    for path in paths:
        before, after = compress_image(path)
        total_before += before
        total_after += after

    saved = total_before - total_after
    print(
        f"Done: {len(paths)} files, "
        f"{total_before // 1024 // 1024}MB -> {total_after // 1024 // 1024}MB "
        f"(saved {saved // 1024 // 1024}MB)"
    )


if __name__ == "__main__":
    main()
