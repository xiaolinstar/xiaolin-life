#!/usr/bin/env python3
"""为 Markdown 中 CDN URL 插入项目对象键前缀（如 life/、docs/）。

已含 life/、docs/ 等一级前缀的 URL 不会重复添加。

环境变量：
  MEDIA_CDN_BASE  默认 https://media.xiaolin.fun
  COS_PREFIX      默认 life（xiaolin-life）；dcos 仓库设为 docs

用法：
  python3 scripts/rewrite-cdn-prefix.py              # 预览
  python3 scripts/rewrite-cdn-prefix.py --apply
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
# 共享 Bucket 中已占用的一级前缀，勿再包裹 COS_PREFIX
RESERVED_TOP = frozenset({"life", "docs"})


def rewrite_text(text: str, cdn_base: str, prefix: str) -> tuple[str, int]:
    cdn = cdn_base.rstrip("/")
    pref = prefix.strip("/")
    if not pref:
        return text, 0

    reserved = RESERVED_TOP | {pref}
    # 匹配 CDN 根下尚未带保留前缀的路径
    reserved_alt = "|".join(re.escape(p) for p in sorted(reserved, key=len, reverse=True))
    pattern = re.compile(
        rf"({re.escape(cdn)}/)(?!({reserved_alt})/)([^\s\)\"'<>]+)"
    )
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}{pref}/{match.group(3)}"

    return pattern.sub(repl, text), count


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
    parser.add_argument("paths", nargs="*", help="Markdown 文件或目录（默认 content/）")
    parser.add_argument("--apply", action="store_true", help="写入文件")
    parser.add_argument(
        "--cdn-base",
        default=os.environ.get("MEDIA_CDN_BASE", DEFAULT_CDN),
    )
    parser.add_argument(
        "--prefix",
        default=os.environ.get("COS_PREFIX", DEFAULT_PREFIX),
    )
    args = parser.parse_args()

    targets = collect_targets(args.paths)
    total = 0
    changed_files = 0

    for path in targets:
        text = path.read_text(encoding="utf-8")
        new_text, count = rewrite_text(text, args.cdn_base, args.prefix)
        if count:
            rel = path.relative_to(ROOT)
            print(f"{rel}: {count} 处")
            total += count
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
                changed_files += 1

    if total == 0:
        print("无需添加前缀（或已全部带 life/、docs/ 等前缀）。")
        return

    if args.apply:
        print(f"\n已写入: {changed_files} 个文件，共 {total} 处")
        print(f"  插入前缀: {args.prefix}/")
    else:
        print(f"\n预览共 {total} 处，加 --apply 写入。")


if __name__ == "__main__":
    main()
