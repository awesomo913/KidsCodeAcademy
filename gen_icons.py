"""Generate app icons for Kids Code Academy.

Produces PNGs in ./icons/:
  icon-192.png           — small launcher
  icon-512.png           — large / splash
  icon-512-maskable.png  — Android adaptive (12% safe-area inset)

Design: bright sunny background + chunky robot face (Bytey).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG_TOP = (255, 217, 102, 255)
BG_BOT = (255, 138, 191, 255)
BODY = (96, 142, 255, 255)
EYE = (16, 24, 48, 255)
EYE_SHINE = (255, 255, 255, 255)
HEART = (255, 90, 120, 255)
TEXT_COLOR = (24, 24, 64, 255)

ICONS_DIR = Path(__file__).parent / "icons"


def _load_font(size: int):
    for path in [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/seguisb.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / max(1, size - 1)
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    return img


def _draw_bytey(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: int) -> None:
    # Antenna
    draw.line([(cx, cy - int(scale * 1.15)), (cx, cy - int(scale * 0.85))], fill=BODY, width=max(2, scale // 18))
    draw.ellipse(
        [cx - scale // 12, cy - int(scale * 1.22), cx + scale // 12, cy - int(scale * 1.05)],
        fill=HEART,
    )
    # Head (rounded square)
    head = [cx - scale, cy - scale, cx + scale, cy + scale]
    draw.rounded_rectangle(head, radius=scale // 4, fill=BODY)
    # Eyes
    eye_y = cy - scale // 5
    eye_dx = scale // 2
    eye_r = scale // 4
    for ex in (cx - eye_dx, cx + eye_dx):
        draw.ellipse([ex - eye_r, eye_y - eye_r, ex + eye_r, eye_y + eye_r], fill=EYE)
        sh = eye_r // 2
        draw.ellipse([ex - sh, eye_y - sh - sh // 2, ex - sh + sh, eye_y - sh // 2], fill=EYE_SHINE)
    # Smile
    smile = [cx - scale // 2, cy + scale // 8, cx + scale // 2, cy + scale // 2]
    draw.arc(smile, start=20, end=160, fill=EYE, width=max(3, scale // 16))
    # Heart on chest
    hx, hy, hr = cx, cy + int(scale * 0.62), scale // 5
    draw.ellipse([hx - hr, hy - hr, hx, hy], fill=HEART)
    draw.ellipse([hx, hy - hr, hx + hr, hy], fill=HEART)
    draw.polygon(
        [(hx - hr, hy - hr // 4), (hx + hr, hy - hr // 4), (hx, hy + hr)],
        fill=HEART,
    )


def _render(size: int, inset_ratio: float = 0.0) -> Image.Image:
    img = _gradient(size)
    draw = ImageDraw.Draw(img)
    safe = int(size * inset_ratio)
    inner = size - 2 * safe
    cx = size // 2
    cy = size // 2 - inner // 12
    _draw_bytey(draw, cx, cy, scale=int(inner * 0.30))
    # Caption
    font = _load_font(int(inner * 0.13))
    text = "Kids"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]
    draw.text((cx - tw // 2, cy + int(inner * 0.32)), text, fill=TEXT_COLOR, font=font)
    return img


def main() -> None:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    _render(192).save(ICONS_DIR / "icon-192.png", optimize=True)
    _render(512).save(ICONS_DIR / "icon-512.png", optimize=True)
    _render(512, inset_ratio=0.12).save(
        ICONS_DIR / "icon-512-maskable.png", optimize=True
    )
    # Also produce a .ico for PyInstaller --icon
    ico = _render(256)
    ico.save(ICONS_DIR / "app.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    for path in ("icon-192.png", "icon-512.png", "icon-512-maskable.png", "app.ico"):
        print(f"wrote {ICONS_DIR / path}")


if __name__ == "__main__":
    main()
