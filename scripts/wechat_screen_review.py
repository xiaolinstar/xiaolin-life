#!/usr/bin/env python3
"""Convert a screen-review Markdown page into a WeChat publish pack HTML."""

from __future__ import annotations

import argparse
import html as html_lib
import re
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FONT_SANS = (
    "-apple-system,BlinkMacSystemFont,'PingFang SC',"
    "'Hiragino Sans GB','Microsoft YaHei',sans-serif"
)
FONT_SERIF = "'Songti SC','Noto Serif SC','STSong',serif"

P = (
    "margin:0 0 18px;color:#222222;font-size:16px;line-height:1.9;"
    f"text-align:justify;font-family:{FONT_SANS};"
)
CAPTION = (
    "margin:8px 0 0;color:#888888;font-size:13px;line-height:1.6;"
    f"text-align:center;font-family:{FONT_SANS};"
)


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith(" ") or line.startswith("-"):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, body


def inline_md(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def extract_movie_info(body: str) -> tuple[str, str, str]:
    m = re.search(
        r">\s*\*\*电影信息\*\*\s*\n>\s*(.+?)\n>\s*(.+?)(?:\n\n|\n##)",
        body,
        re.S,
    )
    if m:
        line1 = re.sub(r"^>\s*", "", m.group(1)).strip()
        line2 = re.sub(r"^>\s*", "", m.group(2)).strip()
        return line1, line2, body[m.end() :]
    return "", "", body


def convert_body(body: str) -> str:
    body = re.sub(
        r">\s*\*\*电影信息\*\*.*?(?=\n## |\n### |\Z)",
        "",
        body,
        count=1,
        flags=re.S,
    )

    lines = body.splitlines()
    out: list[str] = []
    i = 0
    quote_buf: list[str] = []

    def flush_quote() -> None:
        nonlocal quote_buf
        chunks = [
            re.sub(r"^>\s?", "", q).strip().strip("*").strip()
            for q in quote_buf
            if q.strip() not in {"", ">"}
        ]
        quote_buf = []
        if not chunks:
            return
        inner: list[str] = []
        for idx, t in enumerate(chunks):
            style = (
                "margin:0 0 8px;color:#444444;font-size:15px;line-height:1.75;font-style:italic;"
                if idx == 0 and re.search(r"[A-Za-z]", t)
                else "margin:0;color:#222222;font-size:15px;line-height:1.75;"
            )
            if idx == len(chunks) - 1:
                style = style.replace("margin:0 0 8px", "margin:0")
            inner.append(f'<p style="{style}font-family:{FONT_SANS};">{inline_md(t)}</p>')
        out.append(
            '<section style="margin:20px 0;padding:12px 14px 12px 16px;'
            'border-left:3px solid #222222;background:#f7f7f5;">'
            + "".join(inner)
            + "</section>"
        )

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        if raw.startswith(">"):
            quote_buf.append(raw)
            i += 1
            continue
        flush_quote()

        if not raw:
            i += 1
            continue

        if raw == "---":
            out.append(
                '<p style="margin:28px 0 20px;border-top:1px solid #e6e6e6;'
                'font-size:0;line-height:0;">&nbsp;</p>'
            )
            i += 1
            continue

        if raw.startswith("## "):
            title = inline_md(raw[3:].strip())
            out.append(
                f'<h2 style="margin:32px 0 14px;padding:0 0 8px;color:#111111;'
                f"font-size:18px;line-height:1.5;font-weight:600;"
                f"border-bottom:1px solid #e6e6e6;font-family:{FONT_SERIF};\">{title}</h2>"
            )
            i += 1
            continue

        if raw.startswith("### "):
            title = inline_md(raw[4:].strip())
            out.append(
                f'<h3 style="margin:26px 0 12px;color:#111111;font-size:17px;'
                f'line-height:1.5;font-weight:600;font-family:{FONT_SERIF};">{title}</h3>'
            )
            i += 1
            continue

        img = re.match(r"!\[(.*?)\]\((.*?)\)", raw)
        if img:
            alt, src = img.group(1), img.group(2)
            caption = ""
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                cand = lines[j].strip()
                if cand.startswith("*") and cand.endswith("*") and not cand.startswith("**"):
                    caption = cand.strip("*").strip()
                    i = j
            block = (
                '<section style="margin:22px 0;">'
                f'<img src="{src}" alt="{inline_md(alt)}" '
                'style="display:block;width:100%;max-width:100%;margin:0 auto;border:0;" />'
            )
            if caption:
                block += f'<p style="{CAPTION}">{inline_md(caption)}</p>'
            block += "</section>"
            out.append(block)
            i += 1
            continue

        if raw.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(inline_md(lines[i][2:].strip()))
                i += 1
            lis = "".join(
                f'<p style="margin:0 0 8px;color:#222222;font-size:16px;line-height:1.9;'
                f'font-family:{FONT_SANS};">· {item}</p>'
                for item in items
            )
            out.append(f'<section style="margin:0 0 18px;padding-left:4px;">{lis}</section>')
            continue

        if raw.startswith("|"):
            i += 1
            continue

        out.append(f'<p style="{P}">{inline_md(raw)}</p>')
        i += 1

    flush_quote()
    return "\n".join(out)


def build_article_body(
    film_title: str,
    info1: str,
    info2: str,
    dims: str,
    overall: str,
    lead: str,
    body_html: str,
) -> str:
    """正文区：不含公众号标题/摘要，避免和后台字段重复。"""
    return f"""<section id="article-body" style="max-width:677px;margin:0 auto;padding:8px 0 24px;background:#ffffff;color:#222222;font-family:{FONT_SANS};font-size:16px;line-height:1.9;">
    <p style="margin:0 0 8px;color:#888888;font-size:12px;letter-spacing:4px;text-align:center;">光影人生</p>
    <p style="margin:0 0 20px;color:#666666;font-size:14px;line-height:1.7;text-align:center;font-family:{FONT_SERIF};">《{inline_md(film_title)}》</p>
    <p style="margin:0 0 20px;border-top:1px solid #e6e6e6;font-size:0;line-height:0;">&nbsp;</p>
    <p style="margin:0 0 6px;color:#555555;font-size:14px;line-height:1.8;text-align:center;">{inline_md(info1)}</p>
    <p style="margin:0 0 24px;color:#555555;font-size:14px;line-height:1.8;text-align:center;">{inline_md(info2)}</p>
    <section style="margin:0 0 28px;padding:16px 14px;background:#f7f7f5;border:1px solid #ecece8;">
      <p style="margin:0 0 8px;color:#888888;font-size:12px;letter-spacing:3px;text-align:center;">评分推荐</p>
      <p style="margin:0 0 10px;color:#333333;font-size:14px;line-height:1.8;text-align:center;">{inline_md(dims)}</p>
      <p style="margin:0;color:#111111;font-size:20px;line-height:1.4;font-weight:600;text-align:center;font-family:{FONT_SERIF};">综合 {inline_md(overall)}</p>
    </section>
    <p style="{P}">{inline_md(lead)}</p>
{body_html}
    <p style="margin:28px 0 0;color:#888888;font-size:12px;line-height:1.7;text-align:center;letter-spacing:1px;">— 光影人生 · 好好生活 —</p>
  </section>"""


def build_pack_html(
    *,
    wechat_title: str,
    digest: str,
    film_title: str,
    cover_file: str,
    cover_note: str,
    article_body: str,
) -> str:
    esc_title = html_lib.escape(wechat_title)
    esc_digest = html_lib.escape(digest)
    digest_len = len(digest)
    digest_hint = "建议 54–120 字" if digest_len > 120 else f"当前 {digest_len} 字"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>公众号发布包 · {esc_title}</title>
  <style>
    :root {{
      --ink: #111;
      --muted: #666;
      --line: #e6e6e6;
      --panel: #f7f7f5;
      --accent: #222;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #efefed;
      color: var(--ink);
      font-family: {FONT_SANS};
    }}
    .shell {{
      max-width: 920px;
      margin: 0 auto;
      padding: 24px 16px 64px;
    }}
    .hero {{
      margin-bottom: 20px;
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 22px;
      font-family: {FONT_SERIF};
      font-weight: 600;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.7;
    }}
    .panel {{
      background: #fff;
      border: 1px solid var(--line);
      margin-bottom: 16px;
      padding: 16px;
    }}
    .panel-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .panel-label {{
      font-size: 12px;
      letter-spacing: 3px;
      color: #888;
      text-transform: uppercase;
    }}
    .panel-meta {{
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }}
    .copy-value {{
      margin: 0;
      padding: 12px 14px;
      background: var(--panel);
      border: 1px solid #ecece8;
      font-size: 16px;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .copy-value.title {{
      font-family: {FONT_SERIF};
      font-size: 20px;
      font-weight: 600;
    }}
    button.copy-btn {{
      border: 1px solid #222;
      background: #222;
      color: #fff;
      font-size: 13px;
      padding: 6px 12px;
      cursor: pointer;
      flex-shrink: 0;
    }}
    button.copy-btn:hover {{ opacity: 0.88; }}
    button.copy-btn.ok {{ background: #2f6b3a; border-color: #2f6b3a; }}
    .cover-wrap img {{
      display: block;
      width: 100%;
      max-width: 677px;
      margin: 0 auto 10px;
      border: 0;
    }}
    .body-frame {{
      border: 1px dashed #d2d2ce;
      padding: 12px;
      background: #fff;
    }}
    .toast {{
      position: fixed;
      right: 16px;
      bottom: 16px;
      background: #222;
      color: #fff;
      padding: 10px 14px;
      font-size: 13px;
      opacity: 0;
      pointer-events: none;
      transition: opacity .2s ease;
    }}
    .toast.show {{ opacity: 1; }}
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <h1>光影人生 · 公众号发布包</h1>
      <p>标题 / 摘要填后台对应字段；正文点「复制正文」后粘贴到编辑器。封面用站点同款图，在后台「封面」处本地上传。</p>
    </div>

    <section class="panel">
      <div class="panel-head">
        <div class="panel-label">封面 COVER</div>
      </div>
      <p class="panel-meta">{html_lib.escape(cover_note)}</p>
      <div class="cover-wrap">
        <img src="{html_lib.escape(cover_file)}" alt="公众号封面预览" />
      </div>
      <p class="panel-meta">本地文件：<code>{html_lib.escape(cover_file)}</code>（与本 HTML 同目录，直接拖到公众号封面上传即可）</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div class="panel-label">标题 TITLE</div>
        <button type="button" class="copy-btn" data-copy-text="{esc_title}">复制标题</button>
      </div>
      <p class="panel-meta">粘贴到公众号「标题」输入框（不要再当正文大标题重复贴一遍）。</p>
      <p class="copy-value title" id="field-title">{esc_title}</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div class="panel-label">摘要 DIGEST</div>
        <button type="button" class="copy-btn" data-copy-text="{esc_digest}">复制摘要</button>
      </div>
      <p class="panel-meta">粘贴到公众号「摘要」；{digest_hint}。列表页与转发时显示。</p>
      <p class="copy-value" id="field-digest">{esc_digest}</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div class="panel-label">正文 BODY</div>
        <button type="button" class="copy-btn" data-copy-body="article-body">复制正文</button>
      </div>
      <p class="panel-meta">正文只保留栏目、片名、信息、评分与影评内容；公众号标题与摘要已拆出。片名识别：《{html_lib.escape(film_title)}》</p>
      <div class="body-frame">
{article_body}
      </div>
    </section>
  </div>

  <div class="toast" id="toast">已复制</div>
  <script>
    const toast = document.getElementById('toast');
    function flash(msg) {{
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1400);
    }}
    async function copyText(text, btn) {{
      try {{
        await navigator.clipboard.writeText(text);
      }} catch (err) {{
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }}
      if (btn) {{
        const old = btn.textContent;
        btn.classList.add('ok');
        btn.textContent = '已复制';
        setTimeout(() => {{ btn.classList.remove('ok'); btn.textContent = old; }}, 1200);
      }}
      flash('已复制');
    }}
    document.querySelectorAll('[data-copy-text]').forEach((btn) => {{
      btn.addEventListener('click', () => copyText(btn.getAttribute('data-copy-text') || '', btn));
    }});
    document.querySelectorAll('[data-copy-body]').forEach((btn) => {{
      btn.addEventListener('click', async () => {{
        const id = btn.getAttribute('data-copy-body');
        const node = document.getElementById(id);
        if (!node) return;
        const range = document.createRange();
        range.selectNodeContents(node);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        try {{
          document.execCommand('copy');
          flash('正文已复制，可粘贴到公众号编辑器');
          const old = btn.textContent;
          btn.classList.add('ok');
          btn.textContent = '已复制';
          setTimeout(() => {{ btn.classList.remove('ok'); btn.textContent = old; }}, 1200);
        }} catch (err) {{
          flash('复制失败，请手动选中正文区');
        }}
        sel.removeAllRanges();
      }});
    }});
  </script>
</body>
</html>
"""


def resolve_cover(src_dir: Path, dest_dir: Path, slug: str) -> tuple[str, str]:
    """Copy page featured/cover image beside the HTML for WeChat upload."""
    candidates = [
        src_dir / "featured.jpg",
        src_dir / "featured.png",
        src_dir / "feature.jpg",
        src_dir / "cover.jpg",
        src_dir / "background.jpg",
    ]
    src_cover = next((p for p in candidates if p.is_file()), None)
    if not src_cover:
        return "", "未找到站点封面（featured.jpg）。请自行准备 2.35:1 或 16:9 横图后上传。"
    dest_name = f"{slug}-cover{src_cover.suffix.lower()}"
    dest_cover = dest_dir / dest_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_cover, dest_cover)
    note = (
        f"建议直接使用站点封面（{src_cover.name}，已复制到发布包旁）。"
        "当前为 16:9，公众号横版封面可用；如后台裁切框偏宽，可略微居中裁切。"
    )
    return dest_name, note


def sync_status(src: Path, dest: Path) -> tuple[str, bool]:
    """Return (message, is_fresh). Fresh means HTML exists and is newer than MD (+ cover source)."""
    if not dest.is_file():
        return f"missing {dest.name}", False
    src_mtime = src.stat().st_mtime
    dest_mtime = dest.stat().st_mtime
    if src_mtime > dest_mtime:
        return (
            f"STALE: {src.relative_to(ROOT)} newer than {dest.relative_to(ROOT)} "
            f"(md mtime > html). Re-run export before publishing or committing.",
            False,
        )
    featured = src.parent / "featured.jpg"
    if featured.is_file() and featured.stat().st_mtime > dest_mtime:
        return (
            f"STALE: {featured.relative_to(ROOT)} newer than {dest.relative_to(ROOT)}. Re-run export.",
            False,
        )
    return f"fresh: {dest.relative_to(ROOT)} >= source mtimes", True


def convert_file(src: Path, dest: Path, wechat_title: str = "") -> None:
    text = src.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    info1, info2, body = extract_movie_info(body)

    score_m = re.search(
        r"## 评分推荐\s*\n\s*\|[^\n]+\|\s*\n\|[^\n]+\|\s*\n\|([^\n]+)\|\s*\n\s*\n(.+?)\s*\n\s*\n(?=## )",
        body,
        re.S,
    )
    dims = overall = lead = ""
    if score_m:
        cells = [c.strip().replace("**", "") for c in score_m.group(1).split("|") if c.strip()]
        labels = ["剧情", "主题", "表演", "配乐"]
        dims = " · ".join(f"{labels[i]} {cells[i]}" for i in range(min(4, len(cells))))
        overall = cells[4] if len(cells) > 4 else ""
        lead = score_m.group(2).strip()
        body = body[score_m.end() :]
    else:
        body = re.sub(r"## 评分推荐.*?(?=\n## )", "", body, count=1, flags=re.S)

    film_title = meta.get("title", src.parent.name)
    digest = meta.get("summary") or meta.get("description") or ""
    title = wechat_title.strip() or film_title

    body_html = convert_body(body)
    article_body = build_article_body(film_title, info1, info2, dims, overall, lead, body_html)

    dest.parent.mkdir(parents=True, exist_ok=True)
    cover_file, cover_note = resolve_cover(src.parent, dest.parent, src.parent.name)
    html = build_pack_html(
        wechat_title=title,
        digest=digest,
        film_title=film_title,
        cover_file=cover_file or "",
        cover_note=cover_note,
        article_body=article_body,
    )
    # Stamp source path + mtime into HTML for later --check / human audit.
    stamp = (
        f"<!-- source: {src.relative_to(ROOT)} "
        f"mtime:{int(src.stat().st_mtime)} exported:{int(time.time())} -->\n"
    )
    dest.write_text(stamp + html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        default="content/screen/shawshank-redemption/index.md",
        help="Markdown page path",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
        help="Output HTML path (default: docs/wechat/<slug>.html)",
    )
    parser.add_argument(
        "--title",
        default="",
        help="WeChat article title (后台标题；默认同页面 title)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check whether existing HTML is newer than Markdown; exit 1 if stale/missing",
    )
    args = parser.parse_args()
    src = (ROOT / args.source).resolve()
    if not src.is_file():
        raise SystemExit(f"source not found: {src}")
    if args.output:
        dest = (ROOT / args.output).resolve()
    else:
        dest = ROOT / "docs" / "wechat" / f"{src.parent.name}.html"

    if args.check:
        msg, fresh = sync_status(src, dest)
        print(msg)
        raise SystemExit(0 if fresh else 1)

    # Always overwrite: publish pack must match current Markdown, never reuse stale HTML.
    if dest.is_file():
        _, fresh = sync_status(src, dest)
        if not fresh:
            print(f"note: rebuilding stale pack → {dest.relative_to(ROOT)}")
        else:
            print(f"note: rebuilding anyway (export always re-renders from MD)")
    convert_file(src, dest, wechat_title=args.title)
    print(f"wrote {dest.relative_to(ROOT)}")
    msg, fresh = sync_status(src, dest)
    print(msg)
    if not fresh:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
