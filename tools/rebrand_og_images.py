from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "og-results"
OUTPUT = ROOT / "og-results-v2"
FONT_PATH = Path(r"C:\Windows\Fonts\malgunbd.ttf")
BRAND_NAME = "번호의 주인: 야구편"
BRAND_RED = (228, 41, 57, 255)
BRAND_DARK = (25, 31, 40, 255)


def load_brand_font(max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(28, 17, -1):
        candidate = ImageFont.truetype(str(FONT_PATH), size=size)
        left, _, right, _ = candidate.getbbox(BRAND_NAME)
        if right - left <= max_width:
            return candidate
    return ImageFont.truetype(str(FONT_PATH), size=17)


def draw_brand_badge(source: Image.Image) -> Image.Image:
    canvas = source.convert("RGBA")
    badge_box = (692, 140, 1048, 207)
    radius = 24

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (badge_box[0], badge_box[1] + 3, badge_box[2], badge_box[3] + 3),
        radius=radius,
        fill=(25, 31, 40, 38),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    canvas = Image.alpha_composite(canvas, shadow)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        badge_box,
        radius=radius,
        fill=(255, 255, 255, 255),
        outline=(255, 255, 255, 255),
        width=2,
    )

    icon_center = (727, 173)
    icon_radius = 17
    draw.ellipse(
        (
            icon_center[0] - icon_radius,
            icon_center[1] - icon_radius,
            icon_center[0] + icon_radius,
            icon_center[1] + icon_radius,
        ),
        fill=(255, 255, 255, 255),
        outline=BRAND_RED,
        width=3,
    )
    draw.arc((715, 153, 735, 192), start=285, end=75, fill=BRAND_RED, width=2)
    draw.arc((719, 153, 739, 192), start=105, end=255, fill=BRAND_RED, width=2)
    for offset_y in (-8, -2, 4, 10):
        draw.line((720, 173 + offset_y, 724, 170 + offset_y), fill=BRAND_RED, width=1)
        draw.line((730, 170 + offset_y, 734, 173 + offset_y), fill=BRAND_RED, width=1)

    font = load_brand_font(276)
    draw.text(
        (756, 173),
        BRAND_NAME,
        font=font,
        fill=BRAND_DARK,
        anchor="lm",
    )
    return Image.alpha_composite(canvas, overlay)


def main() -> None:
    source_files = sorted(SOURCE.glob("*/*.png"))
    if len(source_files) != 50:
        raise RuntimeError(f"Expected 50 OG images, found {len(source_files)}")

    for source_path in source_files:
        relative_path = source_path.relative_to(SOURCE)
        output_path = OUTPUT / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(source_path) as source:
            if source.size != (1200, 600):
                raise RuntimeError(f"Unexpected image size: {source_path} {source.size}")
            result = draw_brand_badge(source)
            result.convert("RGB").save(output_path, format="PNG", optimize=True)

    print(f"Generated {len(source_files)} images in {OUTPUT}")


if __name__ == "__main__":
    main()
