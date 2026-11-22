#!/usr/bin/env python3
"""Draw one front page summing up Sunday 22 November 2026.

Renders at 2x and downsamples, so text and shapes are antialiased.
Only the resulting entry.png is shipped; this script is the drawing code.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

W = 1024
S = 2                      # supersampling factor
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
PAPER   = (246, 242, 232)
INK     = (22, 24, 28)
GREY    = (92, 94, 98)
LGREY   = (150, 148, 142)
RULE    = (198, 191, 176)
RED     = (176, 18, 30)
NAVY    = (21, 46, 76)
GOLD    = (188, 138, 26)
TEAL    = (16, 106, 98)

REG = {
    "EUROPE":       (30, 78, 140),
    "MIDDLE EAST":  (166, 36, 43),
    "AMERICAS":     (24, 107, 87),
    "ASIA":         (176, 113, 26),
    "AFRICA":       (106, 62, 143),
    "OCEANIA":      (23, 112, 140),
    "WORLD":        (58, 63, 70),
}

# ---------------------------------------------------------------- fonts
def F(face, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", face), int(round(size * S)))

SERIF_B = "PTSerif-Bold.ttf"
SERIF   = "PTSerif-Reg.ttf"
SERIF_I = "PTSerif-It.ttf"
SERIF_BI= "PTSerif-BoldIt.ttf"
SANS_B  = "PTSans-Bold.ttf"
SANS    = "PTSans-Reg.ttf"
NARROW_B= "PTSansNarrow-Bold.ttf"
NARROW  = "PTSansNarrow-Reg.ttf"

# ---------------------------------------------------------------- text helpers
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return (b[2] - b[0]) / S

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def ellipsize(d, s, f, maxw):
    if tw(d, s, f) <= maxw:
        return s
    while s and tw(d, s + "\u2026", f) > maxw:
        s = s[:-1]
    return s.rstrip() + "\u2026"

def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text((xy[0] * S, xy[1] * S), s, font=f, fill=fill, anchor=anchor)

def para(d, x, y, maxw, s, f, fill, lh, maxlines, ell=True):
    lines = wrap(d, s, f, maxw)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        lines[-1] = ellipsize(d, lines[-1], f, maxw)
    for i, ln in enumerate(lines):
        text(d, (x, y + i * lh), ln, f, fill)
    return len(lines) * lh

def fit_headline(d, s, maxw, maxlines, sizes):
    """Pick the largest size at which s fits in maxlines; return font, lines."""
    for sz in sizes:
        f = F(SERIF_B, sz)
        lines = wrap(d, s, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
    f = F(SERIF_B, sizes[-1])
    lines = wrap(d, s, f, maxw)[:maxlines]
    lines[-1] = ellipsize(d, lines[-1], f, maxw)
    return f, lines

def rule(d, x0, y, x1, col=RULE, wd=1):
    d.rectangle([x0 * S, y * S, x1 * S, y * S + max(1, int(wd * S))], fill=col)

def box(d, x0, y0, x1, y1, fill=None, outline=None, wd=1):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=fill, outline=outline,
                width=max(1, int(wd * S)))

# ---------------------------------------------------------------- icons
# Every icon is drawn in fractions of its box, so it looks the same at any size.
def _ell(d, cx, cy, rx, ry, fill=None, outline=None, wd=1):
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
              fill=fill, outline=outline, width=max(1, int(wd * S)))

def _dot(d, cx, cy, r, fill):
    _ell(d, cx, cy, r, r, fill=fill)

def _poly(d, pts, fill):
    d.polygon([(px * S, py * S) for px, py in pts], fill=fill)

def _line(d, pts, fill, wd=1.2):
    d.line([(px * S, py * S) for px, py in pts], fill=fill, width=max(1, int(wd * S)))

def icon_talks(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (28, 62, 96))
    cx, cy, r = x + 0.14 * w, y + 0.50 * h, 0.34 * h
    _ell(d, cx, cy, r, r, outline=(120, 170, 210), wd=1.2)
    _ell(d, cx, cy, r, r * 0.42, outline=(120, 170, 210), wd=1.0)
    _line(d, [(cx - r, cy), (cx + r, cy)], (120, 170, 210), 1.0)
    _line(d, [(cx, cy - r), (cx, cy + r)], (120, 170, 210), 1.0)
    tx, ty = x + 0.70 * w, y + 0.66 * h
    _ell(d, tx, ty, 0.20 * w, 0.15 * h, fill=(232, 224, 202))
    for i in range(6):
        a = math.pi * (0.10 + 0.16 * i)
        _dot(d, tx + 0.16 * w * math.cos(a), ty - 0.30 * h * math.sin(a), 0.075 * h, (224, 192, 122))
    # clock
    kx, ky, kr = x + w - 0.10 * w, y + 0.24 * h, 0.14 * h
    _ell(d, kx, ky, kr, kr, fill=(242, 238, 226))
    _line(d, [(kx, ky), (kx, ky - 0.7 * kr)], RED, 1.3)
    _line(d, [(kx, ky), (kx + 0.55 * kr, ky + 0.25 * kr)], RED, 1.3)

def icon_shipfire(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (18, 30, 44))
    d.rectangle([x * S, (y + 0.74 * h) * S, (x + w) * S, (y + h) * S], fill=(12, 44, 70))
    for i in range(5):
        _line(d, [(x + (0.06 + i * 0.20) * w, y + 0.88 * h),
                  (x + (0.14 + i * 0.20) * w, y + 0.88 * h)], (44, 96, 128), 1.0)
    hx, hy = x + 0.20 * w, y + 0.74 * h
    _poly(d, [(hx, hy), (hx + 0.46 * w, hy), (hx + 0.41 * w, hy + 0.13 * h),
              (hx + 0.03 * w, hy + 0.13 * h)], (100, 106, 114))
    d.rectangle([(hx + 0.30 * w) * S, (hy - 0.20 * h) * S, (hx + 0.40 * w) * S, hy * S], fill=(224, 222, 214))
    d.rectangle([(hx + 0.14 * w) * S, (hy - 0.12 * h) * S, (hx + 0.26 * w) * S, hy * S], fill=(202, 200, 192))
    for fx, fh in ((hx + 0.13 * w, 0.40 * h), (hx + 0.23 * w, 0.52 * h), (hx + 0.34 * w, 0.34 * h)):
        _poly(d, [(fx - 0.035 * w, hy - 0.02 * h), (fx, hy - fh), (fx + 0.035 * w, hy - 0.02 * h)], (242, 142, 42))
        _poly(d, [(fx - 0.014 * w, hy - 0.02 * h), (fx + 0.004 * w, hy - fh * 0.62), (fx + 0.02 * w, hy - 0.02 * h)], (252, 212, 92))
    for i in range(4):
        _dot(d, hx + 0.26 * w + i * 0.035 * w, hy - 0.62 * h - i * 0.10 * h, (0.09 - i * 0.012) * h, (72, 76, 84))
    dx, dy = x + 0.84 * w, y + 0.24 * h
    _line(d, [(dx - 0.09 * w, dy), (dx + 0.09 * w, dy)], (182, 192, 202), 1.2)
    for sg in (-1, 1):
        _line(d, [(dx + sg * 0.09 * w, dy), (dx + sg * 0.13 * w, dy - 0.10 * h)], (182, 192, 202), 1.0)
        _line(d, [(dx + sg * 0.13 * w, dy - 0.10 * h), (dx + sg * 0.13 * w, dy - 0.03 * h)], (182, 192, 202), 1.0)
    _dot(d, dx, dy, 0.04 * h, (212, 218, 226))

def icon_missile(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (48, 26, 30))
    cx, cy = x + 0.84 * w, y + 1.02 * h
    for r in (0.42, 0.66, 0.90):
        d.arc([(cx - r * h) * S, (cy - r * h) * S, (cx + r * h) * S, (cy + r * h) * S],
              200, 340, fill=(150, 82, 82), width=max(1, int(1.1 * S)))
    _dot(d, cx, cy - 0.02 * h, 0.06 * h, (222, 124, 92))
    _line(d, [(x + 0.05 * w, y + 0.22 * h), (x + 0.50 * w, y + 0.66 * h)], (232, 202, 152), 2.0)
    tx, ty = x + 0.60 * w, y + 0.70 * h
    _poly(d, [(tx + 0.02 * w, ty), (tx - 0.035 * w, ty - 0.07 * h), (tx - 0.02 * w, ty + 0.06 * h)], (242, 232, 212))
    _ell(d, tx + 0.05 * w, ty, 0.16 * h, 0.16 * h, outline=(240, 202, 122), wd=1.4)
    _line(d, [(tx - 0.02 * w, ty), (tx + 0.12 * w, ty)], (240, 202, 122), 1.0)
    _line(d, [(tx + 0.05 * w, ty - 0.07 * h), (tx + 0.05 * w, ty + 0.07 * h)], (240, 202, 122), 1.0)

def icon_wanted(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (74, 24, 28))
    px, py, pw, ph = x + 0.28 * w, y + 0.06 * h, 0.44 * w, 0.88 * h
    box(d, px, py, px + pw, py + ph, (232, 222, 196))
    text(d, (px + pw / 2, py + 0.10 * ph), "WANTED", F(NARROW_B, 0.22 * ph), RED, "ma")
    _dot(d, px + pw / 2, py + 0.48 * ph, 0.20 * ph, (150, 140, 125))
    d.rectangle([(px + 0.22 * pw) * S, (py + 0.58 * ph) * S, (px + 0.78 * pw) * S, (py + 0.72 * ph) * S], fill=(150, 140, 125))
    text(d, (px + pw / 2, py + 0.90 * ph), "$5M", F(NARROW_B, 0.24 * ph), INK, "ma")

def icon_boat(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (20, 62, 96))
    d.rectangle([x * S, (y + 0.70 * h) * S, (x + w) * S, (y + h) * S], fill=(12, 44, 74))
    cx, cy = x + 0.50 * w, y + 0.62 * h
    _poly(d, [(cx - 0.32 * w, cy + 0.10 * h), (cx + 0.30 * w, cy - 0.10 * h),
              (cx + 0.22 * w, cy + 0.14 * h), (cx - 0.28 * w, cy + 0.24 * h)], (226, 220, 204))
    for i in range(4):
        _dot(d, cx - 0.22 * w + i * 0.10 * w, cy + 0.28 * h + (i % 2) * 0.05 * h, 0.055 * h, (232, 202, 162))
    for i in range(3):
        yy = y + 0.86 * h + i * 0.03 * h
        d.arc([(x + (0.10 + i * 0.22) * w) * S, (yy - 0.05 * h) * S,
               (x + (0.26 + i * 0.22) * w) * S, (yy + 0.05 * h) * S],
              200, 340, fill=(94, 152, 192), width=max(1, int(1.1 * S)))

def icon_cyber(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (26, 30, 36))
    for i in range(2):
        rx = x + (0.08 + i * 0.16) * w
        box(d, rx, y + 0.12 * h, rx + 0.12 * w, y + 0.88 * h, (46, 52, 60), outline=(90, 98, 108))
        for j in range(4):
            d.rectangle([(rx + 0.02 * w) * S, (y + (0.20 + j * 0.15) * h) * S,
                         (rx + 0.10 * w) * S, (y + (0.26 + j * 0.15) * h) * S], fill=(70, 78, 88))
            _dot(d, rx + 0.09 * w, y + (0.23 + j * 0.15) * h, 0.018 * h,
                 (120, 220, 140) if j % 2 else (232, 122, 92))
    wx, wy = x + 0.78 * w, y + 0.50 * h
    _poly(d, [(wx, wy - 0.30 * h), (wx + 0.14 * w, wy + 0.22 * h), (wx - 0.14 * w, wy + 0.22 * h)], (232, 182, 42))
    text(d, (wx, wy + 0.02 * h), "!", F(SANS_B, 0.36 * h), INK, "mm")
    _line(d, [(x + 0.44 * w, y + 0.20 * h), (x + 0.56 * w, y + 0.36 * h)], RED, 1.3)
    _line(d, [(x + 0.44 * w, y + 0.36 * h), (x + 0.56 * w, y + 0.20 * h)], RED, 1.3)

def icon_parliament(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (208, 198, 174))
    cx = x + w / 2
    _poly(d, [(cx - 0.26 * w, y + 0.26 * h), (cx, y + 0.05 * h), (cx + 0.26 * w, y + 0.26 * h)], (152, 140, 118))
    d.rectangle([(cx - 0.26 * w) * S, (y + 0.26 * h) * S, (cx + 0.26 * w) * S, (y + 0.33 * h) * S], fill=(152, 140, 118))
    for i in range(5):
        px = cx - 0.22 * w + i * 0.11 * w
        d.rectangle([px * S, (y + 0.34 * h) * S, (px + 0.055 * w) * S, (y + 0.78 * h) * S], fill=(242, 236, 220))
    d.rectangle([(cx - 0.27 * w) * S, (y + 0.78 * h) * S, (cx + 0.27 * w) * S, (y + 0.88 * h) * S], fill=(152, 140, 118))
    for sg, col in ((-1, (42, 62, 102)), (1, (124, 62, 42))):
        _dot(d, cx + sg * 0.16 * w, y + 0.93 * h, 0.055 * h, col)

def icon_hospital(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (224, 228, 230))
    bx = x + 0.10 * w
    box(d, bx, y + 0.24 * h, bx + 0.30 * w, y + 0.92 * h, (246, 246, 242), outline=(162, 168, 172))
    for i in range(2):
        for j in range(2):
            d.rectangle([(bx + (0.05 + j * 0.11) * w) * S, (y + (0.34 + i * 0.20) * h) * S,
                         (bx + (0.11 + j * 0.11) * w) * S, (y + (0.46 + i * 0.20) * h) * S], fill=(150, 172, 192))
    d.rectangle([(bx + 0.11 * w) * S, (y + 0.06 * h) * S, (bx + 0.19 * w) * S, (y + 0.22 * h) * S], fill=RED)
    d.rectangle([(bx + 0.05 * w) * S, (y + 0.11 * h) * S, (bx + 0.25 * w) * S, (y + 0.17 * h) * S], fill=RED)
    pts = []
    for i in range(41):
        t = i / 40
        yy = y + 0.55 * h + (-0.16 * h if i % 10 == 1 else (-0.02 * h if i % 10 == 2 else 0))
        pts.append((x + (0.46 + t * 0.48) * w, yy))
    _line(d, pts, (18, 122, 92), 1.5)

def icon_bottle(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (54, 42, 32))
    cx, cy = x + 0.36 * w, y + 0.54 * h
    d.rectangle([(cx - 0.055 * w) * S, (cy - 0.36 * h) * S, (cx + 0.055 * w) * S, (cy + 0.36 * h) * S], fill=(192, 212, 182))
    d.rectangle([(cx - 0.028 * w) * S, (cy - 0.48 * h) * S, (cx + 0.028 * w) * S, (cy - 0.34 * h) * S], fill=(192, 212, 182))
    d.rectangle([(cx - 0.062 * w) * S, (cy - 0.10 * h) * S, (cx + 0.062 * w) * S, (cy + 0.14 * h) * S], fill=(232, 222, 192))
    sx, sy = x + 0.70 * w, y + 0.52 * h
    _dot(d, sx, sy, 0.20 * h, (232, 228, 216))
    d.rectangle([(sx - 0.11 * h) * S, (sy + 0.10 * h) * S, (sx + 0.11 * h) * S, (sy + 0.30 * h) * S], fill=(232, 228, 216))
    _dot(d, sx - 0.07 * h, sy - 0.03 * h, 0.04 * h, INK)
    _dot(d, sx + 0.07 * h, sy - 0.03 * h, 0.04 * h, INK)

def icon_sub(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (16, 44, 70))
    cx, cy = x + 0.50 * w, y + 0.58 * h
    _ell(d, cx, cy, 0.30 * w, 0.20 * h, fill=(62, 70, 78))
    _poly(d, [(cx - 0.30 * w, cy), (cx - 0.38 * w, cy - 0.16 * h), (cx - 0.38 * w, cy + 0.16 * h)], (62, 70, 78))
    d.rectangle([(cx + 0.02 * w) * S, (cy - 0.42 * h) * S, (cx + 0.06 * w) * S, (cy - 0.16 * h) * S], fill=(62, 70, 78))
    d.rectangle([(cx - 0.02 * w) * S, (cy - 0.50 * h) * S, (cx + 0.10 * w) * S, (cy - 0.42 * h) * S], fill=(62, 70, 78))
    _line(d, [(cx - 0.02 * w, cy - 0.50 * h), (cx - 0.02 * w, cy - 0.76 * h)], (204, 204, 204), 1.1)
    d.rectangle([(cx - 0.01 * w) * S, (cy - 0.76 * h) * S, (cx + 0.10 * w) * S, (cy - 0.62 * h) * S], fill=(232, 232, 228))
    d.rectangle([(cx - 0.01 * w) * S, (cy - 0.69 * h) * S, (cx + 0.10 * w) * S, (cy - 0.62 * h) * S], fill=(182, 42, 42))
    for i in range(3):
        d.arc([(x + (0.08 + i * 0.28) * w) * S, (cy + 0.22 * h) * S,
               (x + (0.30 + i * 0.28) * w) * S, (cy + 0.44 * h) * S],
              200, 340, fill=(72, 124, 164), width=max(1, int(1.1 * S)))

def icon_trade(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (224, 216, 196))
    cx, cy = x + 0.50 * w, y + 0.80 * h
    _poly(d, [(cx - 0.34 * w, cy - 0.06 * h), (cx + 0.30 * w, cy - 0.06 * h),
              (cx + 0.25 * w, cy + 0.14 * h), (cx - 0.29 * w, cy + 0.14 * h)], (62, 68, 74))
    cols = [(182, 62, 52), (32, 92, 142), (202, 152, 42), (42, 122, 92)]
    for i in range(5):
        for j in range(2):
            d.rectangle([(cx - 0.29 * w + i * 0.11 * w) * S, (cy - (0.20 + j * 0.13) * h) * S,
                         (cx - 0.22 * w + i * 0.11 * w) * S, (cy - (0.09 + j * 0.13) * h) * S], fill=cols[(i + j) % 4])
    d.rectangle([(x + 0.06 * w) * S, (y + 0.10 * h) * S, (x + 0.26 * w) * S, (y + 0.30 * h) * S], fill=(30, 60, 140))
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        _dot(d, x + 0.16 * w + 0.07 * w * math.cos(a), y + 0.20 * h + 0.07 * w * math.sin(a), 0.018 * h, (240, 202, 62))
    d.rectangle([(x + 0.74 * w) * S, (y + 0.10 * h) * S, (x + 0.94 * w) * S, (y + 0.20 * h) * S], fill=(202, 42, 42))
    d.rectangle([(x + 0.74 * w) * S, (y + 0.20 * h) * S, (x + 0.94 * w) * S, (y + 0.30 * h) * S], fill=(242, 242, 238))
    _line(d, [(x + 0.28 * w, y + 0.26 * h), (x + 0.72 * w, y + 0.26 * h)], (124, 114, 98), 1.2)

def icon_protest(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (234, 228, 212))
    for px, py, col in ((0.10, 0.10, RED), (0.40, 0.05, NAVY), (0.70, 0.12, TEAL)):
        sx = x + px * w
        _line(d, [(sx + 0.05 * w, y + py * h + 0.30 * h), (sx + 0.05 * w, y + 0.80 * h)], (112, 102, 90), 1.2)
        box(d, sx, y + py * h, sx + 0.20 * w, y + py * h + 0.30 * h, col)
        text(d, (sx + 0.10 * w, y + py * h + 0.16 * h), "!", F(SANS_B, 0.30 * h), (255, 255, 255), "mm")
    for i in range(7):
        cx = x + (0.09 + i * 0.135) * w
        cy = y + 0.86 * h - (i % 2) * 0.05 * h
        _dot(d, cx, cy, 0.10 * h, (60, 56, 52))
        d.rectangle([(cx - 0.055 * w) * S, (cy + 0.08 * h) * S, (cx + 0.055 * w) * S, (cy + 0.22 * h) * S], fill=(60, 56, 52))

def icon_market(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (24, 32, 40))
    for i in range(1, 4):
        _line(d, [(x + 0.03 * w, y + i * h / 4), (x + 0.97 * w, y + i * h / 4)], (48, 58, 68), 0.8)
    pts = [(0, .30), (.18, .40), (.34, .34), (.5, .52), (.66, .50), (.82, .72), (1, .80)]
    poly = [(x + (0.05 + t * 0.88) * w, y + (0.12 + v * 0.72) * h) for t, v in pts]
    _line(d, poly, (232, 92, 72), 2.0)
    ax, ay = poly[-1]
    _poly(d, [(ax, ay), (ax - 0.05 * w, ay - 0.02 * h), (ax - 0.025 * w, ay - 0.13 * h)], (232, 92, 72))
    text(d, (x + 0.94 * w, y + 0.10 * h), "-2.4%", F(SANS_B, 0.28 * h), (242, 122, 92), "ra")

def icon_swim(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (16, 52, 82))
    for i in range(3):
        d.arc([(x + (0.02 + i * 0.30) * w) * S, (y + 0.70 * h) * S,
               (x + (0.26 + i * 0.30) * w) * S, (y + 0.86 * h) * S],
              195, 345, fill=(80, 150, 196), width=max(1, int(1.3 * S)))
    # swimmer: head, arm arc, body, splash
    hx, hy = x + 0.56 * w, y + 0.36 * h
    _dot(d, hx, hy, 0.085 * h, (232, 202, 162))
    _line(d, [(hx - 0.02 * w, hy + 0.07 * h), (hx - 0.20 * w, hy + 0.14 * h),
              (hx - 0.34 * w, hy + 0.09 * h)], (226, 196, 156), 3.2)
    _line(d, [(hx + 0.05 * w, hy + 0.08 * h), (hx + 0.17 * w, hy + 0.02 * h),
              (hx + 0.26 * w, hy - 0.10 * h)], (226, 196, 156), 2.6)
    for i in range(5):
        _dot(d, hx - 0.36 * w - i * 0.03 * w, hy + 0.10 * h - (i % 2) * 0.05 * h,
             0.020 * h, (200, 226, 240))
    # distant tanker
    _line(d, [(x + 0.72 * w, y + 0.22 * h), (x + 0.90 * w, y + 0.22 * h)], (150, 180, 200), 1.4)

ICONS = {
    "talks": icon_talks, "swim": icon_swim, "ship": icon_shipfire, "missile": icon_missile,
    "wanted": icon_wanted, "boat": icon_boat, "cyber": icon_cyber,
    "parliament": icon_parliament, "hospital": icon_hospital, "bottle": icon_bottle,
    "sub": icon_sub, "trade": icon_trade, "protest": icon_protest, "market": icon_market,
}

# ---------------------------------------------------------------- content
LEADS = [
    dict(region="WORLD", kicker="CLIMATE \u00b7 COP31", chip="TOP STORY",
         head="Climate talks run into a second day of overtime",
         dek="Negotiators worked through the night in Antalya after a fight over fossil fuels blocked a final text. The summit president said a deal all parties can accept was close.",
         src="Reuters \u00b7 AP \u00b7 BBC \u00b7 DW", icon="talks", chip2="~200 NATIONS"),
    dict(region="EUROPE", kicker="BALTIC \u00b7 UKRAINE WAR", chip="ESCALATION",
         head="War spills into the Baltic as a Russian ship burns",
         dek="Finland says Ukraine was likely behind the drone that set the cargo ship Sparta II ablaze in the Gulf of Finland. Russia fired 400+ drones and 110 missiles overnight.",
         src="Guardian \u00b7 BBC \u00b7 Reuters", icon="ship", chip2="400+ DRONES"),
    dict(region="MIDDLE EAST", kicker="IRAN \u00b7 GULF", chip="REGION ON EDGE",
         head="Iran strikes US bases in Bahrain as tankers burn",
         dek="Tehran targeted US sites in Bahrain, where a fire broke out at an industrial plant. Two tankers were hit near Oman and Houthi missiles flew at Saudi Arabia.",
         src="Al Jazeera \u00b7 AP \u00b7 Reuters", icon="missile", chip2="2 TANKERS HIT"),
]

MEDIUM = [
    dict(region="AMERICAS", kicker="MEXICO", head="El Chapo Isidro seized in a shoot-out; 11 killed",
         dek="The FBI most-wanted boss, Fausto Isidro Meza Flores, was captured by special forces in Sinaloa.",
         src="BBC \u00b7 AP \u00b7 Al Jazeera", icon="wanted"),
    dict(region="AFRICA", kicker="NIGERIA", head="Mourners\u2019 boat capsizes, killing at least 24",
         dek="The overcrowded vessel was carrying mourners to a funeral in Bayelsa state when it went down.",
         src="Al Jazeera \u00b7 AFP", icon="boat"),
    dict(region="AMERICAS", kicker="UNITED STATES", head="FBI crime database hit by apparent hack",
         dek="The NCIC, used by police nationwide, was reportedly breached; hackers also hit the USDA.",
         src="BBC \u00b7 Japan Times", icon="cyber"),
    dict(region="MIDDLE EAST", kicker="ISRAEL", head="Eisenkot invites Likud to \u201cmarathon\u201d talks",
         dek="The incoming prime minister asked Netanyahu\u2019s party to join coalition negotiations.",
         src="France 24", icon="parliament"),
    dict(region="AMERICAS", kicker="BRAZIL", head="Bolsonaro in intensive care with bowel obstruction",
         dek="The former president is being treated in Brasilia, his family said.",
         src="Al Jazeera", icon="hospital"),
    dict(region="ASIA", kicker="INDIA", head="Illicit alcohol kills 11 in Manipur",
         dek="The state ordered a probe into the toxic batch and promised arrests.",
         src="Al Jazeera", icon="bottle"),
    dict(region="OCEANIA", kicker="AUSTRALIA", head="Marles: US report on AUKUS subs \u201cis wrong\u201d",
         dek="The defence minister rejected a Congressional Budget Office warning that the submarine sale could shrink the US fleet.",
         src="ABC News", icon="sub"),
    dict(region="ASIA", kicker="TRADE", head="EU and Indonesia sign a trade pact after 10 years",
         dek="The deal lands days after a new EU\u2013UK agreement on trade and young people.",
         src="DW \u00b7 France 24", icon="trade"),
    dict(region="EUROPE", kicker="FRANCE", head="Sixth weekend of protests; clashes across France",
         dek="Turnout fell at the day\u2019s marches, the interior ministry said, but skirmishes ran into the night.",
         src="Al Jazeera \u00b7 Japan Times", icon="protest"),
    dict(region="MIDDLE EAST", kicker="GULF", head="Swimmer crosses Hormuz despite the Iran war",
         dek="An endurance athlete swam the Strait of Hormuz despite the war raging around it.",
         src="ABC News \u00b7 France 24", icon="swim"),
]

BRIEFS = [
    ("EUROPE", "Denmark expels Russia\u2019s defence attach\u00e9 over an alleged plot to kill a US-Ukrainian rapper.", "BBC"),
    ("EUROPE", "EU and UK sign a post-Brexit deal; Miliband says it does not depend on tuition fees.", "BBC"),
    ("EUROPE", "Zelensky calls the Crimea bridge strikes a \u201cfair response\u201d to 109 Russian attacks on bridges.", "BBC"),
    ("EUROPE", "Thousands rally across Europe over living costs, housing and public services.", "Al Jazeera"),
    ("MIDDLE EAST", "Lebanon\u2019s Aoun demands an Israeli withdrawal and decries Iran\u2019s interference.", "Al Jazeera"),
    ("MIDDLE EAST", "An Israeli strike hits a food-aid vehicle in Gaza, killing three.", "Al Jazeera"),
    ("MIDDLE EAST", "Bessent confirms he is living on a US military base over Iran fears.", "Al Jazeera"),
    ("MIDDLE EAST", "Iran\u2019s FM seeks guarantees before talks; Trump calls the terms unacceptable.", "Japan Times"),
    ("AMERICAS", "A man is convicted of starting the Palisades fire, which killed 12 and destroyed 6,800 buildings.", "BBC"),
    ("AMERICAS", "Mamdani plans to close New York\u2019s Rikers Island jail by 2032.", "BBC"),
    ("AMERICAS", "Trump ousts his cyber director after outages hit air travel and banks.", "Japan Times"),
    ("AMERICAS", "Trump basks in summit pomp as Xi strengthens his hand.", "Japan Times"),
    ("ASIA", "Japan\u2019s Princess Aiko returns from a visit to Singapore.", "Japan Times"),
    ("ASIA", "Nagano\u2019s celery farmers are running out of altitude as warming bites.", "Japan Times"),
    ("ASIA", "Mao Shimada wins the Finlandia Trophy to book a place in the Grand Prix Final.", "Japan Times"),
    ("AFRICA", "South Africa\u2019s ANC fights to hold key cities after its election setback.", "BBC"),
    ("AFRICA", "Nigeria\u2019s youth registration lags ahead of 2027, worrying democracy campaigners.", "BBC"),
    ("AFRICA", "Ethiopia and Eritrea mass troops along their border.", "France 24"),
    ("OCEANIA", "Fred Nile, veteran NSW politician and Christian Democrat figurehead, dies at 92.", "Guardian"),
    ("OCEANIA", "The Wallabies hold off Wales; Scotland overpower Japan.", "ABC \u00b7 Japan Times"),
    ("WORLD", "UN talks open a path to a pact on \u201ckiller robots\u201d.", "Japan Times"),
    ("WORLD", "An Anthropic researcher says Claude may have helped prove the Riemann hypothesis.", "BBC"),
    ("WORLD", "Piastri takes a Las Vegas grid penalty as rivals warn of \u201cchaos\u201d in the cold.", "ABC News"),
    ("WORLD", "A lock of George Washington\u2019s hair sells for $4,000.", "BBC"),
]

assert len(LEADS) == 3 and len(MEDIUM) == 10 and len(BRIEFS) == 24
N_STORIES = len(LEADS) + len(MEDIUM) + len(BRIEFS)

REGION_COUNTS = {}
for s in LEADS + MEDIUM:
    REGION_COUNTS[s["region"]] = REGION_COUNTS.get(s["region"], 0) + 1
for r, _, _ in BRIEFS:
    REGION_COUNTS[r] = REGION_COUNTS.get(r, 0) + 1

# ---------------------------------------------------------------- world map
def load_land(w, h):
    """Return a dot mask of land, equirectangular, lat 84..-58."""
    with open(os.path.join(HERE, "countries.geojson")) as fh:
        gj = json.load(fh)
    mask = Image.new("L", (int(w * S), int(h * S)), 0)
    md = ImageDraw.Draw(mask)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 84.0, -58.0
    def proj(lon, lat):
        return (((lon - lon0) / (lon1 - lon0)) * w * S,
                ((lat0 - lat) / (lat0 - lat1)) * h * S)
    for feat in gj["features"]:
        geom = feat.get("geometry") or {}
        polys = geom.get("coordinates") or []
        if geom.get("type") == "Polygon":
            polys = [polys]
        for poly in polys:
            for ring in poly[:1]:
                pts = [proj(x, y) for x, y in ring]
                if len(pts) > 2:
                    md.polygon(pts, fill=255)
    return mask

def draw_map(d, x, y, w, h):
    box(d, x, y, x + w, y + h, (238, 233, 219))
    mask = load_land(w, h)
    step = 3.3
    px = mask.load()
    gy = 2.0
    while gy < h:
        gx = 2.0
        while gx < w:
            if px[int(gx * S), int(gy * S)] > 128:
                d.ellipse([((x + gx) * S) - 1.15 * S, ((y + gy) * S) - 1.15 * S,
                           ((x + gx) * S) + 1.15 * S, ((y + gy) * S) + 1.15 * S],
                          fill=(166, 158, 138))
            gx += step
        gy += step
    # equator hint
    ey = y + (84.0 / 142.0) * h
    d.line([x * S, ey * S, (x + w) * S, ey * S], fill=(214, 206, 188), width=int(1 * S))
    return

# number, latitude, longitude, and a nudge (px) for the bubble where pins crowd
PINS = [
    (1, 36.9, 30.7, -10, -16), (2, 60.0, 26.0, 0, 0), (3, 26.0, 50.5, 22, -2),
    (4, 25.5, -108.5, 0, 0), (5, 4.8, 6.3, 0, 0), (6, 38.9, -77.0, 0, 0),
    (7, 31.8, 35.2, 10, 16), (8, -15.8, -47.9, 0, 0), (9, 24.8, 93.9, 0, 0),
    (10, -35.3, 149.1, 0, 0), (11, -6.2, 106.8, 0, 0), (12, 48.9, 2.4, 0, 0),
    (13, 26.6, 56.3, 14, 16),
]

def pin_xy(n, lat, lon, x, y, w, h):
    px = x + (lon + 180.0) / 360.0 * w
    py = y + (84.0 - lat) / 142.0 * h
    return px, py

def draw_pins(d, x, y, w, h):
    for n, lat, lon, ox, oy in PINS:
        px, py = pin_xy(n, lat, lon, x, y, w, h)
        if ox or oy:
            _line(d, [(px, py), (px + ox, py + oy)], (150, 30, 36), 0.9)
            _dot(d, px, py, 1.6, RED)
        bx, by = px + ox, py + oy
        d.ellipse([(bx - 5.6) * S, (by - 5.6) * S, (bx + 5.6) * S, (by + 5.6) * S],
                  fill=RED, outline=(250, 246, 236), width=int(0.9 * S))
        text(d, (bx, by + 0.2), str(n), F(SANS_B, 6.2), (255, 255, 255), "mm")

# ---------------------------------------------------------------- build
def build(out):
    img = Image.new("RGB", (W * S, W * S), PAPER)
    d = ImageDraw.Draw(img)
    M = 12
    RIGHT = W - M

    # ---- header
    rule(d, 0, 0, W, INK, 3)
    text(d, (M, 7), "THE WORLD IN ONE DAY", F(NARROW_B, 10.5), INK)
    text(d, (RIGHT, 7.5), f"{N_STORIES} STORIES \u00b7 7 REGIONS \u00b7 EVERY STORY DATED", F(NARROW, 9), GREY, "ra")

    title = "Sunday 22 November 2026"
    f = F(SERIF_B, 53)
    while tw(d, title, f) > W - 2 * M - 8:
        f = F(SERIF_B, f.size / S - 1)
    text(d, (W / 2, 13), title, f, INK, "ma")

    deck = "COP31 in overtime  \u00b7  Russia\u2019s war reaches the Baltic  \u00b7  Iran strikes Bahrain  \u00b7  El Chapo Isidro captured"
    df = F(SERIF_BI, 13)
    while tw(d, deck, df) > W - 2 * M - 4:
        df = F(SERIF_BI, df.size / S - 0.5)
    text(d, (W / 2, 71), deck, df, RED, "ma")
    rule(d, M, 88, RIGHT, INK, 1.4)

    # ---- stat strip
    stats = [("~200", "NATIONS AT COP31"), ("400+", "DRONES OVER UKRAINE"),
             ("11", "KILLED IN SINALOA"), ("24", "DEAD IN NIGERIA BOAT"),
             ("109", "RUSSIAN ATTACKS ON BRIDGES")]
    cw = (RIGHT - M) / len(stats)
    for i, (num, lab) in enumerate(stats):
        cx = M + cw * i + cw / 2
        text(d, (cx, 93), num, F(SERIF_B, 24), INK, "ma")
        text(d, (cx, 119), lab, F(NARROW_B, 7.6), GREY, "ma")
        if i:
            d.line([(M + cw * i) * S, 95 * S, (M + cw * i) * S, 126 * S], fill=RULE, width=int(1 * S))
    rule(d, M, 132, RIGHT, RULE, 1)

    # ---- region bar
    order = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA", "AFRICA", "OCEANIA", "WORLD"]
    total = sum(REGION_COUNTS.values())
    bx = M
    barw = RIGHT - M
    for r in order:
        n = REGION_COUNTS[r]
        seg = barw * n / total
        d.rectangle([bx * S, 137 * S, (bx + seg) * S, 151 * S], fill=REG[r])
        text(d, (bx + seg / 2, 144), f"{r}  {n}", F(NARROW_B, 8.4), (255, 255, 255), "mm")
        bx += seg

    # ---- leads
    y0 = 158
    colw = (barw - 2 * 10) / 3
    lead_h = 212
    for i, s in enumerate(LEADS):
        x = M + i * (colw + 10)
        # tag bar
        d.rectangle([x * S, y0 * S, (x + colw) * S, (y0 + 13) * S], fill=REG[s["region"]])
        d.rectangle([(x + 2) * S, (y0 + 2) * S, (x + 13) * S, (y0 + 11) * S], fill=(255, 255, 255))
        text(d, (x + 7.5, y0 + 6.6), str(i + 1), F(NARROW_B, 7.6), REG[s["region"]], "mm")
        text(d, (x + 17, y0 + 6.6), s["kicker"], F(NARROW_B, 8.2), (255, 255, 255), "lm")
        cw2 = tw(d, s["chip"], F(NARROW_B, 7.4)) + 9
        d.rectangle([(x + colw - cw2) * S, (y0 + 2) * S, (x + colw - 2) * S, (y0 + 11) * S], fill=(255, 255, 255))
        text(d, (x + colw - cw2 / 2 - 2, y0 + 6.6), s["chip"], F(NARROW_B, 7.4), REG[s["region"]], "mm")
        # art
        ICONS[s["icon"]](d, x, y0 + 15, colw, 88)
        if s.get("chip2"):
            lab = s["chip2"]
            cw3 = tw(d, lab, F(NARROW_B, 7.6)) + 10
            d.rectangle([(x + 5) * S, (y0 + 15 + 88 - 14) * S, (x + 5 + cw3) * S, (y0 + 15 + 88 - 4) * S], fill=(250, 247, 238))
            text(d, (x + 5 + cw3 / 2, y0 + 15 + 88 - 9), lab, F(NARROW_B, 7.6), INK, "mm")
        # headline
        hf, lines = fit_headline(d, s["head"], colw, 3, [21, 20, 19, 18])
        hy = y0 + 108
        for ln in lines:
            text(d, (x, hy), ln, hf, INK)
            hy += 21
        # dek
        dy = max(hy + 1, y0 + 108 + 3 * 21)
        para(d, x, dy, colw, s["dek"], F(NARROW, 9.2), (52, 54, 58), 10.6, 3)
        text(d, (x, y0 + lead_h - 9), s["src"], F(NARROW, 7.2), GREY)
        if i < 2:
            d.line([((x + colw + 5)) * S, y0 * S, ((x + colw + 5)) * S, (y0 + lead_h - 4) * S], fill=RULE, width=int(1 * S))

    rule(d, M, 376, RIGHT, INK, 1.2)

    # ---- medium grid
    gy0 = 384
    gap = 8
    mcw = (barw - 4 * gap) / 5
    cellh = 108
    for i, s in enumerate(MEDIUM):
        row, col = divmod(i, 5)
        x = M + col * (mcw + gap)
        y = gy0 + row * (cellh + 6)
        d.rectangle([x * S, y * S, (x + mcw) * S, (y + 10) * S], fill=REG[s["region"]])
        d.rectangle([(x + 1.5) * S, (y + 1.5) * S, (x + 10.5) * S, (y + 8.5) * S], fill=(255, 255, 255))
        text(d, (x + 6, y + 5.2), str(i + 4), F(NARROW_B, 6.4), REG[s["region"]], "mm")
        text(d, (x + 13, y + 5.2), s["kicker"], F(NARROW_B, 7.6), (255, 255, 255), "lm")
        ICONS[s["icon"]](d, x, y + 11, mcw, 38)
        hf, lines = fit_headline(d, s["head"], mcw, 2, [10.8, 10.4, 10.0, 9.6, 9.2])
        hy = y + 55
        for ln in lines:
            text(d, (x, hy), ln, hf, INK)
            hy += 10.6
        para(d, x, hy + 1.0, mcw, s["dek"], F(NARROW, 7.6), (62, 64, 68), 8.6, 2)
        text(d, (x, y + cellh - 6), s["src"], F(NARROW, 6.4), GREY)

    rule(d, M, 610, RIGHT, INK, 1.2)

    # ---- bottom: map + briefs
    by = 618
    mapw = 320
    # map panel
    text(d, (M, by), "WHERE IT HAPPENED", F(NARROW_B, 9), INK)
    text(d, (M + mapw, by), "pins mark the 13 lead and main stories", F(NARROW, 7), GREY, "ra")
    draw_map(d, M, by + 13, mapw, 168)
    draw_pins(d, M, by + 13, mapw, 168)

    # region tally
    ty = by + 188
    text(d, (M, ty), "THE DAY BY REGION", F(NARROW_B, 8), INK)
    ty += 11
    mx = max(REGION_COUNTS.values())
    for r in order:
        n = REGION_COUNTS[r]
        text(d, (M, ty), r, F(NARROW_B, 7.2), REG[r])
        bw2 = 120 * n / mx
        d.rectangle([(M + 78) * S, (ty + 1) * S, (M + 78 + bw2) * S, (ty + 7) * S], fill=REG[r])
        text(d, (M + 78 + bw2 + 3, ty), str(n), F(NARROW_B, 7.2), GREY)
        ty += 10.2
    text(d, (M, ty + 2), "13 numbered datelines \u00b7 37 stories \u00b7 7 regions", F(NARROW, 7), GREY)

    # briefs
    bx0 = M + mapw + 18
    text(d, (bx0, by), f"ALSO ON SUNDAY \u2014 {len(BRIEFS)} MORE STORIES", F(NARROW_B, 9), INK)
    text(d, (RIGHT, by), "all dated 22 Nov 2026", F(NARROW, 7), GREY, "ra")
    bw = (RIGHT - bx0 - 10) / 2
    rows = (len(BRIEFS) + 1) // 2
    lh = 23.2
    for i, (r, txt, src) in enumerate(BRIEFS):
        col = i // rows
        row = i % rows
        x = bx0 + col * (bw + 10)
        y = by + 14 + row * lh
        text(d, (x, y), f"{i + 1}", F(NARROW_B, 8.2), RED)
        text(d, (x + 12, y), r, F(NARROW_B, 7.4), REG[r])
        line = ellipsize(d, txt, F(NARROW, 8.0), bw - 12)
        text(d, (x + 12 + tw(d, r, F(NARROW_B, 7.4)) + 4, y), line, F(NARROW, 8.0), (40, 42, 46))
        d.line([x * S, (y + lh - 5) * S, (x + bw) * S, (y + lh - 5) * S], fill=(222, 215, 200), width=int(0.8 * S))

    # ---- footer
    fy = 928
    rule(d, M, fy - 4, RIGHT, INK, 1.2)
    box(d, M, fy, RIGHT, fy + 70, (240, 230, 222))
    d.rectangle([M * S, fy * S, (M + 3) * S, (fy + 70) * S], fill=RED)
    text(d, (M + 8, fy + 6), "DATE CHECK", F(NARROW_B, 8), RED)
    check = ("Wires read to 04:30 UTC on 22 November 2026. Every item was reported, or was still developing, on the day in at "
             "least one time zone. Left out as other days\u2019 news: Peru\u2019s M6.8 quake (20 Nov, local), COP31\u2019s opening "
             "(9 Nov), the ICJ\u2019s Myanmar genocide ruling (21 Nov) and last week\u2019s Kerch bridge attack.")
    cf = F(NARROW, 8.2)
    nlines = len(wrap(d, check, cf, RIGHT - M - 74))
    para(d, M + 64, fy + 5, RIGHT - M - 74, check, cf, (60, 50, 48), 10.2, 3)
    sy = fy + 6 + nlines * 10.2 + 6
    text(d, (M, sy), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, The Guardian, DW, France 24, ABC News Australia, The Japan Times.",
         F(NARROW, 7.2), GREY)
    text(d, (M, sy + 10), "Illustrations and map drawn in code. Stories attributed beside each item; figures as reported on the day.",
         F(NARROW, 7.2), GREY)
    text(d, (M, sy + 20), "Type: PT Serif and PT Sans Narrow. Map: Natural Earth 1:110m. Drawn with Python and Pillow.",
         F(NARROW, 7.0), (128, 120, 112))
    text(d, (M, sy + 30), "Figures are as the named outlets reported them before 04:30 UTC; developing stories may have moved on since.",
         F(NARROW, 7.0), (128, 120, 112))

    # bottom bar
    d.rectangle([0, (W - 6) * S, W * S, W * S], fill=INK)
    text(d, (M, W - 3.2), "THE WORLD IN ONE DAY", F(NARROW_B, 6.2), (235, 230, 220), "lm")
    text(d, (RIGHT, W - 3.2), "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE", F(NARROW, 6.2), (200, 195, 185), "rm")

    img = img.resize((W, W), Image.LANCZOS)
    img.save(out, optimize=True)
    return img

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    im = build(out)
    print(out, im.size, os.path.getsize(out), "bytes")
