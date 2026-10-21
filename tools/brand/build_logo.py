"""Generate site logo + favicons from tools/brand/logo-source.jpg.

Run: python3 tools/brand/build_logo.py
"""
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent / "public_html"
ASSETS = ROOT / "assets"

SRC = HERE / "logo-source.jpg"
MARK_BOX = (138, 88, 832, 616)       # GU mark
WORDMARK_BOX = (40, 637, 984, 749)   # "GHAR UPGRADE"


def knock_out_white(img: Image.Image, soft: int = 70) -> Image.Image:
    """Make the near-white background transparent, un-mixing anti-aliased edges."""
    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    dist = 255.0 - rgb.min(axis=2)
    alpha = np.clip((dist - 8) / (soft - 8), 0.0, 1.0)
    a = np.maximum(alpha[..., None], 1e-3)
    color = np.clip((rgb - (1 - a) * 255.0) / a, 0, 255)
    out = np.dstack([color, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out)


def trim(img: Image.Image) -> Image.Image:
    return img.crop(img.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())


def square(img: Image.Image, pad: float = 0.04) -> Image.Image:
    side = int(max(img.size) * (1 + 2 * pad))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    return canvas


def main() -> None:
    src = Image.open(SRC)
    mark = trim(knock_out_white(src.crop(MARK_BOX)))
    word = trim(knock_out_white(src.crop(WORDMARK_BOX)))

    # Horizontal header logo (2x of the 240x45 slot)
    height = 280
    mark_h = height
    mark_r = mark.resize((round(mark.width * mark_h / mark.height), mark_h), Image.LANCZOS)
    word_h = 112
    word_r = word.resize((round(word.width * word_h / word.height), word_h), Image.LANCZOS)
    gap = 44
    logo = Image.new("RGBA", (mark_r.width + gap + word_r.width, height), (0, 0, 0, 0))
    logo.paste(mark_r, (0, 0), mark_r)
    logo.paste(word_r, (mark_r.width + gap, (height - word_h) // 2), word_r)
    logo.save(ASSETS / "ghar-upgrade-logo.png", optimize=True)

    # Full stacked logo (as supplied) for social / print use
    src.convert("RGB").save(ASSETS / "ghar-upgrade-logo-full.jpg", quality=90, optimize=True)

    icon = square(mark)
    icon.resize((32, 32), Image.LANCZOS).save(ASSETS / "favicon-32.png", optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(ASSETS / "favicon.png", optimize=True)
    icon.resize((256, 256), Image.LANCZOS).save(
        ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    touch_bg = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    touch = square(mark, pad=0.1).resize((180, 180), Image.LANCZOS)
    touch_bg.alpha_composite(touch)
    touch_bg.convert("RGB").save(ASSETS / "apple-touch-icon.png", optimize=True)

    buf = io.BytesIO()
    icon.resize((256, 256), Image.LANCZOS).save(buf, "PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    (ASSETS / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 256 256"><image width="256" height="256" '
        f'xlink:href="data:image/png;base64,{b64}"/></svg>'
    )

    print("logo", logo.size)


if __name__ == "__main__":
    main()
