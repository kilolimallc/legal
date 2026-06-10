#!/usr/bin/env python3
"""
Generate App Store promotional images for the "10 in 24" promoted In-App Purchases.

Apple Guideline 2.3.2 requires the promotional image for each promoted IAP to be:
  - 1024 x 1024 px, PNG/JPEG, RGB, flattened (no alpha / transparency)
  - unique (not identical to the app icon)
  - distinct from the promo image of every other promoted product

This produces two distinct images:
  - promo-monthly-1024.png : "24-hour duty ring" motif (cool blue / white)
  - promo-annual-1024.png  : "12-month grid" motif (navy / amber, BEST VALUE)

Both deliberately AVOID the app icon's "10:24" clock-numeral motif.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- config
S = 3                      # supersample factor (render big, downscale = anti-alias)
SIZE = 1024
W = SIZE * S

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
F_BOLD = os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "InstrumentSans-Regular.ttf")

# brand palette
BLUE = (49, 111, 183)          # #316FB7 brand
BLUE_LT = (74, 134, 205)
NAVY = (18, 46, 86)            # deep
NAVY_D = (11, 30, 58)
WHITE = (255, 255, 255)
CYAN = (150, 214, 255)
AMBER = (245, 176, 52)         # #F5B034 accent for Annual
AMBER_D = (214, 142, 28)


def font(path, px):
    return ImageFont.truetype(path, px * S)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(top, bottom):
    """Vertical gradient RGB image."""
    img = Image.new("RGB", (W, W), top)
    px = img.load()
    for y in range(W):
        c = lerp(top, bottom, y / (W - 1))
        for x in range(W):
            px[x, y] = c
    return img


def dgrad(c0, c1):
    """Diagonal (top-left -> bottom-right) gradient RGB image."""
    img = Image.new("RGB", (W, W), c0)
    px = img.load()
    denom = 2 * (W - 1)
    for y in range(W):
        for x in range(W):
            px[x, y] = lerp(c0, c1, (x + y) / denom)
    return img


def radial_glow(img, cx, cy, radius, color, max_alpha):
    """Soft additive-ish radial glow blended onto img (RGB)."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 60
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        a = int(max_alpha * (1 - t) ** 2)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    base = img.convert("RGBA")
    base.alpha_composite(glow)
    return base.convert("RGB")


