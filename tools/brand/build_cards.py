"""Generate the homepage "Our homes" promo cards (1024x576) from project photos.

Run: python3 tools/brand/build_cards.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent.parent / "public_html" / "assets"
FONTS = HERE / "fonts"

W, H = 1024, 576
INK = (26, 26, 26)
GREY = (85, 85, 85)

CARDS = [
    ("mss-card-2bhk.jpg", "mss-2bhk-home.jpg", "2 BHK Homes", "₹64 Lakhs · Prices negotiable", (30, 111, 217), (11, 47, 107), "house"),
    ("mss-card-duplex.jpg", "mss-duplex-villa.jpg", "Duplex Homes", "₹81 Lakhs · Prices negotiable", (255, 138, 26), (214, 72, 30), "duplex"),
    ("mss-card-gated.jpg", "mss-gated-entrance.jpg", "Gated Community", "40 FT CC roads · 24/7 security", (31, 157, 85), (16, 110, 58), "shield"),
    ("mss-card-clubhouse.jpg", "mss-clubhouse.jpg", "Clubhouse", "Leisure for the whole family", (214, 37, 96), (150, 20, 70), "club"),
]


def font(name: str, size: int, weight: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / name), size)
    f.set_variation_by_axes([weight])
    return f


def draw_icon(d: ImageDraw.ImageDraw, kind: str, cx: int, cy: int, s: int) -> None:
    white = (255, 255, 255)
    lw = max(4, s // 9)
    if kind in ("house", "duplex"):
        top = cy - s // 2 if kind == "house" else cy - int(s * 0.62)
        d.line([(cx - s // 2, top + s // 2), (cx, top), (cx + s // 2, top + s // 2)], fill=white, width=lw, joint="curve")
        body_top = top + s // 2 - lw // 2
        body_bottom = cy + int(s * 0.45)
        d.rectangle([cx - int(s * 0.36), body_top, cx + int(s * 0.36), body_bottom], outline=white, width=lw)
        if kind == "duplex":
            mid = (body_top + body_bottom) // 2
            d.line([(cx - int(s * 0.36), mid), (cx + int(s * 0.36), mid)], fill=white, width=lw)
        d.rectangle([cx - int(s * 0.09), body_bottom - int(s * 0.28), cx + int(s * 0.09), body_bottom], fill=white)
    elif kind == "shield":
        pts = [(cx, cy - int(s * 0.55)), (cx + int(s * 0.45), cy - int(s * 0.38)), (cx + int(s * 0.42), cy + int(s * 0.08)),
               (cx, cy + int(s * 0.55)), (cx - int(s * 0.42), cy + int(s * 0.08)), (cx - int(s * 0.45), cy - int(s * 0.38))]
        d.line(pts + [pts[0]], fill=white, width=lw, joint="curve")
        d.line([(cx - int(s * 0.18), cy), (cx - int(s * 0.03), cy + int(s * 0.16)), (cx + int(s * 0.22), cy - int(s * 0.14))], fill=white, width=lw, joint="curve")
    elif kind == "club":
        d.polygon([(cx - int(s * 0.55), cy - int(s * 0.22)), (cx, cy - int(s * 0.55)), (cx + int(s * 0.55), cy - int(s * 0.22))], outline=white, width=lw)
        for dx in (-0.36, -0.12, 0.12, 0.36):
            x = cx + int(s * dx)
            d.line([(x, cy - int(s * 0.12)), (x, cy + int(s * 0.38))], fill=white, width=lw)
        d.line([(cx - int(s * 0.55), cy + int(s * 0.48)), (cx + int(s * 0.55), cy + int(s * 0.48))], fill=white, width=lw)


def build(out_name, photo, title, sub, c1, c2, icon) -> None:
    card = ImageOps.fit(Image.open(ASSETS / photo).convert("RGB"), (W, H), Image.LANCZOS, centering=(0.5, 0.35)).convert("RGBA")

    panel = (16, 404, 1008, 556)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([panel[0], panel[1] + 6, panel[2], panel[3] + 6], 26, fill=(0, 0, 0, 90))
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(panel, 26, fill=(255, 255, 255, 245))
    d.rounded_rectangle([panel[0], panel[1], panel[2], panel[1] + 6], 3, fill=c1 + (255,))

    size = 72
    title_font = font("Outfit.ttf", size, 800)
    while title_font.getlength(title) > 570:
        size -= 2
        title_font = font("Outfit.ttf", size, 800)
    sub_font = font("PlusJakartaSans.ttf", 34, 600)
    d.text((64, 416 + (72 - size) // 2), title, font=title_font, fill=c2)
    d.text((66, 500), sub, font=sub_font, fill=GREY)

    bx, by, br = 925, 480, 40
    d.ellipse([bx - br - 3, by - br - 3, bx + br + 3, by + br + 3], fill=(235, 235, 235, 255))
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 255, 255, 255))
    d.line([(bx - 14, by), (bx + 14, by)], fill=INK, width=5)
    d.line([(bx + 3, by - 12), (bx + 15, by), (bx + 3, by + 12)], fill=INK, width=5, joint="curve")

    ix, iy, ir = 764, 392, 74
    d.ellipse([ix - ir - 8, iy - ir - 8, ix + ir + 8, iy + ir + 8], fill=(255, 255, 255, 255))
    d.ellipse([ix - ir, iy - ir, ix + ir, iy + ir], fill=c1 + (255,))
    d.ellipse([ix - ir + 10, iy - ir + 10, ix + ir - 10, iy + ir - 10], outline=(255, 255, 255, 90), width=3)
    draw_icon(d, icon, ix, iy + 4, 64)

    card.alpha_composite(layer)
    card.convert("RGB").save(ASSETS / out_name, "JPEG", quality=86, optimize=True, progressive=True)
    print("card", out_name)


def main() -> None:
    for spec in CARDS:
        build(*spec)


if __name__ == "__main__":
    main()
