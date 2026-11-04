"""Mixed puzzle books: build puzzles from a plan, lay out puzzle and solution pages.

A book's `plan` is a list of sections, e.g.
    {"kind": "ws", "pool": "XMAS", "count": 50, "words": 20, "size": 17}
    {"kind": "sudoku", "levels": [("easy", 60), ("medium", 40)]}
    {"kind": "sudoku6", "count": 80, "clues": 16}
    {"kind": "maze", "count": 60, "start": (8, 10), "end": (16, 20)}
    {"kind": "scramble", "pool": "XMAS", "count": 40, "words": 12}
    {"kind": "crypto", "source": "QUOTES", "count": 60}
Sections run one after another, or round-robin when `book.interleave` is set
(used by activity and advent books so puzzle types alternate).
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth

from . import puzzles, render, sudoku, wordsearch, xmas_words
from .render import BOLD, DARK, SANS, SERIF, Box, fit_lines, wrap
from .specs import INCH

POOLS = {
    "XMAS": xmas_words.XMAS,
    "KIDS": xmas_words.KIDS,
    "BIBLE": xmas_words.BIBLE,
    "NOSTALGIA": xmas_words.NOSTALGIA,
    "WORLD": xmas_words.WORLD,
    "GENERAL": wordsearch.THEMES,
}
from .text_content import GENERAL_QUOTES  # noqa: E402
QUOTE_SOURCES = {"QUOTES": xmas_words.QUOTES, "SCRIPTURE": xmas_words.SCRIPTURE, "GENERAL": GENERAL_QUOTES}

KIND_NAMES = {
    "ws": "Word Search", "sudoku": "Sudoku", "sudoku6": "Mini Sudoku",
    "maze": "Maze", "scramble": "Word Scramble", "crypto": "Cryptogram",
}

HOW_TO = {
    "ws": "Word Search: find every word from the list in the grid of letters. Words can run across, down, diagonally and backwards. Two-word entries appear without the space.",
    "ws_kids": "Word Search: find every word from the list in the grid. Words go across, down, or diagonally. Circle each one, then tick its box!",
    "sudoku": "Sudoku: fill every empty square with a number from 1 to 9 so that each row, each column and each bold 3 x 3 box has every number exactly once.",
    "sudoku6": "Mini Sudoku: fill the grid with the numbers 1 to 6 so that each row, each column and each bold box has every number exactly once.",
    "maze": "Mazes: start at the arrow at the top left and find the one path that leads to the exit at the bottom right.",
    "scramble": "Word Scramble: rearrange the letters to spell a word that fits the page's theme. Some answers are two words.",
    "crypto": "Cryptograms: each quote is written in a secret code where every letter stands for a different letter. The code changes with every puzzle. Start with the hint letters, then look for short words such as THE, AND and OF.",
}


@dataclass
class Item:
    kind: str
    title: str
    data: object
    spec: dict
    num: int = 0
    label: str = ""


# ---------------------------------------------------------------- generation

def _themes(rng: random.Random, pool: dict, count: int) -> list[tuple[str, list[str]]]:
    themes = list(pool.items())
    rng.shuffle(themes)
    out = []
    for k in range(count):
        title, words = themes[k % len(themes)]
        rnd = k // len(themes)
        out.append((title if rnd == 0 else f"{title} {'I' * (rnd + 1)}", words))
    return out


def make_section(rng: random.Random, spec: dict) -> list[Item]:
    kind = spec["kind"]
    items: list[Item] = []
    if kind == "ws":
        dirs = wordsearch.DIRS_EASY if spec.get("dirs") == "easy" else wordsearch.DIRS_ALL
        for title, words in _themes(rng, POOLS[spec["pool"]], spec["count"]):
            ws = wordsearch.make_puzzle(rng, title, words, size=spec.get("size", 15),
                                        count=spec.get("words", 15), dirs=dirs)
            items.append(Item(kind, title, ws, spec))
    elif kind == "sudoku":
        for level, count in spec["levels"]:
            for _ in range(count):
                items.append(Item(kind, f"Sudoku ({level.title()})", sudoku.make_puzzle(rng, level), spec))
    elif kind == "sudoku6":
        for _ in range(spec["count"]):
            items.append(Item(kind, "Mini Sudoku", puzzles.make_sudoku6(rng, spec.get("clues", 15)), spec))
    elif kind == "maze":
        n = spec["count"]
        (c0, r0), (c1, r1) = spec["start"], spec["end"]
        for k in range(n):
            t = k / max(1, n - 1)
            cols, rows = round(c0 + (c1 - c0) * t), round(r0 + (r1 - r0) * t)
            items.append(Item(kind, "Maze", puzzles.make_maze(rng, cols, rows), spec))
    elif kind == "scramble":
        for title, words in _themes(rng, POOLS[spec["pool"]], spec["count"]):
            sc = puzzles.make_scramble(rng, title, words, count=spec.get("words", 12), max_len=spec.get("max_len", 12))
            items.append(Item(kind, title, sc, spec))
    elif kind == "crypto":
        quotes = list(QUOTE_SOURCES[spec["source"]])
        rng.shuffle(quotes)
        for q, src in quotes[: spec["count"]]:
            items.append(Item(kind, "Cryptogram", puzzles.make_cryptogram(rng, q, src, spec.get("hints", 2)), spec))
    else:
        raise ValueError(kind)
    return items


def make_items(book) -> list[Item]:
    rng = random.Random(book.seed)
    sections = [make_section(rng, spec) for spec in book.plan]
    if book.interleave:
        items = []
        for k in range(max(len(s) for s in sections)):
            for s in sections:
                if k < len(s):
                    items.append(s[k])
    else:
        items = [it for s in sections for it in s]
    per_day = len(sections)
    for i, it in enumerate(items, 1):
        it.num = i
        if book.advent:
            it.label = f"Day {(i - 1) // per_day + 1}"
        else:
            it.label = f"Puzzle {i}"
    return items


# ---------------------------------------------------------------- drawing helpers

def heading(c, rect: Box, item: Item, size: float) -> float:
    """Draw the slot heading; return the y just under it."""
    name = item.title if item.kind in ("ws", "scramble") else KIND_NAMES[item.kind]
    if item.kind == "sudoku":
        name = item.title
    if item.label.startswith("Day"):
        name = f"{KIND_NAMES[item.kind]}" + (f": {item.title}" if item.kind in ("ws", "scramble") else "")
    text = f"{item.label}  ·  {name}"
    fs, lines = fit_lines(text, SERIF, size, rect.w, 2, 9)
    c.setFillColor(DARK)
    c.setFont(SERIF, fs)
    y = rect.y1 - fs
    for line in lines:
        c.drawCentredString(rect.cx, y, line)
        y -= fs * 1.2
    return y - fs * 0.3


def draw_sudoku6(c, x, y, size, grid, given=None):
    w, h = size, size  # 6 columns x 6 rows, square cells
    cell = size / 6
    c.setStrokeColor(black)
    for k in range(7):
        c.setLineWidth(2.4 if k % 3 == 0 else 0.7)
        c.line(x + k * cell, y, x + k * cell, y + h)
    for k in range(7):
        c.setLineWidth(2.4 if k % 2 == 0 else 0.7)
        c.line(x, y + k * cell, x + w, y + k * cell)
    fs = cell * 0.6
    for i, v in enumerate(grid):
        if not v:
            continue
        r, col = divmod(i, 6)
        ans = given is not None and not given[i]
        c.setFont(SANS if ans else BOLD, fs)
        c.setFillColor(HexColor("#777777") if ans else black)
        c.drawCentredString(x + col * cell + cell / 2, y + h - (r + 1) * cell + (cell - fs * 0.72) / 2, str(v))
    c.setFillColor(black)


def draw_maze(c, x, y, w, h, maze: puzzles.Maze, solution: bool = False, line: float = 1.6):
    cell = min(w / maze.cols, h / maze.rows)
    mw, mh = cell * maze.cols, cell * maze.rows
    x += (w - mw) / 2
    y += (h - mh) / 2
    top = y + mh

    def px(col):
        return x + col * cell

    def py(row):
        return top - row * cell

    if solution:
        c.setStrokeColor(HexColor("#9E9E9E"))
        c.setLineWidth(max(1.2, cell * 0.35))
        c.setLineCap(1)
        c.setLineJoin(1)
        path = maze.solution()
        p = c.beginPath()
        p.moveTo(px(0) + cell / 2, top + cell * 0.4)
        for col, row in path:
            p.lineTo(px(col) + cell / 2, py(row) - cell / 2)
        p.lineTo(px(maze.cols - 1) + cell / 2, y - cell * 0.4)
        c.drawPath(p, stroke=1, fill=0)
        c.setLineCap(0)
        c.setLineJoin(0)
    c.setStrokeColor(black)
    c.setLineWidth(line)
    c.setLineCap(2)
    for row in range(maze.rows):
        for col in range(maze.cols):
            # top wall
            if row == 0:
                if col != 0:
                    c.line(px(col), py(0), px(col + 1), py(0))
            elif not maze.is_open((col, row), (col, row - 1)):
                c.line(px(col), py(row), px(col + 1), py(row))
            # left wall
            if col == 0 or not maze.is_open((col, row), (col - 1, row)):
                c.line(px(col), py(row), px(col), py(row + 1))
    # outer right and bottom (leave the exit open)
    c.line(px(maze.cols), top, px(maze.cols), y)
    c.line(x, y, px(maze.cols - 1), y)
    c.setLineCap(0)
    if not solution:
        # entry and exit arrows
        ax = px(0) + cell / 2
        _arrow(c, ax, top + cell * 1.1, ax, top + cell * 0.15, cell)
        ex = px(maze.cols - 1) + cell / 2
        _arrow(c, ex, y - cell * 0.15, ex, y - cell * 1.1, cell)


def _arrow(c, x0, y0, x1, y1, cell):
    s = max(5, min(cell * 0.35, 12))
    c.setLineWidth(1.6)
    c.line(x0, y0, x1, y1)
    p = c.beginPath()
    p.moveTo(x1, y1)
    p.lineTo(x1 - s / 2, y1 + s)
    p.lineTo(x1 + s / 2, y1 + s)
    p.close()
    c.setFillColor(black)
    c.drawPath(p, stroke=0, fill=1)


def crypto_layout(cg: puzzles.Cryptogram, width: float, cell: float) -> list[list[str]]:
    """Split the cipher text into lines of words that fit `width`."""
    words = cg.cipher.split(" ")
    lines, cur, cur_w = [], [], 0.0
    for w in words:
        ww = len(w) * cell
        add = ww if not cur else ww + cell * 0.8
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [w], ww
        else:
            cur.append(w)
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def crypto_height(cg, width, cell) -> float:
    return len(crypto_layout(cg, width, cell)) * cell * 2.05


def draw_crypto(c, x, y_top, width, cg: puzzles.Cryptogram, cell: float, solved: float = 0.0):
    """Answer blanks above each cipher letter. `solved` 0..1 pre-fills that share of letters (cover art)."""
    lines = crypto_layout(cg, width, cell)
    rev = {v: k for k, v in cg.key.items()}
    shown = set(cg.hints)
    if solved:
        letters = sorted(set(ch for ch in cg.cipher if ch.isalpha()))
        shown |= set(letters[: int(len(letters) * solved)])
    fs = cell * 0.62
    y = y_top
    for words in lines:
        total = sum(len(w) for w in words) * cell + (len(words) - 1) * cell * 0.8
        cx = x + (width - total) / 2
        for w in words:
            for ch in w:
                if ch.isalpha():
                    c.setStrokeColor(black)
                    c.setLineWidth(0.9)
                    c.line(cx + cell * 0.1, y - cell * 0.95, cx + cell * 0.9, y - cell * 0.95)
                    if ch in shown:
                        c.setFont(SANS, fs)
                        c.setFillColor(HexColor("#666666"))
                        c.drawCentredString(cx + cell / 2, y - cell * 0.85, rev[ch])
                    c.setFont(BOLD, fs * 0.92)
                    c.setFillColor(black)
                    c.drawCentredString(cx + cell / 2, y - cell * 1.7, ch)
                else:
                    c.setFont(BOLD, fs)
                    c.setFillColor(black)
                    c.drawCentredString(cx + cell / 2, y - cell * 1.7, ch)
                cx += cell
            cx += cell * 0.8
        y -= cell * 2.05
    return y


# ---------------------------------------------------------------- puzzle slots

def big(book) -> bool:
    return book.trim.is_large


def draw_slot(c, rect: Box, item: Item, book):
    lp = big(book)
    hsize = 22 if lp else 15
    y = heading(c, rect, item, hsize)
    area = Box(rect.x0, rect.y0, rect.x1, y - 6)
    k = item.kind
    if k == "ws":
        ws = item.data
        kids = item.spec.get("dirs") == "easy"
        wf = (18 if kids else 16) if lp else 11
        words = ws.words
        cols = 3 if (lp or len(words) <= 12) else 2
        rows = -(-len(words) // cols)
        list_h = rows * wf * 1.5 + 8
        size = min(area.w * 0.96, area.h - list_h - 22)
        gy = area.y1 - size - 6
        render.draw_wordsearch(c, area.cx - size / 2, gy, size, ws)
        c.setFont(SANS, wf)
        c.setFillColor(DARK)
        colw = area.w / cols
        y0 = gy - 12 - wf * 1.2
        for i, w in enumerate(words):
            col, r = divmod(i, rows)
            text = "□ " + w
            fs = wf
            while stringWidth(text, SANS, fs) > colw - 6 and fs > 7:
                fs -= 0.5
            c.setFont(SANS, fs)
            c.drawString(area.x0 + col * colw + 4, y0 - r * wf * 1.5, text)
    elif k == "sudoku":
        puzzle, _ = item.data
        size = min(area.w * 0.92, area.h - 8)
        render.draw_sudoku(c, area.cx - size / 2, area.y1 - size - 4, size, puzzle)
    elif k == "sudoku6":
        puzzle, _ = item.data
        size = min(area.w * 0.8, area.h - 8)
        draw_sudoku6(c, area.cx - size / 2, area.y1 - size - 4, size, puzzle)
    elif k == "maze":
        pad = 0.35 * INCH
        draw_maze(c, area.x0, area.y0 + pad, area.w, area.h - 2 * pad, item.data, line=2.0 if lp else 1.5)
        c.setFont(BOLD, 13 if lp else 10)
        c.setFillColor(DARK)
        c.drawString(area.x0, area.y1 - 12, "START")
        c.drawRightString(area.x1, area.y0 + 2, "FINISH")
    elif k == "scramble":
        sc = item.data
        n = len(sc.words)
        fs = 20 if lp else 14
        if item.spec.get("dirs") == "easy" or item.spec.get("kids"):
            fs += 2
        step = min(area.h / (n + 1), fs * 2.6)
        y = area.y1 - step * 0.8
        c.setFont(SANS, fs * 0.7)
        c.setFillColor(DARK)
        c.drawCentredString(area.cx, y + step * 0.45, "Unscramble each word. Hint: they all fit the theme above.")
        for i, s in enumerate(sc.scrambled, 1):
            words_n = sc.words[i - 1].count(" ") + 1
            c.setFont(BOLD, fs)
            c.drawString(area.x0 + 6, y - step * 0.3, f"{i}.")
            c.drawString(area.x0 + fs * 2.2, y - step * 0.3, s)
            if words_n > 1:
                c.setFont(SANS, fs * 0.55)
                c.drawString(area.x0 + fs * 2.2, y - step * 0.3 - fs * 0.75, f"({words_n} words)")
            c.setStrokeColor(DARK)
            c.setLineWidth(0.8)
            lx = area.x0 + area.w * 0.5
            c.line(lx, y - step * 0.32, area.x1 - 6, y - step * 0.32)
            y -= step
    elif k == "crypto":
        cg = item.data
        cell = crypto_cell(book)
        hint = "Hints: " + ",  ".join(f"{k2} = {v}" for k2, v in sorted(cg.hints.items()))
        c.setFont(SANS, 13 if lp else 10)
        c.setFillColor(DARK)
        c.drawCentredString(area.cx, area.y1 - 12, hint)
        draw_crypto(c, area.x0, area.y1 - 24, area.w, cg, cell)


def crypto_cell(book) -> float:
    return 0.38 * INCH if big(book) else 0.25 * INCH


def slot_height(item: Item, book, width: float) -> float:
    """Height a cryptogram slot needs (other kinds take a fixed share)."""
    hs = 22 if big(book) else 15
    return hs * 2.5 + 34 + crypto_height(item.data, width, crypto_cell(book))


def live_area(book) -> tuple[float, float]:
    """Conservative live-area size (narrowest width any page in a book this size gets)."""
    from .specs import gutter_for
    W = book.trim.width * INCH - (gutter_for(400) + 0.125) * INCH - 0.5 * INCH
    H = book.trim.height * INCH - 1.3 * INCH
    return W, H


def puzzle_pages(items: list[Item], book) -> list:
    pages = []
    i = 0
    lp = big(book)
    while i < len(items):
        it = items[i]
        group = [it]
        if it.kind in ("sudoku", "sudoku6") and lp:
            if i + 1 < len(items) and items[i + 1].kind == it.kind:
                group.append(items[i + 1])
        elif it.kind == "crypto":
            # pack as many cryptograms as fit on the page
            W, H = live_area(book)
            used = slot_height(it, book, W)
            j = i + 1
            while j < len(items) and items[j].kind == "crypto" and len(group) < 3:
                h = slot_height(items[j], book, W) + 14
                if used + h > H:
                    break
                group.append(items[j])
                used += h
                j += 1
        pages.append(_page_for(group, book))
        i += len(group)
    return pages


def _page_for(group: list[Item], book):
    def fn(c, box: Box, n: int) -> None:
        if group[0].kind == "crypto":
            y = box.y1
            for it in group:
                h = slot_height(it, book, box.w)
                draw_slot(c, Box(box.x0, y - h, box.x1, y), it, book)
                y -= h + 14
            return
        slot_h = box.h / len(group)
        for k, it in enumerate(group):
            top = box.y1 - k * slot_h
            draw_slot(c, Box(box.x0, top - slot_h + (14 if len(group) > 1 else 0), box.x1, top), it, book)
    return fn


# ---------------------------------------------------------------- solutions

def solution_pages(items: list[Item], book) -> list:
    pages = []
    lp = big(book)
    kinds = []
    for it in items:
        if it.kind not in kinds:
            kinds.append(it.kind)
    text_blocks = []
    for kind in kinds:
        group = [it for it in items if it.kind == kind]
        if kind in ("scramble", "crypto"):
            for it in group:
                if kind == "scramble":
                    lines = [f"{i}. {w}" for i, w in enumerate(it.data.words, 1)]
                    text_blocks.append((f"{it.label}: {it.title}", lines))
                else:
                    text_blocks.append((it.label, [it.data.quote, "— " + it.data.source]))
            continue
        if kind == "ws":
            cols, rows = 2, 2
        elif kind == "sudoku":
            cols, rows = (2, 3) if lp else (2, 2)
        elif kind == "sudoku6":
            cols, rows = (3, 3) if lp else (2, 3)
        else:  # maze
            cols, rows = 2, 2
        per = cols * rows
        for k in range(0, len(group), per):
            pages.append(_grid_solutions(group[k:k + per], cols, rows, book))
    if text_blocks:
        pages += _text_solutions(text_blocks, book)
    return pages


def _grid_solutions(group, cols, rows, book):
    def fn(c, box: Box, n: int) -> None:
        cw, ch = box.w / cols, box.h / rows
        for k, it in enumerate(group):
            r, col = divmod(k, cols)
            cx = box.x0 + col * cw + cw / 2
            top = box.y1 - r * ch
            c.setFillColor(DARK)
            c.setFont(BOLD, 11 if big(book) else 9)
            label = it.label if it.kind not in ("ws",) else f"{it.label}: {it.title}"
            c.drawCentredString(cx, top - 12, label)
            size = min(cw * 0.88, ch - 30)
            if it.kind == "ws":
                render.draw_wordsearch(c, cx - size / 2, top - 22 - size, size, it.data, solution=True)
            elif it.kind == "sudoku":
                p, s = it.data
                render.draw_sudoku(c, cx - size / 2, top - 22 - size, size, s, given=p)
            elif it.kind == "sudoku6":
                p, s = it.data
                draw_sudoku6(c, cx - size / 2, top - 22 - size, size, s, given=p)
            elif it.kind == "maze":
                draw_maze(c, cx - size / 2, top - 22 - size, size, size, it.data, solution=True, line=1.0)
    return fn


def _text_solutions(blocks, book):
    fs = 12 if big(book) else 9.5
    lead = fs * 1.3
    pages_layout = []  # list of pages, each a list of (col, y, heading, lines)
    # measure using a nominal live area; actual box is similar on every page
    W, H = live_area(book)
    colw = (W - 18) / 2
    page, col, y = [], 0, 0.0
    for head, lines in blocks:
        wrapped = []
        for ln in lines:
            wrapped += wrap(ln, SANS, fs, colw)
        need = lead * (len(wrapped) + 1) + fs * 0.6
        if y + need > H:
            col += 1
            y = 0.0
            if col > 1:
                pages_layout.append(page)
                page, col = [], 0
        page.append((col, y, head, wrapped))
        y += need
    if page:
        pages_layout.append(page)

    def make(layout):
        def fn(c, box: Box, n: int) -> None:
            cw = (box.w - 18) / 2
            for col, y, head, wrapped in layout:
                x = box.x0 + col * (cw + 18)
                yy = box.y1 - y - fs
                c.setFillColor(DARK)
                c.setFont(BOLD, fs)
                c.drawString(x, yy, head)
                c.setFont(SANS, fs)
                for ln in wrapped:
                    yy -= lead
                    c.drawString(x, yy, ln)
        return fn
    return [make(l) for l in pages_layout]


# ---------------------------------------------------------------- book + cover

def how_to(items: list[Item]) -> list[str]:
    seen, out = set(), []
    for it in items:
        key = "ws_kids" if it.kind == "ws" and it.spec.get("dirs") == "easy" else it.kind
        if key not in seen:
            seen.add(key)
            out.append(HOW_TO[key])
    out.append("All the answers are at the back of the book.")
    return out


def book_pages(book) -> tuple[list, int]:
    render.register_fonts()
    items = make_items(book)
    lp = big(book)
    title_main = book.title.split(":")[0]
    title_sub = book.title.split(":", 1)[1].strip() if ":" in book.title else book.subtitle
    tips = how_to(items)
    pages = [
        render.title_page(title_main, title_sub, book.author),
        render.copyright_page(book.author, book.copyright_extra),
        render.text_page("How to Play", tips, size=16 if lp else 10.5),
        render.blank_page,
    ]
    pages += puzzle_pages(items, book)
    if len(pages) % 2:
        pages.append(render.notes_page)
    pages += [render.section_page("Solutions"), render.blank_page]
    pages += solution_pages(items, book)
    pages.append(render.text_page("Merry Christmas!" if book.season == "christmas" else "Thank You!", [
        "Thank you for spending part of your holiday season with these puzzles." if book.season == "christmas"
        else "Thank you for choosing this book. We hope you enjoyed the puzzles.",
        "If you enjoyed them, a short review on Amazon would mean a great deal. "
        "Reviews help other puzzle fans find this book.",
        f"Look for more books from {book.author}.",
    ], size=15 if lp else 11))
    return pages, len(items)


def cover_art(book):
    rng = random.Random(book.seed + 99)
    kind = book.cover_art or book.plan[0]["kind"]
    if kind == "ws":
        spec = next((s for s in book.plan if s["kind"] == "ws"), {"pool": "XMAS", "dirs": "all"})
        pool = POOLS[spec.get("pool", "XMAS")]
        title, words = next(iter(pool.items()))
        short = [w for w in words if len(w.replace(" ", "")) <= 9]
        ws = wordsearch.make_puzzle(rng, title, short, size=10, count=6, dirs=wordsearch.DIRS_EASY)
        ws.placements = ws.placements[:3]
        return lambda c, x, y, s: render.draw_wordsearch(c, x + s * 0.04, y + s * 0.04, s * 0.92, ws, solution=True)
    if kind == "sudoku":
        p, _ = sudoku.make_puzzle(rng, "medium", tries=1)
        return lambda c, x, y, s: render.draw_sudoku(c, x, y, s, p)
    if kind == "sudoku6":
        p, _ = puzzles.make_sudoku6(rng, 16)
        return lambda c, x, y, s: draw_sudoku6(c, x, y, s, p)
    if kind == "maze":
        m = puzzles.make_maze(rng, 12, 12)
        return lambda c, x, y, s: draw_maze(c, x + s * 0.06, y + s * 0.06, s * 0.88, s * 0.88, m, line=2.2)
    if kind == "crypto":
        cg = puzzles.make_cryptogram(rng, "Joy to the world, the Lord is come!", "", 2)

        def art(c, x, y, s):
            cell = s / 11
            draw_crypto(c, x + s * 0.03, y + s * 0.8, s * 0.94, cg, cell, solved=0.5)
        return art
    if kind == "scramble":
        def art(c, x, y, s):
            fs = s / 11
            words = [("NWOSNAM", "SNOWMAN"), ("LYLHO", "HOLLY"), ("GLEISH", "SLEIGH"), ("RATS", "STAR")]
            yy = y + s - fs * 1.6
            for scr, ans in words:
                c.setFont(BOLD, fs)
                c.setFillColor(black)
                c.drawString(x + s * 0.06, yy, scr)
                c.setFont(SANS, fs * 0.8)
                c.setFillColor(HexColor("#B22222"))
                c.drawRightString(x + s * 0.94, yy, ans)
                c.setStrokeColor(HexColor("#999999"))
                c.line(x + s * 0.58, yy - fs * 0.25, x + s * 0.94, yy - fs * 0.25)
                yy -= fs * 2.1
        return art
    raise ValueError(kind)
