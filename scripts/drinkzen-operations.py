#!/usr/bin/env python3
"""DrinkZen 本地发布台账：登记真实发布、保留历史、检查版本与采集效果。"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/drinkzen-operations.json"
PLATFORMS = ("xiaohongshu", "dianping")
MARKER = "\n## plog 分发版"
METRICS = ("views", "likes", "saves", "comments", "profile_visits", "miniapp_visits", "product_queries")


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "articles": {}}
    ledger = json.loads(path.read_text(encoding="utf-8"))
    if ledger.get("schema_version") != 1 or not isinstance(ledger.get("articles"), dict):
        raise ValueError("台账格式或版本不支持")
    return ledger


def save_ledger(path: Path, ledger: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def article_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / "content/drinkzen").resolve()) or path.name != "index.md" or not path.is_file():
        raise ValueError("article 必须是现存的 content/drinkzen/**/index.md")
    return path


def snapshot(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    origin, separator, plog = text.partition(MARKER)
    if not separator or not plog.strip():
        raise ValueError("文章没有 plog 分发版，不能登记社媒发布版本")
    digest = lambda value: hashlib.sha256(value.strip().encode("utf-8")).hexdigest()
    return {"origin_sha256": digest(origin), "plog_sha256": digest(plog)}


def timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("时间须带时区，例如 2026-10-11T11:30:00+08:00")
    return parsed.isoformat()


def publication_url(value: str, platform: str) -> str:
    parsed = urlparse(value)
    domains = {"xiaohongshu": ("xiaohongshu.com", "xhslink.com"), "dianping": ("dianping.com",)}[platform]
    hostname = parsed.hostname or ""
    if parsed.scheme not in ("http", "https") or parsed.username or parsed.password or not any(
        hostname == domain or hostname.endswith("." + domain) for domain in domains
    ):
        raise ValueError("发布链接域名不属于所选平台")
    return value


def entry_for(ledger: dict, path: Path) -> dict:
    return ledger["articles"].setdefault(path.relative_to(ROOT).as_posix(), {
        "product_id": None, "menu_evidence": None, "menu_checked_at": None,
        "followup": None, "platforms": {},
    })


def collect_status(ledger: dict) -> list[dict]:
    candidates = {
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "content/drinkzen").rglob("index.md")
        if MARKER in p.read_text(encoding="utf-8")
    } | set(ledger["articles"])
    rows = []
    for key in sorted(candidates):
        entry = ledger["articles"].get(key, {})
        try:
            current = snapshot(article_path(key))
            problem = None
        except ValueError as exc:
            current, problem = None, str(exc)
        platforms = {}
        for platform in PLATFORMS:
            history = entry.get("platforms", {}).get(platform, {}).get("history", [])
            if not history:
                platforms[platform] = "未登记"
            elif current is None or any(history[-1].get(k) != v for k, v in current.items()):
                platforms[platform] = "待同步"
            else:
                platforms[platform] = "已登记当前版本"
        rows.append({
            "article": key, "product_id": entry.get("product_id"),
            "menu_checked_at": entry.get("menu_checked_at"),
            "followup": entry.get("followup"), "problem": problem, "platforms": platforms,
        })
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status", help="只读查看版本与待办")
    status.add_argument("--json", action="store_true")
    link = sub.add_parser("link", help="登记实际产品关联与菜单证据，不同步后台")
    link.add_argument("--article", required=True)
    link.add_argument("--product-id")
    link.add_argument("--menu-evidence")
    link.add_argument("--menu-checked-at")
    record = sub.add_parser("record", help="实际发布或线上纠正后登记，保留历史")
    record.add_argument("--article", required=True)
    record.add_argument("--platform", choices=PLATFORMS, required=True)
    record.add_argument("--url", required=True)
    record.add_argument("--published-at", required=True)
    record.add_argument("--note", required=True)
    metrics = sub.add_parser("metrics", help="给最近一次发布追加观测，不填的数值为未知")
    metrics.add_argument("--article", required=True)
    metrics.add_argument("--platform", choices=PLATFORMS, required=True)
    metrics.add_argument("--observed-at", required=True)
    metrics.add_argument("--note", required=True)
    for metric in METRICS:
        metrics.add_argument("--" + metric.replace("_", "-"), type=int)
    note = sub.add_parser("note", help="登记或解决外部菜单变化等跟进事项")
    note.add_argument("--article", required=True)
    group = note.add_mutually_exclusive_group(required=True)
    group.add_argument("--text")
    group.add_argument("--resolved", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        ledger = load_ledger(args.ledger)
        if args.command == "status":
            rows = collect_status(ledger)
            if args.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                for row in rows:
                    states = " / ".join(f"{p}={row['platforms'][p]}" for p in PLATFORMS)
                    print(f"{row['article']}: menu={row['menu_checked_at'] or '未核实'} product={row['product_id'] or '待关联'} {states}")
                    if row["followup"] or row["problem"]:
                        print(f"  跟进：{row['followup'] or row['problem']}")
                print(f"共 {len(rows)} 篇；状态仅来自本地台账，不代表已核验线上内容。")
            return
        path = article_path(args.article)
        entry = entry_for(ledger, path)
        if args.command == "link":
            if not args.product_id and not args.menu_evidence:
                raise ValueError("至少登记产品 ID 或菜单证据")
            if bool(args.menu_evidence) != bool(args.menu_checked_at):
                raise ValueError("菜单证据与核实日期必须一起提供")
            if args.product_id:
                entry["product_id"] = args.product_id
            if args.menu_evidence:
                date.fromisoformat(args.menu_checked_at)
                entry.update(menu_evidence=args.menu_evidence, menu_checked_at=args.menu_checked_at)
        elif args.command == "record":
            event = {
                "url": publication_url(args.url, args.platform),
                "published_at": timestamp(args.published_at),
                **snapshot(path), "note": args.note,
            }
            platform = entry["platforms"].setdefault(args.platform, {"history": [], "metrics": []})
            platform["history"].append(event)
        elif args.command == "metrics":
            platform = entry["platforms"].get(args.platform)
            if not platform or not platform["history"]:
                raise ValueError("先登记真实发布，再记录观测数据")
            values = {metric: getattr(args, metric) for metric in METRICS}
            if any(value is not None and value < 0 for value in values.values()):
                raise ValueError("观测数据不能为负数")
            observed_at = timestamp(args.observed_at)
            if datetime.fromisoformat(observed_at) < datetime.fromisoformat(platform["history"][-1]["published_at"]):
                raise ValueError("观测时间不能早于发布/修正时间")
            platform["metrics"].append({
                "observed_at": observed_at, "publication_index": len(platform["history"]) - 1,
                **values, "note": args.note,
            })
        elif args.command == "note":
            entry["followup"] = None if args.resolved else args.text
        save_ledger(args.ledger, ledger)
        print(f"已更新本地台账：{path.relative_to(ROOT)}；未执行线上写入。")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
