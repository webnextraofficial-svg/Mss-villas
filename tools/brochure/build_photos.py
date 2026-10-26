"""Generate site photos from the MSS Balaji Grandeur brochure PDF.

Run: python3 tools/brochure/build_photos.py
"""
import io
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ASSETS = ROOT / "public_html" / "assets"
PDF = ROOT / "brochure 21st july 2026 Green colour.pdf"


def xref_image(doc: fitz.Document, xref: int) -> Image.Image:
    return Image.open(io.BytesIO(fitz.Pixmap(doc, xref).tobytes("png"))).convert("RGB")


def page_render(doc: fitz.Document, page: int, clip=None, zoom: float = 2.0) -> Image.Image:
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def clubhouse(doc: fitz.Document) -> Image.Image:
    # Building (xref 935, soft mask 936) is cut out over a separate sky image (xref 934).
    building = xref_image(doc, 935)
    mask = xref_image(doc, 936).convert("L")
    sky = xref_image(doc, 934).resize(building.size, Image.LANCZOS)
    sky.paste(building, (0, 0), mask)
    return sky


def crop(img: Image.Image, ratio: float, fx: float = 0.5, fy: float = 0.5) -> Image.Image:
    """Largest crop of the given aspect ratio, centred on the focus point (fractions)."""
    w, h = img.size
    if w / h > ratio:
        cw, ch = round(h * ratio), h
    else:
        cw, ch = w, round(w / ratio)
    x = min(max(round(fx * w - cw / 2), 0), w - cw)
    y = min(max(round(fy * h - ch / 2), 0), h - ch)
    return img.crop((x, y, x + cw, y + ch))


def save(img: Image.Image, name: str, size: tuple) -> None:
    out = crop(img, size[0] / size[1]).resize(size, Image.LANCZOS)
    out.save(ASSETS / name, quality=86, optimize=True, progressive=True)
    print(name, size)


def main() -> None:
    doc = fitz.open(PDF)

    street = page_render(doc, 10, zoom=1.5)
    gate = page_render(doc, 2, clip=fitz.Rect(0, 0, 1322, 612))
    club = clubhouse(doc)

    save(crop(street, 16 / 9), "mss-hero-duplex.jpg", (1280, 720))
    save(crop(street, 4 / 3, fx=0.22), "mss-cc-road.jpg", (1152, 864))
    save(crop(street, 4 / 3, fx=0.72), "mss-2bhk-row.jpg", (1152, 864))
    save(xref_image(doc, 580), "mss-2bhk-home.jpg", (1152, 864))
    save(xref_image(doc, 218), "mss-duplex-villa.jpg", (1152, 864))
    save(crop(xref_image(doc, 400), 1, fx=0.5), "mss-villas-evening.jpg", (1024, 1024))
    save(crop(gate, 4 / 3, fx=0.47), "mss-gated-entrance.jpg", (1152, 864))
    save(crop(club, 4 / 3, fx=0.42), "mss-clubhouse.jpg", (1152, 864))
    save(crop(club, 16 / 9, fx=0.45), "mss-clubhouse-evening.jpg", (1280, 720))
    save(xref_image(doc, 1110), "mss-park.jpg", (1280, 720))
    save(xref_image(doc, 1286), "mss-garden-walkway.jpg", (1152, 864))
    save(crop(xref_image(doc, 1458), 4 / 3, fx=0.45), "mss-sports-courts.jpg", (768, 576))


if __name__ == "__main__":
    main()
