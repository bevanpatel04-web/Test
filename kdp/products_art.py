"""Line-art generators: mandalas, patterns, color-by-number mosaics, verse lettering,
pencil-control tracing and scissor-skills pages."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw
from reportlab.lib.colors import HexColor, black, white

from .render import BOLD, DARK, SANS, SERIF, Box, fit_lines, wrap
from .specs import INCH

GREY = HexColor("#A6A6A6")

# ================================================================ mandalas & patterns


def _petal(c, cx, cy, r0, r1, ang, width):
    """A pointed petal from radius r0 to r1 around angle `ang` (radians); `width` is its half-angle."""
    rm = r0 + (r1 - r0) * 0.55
    x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
    x1, y1 = cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)
    ax, ay = cx + rm * math.cos(ang + width), cy + rm * math.sin(ang + width)
    bx, by = cx + rm * math.cos(ang - width), cy + rm * math.sin(ang - width)
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.curveTo(ax, ay, ax, ay, x1, y1)
    p.curveTo(bx, by, bx, by, x0, y0)
    p.close()
    c.drawPath(p, stroke=1, fill=0)


def draw_mandala(c, cx, cy, R, rng: random.Random, bold: float = 2.2):
    c.setStrokeColor(black)
    c.setLineWidth(bold)
    c.setLineJoin(1)
    n = rng.choice([8, 10, 12, 16])
    radii = sorted(rng.sample(range(12, 96), 5)) + [100]
    radii = [R * x / 100 for x in radii]
    c.circle(cx, cy, radii[0], stroke=1, fill=0)
    prev = radii[0]
    for k, r in enumerate(radii[1:]):
        motif = rng.choice(["petals", "dots", "scallops", "petals2", "rays", "leaves"])
        m = n * rng.choice([1, 1, 2]) if motif in ("dots", "scallops") else n
        if motif in ("petals", "petals2", "leaves"):
            w = math.pi / m * (0.9 if motif != "leaves" else 0.55)
            off = (math.pi / m) if (k % 2) else 0
            for i in range(m):
                _petal(c, cx, cy, prev, r, 2 * math.pi * i / m + off, w)
            if motif == "petals2":
                for i in range(m):
                    _petal(c, cx, cy, prev + (r - prev) * 0.25, r - (r - prev) * 0.15, 2 * math.pi * i / m + off, w * 0.45)
        elif motif == "dots":
            rr = min((r - prev) / 2.4, math.pi * r / m * 0.8)
            for i in range(m):
                a = 2 * math.pi * i / m
                rad = (prev + r) / 2
                c.circle(cx + rad * math.cos(a), cy + rad * math.sin(a), rr, stroke=1, fill=0)
            c.circle(cx, cy, r, stroke=1, fill=0)
        elif motif == "scallops":
            for i in range(m):
                a0 = 360 * i / m
                ext = 360 / m
                rad = r
                # arc bumps along circle radius r
                bx = cx + rad * math.cos(math.radians(a0 + ext / 2))
                by = cy + rad * math.sin(math.radians(a0 + ext / 2))
                br = math.pi * rad / m
                c.arc(bx - br, by - br, bx + br, by + br, a0 + ext / 2 - 90, 180)
            c.circle(cx, cy, prev + (r - prev) * 0.15, stroke=1, fill=0)
        else:  # rays
            for i in range(m):
                a = 2 * math.pi * i / m
                c.line(cx + prev * math.cos(a), cy + prev * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a))
            c.circle(cx, cy, r, stroke=1, fill=0)
        prev = r
    c.setLineJoin(0)


def draw_truchet(c, x, y, size, rng, cells=6, bold=2.4):
    c.setStrokeColor(black)
    c.setLineWidth(bold)
    s = size / cells
    for i in range(cells):
        for j in range(cells):
            x0, y0 = x + i * s, y + j * s
            if rng.random() < 0.5:
                c.arc(x0 - s / 2, y0 - s / 2, x0 + s / 2, y0 + s / 2, 0, 90)
                c.arc(x0 + s / 2, y0 + s / 2, x0 + 3 * s / 2, y0 + 3 * s / 2, 180, 90)
            else:
                c.arc(x0 + s / 2, y0 - s / 2, x0 + 3 * s / 2, y0 + s / 2, 90, 90)
                c.arc(x0 - s / 2, y0 + s / 2, x0 + s / 2, y0 + 3 * s / 2, 270, 90)
    c.rect(x, y, size, size)


def draw_circles_pattern(c, x, y, size, rng, bold=2.2):
    """Overlapping-circle lattice (flower-of-life style) clipped to a square."""
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, size, size)
    c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(black)
    c.setLineWidth(bold)
    r = size / rng.choice([4, 5, 6])
    dy = r * math.sqrt(3) / 2
    row = 0
    yy = y - r
    while yy < y + size + r:
        xx = x - r + (r / 2 if row % 2 else 0)
        while xx < x + size + r:
            c.circle(xx, yy, r, stroke=1, fill=0)
            xx += r
        yy += dy
        row += 1
    c.restoreState()
    c.setLineWidth(bold)
    c.rect(x, y, size, size)


def draw_star_pattern(c, x, y, size, rng, bold=2.2):
    c.setStrokeColor(black)
    c.setLineWidth(bold)
    cx, cy = x + size / 2, y + size / 2
    pts = rng.choice([5, 6, 8, 12])
    for k in range(rng.choice([5, 6, 7]), 0, -1):
        R = size / 2 * k / 7
        rin = R * rng.uniform(0.45, 0.7)
        rot = (k % 2) * math.pi / pts
        p = c.beginPath()
        for i in range(2 * pts + 1):
            rr = R if i % 2 == 0 else rin
            a = math.pi * i / pts + rot + math.pi / 2
            px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
            p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
        c.drawPath(p, stroke=1, fill=0)
    c.circle(cx, cy, size * 0.04, stroke=1, fill=0)


def draw_tiles(c, x, y, size, rng, bold=2.2):
    """Grid of tiles, each with one of several simple motifs (bold & easy)."""
    c.setStrokeColor(black)
    c.setLineWidth(bold)
    n = rng.choice([3, 4, 5])
    s = size / n
    motifs = rng.sample(["diamond", "circle", "quarter", "flower", "cross", "square"], 3)
    for i in range(n):
        for j in range(n):
            x0, y0 = x + i * s, y + j * s
            c.rect(x0, y0, s, s)
            m = motifs[(i + j) % len(motifs)]
            cx, cy = x0 + s / 2, y0 + s / 2
            if m == "diamond":
                p = c.beginPath(); p.moveTo(cx, y0 + s * 0.1); p.lineTo(x0 + s * 0.9, cy); p.lineTo(cx, y0 + s * 0.9); p.lineTo(x0 + s * 0.1, cy); p.close()
                c.drawPath(p, stroke=1, fill=0)
                c.circle(cx, cy, s * 0.12, stroke=1, fill=0)
            elif m == "circle":
                c.circle(cx, cy, s * 0.38, stroke=1, fill=0)
                c.circle(cx, cy, s * 0.2, stroke=1, fill=0)
            elif m == "quarter":
                for (ax, ay, st) in ((x0, y0, 0), (x0 + s, y0, 90), (x0 + s, y0 + s, 180), (x0, y0 + s, 270)):
                    c.arc(ax - s * 0.4, ay - s * 0.4, ax + s * 0.4, ay + s * 0.4, st, 90)
            elif m == "flower":
                for k in range(6):
                    _petal(c, cx, cy, s * 0.08, s * 0.42, 2 * math.pi * k / 6, 0.45)
            elif m == "cross":
                c.line(x0, y0, x0 + s, y0 + s); c.line(x0, y0 + s, x0 + s, y0)
                c.circle(cx, cy, s * 0.18, stroke=1, fill=0)
            else:
                c.rect(cx - s * 0.3, cy - s * 0.3, s * 0.6, s * 0.6)
                c.rect(cx - s * 0.15, cy - s * 0.15, s * 0.3, s * 0.3)


PATTERNS = [draw_truchet, draw_circles_pattern, draw_star_pattern, draw_tiles]


def coloring_design(c, box: Box, rng: random.Random, kind: str):
    size = min(box.w, box.h) * 0.95
    x, y = box.cx - size / 2, box.y0 + (box.h - size) / 2
    if kind == "mandala":
        draw_mandala(c, box.cx, y + size / 2, size / 2, rng)
    else:
        rng.choice(PATTERNS)(c, x, y, size, rng)


# ================================================================ color-by-number mosaics

# Palette: number -> (name, grey level for the solution preview, RGB for rasterising)
PALETTE = {
    1: ("Red", 0.45, (220, 40, 40)), 2: ("Orange", 0.6, (245, 140, 30)), 3: ("Yellow", 0.85, (250, 220, 40)),
    4: ("Light green", 0.7, (130, 210, 90)), 5: ("Dark green", 0.35, (30, 120, 50)), 6: ("Light blue", 0.75, (120, 190, 240)),
    7: ("Dark blue", 0.3, (30, 60, 160)), 8: ("Purple", 0.4, (130, 60, 170)), 9: ("Pink", 0.78, (245, 150, 190)),
    10: ("Brown", 0.38, (130, 80, 40)), 11: ("Gray", 0.6, (150, 150, 150)), 12: ("Black", 0.08, (20, 20, 20)),
}
RGB2N = {v[2]: k for k, v in PALETTE.items()}


def _pic(name, ops, bg=None):
    return (name, ops, bg)


# Each picture is drawn on a 32 x 32 canvas with simple shapes; colours are palette numbers.
PICTURES = [
    _pic("Heart", [("ellipse", (5, 6, 17, 18), 1), ("ellipse", (15, 6, 27, 18), 1), ("poly", [(5, 13), (27, 13), (16, 27)], 1)], 9),
    _pic("Star", [("star", (16, 16, 13, 5.5, 5), 3)], 7),
    _pic("Pine Tree", [("poly", [(16, 3), (6, 14), (26, 14)], 5), ("poly", [(16, 8), (4, 21), (28, 21)], 5),
                       ("poly", [(16, 13), (3, 27), (29, 27)], 5), ("rect", (14, 27, 18, 31), 10), ("star", (16, 4, 3, 1.3, 5), 3)], 6),
    _pic("House", [("rect", (7, 15, 25, 29), 1), ("poly", [(4, 16), (16, 5), (28, 16)], 10), ("rect", (14, 21, 18, 29), 10),
                   ("rect", (9, 18, 13, 22), 6), ("rect", (19, 18, 23, 22), 6), ("rect", (20, 6, 23, 12), 11)], 4),
    _pic("Sun", [("rays", (16, 16, 14, 12), 2), ("ellipse", (9, 9, 23, 23), 3)], 6),
    _pic("Moon and Stars", [("ellipse", (6, 6, 22, 22), 3), ("ellipse", (11, 4, 27, 20), 7), ("star", (24, 24, 3, 1.3, 5), 3),
                            ("star", (7, 26, 2.5, 1, 5), 3), ("star", (27, 8, 2, 0.8, 5), 3)], 7),
    _pic("Apple", [("ellipse", (6, 9, 26, 29), 1), ("rect", (15, 4, 17, 10), 10), ("ellipse", (17, 4, 24, 9), 4)], None),
    _pic("Mushroom", [("ellipse", (4, 6, 28, 20), 1), ("rect", (12, 14, 20, 28), 11), ("ellipse", (8, 9, 12, 13), 12),
                      ("ellipse", (18, 8, 23, 12), 12), ("ellipse", (14, 13, 18, 16), 12)], 4),
    _pic("Fish", [("ellipse", (5, 9, 23, 23), 2), ("poly", [(21, 16), (29, 9), (29, 23)], 2), ("ellipse", (8, 13, 11, 16), 12)], 6),
    _pic("Flower", [("ellipse", (12, 2, 20, 12), 9), ("ellipse", (12, 14, 20, 24), 9), ("ellipse", (6, 8, 14, 18), 9),
                    ("ellipse", (18, 8, 26, 18), 9), ("ellipse", (12, 9, 20, 17), 3), ("rect", (15, 22, 17, 31), 5),
                    ("ellipse", (17, 24, 24, 28), 5)], 6),
    _pic("Sailboat", [("poly", [(16, 3), (16, 21), (27, 21)], 11), ("poly", [(15, 6), (15, 21), (6, 21)], 1),
                      ("poly", [(4, 22), (28, 22), (24, 27), (8, 27)], 10), ("rect", (0, 27, 32, 32), 7)], 6),
    _pic("Rocket", [("poly", [(16, 2), (11, 10), (21, 10)], 1), ("rect", (11, 10, 21, 24), 11), ("ellipse", (13, 12, 19, 18), 6),
                    ("poly", [(11, 18), (6, 26), (11, 24)], 1), ("poly", [(21, 18), (26, 26), (21, 24)], 1),
                    ("poly", [(12, 24), (20, 24), (16, 31)], 2)], 7),
    _pic("Cupcake", [("poly", [(8, 18), (24, 18), (21, 29), (11, 29)], 6), ("ellipse", (6, 9, 26, 21), 9),
                     ("ellipse", (13, 4, 19, 10), 1)], None),
    _pic("Umbrella", [("ellipse", (3, 5, 29, 27), 8), ("rect", (0, 16, 32, 32), 0), ("rect", (15, 16, 17, 28), 12),
                      ("ellipse", (11, 25, 17, 31), 12), ("ellipse", (13, 26, 15, 29), 0)], None),
    _pic("Ice Cream", [("poly", [(10, 15), (22, 15), (16, 31)], 10), ("ellipse", (8, 5, 24, 18), 9), ("ellipse", (12, 1, 20, 9), 1)], 6),
    _pic("Balloon", [("ellipse", (8, 2, 24, 22), 1), ("poly", [(14, 22), (18, 22), (16, 25)], 1), ("rect", (15, 25, 16, 31), 12)], 6),
    _pic("Cat Face", [("poly", [(6, 4), (12, 11), (6, 13)], 2), ("poly", [(26, 4), (20, 11), (26, 13)], 2), ("ellipse", (5, 8, 27, 28), 2),
                      ("ellipse", (10, 14, 14, 18), 4), ("ellipse", (18, 14, 22, 18), 4), ("poly", [(14, 20), (18, 20), (16, 22)], 9)], 6),
    _pic("Butterfly", [("ellipse", (3, 5, 16, 17), 8), ("ellipse", (16, 5, 29, 17), 8), ("ellipse", (5, 16, 16, 27), 9),
                       ("ellipse", (16, 16, 27, 27), 9), ("ellipse", (14, 6, 18, 27), 12)], 4),
    _pic("Snowman", [("ellipse", (8, 15, 24, 31), 0), ("ellipse", (10, 6, 22, 18), 0), ("rect", (11, 1, 21, 8), 12),
                     ("rect", (8, 7, 24, 9), 12), ("poly", [(16, 11), (16, 13), (21, 12)], 2), ("rect", (10, 16, 22, 18), 1)], 6),
    _pic("Strawberry", [("poly", [(5, 9), (27, 9), (16, 30)], 1), ("ellipse", (5, 5, 27, 18), 1), ("poly", [(10, 5), (22, 5), (16, 10)], 5)], None),
    _pic("Cactus", [("rect", (13, 4, 19, 28), 5), ("rect", (6, 10, 10, 18), 5), ("rect", (6, 16, 13, 19), 5),
                    ("rect", (22, 8, 26, 16), 5), ("rect", (19, 14, 26, 17), 5), ("rect", (9, 26, 23, 31), 2)], 3),
    _pic("Rainbow", [("ellipse", (1, 6, 31, 36), 1), ("ellipse", (4, 9, 28, 33), 2), ("ellipse", (7, 12, 25, 30), 3),
                     ("ellipse", (10, 15, 22, 27), 5), ("ellipse", (13, 18, 19, 24), 6), ("rect", (0, 23, 32, 32), 0)], 6),
    _pic("Crown", [("poly", [(4, 12), (10, 18), (16, 6), (22, 18), (28, 12), (26, 26), (6, 26)], 3), ("ellipse", (14, 18, 18, 22), 1),
                   ("ellipse", (8, 20, 11, 23), 7), ("ellipse", (21, 20, 24, 23), 7)], 8),
    _pic("Owl", [("ellipse", (6, 5, 26, 30), 10), ("ellipse", (8, 9, 16, 17), 0), ("ellipse", (16, 9, 24, 17), 0),
                 ("ellipse", (10, 11, 14, 15), 12), ("ellipse", (18, 11, 22, 15), 12), ("poly", [(14, 17), (18, 17), (16, 21)], 2),
                 ("poly", [(6, 6), (11, 9), (8, 3)], 10), ("poly", [(26, 6), (21, 9), (24, 3)], 10)], 6),
    _pic("Turtle", [("ellipse", (6, 8, 26, 24), 5), ("ellipse", (24, 12, 31, 19), 4), ("ellipse", (5, 21, 11, 27), 4),
                    ("ellipse", (21, 21, 27, 27), 4), ("ellipse", (11, 12, 21, 20), 4)], 6),
]


def rasterize(pic, n: int = 32) -> list[list[int]]:
    name, ops, bg = pic
    scale = 8
    img = Image.new("RGB", (n * scale, n * scale), (255, 255, 255) if not bg else PALETTE[bg][2])
    d = ImageDraw.Draw(img)

    def col(k):
        return (255, 255, 255) if k == 0 else PALETTE[k][2]
    for op, args, k in ops:
        s = lambda v: v * scale * n / 32
        if op == "ellipse":
            x0, y0, x1, y1 = args
            d.ellipse([s(x0), s(y0), s(x1), s(y1)], fill=col(k))
        elif op == "rect":
            x0, y0, x1, y1 = args
            d.rectangle([s(x0), s(y0), s(x1) - 1, s(y1) - 1], fill=col(k))
        elif op == "poly":
            d.polygon([(s(a), s(b)) for a, b in args], fill=col(k))
        elif op == "star":
            cx, cy, R, r, pts = args
            P = []
            for i in range(2 * pts):
                rr = R if i % 2 == 0 else r
                a = math.pi * i / pts - math.pi / 2
                P.append((s(cx + rr * math.cos(a)), s(cy + rr * math.sin(a))))
            d.polygon(P, fill=col(k))
        elif op == "rays":
            cx, cy, R, m = args
            for i in range(m):
                a = 2 * math.pi * i / m
                b1, b2 = a - 0.18, a + 0.18
                d.polygon([(s(cx), s(cy)), (s(cx + R * math.cos(b1)), s(cy + R * math.sin(b1))),
                           (s(cx + R * math.cos(b2)), s(cy + R * math.sin(b2)))], fill=col(k))
    small = img.resize((n, n), Image.NEAREST)
    grid = []
    for y in range(n):
        row = []
        for x in range(n):
            rgb = small.getpixel((x, y))
            row.append(RGB2N.get(rgb, 0))
        grid.append(row)
    return grid


def kaleidoscope(rng: random.Random, n: int = 32) -> list[list[int]]:
    """Abstract 8-fold symmetric mosaic."""
    cols = rng.sample(list(PALETTE.keys())[:11], 4)
    half = n // 2
    tri = {}
    for y in range(half):
        for x in range(y, half):
            tri[(x, y)] = rng.choice(cols + [0, 0])
    # smooth: repeat each choice in 2x2 blocks for bolder shapes
    g = [[0] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            xx, yy = x if x < half else n - 1 - x, y if y < half else n - 1 - y
            a, b = (xx, yy) if xx >= yy else (yy, xx)
            a, b = a // 2 * 2, b // 2 * 2
            a, b = (a, b) if a >= b else (b, a)
            g[y][x] = tri.get((a, b), 0)
    return g


def draw_cbn(c, x, y, size, grid, numbers=True, solution=False):
    n = len(grid)
    cell = size / n
    fs = cell * 0.55
    for r, row in enumerate(grid):
        for col, k in enumerate(row):
            cx, cy = x + col * cell, y + size - (r + 1) * cell
            if solution:
                g = 1.0 if k == 0 else PALETTE[k][1]
                c.setFillColor(HexColor("#%02x%02x%02x" % ((int(g * 255),) * 3)))
                c.rect(cx, cy, cell, cell, stroke=0, fill=1)
            elif numbers and k:
                c.setFillColor(HexColor("#555555"))
                c.setFont(SANS, fs)
                c.drawCentredString(cx + cell / 2, cy + cell * 0.28, str(k))
    c.setStrokeColor(HexColor("#B0B0B0"))
    c.setLineWidth(0.3)
    for i in range(n + 1):
        c.line(x + i * cell, y, x + i * cell, y + size)
        c.line(x, y + i * cell, x + size, y + i * cell)
    c.setStrokeColor(black)
    c.setLineWidth(1.2)
    c.rect(x, y, size, size)


def cbn_legend(c, x, y, grid, width, fs=11):
    used = sorted({k for row in grid for k in row if k})
    per = 4
    colw = width / per
    for i, k in enumerate(used):
        col, r = i % per, i // per
        c.setFont(BOLD, fs)
        c.setFillColor(DARK)
        c.drawString(x + col * colw, y - r * fs * 1.6, f"{k} = {PALETTE[k][0]}")
    c.setFont(SANS, fs * 0.85)
    c.drawString(x, y - (len(used) // per + 1) * fs * 1.6, "Squares without a number stay white.")


# ================================================================ verse lettering

def draw_outline_text(c, lines, font, size, cx, y_top, leading=1.15):
    t = c.beginText()
    t.setTextRenderMode(1)
    c.setStrokeColor(black)
    c.setLineWidth(1.4)
    y = y_top
    from reportlab.pdfbase.pdfmetrics import stringWidth
    for ln in lines:
        w = stringWidth(ln, font, size)
        t.setTextOrigin(cx - w / 2, y - size)
        t.setFont(font, size)
        t.textLine(ln)
        y -= size * leading
    t.setTextRenderMode(0)  # back to filled text, or later text on the page comes out as outlines
    c.drawText(t)
    return y


def verse_page(verse: str, ref: str, rng: random.Random):
    def fn(c, box: Box, n: int) -> None:
        # frame
        c.setStrokeColor(black)
        c.setLineWidth(2.2)
        pad = 6
        c.roundRect(box.x0 + pad, box.y0 + pad, box.w - 2 * pad, box.h - 2 * pad, 18)
        c.roundRect(box.x0 + pad + 10, box.y0 + pad + 10, box.w - 2 * pad - 20, box.h - 2 * pad - 20, 12)
        # corner mandalas
        r = 0.55 * INCH
        for (x, y) in ((box.x0 + pad + 10, box.y0 + pad + 10), (box.x1 - pad - 10, box.y0 + pad + 10),
                       (box.x0 + pad + 10, box.y1 - pad - 10), (box.x1 - pad - 10, box.y1 - pad - 10)):
            c.setFillColor(white)
            c.circle(x, y, r, stroke=1, fill=1)
            draw_mandala(c, x, y, r, rng, bold=1.4)
        words = verse.upper()
        inner = box.w - 1.4 * INCH
        size, lines = fit_lines(words, SERIF, 46, inner, 7, 20)
        total = len(lines) * size * 1.15
        top = box.y0 + box.h * 0.62 + total / 2
        y = draw_outline_text(c, lines, SERIF, size, box.cx, top)
        c.setFont(BOLD, 16)
        c.setFillColor(DARK)
        c.drawCentredString(box.cx, y - 26, ref.upper())
        # bottom band of flowers to colour
        band_y = box.y0 + 1.25 * INCH
        k = 5
        for i in range(k):
            x = box.x0 + 0.8 * INCH + i * (box.w - 1.6 * INCH) / (k - 1)
            for j in range(8):
                _petal(c, x, band_y, 4, 0.45 * INCH, 2 * math.pi * j / 8, 0.32)
            c.circle(x, band_y, 0.1 * INCH, stroke=1, fill=0)
    return fn


# ================================================================ pencil control

def _dash(c, w=2.4):
    c.setStrokeColor(HexColor("#7A7A7A"))
    c.setLineWidth(w)
    c.setDash(7, 6)
    c.setLineCap(1)


def _solid(c):
    c.setDash()
    c.setLineCap(0)


def _start_dot(c, x, y):
    _solid(c)
    c.setFillColor(black)
    c.circle(x, y, 4.5, stroke=0, fill=1)


def trace_rows(kind: str, rows: int = 5):
    """A page of rows of a given stroke type, each starting at a dot."""
    titles = {"horizontal": "Trace the straight lines", "vertical": "Trace the lines from top to bottom",
              "diagonal": "Trace the slanted lines", "zigzag": "Trace the zigzags", "waves": "Trace the waves",
              "loops": "Trace the loops", "arches": "Trace the hills", "castle": "Trace the castle walls",
              "bumps": "Trace the bumps", "spikes": "Trace the mountains"}

    def fn(c, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(BOLD, 24)
        c.drawCentredString(box.cx, box.y1 - 24, titles[kind])
        top = box.y1 - 0.9 * INCH
        step = (top - box.y0) / rows
        for r in range(rows):
            yc = top - step * (r + 0.5)
            amp = step * 0.32
            x0, x1 = box.x0 + 18, box.x1 - 10
            _start_dot(c, x0, yc if kind not in ("vertical",) else yc + amp)
            _dash(c)
            p = c.beginPath()
            if kind == "horizontal":
                p.moveTo(x0, yc); p.lineTo(x1, yc)
            elif kind == "vertical":
                xs = x0
                while xs < x1:
                    p.moveTo(xs, yc + amp); p.lineTo(xs, yc - amp); xs += 0.55 * INCH
            elif kind == "diagonal":
                xs = x0
                while xs + 0.4 * INCH < x1:
                    p.moveTo(xs, yc + amp); p.lineTo(xs + 0.4 * INCH, yc - amp); xs += 0.55 * INCH
            elif kind in ("zigzag", "spikes"):
                seg = 0.5 * INCH if kind == "zigzag" else 0.8 * INCH
                xs, up = x0, True
                p.moveTo(xs, yc)
                while xs + seg / 2 <= x1:
                    xs += seg / 2
                    p.lineTo(xs, yc + (amp if up else -amp) if kind == "zigzag" else (yc + amp * 1.3 if up else yc - amp * 0.7))
                    up = not up
            elif kind == "waves":
                xs = x0
                p.moveTo(xs, yc)
                seg = 0.9 * INCH
                while xs + seg <= x1:
                    p.curveTo(xs + seg / 4, yc + amp * 1.3, xs + seg / 4, yc + amp * 1.3, xs + seg / 2, yc)
                    p.curveTo(xs + seg * 3 / 4, yc - amp * 1.3, xs + seg * 3 / 4, yc - amp * 1.3, xs + seg, yc)
                    xs += seg
            elif kind == "arches" or kind == "bumps":
                xs = x0
                seg = 0.85 * INCH if kind == "arches" else 0.5 * INCH
                p.moveTo(xs, yc - amp * 0.6)
                while xs + seg <= x1:
                    p.curveTo(xs, yc + amp * 1.4, xs + seg, yc + amp * 1.4, xs + seg, yc - amp * 0.6)
                    xs += seg
            elif kind == "loops":
                xs = x0
                p.moveTo(xs, yc - amp * 0.6)
                seg = 0.6 * INCH
                while xs + seg <= x1:
                    p.curveTo(xs + seg * 1.1, yc - amp * 0.6, xs + seg * 1.0, yc + amp * 1.5, xs + seg * 0.55, yc + amp * 1.2)
                    p.curveTo(xs + seg * 0.1, yc + amp * 0.9, xs + seg * 0.5, yc - amp * 0.6, xs + seg, yc - amp * 0.6)
                    xs += seg
            elif kind == "castle":
                xs = x0
                seg = 0.45 * INCH
                p.moveTo(xs, yc - amp)
                up = True
                while xs + seg <= x1:
                    p.lineTo(xs, yc + amp if up else yc - amp)
                    xs += seg
                    p.lineTo(xs, yc + amp if up else yc - amp)
                    up = not up
            c.drawPath(p, stroke=1, fill=0)
            _solid(c)
    return fn


def trace_shapes(shape: str):
    def fn(c, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(BOLD, 24)
        c.drawCentredString(box.cx, box.y1 - 24, f"Trace the {shape}s")
        cols, rows = 2, 3
        cw, ch = box.w / cols, (box.h - 0.9 * INCH) / rows
        for i in range(cols * rows):
            col, r = i % cols, i // cols
            cx = box.x0 + cw * (col + 0.5)
            cy = box.y1 - 0.9 * INCH - ch * (r + 0.5)
            R = min(cw, ch) * 0.36
            _dash(c)
            p = c.beginPath()
            if shape == "circle":
                c.circle(cx, cy, R, stroke=1, fill=0)
            elif shape in ("square", "triangle", "star", "diamond"):
                pts = {"square": [(-1, -1), (1, -1), (1, 1), (-1, 1)], "triangle": [(0, 1.1), (1.05, -0.8), (-1.05, -0.8)],
                       "diamond": [(0, 1.15), (0.85, 0), (0, -1.15), (-0.85, 0)]}.get(shape)
                if shape == "star":
                    pts = []
                    for k in range(10):
                        rr = 1.1 if k % 2 == 0 else 0.45
                        a = math.pi / 2 + math.pi * k / 5
                        pts.append((rr * math.cos(a), rr * math.sin(a)))
                p.moveTo(cx + pts[0][0] * R * 0.8, cy + pts[0][1] * R * 0.8)
                for px, py in pts[1:]:
                    p.lineTo(cx + px * R * 0.8, cy + py * R * 0.8)
                p.close()
                c.drawPath(p, stroke=1, fill=0)
            elif shape == "heart":
                p.moveTo(cx, cy - R)
                p.curveTo(cx - R * 1.6, cy + R * 0.1, cx - R * 0.7, cy + R * 1.3, cx, cy + R * 0.45)
                p.curveTo(cx + R * 0.7, cy + R * 1.3, cx + R * 1.6, cy + R * 0.1, cx, cy - R)
                c.drawPath(p, stroke=1, fill=0)
            elif shape == "spiral":
                p.moveTo(cx, cy)
                for k in range(1, 200):
                    a = k * 0.1
                    rr = R * k / 200
                    p.lineTo(cx + rr * math.cos(a), cy + rr * math.sin(a))
                c.drawPath(p, stroke=1, fill=0)
            _solid(c)
            c.setFillColor(black)
            c.circle(cx + (0 if shape != "circle" else R), cy + (R * 0.88 if shape in ("star", "triangle", "diamond") else (-R if shape == "heart" else 0)) if shape != "spiral" else cy, 4.5, stroke=0, fill=1)
    return fn


# ================================================================ scissor skills

def cut_page(kind: str, rng: random.Random):
    titles = {"straight": "Cut along the straight lines", "zigzag": "Cut along the zigzags", "waves": "Cut along the waves",
              "curves": "Cut along the curvy roads", "steps": "Cut along the steps", "spiral": "Cut the spiral",
              "shapes": "Cut out the shapes", "mixed": "Cut along the lines"}

    def fn(c, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(BOLD, 24)
        c.drawCentredString(box.cx, box.y1 - 24, titles[kind])
        c.setFont(SANS, 13)
        c.drawCentredString(box.cx, box.y1 - 44, "Ask a grown-up for safety scissors. Cut on the dashed lines.")
        top = box.y1 - 0.9 * INCH
        c.setStrokeColor(black)
        c.setLineWidth(3)
        c.setDash(10, 7)
        if kind in ("straight", "zigzag", "waves", "curves", "steps", "mixed"):
            rows = 6
            step = (top - box.y0) / rows
            for r in range(rows):
                y = top - step * (r + 0.5)
                k = kind if kind != "mixed" else rng.choice(["straight", "zigzag", "waves", "steps"])
                p = c.beginPath()
                x0, x1 = box.x0 + 0.45 * INCH, box.x1
                p.moveTo(x0, y)
                amp = step * 0.28
                if k == "straight":
                    p.lineTo(x1, y)
                elif k == "zigzag":
                    xs, up = x0, True
                    while xs < x1 - 0.35 * INCH:
                        xs += 0.35 * INCH
                        p.lineTo(xs, y + (amp if up else -amp)); up = not up
                elif k in ("waves", "curves"):
                    seg = (1.2 if k == "waves" else 2.2) * INCH
                    xs = x0
                    while xs + seg <= x1 + 1:
                        p.curveTo(xs + seg / 4, y + amp * 1.4, xs + seg / 4, y + amp * 1.4, xs + seg / 2, y)
                        p.curveTo(xs + seg * 3 / 4, y - amp * 1.4, xs + seg * 3 / 4, y - amp * 1.4, xs + seg, y)
                        xs += seg
                else:
                    xs, up = x0, True
                    while xs < x1 - 0.5 * INCH:
                        p.lineTo(xs, y + (amp if up else -amp)); xs += 0.5 * INCH
                        p.lineTo(xs, y + (amp if up else -amp)); up = not up
                c.drawPath(p, stroke=1, fill=0)
                c.setDash()
                c.setFont(SANS, 22)
                c.setFillColor(black)
                c.drawString(box.x0, y - 8, "✂")
                c.setDash(10, 7)
        elif kind == "spiral":
            cx, cy = box.cx, (top + box.y0) / 2
            R = min(box.w, top - box.y0) * 0.45
            p = c.beginPath()
            p.moveTo(cx + R, cy)
            for k in range(1, 400):
                a = k * 0.04
                rr = R * (1 - k / 430)
                p.lineTo(cx + rr * math.cos(a), cy + rr * math.sin(a))
            c.drawPath(p, stroke=1, fill=0)
        else:  # shapes
            shapes = rng.sample(["circle", "square", "triangle", "star", "heart", "house"], 4)
            cw, ch = box.w / 2, (top - box.y0) / 2
            for i, sh in enumerate(shapes):
                cx = box.x0 + cw * (i % 2 + 0.5)
                cy = top - ch * (i // 2 + 0.5)
                R = min(cw, ch) * 0.36
                p = c.beginPath()
                if sh == "circle":
                    c.circle(cx, cy, R, stroke=1, fill=0)
                    continue
                pts = {"square": [(-1, -1), (1, -1), (1, 1), (-1, 1)], "triangle": [(0, 1.1), (1.05, -0.85), (-1.05, -0.85)],
                       "house": [(-0.9, -1), (0.9, -1), (0.9, 0.25), (0, 1.1), (-0.9, 0.25)]}.get(sh)
                if sh == "star":
                    pts = [((1.15 if k % 2 == 0 else 0.5) * math.cos(math.pi / 2 + math.pi * k / 5),
                            (1.15 if k % 2 == 0 else 0.5) * math.sin(math.pi / 2 + math.pi * k / 5)) for k in range(10)]
                if sh == "heart":
                    p.moveTo(cx, cy - R)
                    p.curveTo(cx - R * 1.6, cy + R * 0.1, cx - R * 0.7, cy + R * 1.3, cx, cy + R * 0.45)
                    p.curveTo(cx + R * 0.7, cy + R * 1.3, cx + R * 1.6, cy + R * 0.1, cx, cy - R)
                else:
                    p.moveTo(cx + pts[0][0] * R, cy + pts[0][1] * R)
                    for px, py in pts[1:]:
                        p.lineTo(cx + px * R, cy + py * R)
                    p.close()
                c.drawPath(p, stroke=1, fill=0)
        c.setDash()
    return fn
