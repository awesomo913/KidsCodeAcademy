"""Generate procedural mascot frames for Bytey.

Writes PNG sprite frames to ./assets/mascot/:
  idle_01..08.png    — gentle bob + blink
  wave_01..06.png    — arm raise + side wave
  cheer_01..06.png   — jump + arms up
  think_01..04.png   — head tilt + thought bubble pulse

All frames same canvas size so CSS @keyframes can swap by changing background-image.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent / "assets" / "mascot"
SIZE = 320  # square canvas

BODY = (96, 142, 255, 255)
BODY_DARK = (64, 100, 200, 255)
EYE = (16, 24, 48, 255)
EYE_SHINE = (255, 255, 255, 255)
HEART = (255, 90, 120, 255)
ANTENNA_TIP = (255, 200, 60, 255)
SHADOW = (0, 0, 0, 60)
BUBBLE = (255, 255, 255, 220)
BUBBLE_EDGE = (24, 24, 64, 255)


def _new_canvas() -> Image.Image:
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _draw_shadow(draw: ImageDraw.ImageDraw, cx: int, cy: int, w: int) -> None:
    draw.ellipse([cx - w, cy - w // 4, cx + w, cy + w // 4], fill=SHADOW)


def _draw_body(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    scale: int,
    *,
    arm_left_angle: float = 0.0,
    arm_right_angle: float = 0.0,
    eye_open: float = 1.0,
    smile_curve: float = 1.0,
    antenna_offset: int = 0,
) -> None:
    # Antenna
    tip_x = cx + antenna_offset
    tip_y = cy - int(scale * 1.55)
    draw.line([(cx, cy - scale), (tip_x, tip_y)], fill=BODY_DARK, width=max(3, scale // 16))
    tip_r = max(6, scale // 10)
    draw.ellipse([tip_x - tip_r, tip_y - tip_r, tip_x + tip_r, tip_y + tip_r], fill=ANTENNA_TIP)

    # Head (rounded rect)
    head = [cx - scale, cy - scale, cx + scale, cy + scale]
    draw.rounded_rectangle(head, radius=scale // 4, fill=BODY)

    # Eyes (height scaled by eye_open for blinking)
    eye_y = cy - scale // 5
    eye_dx = scale // 2
    eye_r = scale // 4
    eye_h = max(2, int(eye_r * eye_open))
    for ex in (cx - eye_dx, cx + eye_dx):
        draw.ellipse([ex - eye_r, eye_y - eye_h, ex + eye_r, eye_y + eye_h], fill=EYE)
        sh = max(2, eye_r // 2)
        if eye_open > 0.4:
            draw.ellipse(
                [ex - sh, eye_y - eye_h, ex - sh + sh, eye_y - eye_h + sh],
                fill=EYE_SHINE,
            )

    # Smile
    smile_box = [
        cx - scale // 2,
        cy + scale // 8,
        cx + scale // 2,
        cy + scale // 2 + int(scale * 0.05 * smile_curve),
    ]
    draw.arc(smile_box, start=20, end=160, fill=EYE, width=max(3, scale // 16))

    # Heart on chest
    hx, hy, hr = cx, cy + int(scale * 0.62), scale // 5
    draw.ellipse([hx - hr, hy - hr, hx, hy], fill=HEART)
    draw.ellipse([hx, hy - hr, hx + hr, hy], fill=HEART)
    draw.polygon(
        [(hx - hr, hy - hr // 4), (hx + hr, hy - hr // 4), (hx, hy + hr)],
        fill=HEART,
    )

    # Arms (rectangles rotated around shoulder)
    arm_w = max(8, scale // 6)
    arm_len = int(scale * 0.85)
    for sign, angle in ((-1, arm_left_angle), (1, arm_right_angle)):
        sx = cx + sign * scale
        sy = cy + scale // 4
        ex = sx + int(math.cos(angle) * arm_len * sign)
        ey = sy - int(math.sin(angle) * arm_len)
        draw.line([(sx, sy), (ex, ey)], fill=BODY_DARK, width=arm_w)
        # Hand
        hand_r = max(6, scale // 9)
        draw.ellipse([ex - hand_r, ey - hand_r, ex + hand_r, ey + hand_r], fill=BODY_DARK)


def _frame_idle(i: int, total: int) -> Image.Image:
    img = _new_canvas()
    draw = ImageDraw.Draw(img)
    cx = SIZE // 2
    bob = int(math.sin(i / total * math.pi * 2) * 6)
    cy = SIZE // 2 + bob
    scale = 92
    _draw_shadow(draw, cx, SIZE - 50 - bob // 2, scale)
    blink = 1.0
    if i == total - 1:
        blink = 0.15  # quick blink on last frame
    _draw_body(draw, cx, cy, scale, eye_open=blink)
    return img


def _frame_wave(i: int, total: int) -> Image.Image:
    img = _new_canvas()
    draw = ImageDraw.Draw(img)
    cx = SIZE // 2
    cy = SIZE // 2
    scale = 92
    _draw_shadow(draw, cx, SIZE - 50, scale)
    # Right arm rises and waves side-to-side
    progress = i / max(1, total - 1)
    base_angle = math.radians(30 + 80 * progress)
    wave = math.sin(progress * math.pi * 3) * math.radians(15)
    _draw_body(
        draw,
        cx,
        cy,
        scale,
        arm_right_angle=base_angle + wave,
        antenna_offset=int(math.sin(progress * math.pi * 2) * 6),
    )
    return img


def _frame_cheer(i: int, total: int) -> Image.Image:
    img = _new_canvas()
    draw = ImageDraw.Draw(img)
    progress = i / max(1, total - 1)
    cx = SIZE // 2
    jump = int(math.sin(progress * math.pi) * 26)
    cy = SIZE // 2 - jump
    scale = 92
    _draw_shadow(draw, cx, SIZE - 50, max(scale - jump, scale // 2))
    arm_angle = math.radians(80 + 25 * progress)
    _draw_body(
        draw,
        cx,
        cy,
        scale,
        arm_left_angle=arm_angle,
        arm_right_angle=arm_angle,
        smile_curve=1.4,
    )
    # Sparkles
    for sx, sy in [(cx - 130, cy - 80), (cx + 120, cy - 60), (cx - 100, cy + 90), (cx + 110, cy + 70)]:
        r = 5 + int(math.sin(progress * math.pi * 2 + sx) * 3)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=ANTENNA_TIP)
    return img


def _frame_think(i: int, total: int) -> Image.Image:
    img = _new_canvas()
    draw = ImageDraw.Draw(img)
    cx = SIZE // 2
    cy = SIZE // 2
    scale = 92
    _draw_shadow(draw, cx, SIZE - 50, scale)
    progress = i / max(1, total - 1)
    tilt = int(math.sin(progress * math.pi) * 4)
    _draw_body(draw, cx + tilt, cy, scale, eye_open=0.7, smile_curve=0.4)
    # Thought bubble pulse
    pulse = 1.0 + 0.15 * math.sin(progress * math.pi * 2)
    bx = cx + scale + 20
    by = cy - scale - 10
    for r, dx, dy in [(int(8 * pulse), -30, 30), (int(12 * pulse), -16, 14), (int(36 * pulse), 0, 0)]:
        draw.ellipse([bx + dx - r, by + dy - r, bx + dx + r, by + dy + r], fill=BUBBLE, outline=BUBBLE_EDGE, width=2)
    # Three dots inside the big bubble
    for k, dx in enumerate((-12, 0, 12)):
        dot_alpha = 1.0 if (i // 1) % 4 > k else 0.4
        col = (24, 24, 64, int(255 * dot_alpha))
        draw.ellipse([bx + dx - 4, by - 4, bx + dx + 4, by + 4], fill=col)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plans = [
        ("idle", 8, _frame_idle),
        ("wave", 6, _frame_wave),
        ("cheer", 6, _frame_cheer),
        ("think", 4, _frame_think),
    ]
    for name, count, fn in plans:
        for i in range(count):
            img = fn(i, count)
            out = OUT_DIR / f"{name}_{i + 1:02d}.png"
            img.save(out, optimize=True)
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
