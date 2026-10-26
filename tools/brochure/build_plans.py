"""Floor-plan and location-map images from the brochure PDF.

Run: python3 tools/brochure/build_plans.py
"""
import io
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ASSETS = ROOT / "public_html" / "assets"
PDF = ROOT / "brochure 21st july 2026 Green colour.pdf"

# Right-hand page of each spread, above the green website bar.
PLANS = {
    "mss-plan-duplex-east.jpg": 3,
    "mss-plan-duplex-west.jpg": 4,
    "mss-plan-2bhk-east.jpg": 5,
    "mss-plan-2bhk-west.jpg": 6,
}


def render(doc, page, rect, zoom=2.0):
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=fitz.Rect(*rect))
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def main():
    doc = fitz.open(PDF)
    for name, page in PLANS.items():
        img = render(doc, page, (792, 0, 1584, 572))
        img.thumbnail((1400, 1400), Image.LANCZOS)
        img.save(ASSETS / name, quality=88, optimize=True, progressive=True)
        print(name, img.size)
    loc = render(doc, 12, (870, 40, 1584, 572))
    loc.thumbnail((1300, 1300), Image.LANCZOS)
    loc.save(ASSETS / "mss-location-map.jpg", quality=88, optimize=True, progressive=True)
    print("mss-location-map.jpg", loc.size)


if __name__ == "__main__":
    main()