def text_center(d, cx, y, s, fnt, fill, tracking=0):
    """Draw text horizontally centered at cx, top at y. Returns (w,h)."""
    if tracking == 0:
        bbox = d.textbbox((0, 0), s, font=fnt)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text((cx - w / 2, y - bbox[1]), s, font=fnt, fill=fill)
        return w, h
    # letter-spaced
    widths = [d.textbbox((0, 0), ch, font=fnt)[2] - d.textbbox((0, 0), ch, font=fnt)[0] for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    asc, desc = fnt.getmetrics()
    for ch, wch in zip(s, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total, asc + desc


def pill(d, cx, cy, text, fnt, bg, fg, padx, pady, tracking=0):
    tw, th = (text_size := d.textbbox((0, 0), text, font=fnt))[2] - text_size[0], text_size[3] - text_size[1]
    if tracking:
        tw = sum((d.textbbox((0, 0), c, font=fnt)[2] - d.textbbox((0, 0), c, font=fnt)[0]) for c in text) + tracking * (len(text) - 1)
    w = tw + padx * 2
    h = th + pady * 2
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h / 2, fill=bg)
    text_center(d, cx, y0 + pady - text_size[1], text, fnt, fg, tracking=tracking)


def plane_glyph(d, cx, cy, sc, fill):
    """Simple clean top-view aircraft silhouette pointing up, centered at (cx,cy)."""
    pts_r = [
        (0.00, -1.00),  # nose
        (0.07, -0.62),
        (0.07, -0.20),
        (0.62, 0.10),   # right wingtip leading
        (0.62, 0.24),   # right wingtip trailing
        (0.09, 0.18),
        (0.08, 0.62),
        (0.30, 0.86),   # right tailplane
        (0.30, 0.98),
        (0.05, 0.80),
        (0.00, 0.82),
    ]
    pts = []
    for x, y in pts_r:
        pts.append((cx + x * sc, cy + y * sc))
    for x, y in reversed(pts_r[1:-1]):
        pts.append((cx - x * sc, cy + y * sc))
    d.polygon(pts, fill=fill)


def check_glyph(d, cx, cy, sc, fill, width):
    d.line([(cx - 0.45 * sc, cy + 0.02 * sc),
            (cx - 0.10 * sc, cy + 0.38 * sc),
            (cx + 0.5 * sc, cy - 0.4 * sc)],
           fill=fill, width=width, joint="curve")


def finish(img, name):
    out = img.resize((SIZE, SIZE), Image.LANCZOS).convert("RGB")
    path = os.path.join(OUT_DIR, name)
    out.save(path, "PNG")
    print("wrote", path, out.size, out.mode)


# ---------------------------------------------------------------- MONTHLY
def make_monthly():
    """Horizontal 24-hour duty/rest timeline — deliberately NON-circular so it
    does not echo the icon's clock-ring / circular-arrow motif."""
    img = vgrad(lerp(BLUE_LT, BLUE, 0.10), NAVY)
    cx = W // 2
    img = radial_glow(img, cx, int(W * 0.34), int(W * 0.40), (130, 185, 245), 60)
    d = ImageDraw.Draw(img, "RGBA")

    # eyebrow wordmark
    text_center(d, cx, int(112 * S), "10 IN 24", font(F_BOLD, 30),
                (255, 255, 255, 235), tracking=int(10 * S))

    # hero plane (aviation cue absent from the icon)
    plane_glyph(d, cx, int(W * 0.305), int(W * 0.092), (255, 255, 255, 255))

    # ---- horizontal 24-hour duty timeline ----
    tx0 = int(W * 0.150)
    tx1 = int(W * 0.850)
    tcy = int(W * 0.520)
    th = int(58 * S)
    tw = tx1 - tx0
    rad = th // 2
    rest_frac = 10.0 / 24.0          # the "10 hours rest in 24" requirement
    split = tx1 - int(tw * rest_frac)

    # base track
    d.rounded_rectangle([tx0, tcy - rad, tx1, tcy + rad], radius=rad,
                        fill=(255, 255, 255, 50))
    # duty segment (left) in lighter blue
    d.rounded_rectangle([tx0, tcy - rad, split + rad, tcy + rad], radius=rad,
                        fill=BLUE_LT + (255,))
    # rest segment (right) in bright cyan
    d.rounded_rectangle([split - rad, tcy - rad, tx1, tcy + rad], radius=rad,
                        fill=CYAN + (255,))
    # boundary knob
    d.ellipse([split - int(20 * S), tcy - int(20 * S),
               split + int(20 * S), tcy + int(20 * S)], fill=WHITE + (255,))

    # 24 hour ticks above the track
    for i in range(25):
        x = tx0 + tw * i / 24
        major = (i % 6 == 0)
        tl = int((26 if major else 13) * S)
        y0 = tcy - rad - int(16 * S)
        d.line([(x, y0), (x, y0 - tl)],
               fill=(255, 255, 255, 210 if major else 95),
               width=int((5 if major else 3) * S))
    # end + milestone labels
    fsm = font(F_REG, 26)
    text_center(d, tx0, int(W * 0.435), "0h", fsm, (255, 255, 255, 200))
    text_center(d, tx1, int(W * 0.435), "24h", fsm, (255, 255, 255, 200))

    # segment captions below
    fcap = font(F_BOLD, 28)
    text_center(d, (tx0 + split) / 2, tcy + rad + int(26 * S), "DUTY",
                fcap, (255, 255, 255, 235), tracking=int(6 * S))
    text_center(d, (split + tx1) / 2, tcy + rad + int(26 * S), "10h REST",
                fcap, CYAN + (255,), tracking=int(4 * S))

    # ---- product label ----
    text_center(d, cx, int(W * 0.715), "Monthly", font(F_BOLD, 94), WHITE + (255,))
    text_center(d, cx, int(W * 0.808), "Flight & Rest Tracking · Part 135",
                font(F_REG, 33), (255, 255, 255, 215))

    finish(img, "promo-monthly-1024.png")


# ---------------------------------------------------------------- ANNUAL
def make_annual():
    img = dgrad(NAVY, lerp(BLUE, NAVY, 0.25))
    cx = W // 2
    img = radial_glow(img, int(W * 0.72), int(W * 0.30), int(W * 0.4), AMBER, 48)
    img = radial_glow(img, int(W * 0.30), int(W * 0.62), int(W * 0.38), (60, 120, 200), 60)
    d = ImageDraw.Draw(img, "RGBA")

    # eyebrow wordmark
    text_center(d, cx, int(108 * S), "10 IN 24", font(F_BOLD, 30),
                (255, 255, 255, 235), tracking=int(10 * S))

    # BEST VALUE pill
    pill(d, cx, int(196 * S), "BEST VALUE", font(F_BOLD, 27),
         AMBER + (255,), NAVY_D + (255,), int(28 * S), int(14 * S), tracking=int(4 * S))

    # ---- 12-month grid (4 cols x 3 rows) ----
    cols, rows = 4, 3
    gap = int(26 * S)
    tile = int(118 * S)
    gw = cols * tile + (cols - 1) * gap
    gh = rows * tile + (rows - 1) * gap
    gx = cx - gw // 2
    gy = int(W * 0.305)
    n = 0
    for r in range(rows):
        for c in range(cols):
            n += 1
            x0 = gx + c * (tile + gap)
            y0 = gy + r * (tile + gap)
            rect = [x0, y0, x0 + tile, y0 + tile]
            # last tile = amber highlight (current/active month), rest white-ish
            if n == 12:
                d.rounded_rectangle(rect, radius=int(26 * S), fill=AMBER + (255,))
                check_glyph(d, x0 + tile / 2, y0 + tile / 2, int(tile * 0.42),
                            NAVY_D + (255,), int(11 * S))
            else:
                # mini "log / record card" => a tracked month
                d.rounded_rectangle(rect, radius=int(26 * S), fill=(255, 255, 255, 235))
                pad = tile * 0.18
                # header strip
                d.rounded_rectangle([x0 + pad, y0 + pad,
                                     x0 + tile - pad, y0 + pad + int(15 * S)],
                                    radius=int(7 * S), fill=BLUE + (255,))
                # two faint record lines
                for k, frac in enumerate((0.50, 0.70)):
                    ll = tile - pad * 2 if k == 0 else (tile - pad * 2) * 0.62
                    ly = y0 + tile * frac
                    d.rounded_rectangle([x0 + pad, ly, x0 + pad + ll, ly + int(10 * S)],
                                        radius=int(5 * S), fill=(BLUE_LT + (150,)))

    # ---- product label ----
    text_center(d, cx, int(W * 0.77), "Annual", font(F_BOLD, 92), WHITE + (255,))
    text_center(d, cx, int(W * 0.862), "12 Months Full Access · Part 135",
                font(F_REG, 33), (255, 255, 255, 210))

    finish(img, "promo-annual-1024.png")


if __name__ == "__main__":
    make_monthly()
    make_annual()
