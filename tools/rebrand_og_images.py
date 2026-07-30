from pathlib import Path
from shutil import copyfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "og-results"
OUTPUTS = (ROOT / "og-results-v2", ROOT / "og-results-v3")

KOREAN_FONT_PATH = Path(r"C:\Windows\Fonts\malgunbd.ttf")
LATIN_FONT_PATH = Path(r"C:\Windows\Fonts\ariblk.ttf")

BRAND_NAME = "번호의 주인: 야구편"
BRAND_RED = (228, 41, 57, 255)
BRAND_DARK = (25, 31, 40, 255)
CARD_FILL = (255, 255, 255, 255)
DIVIDER = (227, 230, 233, 255)

CANVAS_SIZE = (1200, 600)
LEGACY_HEADER_CLEAR_BOX = (570, 64, 1140, 324)
HEADER_CARD_BOX = (650, 54, 1090, 264)
BRAND_BASELINE_Y = 102
DIVIDER_Y = 142
CITY_CENTER_Y = 195
MIN_TITLE_CITY_GAP = 40
TIER_SCAN_BOX = (550, 270, 1170, 470)

TEAM_STYLES = {
    "daegu": {"label": "DAEGU", "color": (0, 64, 153, 255)},
    "seoul-lg": {"label": "SEOUL", "color": (229, 25, 55, 255)},
    "seoul-doosan": {"label": "SEOUL", "color": (0, 32, 91, 255)},
    "suwon": {"label": "SUWON", "color": (0, 0, 0, 255)},
    "seoul-kiwoom": {"label": "SEOUL", "color": (156, 0, 42, 255)},
    "gwangju": {"label": "GWANGJU", "color": (232, 17, 45, 255)},
    "daejeon": {"label": "DAEJEON", "color": (243, 114, 32, 255)},
    "changwon": {"label": "CHANGWON", "color": (0, 49, 111, 255)},
    "busan": {"label": "BUSAN", "color": (0, 38, 84, 255)},
    "incheon": {"label": "INCHEON", "color": (206, 17, 38, 255)},
}


def require_fonts() -> None:
    for font_path in (KOREAN_FONT_PATH, LATIN_FONT_PATH):
        if not font_path.exists():
            raise RuntimeError(f"Required font not found: {font_path}")


