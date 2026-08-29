#!/usr/bin/env python3
"""批量修复 markdown fenced code blocks 缺语言的问题。

读取 markdownlint-cli2 输出，为每个 MD040 错误的 ``` 行添加合适的 language。

策略：
- 启发式：扫描 ``` 后几行内容识别语言（python/bash/yaml/json/sql/sh/text）
- 未知类型：默认 text（保守策略）
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# 语言关键字检测（按优先级排序）
LANG_KEYWORDS = [
    ("python", [r"\bimport\s+\w+", r"\bdef\s+\w+\(", r"\bclass\s+\w+", r"\bprint\(", r"\bfrom\s+\w+\s+import"]),
    ("bash", [r"\$\s+", r"#!/bin/(ba)?sh", r"\becho\s+", r"\bcd\s+", r"\bgrep\s+", r"\bcurl\s+"]),
    ("yaml", [r"^\s*\w+:\s+\S+", r"^\s*-\s+\w+:", r"^---\s*$"]),
    ("json", [r'^\s*\{', r'^\s*\[', r'"\w+":\s*']),
    ("sql", [r"\bSELECT\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bFROM\b", r"\bWHERE\b"]),
    ("html", [r"<\w+", r"</\w+>", r"<!DOCTYPE"]),
    ("css", [r"^\s*\w+\s*\{", r"^\s*\.\w+", r"@media", r"color:\s*"]),
    ("javascript", [r"\bfunction\s+\w+", r"\bconst\s+\w+", r"\blet\s+\w+", r"\bvar\s+\w+", r"=>\s*\{"]),
    ("go", [r"\bfunc\s+\w+\(", r"\bpackage\s+\w+", r"\bimport\s+\("]),
    ("toml", [r"^\[\w+\]", r"^\s*\w+\s*=\s*"]),
    ("sh", [r"\$\s+", r"#!/bin/sh", r"\becho\s+"]),
]


def detect_lang(content: str) -> str:
    """根据 code block 内容推测语言。"""
    for lang, patterns in LANG_KEYWORDS:
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE):
                return lang
    return "text"


def fix_file(filepath: Path, errors: list[tuple[int, int]]) -> int:
    """修复单个文件中所有 MD040 错误（line, col）。"""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    # 按行号从大到小处理（避免修改时偏移）
    errors_sorted = sorted(errors, key=lambda x: x[0], reverse=True)

    fixes = 0
    for line_no, _ in errors_sorted:
        idx = line_no - 1
        if idx >= len(lines):
            continue
        line = lines[idx]
        # 找到 ``` 后面的内容（应该没有语言）
        match = re.match(r"^(\s*)```(\s*)(.*)$", line)
        if not match:
            continue
        indent, _spaces, rest = match.groups()
        if rest.strip():
            # 已经有语言标记（如 ```text），跳过
            continue

        # 找到对应的结束 ```（向下扫描）
        end_idx = None
        for j in range(idx + 1, len(lines)):
            if lines[j].strip().startswith("```") and lines[j].strip() == "```":
                end_idx = j
                break
        if end_idx is None:
            continue

        # 获取 code block 内容
        block_content = "\n".join(lines[idx + 1:end_idx])

        # 推测语言
        lang = detect_lang(block_content)

        # 替换 ``` 行
        lines[idx] = f"{indent}```{lang}"

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return fixes


def main() -> int:
    """主流程：扫描 markdownlint 输出，逐文件修复。"""
    # 1. 跑 markdownlint，收集 MD040 错误
    result = subprocess.run(
        ["pnpm", "exec", "markdownlint-cli2"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # markdownlint 输出走 STDERR
    output = result.stderr or result.stdout

    # 按文件分组
    errors_by_file: dict[Path, list[tuple[int, int]]] = {}
    for line in output.split("\n"):
        match = re.match(r"^([^:]+):(\d+):?(\d+)?\s+error MD040/", line)
        if not match:
            continue
        filepath = Path(match.group(1))
        line_no = int(match.group(2))
        col = int(match.group(3) or 1)
        errors_by_file.setdefault(filepath, []).append((line_no, col))

    # 2. 逐文件修复
    total_fixes = 0
    for filepath, errors in errors_by_file.items():
        if not filepath.exists():
            continue
        fixes = fix_file(filepath, errors)
        total_fixes += fixes
        print(f"  {filepath.name}: {fixes} fenced code blocks fixed")

    print(f"\n✓ 总计修复 {total_fixes} 个 MD040 警告")
    return 0


if __name__ == "__main__":
    sys.exit(main())