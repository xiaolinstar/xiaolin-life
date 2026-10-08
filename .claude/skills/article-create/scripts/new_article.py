#!/usr/bin/env python3
"""new_article.py — xiaolin-life Hugo Page Bundle 脚手架

用法:
    python3 new_article.py [section/slug] "<title>" [options]

示例:
    # 智能归类（推荐）
    python3 new_article.py "奥体夜跑随笔"

    # 手动指定
    python3 new_article.py life/thoughts/olympic-night-run "奥体夜跑随笔"

    # 完整参数
    python3 new_article.py life/thoughts/olympic-night-run "奥体夜跑随笔" \\
        --description "夏夜的奥体中心" \\
        --tags 随笔 跑步 南京 \\
        --categories 生活记录 \\
        --featured \\
        --dry-run

依赖（由 pyproject.toml 管理）:
    uv run --project . python scripts/new_article.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Section 关键词映射（references/sections.md 的程序化版本）
SECTION_HINTS: dict[str, list[str]] = {
    "life/entertainment": ["电影", "剧", "综艺", "演出", "展览", "夜跑", "演唱会", "KTV", "密室"],
    "life/thoughts": ["随笔", "感悟", "思考", "日记", "记录", "心情", "回忆", "梦"],
    "life/media": ["书", "读书", "影评", "乐评", "书评", "读完", "看完", "听"],
    "life/notes": ["笔记", "摘录", "清单", "学习", "知识"],
    "office/tools": ["工具", "效率", "软件", "App", "插件"],
    "office/workflow": ["流程", "方法", "工作流", "SOP", "技巧"],
    "office/experience": ["办公", "远程", "会议", "团队", "管理", "SRE", "运维", "部署"],
}

VALID_SECTION_PREFIXES = ("life/", "office/")


def suggest_section(title: str) -> tuple[str, list[str]]:
    """根据标题推荐 section，返回 (recommended_path, [matched_keywords])。"""
    matches: list[tuple[str, list[str]]] = []
    for section, keywords in SECTION_HINTS.items():
        hits = [k for k in keywords if k in title]
        if hits:
            matches.append((section, hits))
    if not matches:
        return ("life/thoughts", [])
    matches.sort(key=lambda x: -len(x[1]))
    return matches[0]


def validate_slug(slug: str) -> str | None:
    """返回 None 表示 OK，否则返回错误信息。"""
    if re.search(r"[\s一-鿿＀-￯]", slug):
        return "slug 不能含空格、中文或全角字符"
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", slug):
        return "slug 必须是小写字母+数字+连字符，且首尾是字母或数字"
    return None


def build_frontmatter(
    title: str,
    description: str,
    date: str,
    tags: list[str],
    categories: list[str],
    featured: bool,
) -> str:
    fm: dict = {
        "title": title,
        "date": date,
        "draft": True,
    }
    if description:
        fm["description"] = description
    if tags:
        fm["tags"] = tags
    if categories:
        fm["categories"] = categories
    fm["showTableOfContents"] = False
    if featured:
        fm["featured"] = "featured.jpg"

    yaml_text = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{yaml_text}---\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="new-article",
        description="创建 xiaolin-life Hugo Page Bundle 草稿",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="section/slug，如 life/thoughts/olympic-night-run（缺省走关键词推荐）",
    )
    parser.add_argument("title", help="文章标题")
    parser.add_argument("--description", help="一句话描述（用于 meta + 卡片摘要）")
    parser.add_argument("--tags", nargs="*", help="标签，空格分隔")
    parser.add_argument("--categories", nargs="*", help="分类，空格分隔")
    parser.add_argument("--featured", action="store_true", help="生成 featured.jpg 占位")
    parser.add_argument("--no-draft", action="store_true", help="不标记 draft（慎用）")
    parser.add_argument("--date", help="自定义日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--dry-run", action="store_true", help="只打印不执行")

    args = parser.parse_args(argv)

    # 1. 解析 path
    if not args.path:
        recommended, hits = suggest_section(args.title)
        body = (
            f"[bold]推荐 section[/bold]: {recommended}\n"
            f"[dim]匹配关键词: {', '.join(hits) if hits else '（无，默认）'}[/dim]\n\n"
            f"确认后请指定 slug 重新运行：\n"
            f"  pnpm run article:create {recommended}/<your-slug> \"{args.title}\""
        )
        console.print(Panel(body, title="section 归类建议"))
        return 0

    parts = args.path.strip("/").split("/")
    if len(parts) < 2:
        console.print("[red]✗[/red] path 必须是 section/slug 形式（至少 2 段）")
        return 1
    slug = parts[-1]
    section_path = "/".join(parts[:-1])

    # 2. 校验 slug
    if err := validate_slug(slug):
        console.print(f"[red]✗[/red] slug 校验失败: {err}")
        return 1

    # 3. 校验 section
    if not section_path.startswith(VALID_SECTION_PREFIXES):
        console.print(
            f"[red]✗[/red] section 必须是 life/ 或 office/ 开头（饮品走 drinkzen skill）"
        )
        return 1

    # 4. 路径冲突检查
    bundle_path = Path("content") / section_path / slug
    if bundle_path.exists():
        console.print(f"[red]✗[/red] 路径已存在: {bundle_path}")
        return 1

    # 5. 准备 front matter
    date_str = args.date or dt.date.today().isoformat()
    fm_text = build_frontmatter(
        title=args.title,
        description=args.description or "",
        date=date_str,
        tags=args.tags or [],
        categories=args.categories or [],
        featured=args.featured,
    )
    if args.no_draft:
        fm_text = fm_text.replace("draft: true", "draft: false", 1)

    # 6. 报告
    table = Table(title="创建计划", show_header=False)
    table.add_column("key", style="cyan")
    table.add_column("value")
    table.add_row("路径", str(bundle_path))
    table.add_row("标题", args.title)
    if args.description:
        table.add_row("描述", args.description)
    if args.tags:
        table.add_row("tags", ", ".join(args.tags))
    if args.categories:
        table.add_row("categories", ", ".join(args.categories))
    table.add_row("日期", date_str)
    table.add_row("draft", "false (no-draft)" if args.no_draft else "true")
    table.add_row("featured", "✓" if args.featured else "—")
    table.add_row("gallery/", "将创建（空目录）")
    console.print(table)

    console.print("\n[bold]front matter 预览：[/bold]")
    console.print(Panel(fm_text, title="index.md"))

    if args.dry_run:
        console.print("\n[yellow]⚠ DRY-RUN：未实际创建[/yellow]")
        return 0

    # 7. 执行
    bundle_path.mkdir(parents=True, exist_ok=False)
    (bundle_path / "index.md").write_text(fm_text, encoding="utf-8")
    (bundle_path / "gallery").mkdir(exist_ok=True)
    if args.featured:
        (bundle_path / "featured.jpg").write_bytes(b"")

    console.print(f"\n[green]✓[/green] 已创建 [bold]{bundle_path}[/bold]")
    console.print("\n[dim]下一步：[/dim]")
    console.print(f"  1. 编辑 [cyan]{bundle_path}/index.md[/cyan] 写正文")
    console.print(f"  2. 配图: [cyan]pnpm run media:save {bundle_path} <图片...>[/cyan]")
    console.print(f"  3. 预览: [cyan]pnpm run site:dev[/cyan]")
    console.print("  4. 发布: 去掉 [cyan]draft: true[/cyan] 后手动 [cyan]git commit && git push[/cyan]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
