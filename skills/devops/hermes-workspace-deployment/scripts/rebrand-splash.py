#!/usr/bin/env python3
"""Regenerate Hermes-branded splash screen images for the workspace.
Generates avatar (400x400) and banner (1145x196) in dark + light variants,
backs up existing claude-* files, and copies new images into place.

Requires: pillow (pip install pillow)
Usage: python3 rebrand-splash.py
"""

import os, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PUB = os.path.expanduser("~/hermes-workspace/public")
AVATAR_SIZE = 400
BANNER_SIZE = (1145, 196)

GOLD = (255, 172, 2, 255)
GOLD_DIM = (255, 172, 2, 100)
GOLD_BRIGHT = (255, 200, 60, 255)
DARK_BG = (3, 26, 26, 255)  # #031A1A
NOUS_BLUE = (37, 87, 183, 255)
MUTED_DARK = (156, 178, 174, 200)
MUTED_LIGHT = (111, 125, 150, 200)
WHITE = (248, 241, 227, 255)


def _find_font(size):
    """Find a bold system font, falling back to default."""
    import math
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def generate_avatar():
    """400x400 Hermes avatar — winged caduceus with circuit-board accents."""
    sz = AVATAR_SIZE
    img = Image.new("RGBA", (sz, sz), DARK_BG)
    draw = ImageDraw.Draw(img)
    cx, cy = sz // 2, sz // 2

    # circular border glow
    for r in range(cx - 8, cx + 1):
        alpha = int(40 * (r - cx + 8) / 9)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*GOLD[:3], alpha), width=2)

    # geometric wings
    import math
    for flip in (False, True):
        sign = -1 if flip else 1
        bx = cx + sign * 30
        for angle_deg in range(-60, 61, 8):
            angle = math.radians(angle_deg)
            length = 120 - abs(angle_deg) * 0.8
            ex = bx + sign * length * math.cos(angle)
            ey = cy - length * math.sin(angle)
            draw.line([bx, cy, ex, ey], fill=GOLD_DIM, width=2)
            for frac in (0.5, 0.75, 1.0):
                nx = bx + (ex - bx) * frac
                ny = cy + (ey - cy) * frac
                draw.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=GOLD_BRIGHT)

    # staff
    draw.line([cx, cy - 100, cx, cy + 90], fill=GOLD_BRIGHT, width=4)

    # intertwined snakes
    for offset in (-1, 1):
        points = []
        for y in range(-95, 96, 3):
            t = (y + 95) / 190
            x = cx + offset * 22 * math.sin(t * math.pi * 3)
            points.append((x, cy + y))
        for i in range(len(points) - 1):
            alpha = int(180 + 75 * (i / len(points)))
            draw.line([points[i], points[i + 1]], fill=(*GOLD[:3], alpha), width=3)

    # top winged circle
    draw.ellipse([cx - 12, cy - 108, cx + 12, cy - 84], outline=GOLD_BRIGHT, width=3)
    for s in (-1, 1):
        draw.polygon([
            (cx + s * 14, cy - 96),
            (cx + s * 40, cy - 120),
            (cx + s * 32, cy - 100),
            (cx + s * 14, cy - 88),
        ], fill=GOLD)

    # circuit traces on staff
    for y in range(-80, 90, 15):
        for s in (-1, 1):
            lx = cx + s * 6
            rx = cx + s * 18
            draw.line([(lx, cy + y), (rx, cy + y)], fill=GOLD_DIM, width=1)
            draw.ellipse([rx - 2, cy + y - 2, rx + 2, cy + y + 2], fill=GOLD_BRIGHT)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    img = Image.blend(img, img.filter(ImageFilter.SHARPEN), 0.3)
    return img


def generate_banner(light=False):
    """1145x196 'HERMES WORKSPACE' text banner with wing accents."""
    w, h = BANNER_SIZE
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if light:
        accent = NOUS_BLUE
        text_color = (22, 49, 95, 255)
        muted = MUTED_LIGHT
        bg_line = (3, 26, 26, 40)
    else:
        accent = GOLD
        text_color = WHITE
        muted = MUTED_DARK
        bg_line = (3, 26, 26, 80)

    draw.line([(40, h // 2), (w - 40, h // 2)], fill=GOLD_DIM, width=1)
    draw.line([(40, h // 2 - 50), (w - 40, h // 2 - 50)], fill=bg_line, width=1)
    draw.line([(40, h // 2 + 50), (w - 40, h // 2 + 50)], fill=bg_line, width=1)

    font_lg = _find_font(56)
    font_sm = _find_font(18)

    tw = font_lg.getbbox("HERMES")[2] - font_lg.getbbox("HERMES")[0]
    th = font_lg.getbbox("HERMES")[3] - font_lg.getbbox("HERMES")[1]
    main_x = (w - tw) // 2
    main_y = h // 2 - th - 5

    tw2 = font_sm.getbbox("WORKSPACE")[2] - font_sm.getbbox("WORKSPACE")[0]
    sub_x = (w - tw2) // 2
    sub_y = h // 2 + 10

    # glow shadow
    for offset in ((2, 2), (-2, -2), (2, -2), (-2, 2)):
        draw.text((main_x + offset[0], main_y + offset[1]), "HERMES", fill=bg_line, font=font_lg)

    draw.text((main_x, main_y), "HERMES", fill=accent, font=font_lg)
    draw.text((sub_x, sub_y), "WORKSPACE", fill=muted, font=font_sm)

    # flanking wings
    wing_y = main_y + th // 2
    for sx in (main_x - 50, main_x + tw + 50):
        side = -1 if sx < main_x else 1
        draw.polygon([
            (sx, wing_y),
            (sx + side * 35, wing_y - 18),
            (sx + side * 25, wing_y),
            (sx + side * 35, wing_y + 18),
        ], fill=accent)

    return img


def main():
    for f in ("claude-avatar.png", "claude-avatar.webp",
              "claude-banner.png", "claude-banner-light.png"):
        src = os.path.join(PUB, f)
        if os.path.exists(src) and not os.path.exists(src + ".bak"):
            shutil.copy2(src, src + ".bak")

    avatar = generate_avatar()
    avatar.save(os.path.join(PUB, "hermes-avatar.png"), "PNG")
    avatar.save(os.path.join(PUB, "hermes-avatar.webp"), "WEBP", quality=92)

    banner_dark = generate_banner(light=False)
    banner_dark.save(os.path.join(PUB, "hermes-banner.png"), "PNG")

    banner_light = generate_banner(light=True)
    banner_light.save(os.path.join(PUB, "hermes-banner-light.png"), "PNG")

    # Copy to the filenames the workspace HTML actually references
    for hermes_name, claude_name in (
        ("hermes-avatar.png", "claude-avatar.png"),
        ("hermes-avatar.webp", "claude-avatar.webp"),
        ("hermes-banner.png", "claude-banner.png"),
        ("hermes-banner-light.png", "claude-banner-light.png"),
    ):
        shutil.copy2(os.path.join(PUB, hermes_name), os.path.join(PUB, claude_name))

    print("Regenerated splash images. Restart workspace to pick up:")
    print("  systemctl --user restart hermes-workspace")


if __name__ == "__main__":
    main()
