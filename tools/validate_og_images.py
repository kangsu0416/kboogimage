from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageChops
from rebrand_og_images import find_tier_artwork_top


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "og-results"
OUTPUTS = (ROOT / "og-results-v2", ROOT / "og-results-v3")
TEAM_IDS = (
    "daegu",
    "seoul-lg",
    "seoul-doosan",
    "suwon",
    "seoul-kiwoom",
    "gwangju",
    "daejeon",
    "changwon",
    "busan",
    "incheon",
)
TIERS = ("starter", "bronze", "silver", "gold", "champion")
EXPECTED_SIZE = (1200, 600)
HEADER_CARD_BOTTOM = 264
MIN_CARD_TIER_GAP = 32


def foreground_count(image: Image.Image, y: int) -> int:
    count = 0
    for x in range(550, 1170):
        red, green, blue = image.getpixel((x, y))
        is_dark = min(red, green, blue) < 145
        is_saturated = (
            max(red, green, blue) - min(red, green, blue) > 45
            and min(red, green, blue) < 185
        )
        if is_dark or is_saturated:
            count += 1
    return count


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    expected_paths = {
        Path(team_id) / f"tier-{tier}.png"
        for team_id in TEAM_IDS
        for tier in TIERS
    }

    for output_root in OUTPUTS:
        actual_paths = {
            path.relative_to(output_root)
            for path in output_root.glob("*/*.png")
        }
        if actual_paths != expected_paths:
            missing = sorted(str(path) for path in expected_paths - actual_paths)
            extra = sorted(str(path) for path in actual_paths - expected_paths)
            raise RuntimeError(
                f"{output_root.name}: missing={missing}, extra={extra}"
            )

        for relative_path in sorted(expected_paths):
            path = output_root / relative_path
            with Image.open(path) as image:
                image.load()
                if image.size != EXPECTED_SIZE:
                    raise RuntimeError(
                        f"{relative_path}: expected {EXPECTED_SIZE}, got {image.size}"
                    )
                if image.mode != "RGB":
                    raise RuntimeError(
                        f"{relative_path}: expected RGB, got {image.mode}"
                    )
                with Image.open(SOURCE / relative_path) as source:
                    source_rgb = source.convert("RGB")
                    tier_top = find_tier_artwork_top(source_rgb)
                    preserved_source = source_rgb.crop(
                        (
                            0,
                            tier_top,
                            EXPECTED_SIZE[0],
                            EXPECTED_SIZE[1],
                        )
                    )
                    preserved_output = image.crop(
                        (
                            0,
                            tier_top,
                            EXPECTED_SIZE[0],
                            EXPECTED_SIZE[1],
                        )
                    )
                    if ImageChops.difference(
                        preserved_source,
                        preserved_output,
                    ).getbbox() is not None:
                        raise RuntimeError(
                            f"{relative_path}: tier artwork changed below "
                            f"y={tier_top}"
                        )
                for y in range(HEADER_CARD_BOTTOM + 1, tier_top):
                    if foreground_count(image, y) >= 50:
                        raise RuntimeError(
                            f"{relative_path}: legacy header pixels remain at y={y}"
                        )
                if tier_top - HEADER_CARD_BOTTOM < MIN_CARD_TIER_GAP:
                    raise RuntimeError(
                        f"{relative_path}: card/tier gap is "
                        f"{tier_top - HEADER_CARD_BOTTOM}px"
                    )

    for relative_path in sorted(expected_paths):
        v2_path = OUTPUTS[0] / relative_path
        v3_path = OUTPUTS[1] / relative_path
        if digest(v2_path) != digest(v3_path):
            raise RuntimeError(f"v2/v3 mismatch: {relative_path}")

    print("Validated 50 OG images in v2 and v3 (100 files total).")


if __name__ == "__main__":
    main()
