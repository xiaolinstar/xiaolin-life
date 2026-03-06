#!/usr/bin/env python3
"""
将异常系列文章的 Markdown 转换为公众号/知乎友好的格式。

主要处理：
1. 将站内链接 [text](exception-XX.md) 转为纯文本引用
2. 将相对图片路径标注提醒（需手动上传到平台）

使用方式：
    python convert_for_wechat.py exception-06.md
    python convert_for_wechat.py exception-06.md exception-07.md exception-08.md
    python convert_for_wechat.py --all  # 转换所有 exception-*.md

输出文件保存在 wechat/ 子目录下。
"""

import re
import sys
import os
from pathlib import Path

# 文章编号到标题的映射（用于将链接转为可读文本）
ARTICLE_TITLES = {
    "exception-00.md": "四项核心原则",
    "exception-01.md": "异常基础",
    "exception-02.md": "异常分类",
    "exception-03.md": "异常抛出",
    "exception-04.md": "异常处理",
    "exception-05.md": "系统性总结",
    "exception-06.md": "异常文件结构",
    "exception-07.md": "异常类与错误码设计",
    "exception-08.md": "全局异常处理器与项目集成",
}


def convert_internal_links(content: str) -> str:
    """
    将站内链接转为纯文本引用。

    [02篇](exception-02.md) → 02篇《异常分类》
    [四项核心原则](exception-00.md) → 《四项核心原则》
    [02-异常分类](exception-02.md) → 《异常分类》
    """
    def replace_link(match):
        link_text = match.group(1)
        link_target = match.group(2)

        # 只处理站内 exception-XX.md 链接
        if not re.match(r'exception-\d+\.md', link_target):
            return match.group(0)  # 非站内链接保持原样

        article_title = ARTICLE_TITLES.get(link_target, "")

        if article_title and article_title in link_text:
            # 链接文字已包含标题，直接加书名号
            return f"《{link_text}》"
        elif article_title:
            # 链接文字是简称（如 "02篇"），补充标题
            return f"{link_text}《{article_title}》"
        else:
            return link_text

    # 匹配 [text](target) 但排除图片 ![text](target)
    pattern = r'(?<!!)\[([^\]]+)\]\(([^)]+)\)'
    return re.sub(pattern, replace_link, content)


def convert_image_paths(content: str) -> str:
    """
    将相对路径图片标注为需要手动上传。

    ![alt](../img-xxx/file.png) → ![alt](../img-xxx/file.png)
    <!-- ⚠️ 公众号发布提醒：上述图片需手动上传 -->
    """
    def replace_image(match):
        original = match.group(0)
        path = match.group(2)
        if path.startswith('http'):
            return original  # 网络图片保持不变
        return f"{original}\n<!-- ⚠️ 公众号发布提醒：上述图片 {path} 需手动上传到平台 -->"

    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, content)


def add_series_navigation(content: str, current_file: str) -> str:
    """在文末添加系列文章导航（纯文本版）。"""
    # 提取当前文章编号
    match = re.search(r'exception-(\d+)', current_file)
    if not match:
        return content

    current_num = int(match.group(1))

    nav_lines = ["\n---\n", "**异常系列文章导航**\n"]

    for filename, title in sorted(ARTICLE_TITLES.items()):
        num_match = re.search(r'exception-(\d+)', filename)
        if num_match:
            num = int(num_match.group(1))
            prefix = "▶ " if num == current_num else "　 "
            category = "架构设计" if num <= 5 else "编程实践"
            nav_lines.append(f"{prefix}{num:02d}. {title}（{category}）")

    content = content.rstrip() + "\n" + "\n".join(nav_lines) + "\n"
    return content


def convert_file(input_path: str) -> str:
    """转换单个文件。"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = convert_internal_links(content)
    content = convert_image_paths(content)
    content = add_series_navigation(content, os.path.basename(input_path))

    return content


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "wechat")
    os.makedirs(output_dir, exist_ok=True)

    if sys.argv[1] == "--all":
        files = sorted(Path(script_dir).glob("exception-*.md"))
    else:
        files = [Path(f) for f in sys.argv[1:]]

    for filepath in files:
        if not filepath.exists():
            print(f"⚠️  文件不存在: {filepath}")
            continue

        converted = convert_file(str(filepath))
        output_path = os.path.join(output_dir, filepath.name)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted)

        print(f"✅ {filepath.name} → wechat/{filepath.name}")

    print(f"\n转换完成！输出目录: {output_dir}")
    print("提示：将输出文件粘贴到 mdnice.com 或墨滴编辑器中，即可生成公众号排版。")


if __name__ == "__main__":
    main()
