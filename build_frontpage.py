#!/usr/bin/env python3
"""Composite five bespoke editorial illustrations into a 1024x1024 world news
front page for Wednesday, 18 November 2026 (make.fun news-image-20261118).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

REPO_DIR = Path(__file__).resolve().parent
ASSETS_DIR = REPO_DIR / "assets_raw"
OUTPUT_IMAGE = REPO_DIR / "entry.png"
PREVIEW_300 = REPO_DIR.parent / "news18_preview_300.png"
FONTS_DIR = Path(r"C:\Windows\Fonts")

CANVAS_SIZE = 1024
BG_COLOR = (10, 16, 26)
IVORY_PAPER = (245, 240, 229)
INK_DARK = (14, 22, 36)
NAVY_RIBBON = (16, 28, 46)
CRIMSON_RULE = (184, 43, 46)
BRASS_RULE = (202, 159, 86)
PANEL_BORDER = (52, 70, 96)
SUBHEAD_COLOR = (232, 224, 208)


@dataclass(frozen=True)
class StoryPanel:
    image_file: str
    box: tuple[int, int, int, int]
    badge: str
    badge_color: tuple[int, int, int]
    headline_lines: tuple[str, ...]
    subhead: str
    headline_size: int
    subhead_size: int
    badge_size: int
    anchor_x: float = 0.5
    anchor_y: float = 0.5
    zoom: float = 1.0
    scrim_start: float = 0.52
    scrim_max_alpha: int = 238


PANELS: tuple[StoryPanel, ...] = (
    StoryPanel(
        image_file="panel1_shenzhen.jpg",
        box=(16, 122, 604, 554),
        badge="ASIA-PACIFIC · DIPLOMACY",
        badge_color=(186, 40, 46),
        headline_lines=("TRUMP LANDS IN SHENZHEN", "FOR XI TALKS"),
        subhead="Xi greets US leader ahead of APEC & Putin summit",
        headline_size=40,
        subhead_size=21,
        badge_size=18,
        anchor_x=0.46,
        anchor_y=0.33,
        zoom=1.00,
        scrim_start=0.55,
        scrim_max_alpha=244,
    ),
    StoryPanel(
        image_file="panel2_gulf.jpg",
        box=(616, 122, 1008, 554),
        badge="MIDDLE EAST · SECURITY",
        badge_color=(198, 88, 26),
        headline_lines=("GULF STRIKES HIT", "KUWAIT & BAHRAIN"),
        subhead="Iran widens strikes; UN panel faults ceasefire breaches",
        headline_size=36,
        subhead_size=19,
        badge_size=18,
        anchor_x=0.50,
        anchor_y=0.28,
        zoom=1.00,
        scrim_start=0.52,
        scrim_max_alpha=244,
    ),
    StoryPanel(
        image_file="panel3_nvidia.jpg",
        box=(16, 566, 339, 954),
        badge="TECH · MARKETS",
        badge_color=(20, 128, 86),
        headline_lines=("NVIDIA REPORTS;", "HUANG RULED OUT"),
        subhead="Earnings amid export probes & permanent CEO exit",
        headline_size=32,
        subhead_size=18,
        badge_size=17,
        anchor_x=0.52,
        anchor_y=0.25,
        zoom=1.00,
        scrim_start=0.50,
        scrim_max_alpha=246,
    ),
    StoryPanel(
        image_file="panel4_cop31.jpg",
        box=(351, 566, 673, 954),
        badge="CLIMATE · COP31",
        badge_color=(22, 108, 138),
        headline_lines=("COP31 1.5°C ALERT;", "EU GRID DEAL"),
        subhead="Antalya finance gap; EU speeds clean power permits",
        headline_size=32,
        subhead_size=18,
        badge_size=17,
        anchor_x=0.68,
        anchor_y=0.30,
        zoom=1.00,
        scrim_start=0.50,
        scrim_max_alpha=246,
    ),
    StoryPanel(
        image_file="panel5_ukraine.jpg",
        box=(685, 566, 1008, 954),
        badge="EUROPE · WAR",
        badge_color=(52, 88, 134),
        headline_lines=("UKRAINE HITS FUEL", "& CRIMEA BRIDGE"),
        subhead="Strikes slash Russian refining ahead of winter",
        headline_size=32,
        subhead_size=18,
        badge_size=17,
        anchor_x=0.62,
        anchor_y=0.30,
        zoom=1.00,
        scrim_start=0.50,
        scrim_max_alpha=246,
    ),
)

TICKER_LABEL = "18 NOV BRIEF"
TICKER_ITEMS: tuple[str, ...] = (
    "US ENVOYS VISIT CARACAS FOR SECURITY PACT",
    "PEW: ISLAM PROJECTED LARGEST FAITH BY 2035",
    "US WITHDRAWS FDA NOMINEE OVERTON",
)


def load_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    font_path = FONTS_DIR / filename
    if not font_path.exists():
        raise FileNotFoundError(f"Required Windows font not found: {font_path}")
    return ImageFont.truetype(str(font_path), size=size)


def crop_cover(
    img: Image.Image,
    target_w: int,
    target_h: int,
    anchor_x: float = 0.5,
    anchor_y: float = 0.5,
    zoom: float = 1.0,
) -> Image.Image:
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        crop_h = src_h / zoom
        crop_w = crop_h * target_ratio
    else:
        crop_w = src_w / zoom
        crop_h = crop_w / target_ratio

    crop_w = min(crop_w, src_w)
    crop_h = min(crop_h, src_h)

    left = (src_w - crop_w) * max(0.0, min(1.0, anchor_x))
    top = (src_h - crop_h) * max(0.0, min(1.0, anchor_y))
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def apply_bottom_scrim(
    panel: Image.Image,
    start_frac: float = 0.52,
    max_alpha: int = 238,
    color: tuple[int, int, int] = (7, 12, 21),
) -> Image.Image:
    w, h = panel.size
    scrim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scrim)
    start_y = int(h * start_frac)
    span = max(1, h - start_y)

    for y in range(start_y, h):
        t = (y - start_y) / span
        # Smooth ease curve: gentle fade at top, deep solid readability over copy
        alpha = int(max_alpha * (t**1.55))
        draw.line([(0, y), (w, y)], fill=(*color, alpha))

    # Subtle top vignette so top-left badge pops crisply on bright skies too
    top_span = int(h * 0.14)
    for y in range(0, top_span):
        t = 1.0 - (y / max(1, top_span))
        alpha = int(75 * (t**1.6))
        draw.line([(0, y), (w, y)], fill=(*color, alpha))

    return Image.alpha_composite(panel.convert("RGBA"), scrim)


def wrap_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int] | tuple[int, int, int],
    shadow: tuple[int, int, int, int] = (4, 8, 15, 225),
    offset: tuple[int, int] = (0, 2),
) -> None:
    x, y = xy
    ox, oy = offset
    draw.text((x + ox, y + oy), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def draw_badge(
    panel: Image.Image,
    label: str,
    bg_color: tuple[int, int, int],
    font_size: int,
    x: int = 12,
    y: int = 12,
) -> Image.Image:
    overlay = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font("ARIALNB.TTF", font_size)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x = 10
    pad_y = 5
    rect = (x, y, x + tw + pad_x * 2, y + th + pad_y * 2)

    # Subtle shadow under badge + crisp dark rim for bright skies
    shadow_rect = (rect[0] + 1, rect[1] + 2, rect[2] + 1, rect[3] + 2)
    draw.rounded_rectangle(shadow_rect, radius=3, fill=(4, 8, 15, 200))
    draw.rounded_rectangle(
        rect,
        radius=3,
        fill=(*bg_color, 248),
        outline=(255, 255, 255, 95),
        width=1,
    )

    tx = x + pad_x - bbox[0]
    ty = y + pad_y - bbox[1]
    draw.text((tx, ty), label, font=font, fill=(255, 255, 255, 255))
    return Image.alpha_composite(panel, overlay)


def fit_headline_font(
    draw: ImageDraw.ImageDraw,
    lines: Iterable[str],
    desired_size: int,
    max_width: int,
) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(desired_size, 20, -1):
        font = load_font("ARIALNB.TTF", size)
        widest = max(
            draw.textbbox((0, 0), line, font=font)[2]
            - draw.textbbox((0, 0), line, font=font)[0]
            for line in lines
        )
        if widest <= max_width:
            return font, size
    return load_font("ARIALNB.TTF", 20), 20


def render_story_panel(spec: StoryPanel) -> Image.Image:
    x0, y0, x1, y1 = spec.box
    w, h = x1 - x0, y1 - y0

    src_path = ASSETS_DIR / spec.image_file
    with Image.open(src_path) as raw:
        fitted = crop_cover(
            raw.convert("RGB"),
            w,
            h,
            anchor_x=spec.anchor_x,
            anchor_y=spec.anchor_y,
            zoom=spec.zoom,
        )

    panel = apply_bottom_scrim(
        fitted,
        start_frac=spec.scrim_start,
        max_alpha=spec.scrim_max_alpha,
    )
    panel = draw_badge(panel, spec.badge, spec.badge_color, spec.badge_size)

    draw = ImageDraw.Draw(panel)
    pad_x = 13
    pad_bottom = 13
    max_text_w = w - pad_x * 2

    hl_font, actual_hl_size = fit_headline_font(
        draw, spec.headline_lines, spec.headline_size, max_text_w
    )
    sub_font = load_font("segoeuib.ttf", spec.subhead_size)

    sub_lines = wrap_lines(draw, spec.subhead, sub_font, max_text_w)
    sub_line_h = int(spec.subhead_size * 1.22)
    hl_line_h = int(actual_hl_size * 1.05)

    sub_block_h = len(sub_lines) * sub_line_h
    hl_block_h = len(spec.headline_lines) * hl_line_h
    gap_hl_sub = 6

    cur_y = h - pad_bottom - sub_block_h - gap_hl_sub - hl_block_h

    # Subtle accent bar right above headline for visual polish
    draw.rectangle(
        [(pad_x, cur_y - 8), (pad_x + 42, cur_y - 4)],
        fill=(*spec.badge_color, 255),
    )

    for line in spec.headline_lines:
        draw_shadow_text(
            draw,
            (pad_x, cur_y),
            line,
            hl_font,
            fill=(255, 255, 255, 255),
            offset=(0, 2),
        )
        cur_y += hl_line_h

    cur_y += gap_hl_sub
    for line in sub_lines:
        draw_shadow_text(
            draw,
            (pad_x, cur_y),
            line,
            sub_font,
            fill=(*SUBHEAD_COLOR, 255),
            offset=(0, 1),
        )
        cur_y += sub_line_h

    # Crisp 1px editorial panel border
    draw.rectangle([(0, 0), (w - 1, h - 1)], outline=(*PANEL_BORDER, 255), width=1)
    return panel.convert("RGB")


def draw_masthead(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)

    # Top crimson accent bar
    draw.rectangle([(0, 0), (CANVAS_SIZE, 4)], fill=CRIMSON_RULE)

    # Ivory broadsheet masthead band
    draw.rectangle([(0, 4), (CANVAS_SIZE, 62)], fill=IVORY_PAPER)

    title = "WORLD NEWS"
    title_font = load_font("georgiab.ttf", 46)
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    tx = (CANVAS_SIZE - tw) // 2 - tb[0]
    ty = 4 + (58 - th) // 2 - tb[1]
    draw.text((tx, ty), title, font=title_font, fill=INK_DARK)

    # Flanking classic editorial double rules
    left_end = (CANVAS_SIZE - tw) // 2 - 22
    right_start = (CANVAS_SIZE + tw) // 2 + 22
    mid_y = 33
    for offset, color in ((-3, (150, 122, 74)), (3, (150, 122, 74))):
        draw.line([(16, mid_y + offset), (left_end, mid_y + offset)], fill=color, width=1)
        draw.line([(right_start, mid_y + offset), (CANVAS_SIZE - 16, mid_y + offset)], fill=color, width=1)
    draw.line([(16, mid_y), (left_end, mid_y)], fill=CRIMSON_RULE, width=2)
    draw.line([(right_start, mid_y), (CANVAS_SIZE - 16, mid_y)], fill=CRIMSON_RULE, width=2)

    # Deep navy date ribbon
    draw.rectangle([(0, 62), (CANVAS_SIZE, 111)], fill=NAVY_RIBBON)
    draw.line([(0, 62), (CANVAS_SIZE, 62)], fill=BRASS_RULE, width=1)
    draw.line([(0, 110), (CANVAS_SIZE, 110)], fill=BRASS_RULE, width=2)

    date_text = "WEDNESDAY, 18 NOVEMBER 2026"
    date_font = load_font("arialbd.ttf", 35)
    db = draw.textbbox((0, 0), date_text, font=date_font)
    dw, dh = db[2] - db[0], db[3] - db[1]
    dx = (CANVAS_SIZE - dw) // 2 - db[0]
    dy = 62 + (48 - dh) // 2 - db[1]
    draw.text((dx, dy), date_text, font=date_font, fill=(255, 255, 255))

    # Subtle gold-brass diamond ornaments flanking the date string
    cy = 86
    for cx in ((CANVAS_SIZE - dw) // 2 - 26, (CANVAS_SIZE + dw) // 2 + 26):
        diamond = [(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)]
        draw.polygon(diamond, fill=BRASS_RULE)


def draw_ticker(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = 16, 964, 1008, 1012
    draw.rectangle([(x0, y0), (x1, y1)], fill=(19, 31, 49), outline=BRASS_RULE, width=1)

    # Left crimson tag for "18 NOV BRIEF"
    tag_font = load_font("ARIALNB.TTF", 18)
    tb = draw.textbbox((0, 0), TICKER_LABEL, font=tag_font)
    tag_w = (tb[2] - tb[0]) + 20
    draw.rectangle([(x0 + 1, y0 + 1), (x0 + tag_w, y1 - 1)], fill=CRIMSON_RULE)
    tx = x0 + 10 - tb[0]
    ty = y0 + ((y1 - y0) - (tb[3] - tb[1])) // 2 - tb[1]
    draw.text((tx, ty), TICKER_LABEL, font=tag_font, fill=(255, 255, 255))

    # Auto-fit single-line ticker with gold bullet separators between items
    sep = "  •  "
    full_str = sep.join(TICKER_ITEMS)
    avail_w = (x1 - 10) - (x0 + tag_w + 10)
    chosen_font = load_font("ARIALNB.TTF", 15)
    for size in range(20, 12, -1):
        cand = load_font("ARIALNB.TTF", size)
        bb = draw.textbbox((0, 0), full_str, font=cand)
        if (bb[2] - bb[0]) <= avail_w:
            chosen_font = cand
            break

    full_bb = draw.textbbox((0, 0), full_str, font=chosen_font)
    total_w = full_bb[2] - full_bb[0]
    total_h = full_bb[3] - full_bb[1]
    cur_x = x0 + tag_w + 10 + (avail_w - total_w) // 2 - full_bb[0]
    by = y0 + ((y1 - y0) - total_h) // 2 - full_bb[1]

    for idx, item in enumerate(TICKER_ITEMS):
        if idx > 0:
            draw.text((cur_x, by), sep, font=chosen_font, fill=BRASS_RULE)
            cur_x += draw.textlength(sep, font=chosen_font)
        draw.text((cur_x, by), item, font=chosen_font, fill=(246, 241, 231))
        cur_x += draw.textlength(item, font=chosen_font)


def build_frontpage() -> None:
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG_COLOR)
    draw_masthead(canvas)

    for spec in PANELS:
        panel_img = render_story_panel(spec)
        canvas.paste(panel_img, (spec.box[0], spec.box[1]))

    draw_ticker(canvas)

    # Save crisp high-quality 4:4:4 JPEG under filename entry.png (rules accept PNG or JPEG)
    canvas.save(
        OUTPUT_IMAGE,
        format="JPEG",
        quality=94,
        subsampling=0,
        optimize=True,
    )

    # Generate 300x300 downscaled preview outside repo for strict legibility inspection
    preview = canvas.resize((300, 300), Image.Resampling.LANCZOS)
    preview.save(PREVIEW_300, format="PNG", optimize=True)

    raw_bytes = OUTPUT_IMAGE.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    print(f"Wrote {OUTPUT_IMAGE} ({len(raw_bytes):,} bytes, SHA256={digest})")
    print(f"Wrote 300x300 preview to {PREVIEW_300}")


if __name__ == "__main__":
    build_frontpage()
