#!/usr/bin/env python3
"""将 content/ 下 Markdown 中的本地媒体引用替换为 CDN 绝对 URL。

处理两类引用：
  1. /assets/images/ 路径 → CDN 绝对 URL
  2. {{< carousel images="gallery/*" ... >}} → {{< carousel-cdn images="{url,...}" ... >}}
     （按文章目录下 gallery/ 实际文件展开；需先上传 COS）

环境变量：
  MEDIA_CDN_BASE  默认 https://media.xiaolin.fun
  COS_PREFIX      默认 life

用法：
  python3 scripts/rewrite-media-urls.py              # 预览
  python3 scripts/rewrite-media-urls.py --apply      # 写入
  python3 scripts/rewrite-media-urls.py --apply content/office/email/index.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DEFAULT_CDN = "https://media.xiaolin.fun"
DEFAULT_PREFIX = "life"
LOCAL_PREFIX = "/assets/images/"

# ![alt](/assets/images/foo/bar.png) 或裸路径
PATTERN = re.compile(
    r"(?<!\w)" + re.escape(LOCAL_PREFIX) + r"([^\s\)\"'<>]+)"
)

# {{< carousel images="gallery/*" interval="4500" ... >}}
CAROUSEL_PATTERN = re.compile(r"\{\{<\s*carousel\s+([^>]*?)\s*>\}\}")
CAROUSEL_ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def rewrite_carousel(
    text: str, md_path: Path, cdn_base: str
) -> tuple[str, int]:
    """把本地 gallery 轮播改写为 carousel-cdn（CDN URL 列表）。

    对象键与 media-publish.sh 保持一致：文章路径去掉 content/ 前缀。
    仅当 images 指向本地 gallery 且文件存在时改写。
    """
    article_dir = md_path.parent
    try:
        rel = article_dir.relative_to(CONTENT)
    except ValueError:
        return text, 0
    url_prefix = f"{cdn_base.rstrip('/')}/{rel.as_posix()}"
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        attrs = dict(CAROUSEL_ATTR_PATTERN.findall(match.group(1)))
        images_glob = attrs.get("images", "")
        if not images_glob.startswith("gallery/"):
            return match.group(0)

        files = sorted(
            p
            for p in article_dir.glob(images_glob)
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS
        )
        if not files:
            print(
                f"  Skip carousel（gallery 无匹配图片）: {md_path.relative_to(ROOT)}",
                file=sys.stderr,
            )
            return match.group(0)

        urls = ",".join(f"{url_prefix}/{p.name}" for p in files)
        parts = [f'images="{{{urls}}}"']
        for key in ("interval", "aspectRatio", "captions"):
            if key in attrs:
                parts.append(f'{key}="{attrs[key]}"')
        count += 1
        return "{{< carousel-cdn " + " ".join(parts) + " >}}"

    return CAROUSEL_PATTERN.sub(repl, text), count


def rewrite_text(text: str, cdn_base: str, prefix: str = "") -> tuple[str, int]:
    cdn = cdn_base.rstrip("/")
    pref = prefix.strip("/")
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        path = match.group(1)
        if pref:
            return f"{cdn}/{pref}/{path}"
        return f"{cdn}/{path}"

    return PATTERN.sub(repl, text), count


def collect_targets(explicit: list[str]) -> list[Path]:
    if explicit:
        paths: list[Path] = []
        for item in explicit:
            p = Path(item)
            if not p.is_absolute():
                p = ROOT / p
            if p.is_dir():
                paths.extend(sorted(p.rglob("*.md")))
            elif p.is_file():
                paths.append(p)
            else:
                print(f"Skip missing: {item}", file=sys.stderr)
        return paths
    return sorted(CONTENT.rglob("*.md"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="要处理的 Markdown 文件或目录（默认 content/ 全部）",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="写入文件（默认仅预览）",
    )
    parser.add_argument(
        "--cdn-base",
        default=os.environ.get("MEDIA_CDN_BASE", DEFAULT_CDN),
        help=f"CDN 根 URL（默认 {DEFAULT_CDN} 或 MEDIA_CDN_BASE）",
    )
    parser.add_argument(
        "--prefix",
        default=os.environ.get("COS_PREFIX", DEFAULT_PREFIX),
        help=f"对象键前缀（默认 {DEFAULT_PREFIX} 或 COS_PREFIX）",
    )
    args = parser.parse_args()

    targets = collect_targets(args.paths)
    total_files = 0
    total_refs = 0

    for path in targets:
        original = path.read_text(encoding="utf-8")
        updated, n = rewrite_text(original, args.cdn_base, args.prefix)
        updated, n_carousel = rewrite_carousel(updated, path, args.cdn_base)
        n += n_carousel
        if n == 0:
            continue
        total_files += 1
        total_refs += n
        rel = path.relative_to(ROOT)
        print(f"{rel}: {n} 处")
        if args.apply:
            path.write_text(updated, encoding="utf-8")
        else:
            old_lines = original.splitlines()
            new_lines = updated.splitlines()
            for line_no, (old, new) in enumerate(zip(old_lines, new_lines), 1):
                if old != new:
                    print(f"  L{line_no}: {old.strip()}")
                    print(f"     → {new.strip()}")

    mode = "已写入" if args.apply else "预览"
    print(f"\n{mode}: {total_files} 个文件，共 {total_refs} 处引用")
    if not args.apply and total_refs:
        print("确认无误后执行: python3 scripts/rewrite-media-urls.py --apply")


if __name__ == "__main__":
    main()
