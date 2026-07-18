#!/usr/bin/env python3
"""本地生成文章占位图（无需外网）。"""

from __future__ import annotations

import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "photos"
OUT.mkdir(parents=True, exist_ok=True)

DEFAULT_PHOTO_URL = "https://picsum.photos/seed/xiaolin-life-default/1200/630"
DEFAULT_PHOTO_NAME = "article-default.jpg"

PALETTES = {
    "home-bg": ("#0f172a", "#1e3a5f", "#2d6a8a", "今天不上班", "南京生活 · 城市探索"),
    "cityscape": ("#1e293b", "#334155", "#64748b", "南京", "城市漫步"),
    "museum": ("#7c2d12", "#c2410c", "#fb923c", "博物馆", "南京博物院"),
    "mausoleum": ("#14532d", "#166534", "#4ade80", "中山陵", "紫金山"),
    "palace": ("#78350f", "#b45309", "#fcd34d", "朝天宫", "古建风韵"),
    "campus": ("#1e3a8a", "#2563eb", "#93c5fd", "高校", "校园巡礼"),
    "food": ("#9a3412", "#ea580c", "#fdba74", "碳水", "南京味道"),
    "boardgame": ("#581c87", "#9333ea", "#e879f9", "桌游", "聚会时光"),
    "friends": ("#134e4a", "#0d9488", "#5eead4", "聚会", "朋友与游戏"),
}


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def gradient(size: tuple[int, int], c1: str, c2: str, c3: str | None = None) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    r1, g1, b1 = hex_rgb(c1)
    r2, g2, b2 = hex_rgb(c2)
    r3, g3, b3 = hex_rgb(c3) if c3 else (r2, g2, b2)
    for y in range(h):
        t = y / max(h - 1, 1)
        t2 = min(1.0, t * 1.4)
        if c3 and t > 0.55:
            tt = (t - 0.55) / 0.45
            r = lerp(r2, r3, tt)
            g = lerp(g2, g3, tt)
            b = lerp(b2, b3, tt)
        else:
            r = lerp(r1, r2, t2)
            g = lerp(g1, g2, t2)
            b = lerp(b1, b2, t2)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_photo(name: str, size: tuple[int, int], title: str, subtitle: str, colors: tuple[str, ...]) -> None:
    img = gradient(size, *colors)
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = size

    # 装饰圆
    draw.ellipse((w - 280, -60, w + 60, 280), fill=(255, 255, 255, 18))
    draw.ellipse((-80, h - 220, 180, h + 20), fill=(255, 255, 255, 12))

    title_font = load_font(56 if size[0] >= 1600 else 42)
    sub_font = load_font(28 if size[0] >= 1600 else 22)

    draw.text((72, h - 180), title, fill=(255, 255, 255, 245), font=title_font)
    draw.text((72, h - 110), subtitle, fill=(255, 255, 255, 210), font=sub_font)

    # 底部暗角
    for i in range(80):
        alpha = int(120 * (i / 80) ** 2)
        y = h - 80 + i
        if y < h:
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    dest = OUT / f"{name}.jpg"
    img.save(dest, "JPEG", quality=88, optimize=True)
    print(f"generated {dest}")


def ensure_default_photo() -> None:
    dest = OUT / DEFAULT_PHOTO_NAME
    if dest.exists():
        return
    import urllib.request

    print(f"Downloading default photo from {DEFAULT_PHOTO_URL}")
    urllib.request.urlretrieve(DEFAULT_PHOTO_URL, dest)
    print(f"generated {dest}")


def main() -> None:
    ensure_default_photo()
    for name, (c1, c2, c3, title, subtitle) in PALETTES.items():
        # 仓库中已提交真实照片时不覆盖，仅补齐缺失的占位图
        if (OUT / f"{name}.jpg").exists():
            print(f"skip existing {name}.jpg")
            continue
        size = (1920, 1080) if name == "home-bg" else (1200, 630)
        draw_photo(name, size, title, subtitle, (c1, c2, c3))

    print("Done.")


if __name__ == "__main__":
    main()
