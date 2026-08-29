#!/usr/bin/env python3
"""生成奶茶仙人评级数据卡（PNG 图）。

数据卡用于小红书/大众点评分发的「图 4 数据卡」位，
以信息图形式呈现品牌评级 + 核心营养数据。

Usage:
  python3 scripts/generate-rating-card.py \
    --drink "生椰拿铁" \
    --brand "瑞幸咖啡" \
    --size "大杯 450ml" \
    --calories 160 \
    --sugar 7.35 \
    --sat-fat 2.43 \
    --sat-fat-unit "g/100ml" \
    --grade C \
    --config "冰 / 不另外加糖 / 1 份浓缩" \
    --price 21 \
    --output /tmp/rating-card.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ---------- 设计常量 ----------

# 输出尺寸：3:4 竖图（小红书/大众点评主流）
WIDTH = 1080
HEIGHT = 1440

# 配色
COLOR_BG_TOP = (255, 250, 244)        # 米白
COLOR_BG_BOTTOM = (245, 235, 220)     # 米色
COLOR_BRAND = (60, 40, 30)            # 深棕
COLOR_DRINK_NAME = (40, 40, 40)       # 深灰
COLOR_DATA = (60, 60, 60)             # 灰色
COLOR_LABEL = (140, 120, 100)         # 暖灰
COLOR_DIVIDER = (220, 210, 195)       # 分隔线
COLOR_FOOTER = (160, 140, 110)        # 页脚灰

# Nutri-Grade 评级颜色（参考新加坡 Nutri-Grade 标识色）
GRADE_COLORS = {
    "A": (76, 175, 80),     # 绿
    "B": (139, 195, 74),    # 黄绿
    "C": (255, 152, 0),     # 橙
    "D": (244, 67, 54),     # 红
}

# 字体路径（系统已装 Noto Sans CJK SC）
FONT_PATH = Path.home() / ".fonts" / "NotoSansCJKsc-Regular.otf"


# ---------- 文本尺寸辅助 ----------

def get_text_size(font: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    """统一不同 Pillow 版本的 getbbox/getsize 接口。"""
    try:
        # Pillow ≥ 10.0
        left, top, right, bottom = font.getbbox(text)
        return right - left, bottom - top
    except AttributeError:
        # Pillow < 10.0
        return font.getsize(text)


def center_x(font: ImageFont.FreeTypeFont, text: str, y: int,
             draw: ImageDraw.ImageDraw, fill, img_width: int = WIDTH) -> None:
    """水平居中绘制单行文本。"""
    tw, _ = get_text_size(font, text)
    x = (img_width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


# ---------- 主绘制流程 ----------

def draw_card(*, drink: str, brand: str, size: str, calories: int,
              sugar: float, sat_fat: float, sat_fat_unit: str,
              cup_ml: int, grade: str, config: str, price: int | None,
              output: Path) -> None:
    """绘制一张数据卡并保存为 PNG。"""
    grade = grade.upper()
    if grade not in GRADE_COLORS:
        raise ValueError(f"grade 必须是 A/B/C/D 之一，得到 {grade}")

    # 饱和脂肪单位换算：g/100ml → g/杯
    if sat_fat_unit == "g/100ml":
        sat_fat_total = sat_fat * cup_ml / 100
        sat_fat_display_unit = "g/杯"
        sat_fat_display_value = f"{sat_fat_total:.1f}"
    else:
        sat_fat_display_unit = sat_fat_unit
        sat_fat_display_value = f"{sat_fat:g}"

    # 加载字体（不同字号）
    font_brand = ImageFont.truetype(str(FONT_PATH), 36)
    font_grade_big = ImageFont.truetype(str(FONT_PATH), 260)  # 缩 100px 避免与"级"字重叠
    font_grade_sub = ImageFont.truetype(str(FONT_PATH), 72)
    font_drink = ImageFont.truetype(str(FONT_PATH), 72)
    font_size_label = ImageFont.truetype(str(FONT_PATH), 44)
    font_data_value = ImageFont.truetype(str(FONT_PATH), 76)
    font_data_label = ImageFont.truetype(str(FONT_PATH), 44)  # 36→44 更醒目
    font_config = ImageFont.truetype(str(FONT_PATH), 44)
    font_footer = ImageFont.truetype(str(FONT_PATH), 32)  # 价格作为脚注，字号最小化

    # 创建画布 + 米色渐变背景
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG_TOP)
    draw = ImageDraw.Draw(img)

    # 底部渐变（用多个水平条模拟）
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLOR_BG_TOP[0] * (1 - ratio) + COLOR_BG_BOTTOM[0] * ratio)
        g = int(COLOR_BG_TOP[1] * (1 - ratio) + COLOR_BG_BOTTOM[1] * ratio)
        b = int(COLOR_BG_TOP[2] * (1 - ratio) + COLOR_BG_BOTTOM[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # ---- 顶部品牌头 ----
    center_x(font_brand, "奶茶仙人 DrinkZen", y=80, draw=draw,
             fill=COLOR_BRAND)
    # 分隔线
    draw.line([(WIDTH // 4, 150), (WIDTH * 3 // 4, 150)],
              fill=COLOR_DIVIDER, width=3)

    # ---- 评级大字母 ----
    grade_color = GRADE_COLORS[grade]
    center_x(font_grade_big, grade, y=260, draw=draw, fill=grade_color)

    # ---- 饮品名 + 品牌 + 容量 ----
    center_x(font_drink, drink, y=600, draw=draw, fill=COLOR_DRINK_NAME)
    # 品牌 + 容量合并为一行（如「瑞幸咖啡 · 大杯 450ml」）
    if brand and size:
        brand_size_text = f"{brand} · {size}"
    elif brand:
        brand_size_text = brand
    elif size:
        brand_size_text = size
    else:
        brand_size_text = ""
    if brand_size_text:
        center_x(font_size_label, brand_size_text, y=790, draw=draw,
                 fill=COLOR_LABEL)

    # 分隔线
    draw.line([(WIDTH // 4, 900), (WIDTH * 3 // 4, 900)],
              fill=COLOR_DIVIDER, width=3)

    # ---- 数据行（三列并列：热量 / 糖 / 饱和脂肪）----
    data_y = 960
    label_y = 1060

    # 三列中心位置
    col_centers = [WIDTH // 6, WIDTH // 2, WIDTH * 5 // 6]  # 180, 540, 900

    # 列 1：热量（160 大卡）
    cal_text = str(calories)
    cal_unit = "大卡"
    cal_value_x = col_centers[0] - get_text_size(font_data_value, cal_text)[0] // 2
    draw.text((cal_value_x, data_y), cal_text,
              font=font_data_value, fill=COLOR_DATA)
    cal_unit_x = col_centers[0] - get_text_size(font_data_label, cal_unit)[0] // 2
    draw.text((cal_unit_x, label_y), cal_unit,
              font=font_data_label, fill=COLOR_LABEL)

    # 列 2：糖（7.35g 糖）
    sugar_text = f"{sugar:g}"
    sugar_unit = "g 糖"
    sugar_value_x = col_centers[1] - get_text_size(
        font_data_value, sugar_text)[0] // 2
    draw.text((sugar_value_x, data_y), sugar_text,
              font=font_data_value, fill=COLOR_DATA)
    sugar_unit_x = col_centers[1] - get_text_size(
        font_data_label, sugar_unit)[0] // 2
    draw.text((sugar_unit_x, label_y), sugar_unit,
              font=font_data_label, fill=COLOR_LABEL)

    # 列 3：饱和脂肪（10.9g/杯）—— 单行 label 与列 1/2 结构完全对齐
    satfat_text = sat_fat_display_value  # 10.9
    satfat_label = "g 脂"  # 单行「单位 + 简称」，与列 2「g 糖」结构完全一致
    satfat_value_x = col_centers[2] - get_text_size(
        font_data_value, satfat_text)[0] // 2
    draw.text((satfat_value_x, data_y), satfat_text,
              font=font_data_value, fill=COLOR_DATA)
    satfat_label_x = col_centers[2] - get_text_size(
        font_data_label, satfat_label)[0] // 2
    draw.text((satfat_label_x, label_y), satfat_label,
              font=font_data_label, fill=COLOR_LABEL)

    # 分隔线（数据行下方）
    draw.line([(WIDTH // 4, 1180), (WIDTH * 3 // 4, 1180)],
              fill=COLOR_DIVIDER, width=3)

    # ---- 默认参数 ----
    if config:
        center_x(font_config, f"[默认] {config}", y=1240, draw=draw,
                 fill=COLOR_DRINK_NAME)

    # 保存
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "PNG", optimize=True)
    print(f"✓ 数据卡已生成：{output}")


# ---------- CLI ----------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成奶茶仙人评级数据卡（PNG）",
    )
    parser.add_argument("--drink", required=True, help="饮品名，如「生椰拿铁」")
    parser.add_argument("--brand", default="", help="品牌名（可选）")
    parser.add_argument("--size", default="", help="容量，如「大杯 450ml」")
    parser.add_argument("--calories", type=int, required=True,
                        help="热量（大卡）")
    parser.add_argument("--sugar", type=float, required=True,
                        help="糖（克）")
    parser.add_argument("--sat-fat", type=float, required=True,
                        dest="sat_fat", help="饱和脂肪（克）")
    parser.add_argument("--sat-fat-unit", default="g/100ml",
                        dest="sat_fat_unit",
                        help="饱和脂肪单位，默认 g/100ml（自动换算为 g/杯）")
    parser.add_argument("--cup-ml", type=int, default=450,
                        dest="cup_ml",
                        help="杯容量（ml），用于 g/100ml → g/杯 换算，默认 450")
    parser.add_argument("--grade", required=True, choices=["A", "B", "C", "D"],
                        help="Nutri-Grade 评级")
    parser.add_argument("--config", default="",
                        help="默认参数，如「冰 / 不另外加糖」")
    parser.add_argument("--price", type=int, default=None,
                        help="参考价格（元），可选")
    parser.add_argument("--output", required=True, type=Path,
                        help="输出 PNG 路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    draw_card(
        drink=args.drink,
        brand=args.brand,
        size=args.size,
        calories=args.calories,
        sugar=args.sugar,
        sat_fat=args.sat_fat,
        sat_fat_unit=args.sat_fat_unit,
        cup_ml=args.cup_ml,
        grade=args.grade,
        config=args.config,
        price=args.price,
        output=args.output,
    )


if __name__ == "__main__":
    main()