def load_brand_font(max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(30, 19, -1):
        candidate = ImageFont.truetype(str(KOREAN_FONT_PATH), size=size)
        left, _, right, _ = candidate.getbbox(BRAND_NAME)
        if right - left <= max_width:
            return candidate
    return ImageFont.truetype(str(KOREAN_FONT_PATH), size=19)


def load_city_font(label: str, max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(68, 47, -1):
        candidate = ImageFont.truetype(str(LATIN_FONT_PATH), size=size)
        left, _, right, _ = candidate.getbbox(label)
        if right - left <= max_width:
            return candidate
    return ImageFont.truetype(str(LATIN_FONT_PATH), size=47)


def is_foreground(pixel: tuple[int, ...]) -> bool:
    red, green, blue = pixel[:3]
    return (
        min(red, green, blue) < 145
        or (
            max(red, green, blue) - min(red, green, blue) > 45
            and min(red, green, blue) < 185
        )
    )


def find_tier_artwork_top(source: Image.Image) -> int:
    left, top, right, bottom = TIER_SCAN_BOX
    width = right - left
    height = bottom - top
    source_rgb = source.convert("RGB")
    pixels = source_rgb.load()
    foreground = bytearray(width * height)

    for y in range(top, bottom):
        row_offset = (y - top) * width
        for x in range(left, right):
            if is_foreground(pixels[x, y]):
                foreground[row_offset + x - left] = 1

    visited = bytearray(width * height)
    candidate_tops: list[int] = []
    for start_index, present in enumerate(foreground):
        if not present or visited[start_index]:
            continue

        stack = [start_index]
        visited[start_index] = 1
        component_left = component_right = start_index % width
        component_top = component_bottom = start_index // width
        area = 0

        while stack:
            index = stack.pop()
            area += 1
            x = index % width
            y = index // width
            component_left = min(component_left, x)
            component_right = max(component_right, x)
            component_top = min(component_top, y)
            component_bottom = max(component_bottom, y)

            neighbors = []
            if x > 0:
                neighbors.append(index - 1)
            if x + 1 < width:
                neighbors.append(index + 1)
            if y > 0:
                neighbors.append(index - width)
            if y + 1 < height:
                neighbors.append(index + width)
            for neighbor in neighbors:
                if foreground[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    stack.append(neighbor)

        component_width = component_right - component_left + 1
        component_height = component_bottom - component_top + 1
        absolute_top = component_top + top
        if (
            absolute_top >= 280
            and component_width >= 12
            and component_height >= 25
            and area >= 100
        ):
            candidate_tops.append(absolute_top)

    if not candidate_tops:
        raise RuntimeError("Could not find tier artwork")
    return min(candidate_tops)


def draw_baseball_icon(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    radius: int = 18,
) -> None:
    center_x, center_y = center
    draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ),
        fill=(255, 255, 255, 255),
        outline=BRAND_RED,
        width=3,
    )
    draw.arc(
        (center_x - 12, center_y - 20, center_x + 8, center_y + 20),
        start=285,
        end=75,
        fill=BRAND_RED,
        width=2,
    )
    draw.arc(
        (center_x - 8, center_y - 20, center_x + 12, center_y + 20),
        start=105,
        end=255,
        fill=BRAND_RED,
        width=2,
    )
    for offset_y in (-9, -3, 3, 9):
        draw.line(
            (
                center_x - 7,
                center_y + offset_y,
                center_x - 3,
                center_y - 3 + offset_y,
            ),
            fill=BRAND_RED,
            width=1,
        )
        draw.line(
            (
                center_x + 3,
                center_y - 3 + offset_y,
                center_x + 7,
                center_y + offset_y,
            ),
            fill=BRAND_RED,
            width=1,
        )


def clear_legacy_header(source: Image.Image) -> Image.Image:
    canvas = source.convert("RGBA")
    left, top, right, bottom = LEGACY_HEADER_CLEAR_BOX
    width = right - left
    height = bottom - top

    sample = canvas.crop((left, 0, right, 92))
    sample = sample.resize((width, height), Image.Resampling.LANCZOS)
    sample = sample.filter(ImageFilter.GaussianBlur(12))

    replacement = canvas.copy()
    replacement.paste(sample, (left, top))

    mask = Image.new("L", CANVAS_SIZE, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        (left + 18, top + 16, right - 18, bottom - 14),
        radius=34,
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(18))
    cleared = Image.composite(replacement, canvas, mask)

    hard_mask = Image.new("L", CANVAS_SIZE, 0)
    hard_mask_draw = ImageDraw.Draw(hard_mask)
    hard_mask_draw.rectangle(
        (left + 40, top + 36, right - 30, bottom - 8),
        fill=255,
    )
    return Image.composite(replacement, cleared, hard_mask)


def draw_header_card(
    source: Image.Image,
    team_id: str,
    tier_artwork_top: int,
) -> Image.Image:
    style = TEAM_STYLES[team_id]
    canvas = clear_legacy_header(source)

    shadow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    left, top, right, bottom = HEADER_CARD_BOX
    shadow_draw.rounded_rectangle(
        (left, top + 3, right, bottom + 3),
        radius=30,
        fill=(25, 31, 40, 22),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    canvas = Image.alpha_composite(canvas, shadow)

    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        HEADER_CARD_BOX,
        radius=30,
        fill=CARD_FILL,
    )

    brand_font = load_brand_font(278)
    brand_left, brand_top, brand_right, brand_bottom = draw.textbbox(
        (758, BRAND_BASELINE_Y),
        BRAND_NAME,
        font=brand_font,
        anchor="lm",
    )
    group_width = 36 + 16 + (brand_right - brand_left)
    group_left = (left + right - group_width) // 2
    icon_center = (group_left + 18, BRAND_BASELINE_Y)
    text_left = group_left + 36 + 16

    draw_baseball_icon(draw, icon_center)
    draw.text(
        (text_left, BRAND_BASELINE_Y),
        BRAND_NAME,
        font=brand_font,
        fill=BRAND_DARK,
        anchor="lm",
    )

    draw.line(
        (left + 34, DIVIDER_Y, right - 34, DIVIDER_Y),
        fill=DIVIDER,
        width=2,
    )

    city_label = str(style["label"])
    city_color = style["color"]
    city_font = load_city_font(city_label, max_width=382)
    city_box = draw.textbbox(
        ((left + right) // 2, CITY_CENTER_Y),
        city_label,
        font=city_font,
        anchor="mm",
        stroke_width=0,
    )
    city_top = city_box[1]
    title_city_gap = city_top - brand_bottom
    if title_city_gap < MIN_TITLE_CITY_GAP:
        raise RuntimeError(
            f"{team_id}: title/city gap {title_city_gap}px is below "
            f"{MIN_TITLE_CITY_GAP}px"
        )

    draw.text(
        ((left + right) // 2, CITY_CENTER_Y),
        city_label,
        font=city_font,
        fill=city_color,
        anchor="mm",
    )
    underline_y = city_box[3] + 7
    draw.rounded_rectangle(
        (
            city_box[0],
            underline_y,
            city_box[2],
            underline_y + 7,
        ),
        radius=3,
        fill=city_color,
    )
    if underline_y + 7 > bottom - 14:
        raise RuntimeError(f"{team_id}: city underline exceeds header safe area")

    result = Image.alpha_composite(canvas, overlay)

    # Restore from the first connected component of the tier title. This keeps
    # every original glyph pixel while still removing lower legacy city
    # underlines whose vertical position varies between source images.
    preserved_lower_artwork = source.convert("RGBA").crop(
        (0, tier_artwork_top, CANVAS_SIZE[0], CANVAS_SIZE[1])
    )
    result.paste(preserved_lower_artwork, (0, tier_artwork_top))
    return result


def main() -> None:
    require_fonts()
    source_files = sorted(SOURCE.glob("*/*.png"))
    if len(source_files) != 50:
        raise RuntimeError(f"Expected 50 OG images, found {len(source_files)}")

    unknown_team_ids = {
        source_path.parent.name
        for source_path in source_files
        if source_path.parent.name not in TEAM_STYLES
    }
    if unknown_team_ids:
        raise RuntimeError(f"Unknown team directories: {sorted(unknown_team_ids)}")

    for source_path in source_files:
        relative_path = source_path.relative_to(SOURCE)

        with Image.open(source_path) as source:
            if source.size != CANVAS_SIZE:
                raise RuntimeError(f"Unexpected image size: {source_path} {source.size}")
            tier_artwork_top = find_tier_artwork_top(source)
            result = draw_header_card(
                source,
                source_path.parent.name,
                tier_artwork_top,
            )
            result_rgb = result.convert("RGB")
            primary_output_path = OUTPUTS[0] / relative_path
            primary_output_path.parent.mkdir(parents=True, exist_ok=True)
            result_rgb.save(primary_output_path, format="PNG", optimize=True)
            for output_root in OUTPUTS[1:]:
                output_path = output_root / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                copyfile(primary_output_path, output_path)

    print(
        f"Generated {len(source_files)} images in "
        f"{', '.join(str(output) for output in OUTPUTS)}"
    )


if __name__ == "__main__":
    main()
