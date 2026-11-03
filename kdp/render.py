"""PDF rendering for KDP interiors and full-wrap covers (reportlab)."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Callable

from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from . import specs
from .specs import INCH

FONT_DIR = Path(__file__).parent / "fonts"
SANS, BOLD, SERIF = "KSans", "KSans-Bold", "KSerif-Bold"
_registered = False


def register_fonts() -> None:
    """Embed TrueType fonts. KDP rejects PDFs whose fonts are not embedded."""
    global _registered
    if _registered:
        return
    pdfmetrics.registerFont(TTFont(SANS, str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD, str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(SERIF, str(FONT_DIR / "DejaVuSerif-Bold.ttf")))
    _registered = True


GREY = HexColor("#D9D9D9")
DARK = HexColor("#222222")


# ---------------------------------------------------------------- text utils

def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    return simpleSplit(text, font, size, width)


def fit_lines(text: str, font: str, max_size: float, width: float, max_lines: int, min_size: float = 8) -> tuple[float, list[str]]:
    size = max_size
    while size > min_size:
        lines = wrap(text, font, size, width)
        if len(lines) <= max_lines and all(pdfmetrics.stringWidth(l, font, size) <= width for l in lines):
            return size, lines
        size -= 1
    return min_size, wrap(text, font, min_size, width)


def draw_paragraphs(c: Canvas, paras: list[str], x: float, y: float, width: float, font: str, size: float, leading: float | None = None, gap: float | None = None) -> float:
    """Draw left-aligned paragraphs top-down from y; returns the y below the last line."""
    leading = leading or size * 1.35
    gap = size * 0.7 if gap is None else gap
    c.setFont(font, size)
    for p in paras:
        for line in wrap(p, font, size, width):
            c.drawString(x, y - size, line)
            y -= leading
        y -= gap
    return y


# ---------------------------------------------------------------- interior

class Box:
    """Live area of one interior page, in points."""

    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    @property
    def w(self) -> float:
        return self.x1 - self.x0

    @property
    def h(self) -> float:
        return self.y1 - self.y0

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2


PageFn = Callable[[Canvas, Box, int], None]


def render_interior(path: Path, trim: specs.Trim, pages: list[PageFn], numbered_from: int = 5) -> int:
    """Render page functions to a no-bleed interior PDF with mirrored margins.

    Pads to an even page count. Returns the final page count.
    """
    register_fonts()
    pages = list(pages)
    while len(pages) < specs.MIN_PAGES or len(pages) % 2:
        pages.append(notes_page)
    n = len(pages)
    gutter = (specs.gutter_for(n) + 0.125) * INCH
    outside, top, bottom = 0.5 * INCH, 0.6 * INCH, 0.7 * INCH
    W, H = trim.width * INCH, trim.height * INCH
    c = Canvas(str(path), pagesize=(W, H), initialFontName=SANS)
    c.setTitle(path.stem)
    for i, fn in enumerate(pages, start=1):
        recto = i % 2 == 1
        x0 = gutter if recto else outside
        x1 = W - (outside if recto else gutter)
        box = Box(x0, bottom, x1, H - top)
        fn(c, box, i)
        if i >= numbered_from and fn is not blank_page:
            c.setFont(SANS, 11)
            c.setFillColor(DARK)
            c.drawCentredString(box.cx, 0.38 * INCH, str(i))
        c.showPage()
    c.save()
    return n


def blank_page(c: Canvas, box: Box, n: int) -> None:
    pass


def notes_page(c: Canvas, box: Box, n: int) -> None:
    c.setFillColor(DARK)
    c.setFont(BOLD, 20)
    c.drawCentredString(box.cx, box.y1 - 24, "Notes")
    c.setStrokeColor(GREY)
    c.setLineWidth(0.8)
    y = box.y1 - 0.9 * INCH
    while y > box.y0 + 0.2 * INCH:
        c.line(box.x0, y, box.x1, y)
        y -= 0.45 * INCH


def title_page(title: str, subtitle: str, author: str) -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        size, lines = fit_lines(title, SERIF, 40, box.w, 3)
        y = box.y1 - box.h * 0.25
        c.setFont(SERIF, size)
        for line in lines:
            c.drawCentredString(box.cx, y, line)
            y -= size * 1.2
        y -= 10
        ssize, slines = fit_lines(subtitle, SANS, 18, box.w * 0.9, 4)
        c.setFont(SANS, ssize)
        for line in slines:
            c.drawCentredString(box.cx, y, line)
            y -= ssize * 1.35
        c.setFont(BOLD, 16)
        c.drawCentredString(box.cx, box.y0 + 0.8 * INCH, author)
    return fn


def copyright_page(author: str, extra: str = "") -> PageFn:
    year = _dt.date.today().year

    def fn(c: Canvas, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        paras = [
            f"Copyright © {year} {author}. All rights reserved.",
            "No part of this book may be reproduced or distributed in any form without "
            "written permission from the publisher, except for brief quotations in reviews.",
            "Puzzles may be photocopied for the purchaser's personal use.",
        ]
        if extra:
            paras.append(extra)
        draw_paragraphs(c, paras, box.x0, box.y0 + 2.6 * INCH, box.w, SANS, 11)
    return fn


def text_page(heading: str, paras: list[str], size: float = 16) -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(SERIF, 28)
        c.drawCentredString(box.cx, box.y1 - 30, heading)
        draw_paragraphs(c, paras, box.x0, box.y1 - 70, box.w, SANS, size)
    return fn


def section_page(heading: str, sub: str = "") -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(SERIF, 40)
        c.drawCentredString(box.cx, box.y0 + box.h * 0.55, heading)
        if sub:
            c.setFont(SANS, 18)
            c.drawCentredString(box.cx, box.y0 + box.h * 0.55 - 40, sub)
    return fn


# ---------------------------------------------------------------- sudoku

def draw_sudoku(c: Canvas, x: float, y: float, size: float, grid: list[int], given: list[int] | None = None) -> None:
    """Draw a 9x9 grid with lower-left corner (x, y). If `given` is set, filled cells
    not in `given` (i.e. answers) are drawn lighter."""
    cell = size / 9
    c.setStrokeColor(black)
    for k in range(10):
        c.setLineWidth(2.4 if k % 3 == 0 else 0.6)
        c.line(x + k * cell, y, x + k * cell, y + size)
        c.line(x, y + k * cell, x + size, y + k * cell)
    fs = cell * 0.62
    for i, v in enumerate(grid):
        if not v:
            continue
        r, col = divmod(i, 9)
        is_answer = given is not None and not given[i]
        c.setFont(SANS if is_answer else BOLD, fs)
        c.setFillColor(HexColor("#777777") if is_answer else black)
        cx = x + col * cell + cell / 2
        cy = y + size - (r + 1) * cell + (cell - fs * 0.72) / 2
        c.drawCentredString(cx, cy, str(v))
    c.setFillColor(black)


def sudoku_puzzles_page(items: list[tuple[int, str, list[int]]], per_page: int) -> PageFn:
    """items: (number, level, puzzle). per_page is 1 or 2."""
    def fn(c: Canvas, box: Box, n: int) -> None:
        slot_h = box.h / per_page
        for k, (num, level, puzzle) in enumerate(items):
            top = box.y1 - k * slot_h
            label_h = 30
            size = min(box.w * 0.92, slot_h - label_h - 18)
            c.setFillColor(DARK)
            c.setFont(BOLD, 18)
            c.drawString(box.cx - size / 2, top - 20, f"Puzzle {num}")
            c.setFont(SANS, 16)
            c.drawRightString(box.cx + size / 2, top - 20, level.title())
            draw_sudoku(c, box.cx - size / 2, top - label_h - size, size, puzzle)
    return fn


def sudoku_solutions_page(items: list[tuple[int, list[int], list[int]]], cols: int, rows: int) -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        cw, ch = box.w / cols, box.h / rows
        size = min(cw * 0.88, ch - 34)
        for k, (num, puzzle, solution) in enumerate(items):
            r, col = divmod(k, cols)
            cx = box.x0 + col * cw + cw / 2
            top = box.y1 - r * ch
            c.setFillColor(DARK)
            c.setFont(BOLD, 13)
            c.drawCentredString(cx, top - 14, f"Puzzle {num}")
            draw_sudoku(c, cx - size / 2, top - 22 - size, size, solution, given=puzzle)
    return fn


# ---------------------------------------------------------------- word search

def draw_wordsearch(c: Canvas, x: float, y: float, size: float, ws, solution: bool = False) -> None:
    n = len(ws.grid)
    cell = size / n
    if solution:
        c.setStrokeColor(HexColor("#BDBDBD"))
        c.setLineWidth(cell * 0.72)
        c.setLineCap(1)
        for p in ws.placements:
            (r0, c0), (r1, c1) = p.cells()[0], p.cells()[-1]
            c.line(x + c0 * cell + cell / 2, y + size - r0 * cell - cell / 2,
                   x + c1 * cell + cell / 2, y + size - r1 * cell - cell / 2)
        c.setLineCap(0)
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    pad = cell * 0.25
    c.roundRect(x - pad, y - pad, size + 2 * pad, size + 2 * pad, cell * 0.4)
    fs = cell * 0.6
    c.setFont(BOLD, fs)
    c.setFillColor(black)
    for r, row in enumerate(ws.grid):
        for col, ch in enumerate(row):
            c.drawCentredString(x + col * cell + cell / 2, y + size - (r + 1) * cell + (cell - fs * 0.72) / 2, ch)


def wordsearch_page(num: int, ws, word_size: float = 16) -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        c.setFont(SERIF, 24)
        c.drawCentredString(box.cx, box.y1 - 24, f"{num}. {ws.title}")
        words = ws.words
        cols = 3
        rows = -(-len(words) // cols)
        list_h = rows * word_size * 1.5 + 10
        size = min(box.w * 0.94, box.h - 56 - list_h - 24)
        gy = box.y1 - 50 - size
        draw_wordsearch(c, box.cx - size / 2, gy, size, ws)
        c.setFont(SANS, word_size)
        col_w = box.w / cols
        y0 = gy - 30
        for k, w in enumerate(words):
            col, r = divmod(k, rows)
            c.drawString(box.x0 + col * col_w + 18, y0 - r * word_size * 1.5, "□ " + w)
    return fn


def wordsearch_solutions_page(items: list[tuple[int, object]], cols: int = 2, rows: int = 2) -> PageFn:
    def fn(c: Canvas, box: Box, n: int) -> None:
        cw, ch = box.w / cols, box.h / rows
        size = min(cw * 0.86, ch - 40)
        for k, (num, ws) in enumerate(items):
            r, col = divmod(k, cols)
            cx = box.x0 + col * cw + cw / 2
            top = box.y1 - r * ch
            c.setFillColor(DARK)
            c.setFont(BOLD, 12)
            c.drawCentredString(cx, top - 13, f"{num}. {ws.title}")
            draw_wordsearch(c, cx - size / 2, top - 26 - size, size, ws, solution=True)
    return fn


# ---------------------------------------------------------------- cover

def _mix(color, other, t: float):
    return Color(color.red + (other.red - color.red) * t,
                 color.green + (other.green - color.green) * t,
                 color.blue + (other.blue - color.blue) * t)


def snowflake(c: Canvas, x: float, y: float, r: float) -> None:
    import math
    for k in range(6):
        a = math.pi / 3 * k
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        c.line(x, y, ex, ey)
        for f in (0.55,):
            bx, by = x + r * f * math.cos(a), y + r * f * math.sin(a)
            for da in (0.6, -0.6):
                c.line(bx, by, bx + r * 0.3 * math.cos(a + da), by + r * 0.3 * math.sin(a + da))


def draw_snow(c: Canvas, W: float, H: float, base, seed: int) -> None:
    """Scatter soft snowflakes over the background (solid blended colour, no transparency)."""
    import random as _r
    rng = _r.Random(seed)
    c.setLineCap(1)
    for _ in range(int(W * H / (INCH * INCH) * 0.9)):
        r = rng.uniform(0.08, 0.32) * INCH
        c.setStrokeColor(_mix(base, white, rng.uniform(0.10, 0.22)))
        c.setLineWidth(max(0.8, r * 0.09))
        snowflake(c, rng.uniform(0, W), rng.uniform(0, H), r)
    c.setLineCap(0)


def render_cover(path: Path, book, pages: int, art: Callable[[Canvas, float, float, float], None]) -> tuple[float, float]:
    """Full-wrap paperback cover with bleed. `art(c, x, y, size)` draws the front illustration."""
    register_fonts()
    trim = book.trim
    w_in, h_in = specs.cover_size(trim, pages)
    W, H = w_in * INCH, h_in * INCH
    bleed = specs.BLEED * INCH
    spine = specs.spine_width(pages) * INCH
    tw, th = trim.width * INCH, trim.height * INCH
    safe = 0.375 * INCH  # keep text well inside the trim

    primary, accent, ink = HexColor(book.colors[0]), HexColor(book.colors[1]), HexColor(book.colors[2])
    c = Canvas(str(path), pagesize=(W, H), initialFontName=SANS)
    c.setTitle(path.stem)

    # background
    c.setFillColor(primary)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if getattr(book, "decor", "") == "snow":
        draw_snow(c, W, H, primary, book.seed)

    # ---- front cover
    fx0 = bleed + tw + spine
    fx1 = fx0 + tw
    fcx = (fx0 + fx1) / 2
    top = bleed + th
    # title band
    c.setFillColor(ink)
    tsize, tlines = fit_lines(book.cover_title.upper(), SERIF, 64 if trim.is_large else 46, tw - 2 * safe, 3)
    y = top - safe - tsize
    c.setFont(SERIF, tsize)
    for line in tlines:
        c.drawCentredString(fcx, y, line)
        y -= tsize * 1.08
    # strapline
    ssize, slines = fit_lines(book.cover_strap, BOLD, 26 if trim.is_large else 18, tw - 2 * safe, 2)
    c.setFillColor(accent)
    y -= 6
    c.setFont(BOLD, ssize)
    for line in slines:
        c.drawCentredString(fcx, y, line)
        y -= ssize * 1.25
    # artwork panel
    badge_h = (0.9 if trim.is_large else 0.7) * INCH
    art_top = y - 14
    art_bottom = bleed + safe + badge_h + 0.55 * INCH
    size = min(art_top - art_bottom, tw - 2 * safe - 0.4 * INCH)
    ax = fcx - size / 2
    ay = art_bottom + (art_top - art_bottom - size) / 2
    c.setFillColor(white)
    c.roundRect(ax - 14, ay - 14, size + 28, size + 28, 18, stroke=0, fill=1)
    art(c, ax, ay, size)
    # badges
    bw = (tw - 2 * safe - 2 * 10) / 3
    by = bleed + safe + 0.42 * INCH
    for k, text in enumerate(book.cover_badges[:3]):
        bx = fx0 + safe + k * (bw + 10)
        c.setFillColor(accent)
        c.roundRect(bx, by, bw, badge_h, badge_h / 2.6, stroke=0, fill=1)
        c.setFillColor(primary)
        bsize, blines = fit_lines(text.upper(), BOLD, 15 if trim.is_large else 11, bw - 16, 2, 7)
        c.setFont(BOLD, bsize)
        total = len(blines) * bsize * 1.15
        ly = by + badge_h / 2 + total / 2 - bsize * 0.9
        for line in blines:
            c.drawCentredString(bx + bw / 2, ly, line)
            ly -= bsize * 1.15
    c.setFillColor(ink)
    c.setFont(BOLD, 14 if trim.is_large else 11)
    c.drawCentredString(fcx, bleed + safe, book.author)

    # ---- back cover
    bx0 = bleed
    bcx = bx0 + tw / 2
    c.setFillColor(ink)
    hsize, hlines = fit_lines(book.back_headline, SERIF, 30 if trim.is_large else 22, tw - 2 * safe, 3)
    y = top - safe - hsize
    c.setFont(SERIF, hsize)
    for line in hlines:
        c.drawCentredString(bcx, y, line)
        y -= hsize * 1.15
    y -= 12
    body = 15 if trim.is_large else 11.5
    y = draw_paragraphs(c, book.back_paras, bx0 + safe, y, tw - 2 * safe, SANS, body)
    c.setFont(SANS, body)
    for b in book.back_bullets:
        for k, line in enumerate(wrap(b, SANS, body, tw - 2 * safe - 22)):
            c.drawString(bx0 + safe + (0 if k == 0 else 22), y - body, ("✓  " if k == 0 else "") + line)
            y -= body * 1.4
    # sample puzzle in the free space above the barcode
    bcw, bch = specs.BARCODE_W * INCH, specs.BARCODE_H * INCH
    floor = bleed + 0.25 * INCH + bch + 0.35 * INCH
    avail = y - 0.3 * INCH - floor
    if avail > 1.6 * INCH:
        s = min(avail - 28, 3.4 * INCH)
        sx, sy = bcx - s / 2, floor + (avail - s) / 2
        c.setFillColor(white)
        c.roundRect(sx - 12, sy - 12, s + 24, s + 24, 14, stroke=0, fill=1)
        art(c, sx, sy, s)
    # barcode clear zone (KDP prints the ISBN barcode here)
    c.setFillColor(white)
    c.rect(bx0 + tw - 0.25 * INCH - bcw, bleed + 0.25 * INCH, bcw, bch, stroke=0, fill=1)

    # ---- spine
    if pages >= specs.SPINE_TEXT_MIN_PAGES:
        sx = bleed + tw + spine / 2
        c.saveState()
        c.translate(sx, bleed + th / 2)
        c.rotate(-90)
        avail = spine - 2 * 0.0625 * INCH
        fs = min(avail * 0.62, 20)
        c.setFillColor(ink)
        c.setFont(BOLD, fs)
        c.drawCentredString(-th * 0.08, -fs * 0.36, book.spine_text)
        c.setFont(SANS, fs * 0.8)
        c.drawString(th / 2 - 0.5 * INCH - pdfmetrics.stringWidth(book.author, SANS, fs * 0.8), -fs * 0.3, book.author)
        c.restoreState()

    c.showPage()
    c.save()
    return w_in, h_in
