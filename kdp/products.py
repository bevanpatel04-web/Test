"""Builders for the top-seller collection. Each builder returns (pages, item_count);
each art function draws the front-cover illustration into a square."""
from __future__ import annotations

import calendar
import datetime as dt
import math
import random

from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth

from . import compose, products_art as art, products_puzzles as pz, render, sudoku, wordsearch
from .render import BOLD, DARK, SANS, SERIF, Box, draw_paragraphs, fit_lines, wrap
from .specs import INCH
from .text_content import (FILL_IN_STORIES, KJV_VERSES, KNOCK_KNOCK, RIDDLES, WOULD_YOU_RATHER)

GREY = HexColor("#9E9E9E")


# ---------------------------------------------------------------- shared helpers

def front(book, how_to: list[str] | None, belongs: bool = False) -> list:
    t_main = book.title.split(":")[0]
    t_sub = book.title.split(":", 1)[1].strip() if ":" in book.title else book.subtitle
    pages = [render.title_page(t_main, t_sub, book.author), render.copyright_page(book.author, book.copyright_extra)]
    if belongs:
        pages.append(belongs_page)
    if how_to:
        pages.append(render.text_page("How to Play" if not belongs else "How to Use This Book", how_to,
                                      size=16 if book.trim.is_large else 11))
    while len(pages) % 2:
        pages.append(render.blank_page)
    return pages


def belongs_page(c, box: Box, n: int) -> None:
    c.setFillColor(DARK)
    c.setFont(SERIF, 30)
    c.drawCentredString(box.cx, box.y0 + box.h * 0.6, "This book belongs to")
    c.setStrokeColor(DARK)
    c.setLineWidth(1.2)
    c.line(box.x0 + box.w * 0.15, box.y0 + box.h * 0.48, box.x1 - box.w * 0.15, box.y0 + box.h * 0.48)


def thanks(book) -> list:
    return [render.text_page("Thank You!", [
        "We hope you enjoyed this book.",
        "If you did, a short review on Amazon would mean a great deal. Reviews help other readers find this book.",
        f"Look for more books from {book.author}.",
    ], size=15 if book.trim.is_large else 11)]


def finish(pages: list, sol_pages: list, book) -> list:
    if len(pages) % 2:
        pages.append(render.notes_page)
    if sol_pages:
        pages += [render.section_page("Solutions"), render.blank_page] + sol_pages
    return pages + thanks(book)


def single_sided(designs: list) -> list:
    """Coloring / cutting pages: every design gets a blank back so markers and scissors don't ruin the next one."""
    out = []
    for d in designs:
        out += [d, render.blank_page]
    return out


def heading(c, box, text, size=22):
    c.setFillColor(DARK)
    fs, lines = fit_lines(text, SERIF, size, box.w, 2, 11)
    c.setFont(SERIF, fs)
    y = box.y1 - fs
    for ln in lines:
        c.drawCentredString(box.cx, y, ln)
        y -= fs * 1.15
    return y - 6


# ================================================================ 1. murder-mystery logic

LOGIC_HOW = [
    "Every case has suspects, possible weapons and places. Each suspect had exactly one weapon and was in exactly one place.",
    "Read the clues and mark the grid: put an X where something is impossible and a circle where it must be true. "
    "When a row has only one empty square left, that one is the answer.",
    "Once you know where everyone was, the victim's location tells you who did it.",
    "Cases start easy with three suspects and get harder. Solutions are in the back.",
]


def build_logic(book):
    rng = random.Random(book.seed)
    pages = front(book, LOGIC_HOW)
    cases, num = [], 1
    for tier in book.plan:
        for _ in range(tier["count"]):
            cases.append(pz.make_case(rng, num, tier["n"]))
            num += 1
    pages.append(render.blank_page)  # so every case opens as a left/right spread
    for cs in cases:
        pages += [pz.logic_case_page(cs, f"Case {cs.num}"), pz.logic_grid_page(cs, f"Case {cs.num}")]
    blocks = [pz.logic_solution_text(cs, f"Case {cs.num}") for cs in cases]
    return finish(pages, compose._text_solutions(blocks, book), book), len(cases)


def art_logic(book):
    rng = random.Random(book.seed + 5)
    case = pz.make_case(rng, 1, 3)

    def fn(c, x, y, s):
        cell = s / 12
        c.saveState()
        c.translate(x + s * 0.02, y)
        pz.draw_logic_grid(c, 0, s * 0.98, case, cell)
        # a few marks
        c.setFont(BOLD, cell * 0.6)
        c.setFillColor(HexColor("#B22222"))
        gx, gy = 1.55 * INCH, s * 0.98 - 1.25 * INCH
        for (r, k, mark) in ((0, 0, "X"), (0, 1, "O"), (1, 2, "X"), (2, 0, "X"), (1, 4, "O"), (2, 3, "X")):
            c.drawCentredString(gx + k * cell + cell / 2, gy - (r + 1) * cell + cell * 0.28, mark)
        c.restoreState()
    return fn


# ================================================================ 2. crime word search

CRIME_HOW = [
    "Each case is a word search with a twist. Find every word in the list: suspects, places, weapons and clues.",
    "Then read the letters you did not use, from left to right and top to bottom. They spell a secret clue that tells you "
    "which place the culprit was in.",
    "Match the place to the witness statements to name the culprit. Answers are in the back.",
]


def build_crime(book):
    rng = random.Random(book.seed)
    pages = front(book, CRIME_HOW)
    cases = [pz.make_crime_search(rng, i) for i in range(1, book.plan[0]["count"] + 1)]
    for cs in cases:
        pages.append(pz.crime_page(cs))
    items = [compose.Item("ws", cs.title, cs.ws, {}, i, f"Case {i}") for i, cs in enumerate(cases, 1)]
    sols = []
    for k in range(0, len(items), 4):
        sols.append(compose._grid_solutions(items[k:k + 4], 2, 2, book))
    blocks = [(f"Case {i}", [f"Secret clue: {cs.message}", f"Culprit: {cs.killer}"]) for i, cs in enumerate(cases, 1)]
    sols += compose._text_solutions(blocks, book)
    return finish(pages, sols, book), len(cases)


def art_crime(book):
    rng = random.Random(book.seed + 3)
    words = ["ALIBI", "MOTIVE", "CLUE", "KILLER", "POISON", "SUSPECT"]
    ws = wordsearch.make_puzzle(rng, "x", words, size=10, count=6, dirs=wordsearch.DIRS_EASY)
    ws.placements = ws.placements[:3]
    return lambda c, x, y, s: render.draw_wordsearch(c, x + s * 0.04, y + s * 0.04, s * 0.92, ws, solution=True)


# ================================================================ 3. big book of sudoku

def build_sudoku500(book):
    rng = random.Random(book.seed)
    pages = front(book, ["Fill every empty square with a number from 1 to 9 so that each row, each column and each bold "
                         "3 x 3 box contains every number exactly once.",
                         "Puzzles get harder as you go: easy, medium, hard, then expert.",
                         "Every puzzle has exactly one solution. The answers are in the back; the numbers you had to find are grey."])
    items = []
    for level, count in book.plan[0]["levels"]:
        for _ in range(count):
            p, s = sudoku.make_puzzle(rng, level)
            items.append((len(items) + 1, level, p, s))

    def page(group):
        def fn(c, box, n):
            cw, ch = box.w / 2, box.h / 2
            for k, (num, level, p, s) in enumerate(group):
                col, r = k % 2, k // 2
                cx = box.x0 + cw * (col + 0.5)
                top = box.y1 - ch * r
                size = min(cw * 0.9, ch - 34)
                c.setFillColor(DARK)
                c.setFont(BOLD, 12)
                c.drawString(cx - size / 2, top - 14, f"#{num}")
                c.setFont(SANS, 11)
                c.drawRightString(cx + size / 2, top - 14, level.title())
                sudoku_draw(c, cx - size / 2, top - 22 - size, size, p)
        return fn
    for k in range(0, len(items), 4):
        pages.append(page(items[k:k + 4]))

    def sol(group):
        def fn(c, box, n):
            cw, ch = box.w / 3, box.h / 4
            for k, (num, level, p, s) in enumerate(group):
                col, r = k % 3, k // 3
                cx = box.x0 + cw * (col + 0.5)
                top = box.y1 - ch * r
                size = min(cw * 0.88, ch - 22)
                c.setFillColor(DARK)
                c.setFont(BOLD, 9)
                c.drawCentredString(cx, top - 10, f"#{num}")
                render.draw_sudoku(c, cx - size / 2, top - 14 - size, size, s, given=p)
        return fn
    sols = [sol(items[k:k + 12]) for k in range(0, len(items), 12)]
    return finish(pages, sols, book), len(items)


def sudoku_draw(c, x, y, size, grid):
    render.draw_sudoku(c, x, y, size, grid)


def art_sudoku(book):
    rng = random.Random(book.seed + 1)
    p, _ = sudoku.make_puzzle(rng, "medium", tries=1)
    return lambda c, x, y, s: render.draw_sudoku(c, x, y, s, p)


# ================================================================ 4. pattern & mandala coloring

def build_coloring(book):
    rng = random.Random(book.seed)
    pages = front(book, ["Every design is printed on its own page with a blank back, so markers won't ruin the next picture.",
                         "Bold, simple lines make these easy to color: perfect for relaxing, for beginners and for tired eyes.",
                         "Tip: slip a sheet of paper behind the page if you use markers."], belongs=True)
    designs = []
    count = book.plan[0]["count"]
    for i in range(count):
        kind = "mandala" if i % 2 == 0 else "pattern"
        seed = rng.random()

        def fn(c, box, n, kind=kind, seed=seed):
            art.coloring_design(c, Box(box.x0, box.y0, box.x1, box.y1 - 10), random.Random(seed), kind)
        designs.append(fn)
    pages += single_sided(designs)
    return finish(pages, [], book), count


def art_coloring(book):
    rng = random.Random(book.seed + 2)
    return lambda c, x, y, s: art.draw_mandala(c, x + s / 2, y + s / 2, s * 0.47, rng, bold=2.4)


# ================================================================ 5. color-by-number mosaics

def build_cbn(book):
    rng = random.Random(book.seed)
    pages = front(book, ["Each square has a number. Color it with the matching color from the key under the grid.",
                         "Squares without a number stay white.",
                         "Work row by row or color one number at a time, and watch a hidden picture or a kaleidoscope pattern appear!",
                         "Small previews of every finished picture are in the back, shown in shades of grey."])
    pics = [(name, art.rasterize((name, ops, bg))) for name, ops, bg in art.PICTURES]
    n_kal = book.plan[0]["count"] - len(pics)
    kals = [("Kaleidoscope", art.kaleidoscope(rng)) for _ in range(max(0, n_kal))]
    items = pics + kals
    rng.shuffle(items)
    designs = []
    for i, (name, grid) in enumerate(items, 1):
        def fn(c, box, n, grid=grid, i=i):
            c.setFillColor(DARK)
            c.setFont(SERIF, 20)
            c.drawCentredString(box.cx, box.y1 - 20, f"Mystery Mosaic {i}")
            size = min(box.w, box.h - 1.5 * INCH)
            gy = box.y1 - 34 - size
            art.draw_cbn(c, box.cx - size / 2, gy, size, grid)
            art.cbn_legend(c, box.x0, gy - 20, grid, box.w)
        designs.append(fn)
    pages += single_sided(designs)

    def sol(group, start):
        def fn(c, box, n):
            cw, ch = box.w / 3, box.h / 3
            for k, (name, grid) in enumerate(group):
                col, r = k % 3, k // 3
                cx = box.x0 + cw * (col + 0.5)
                top = box.y1 - ch * r
                size = min(cw * 0.86, ch - 24)
                c.setFillColor(DARK)
                c.setFont(BOLD, 10)
                c.drawCentredString(cx, top - 11, f"{start + k}. {name}")
                art.draw_cbn(c, cx - size / 2, top - 16 - size, size, grid, numbers=False, solution=True)
        return fn
    sols = [sol(items[k:k + 9], k + 1) for k in range(0, len(items), 9)]
    return finish(pages, sols, book), len(items)


def art_cbn(book):
    heart = art.rasterize(art.PICTURES[17])  # butterfly

    def fn(c, x, y, s):
        art.draw_cbn(c, x, y, s, heart, numbers=False, solution=True)
    return fn


# ================================================================ 6. bible verse coloring

def build_verse(book):
    rng = random.Random(book.seed)
    pages = front(book, ["Each page pairs a King James Bible verse in big outlined letters with patterns to color.",
                         "Every page has a blank back, so you can use markers, gel pens or pencils.",
                         "Take a moment with each verse as you color. Let it be a quiet time of prayer and reflection."], belongs=True)
    verses = KJV_VERSES[: book.plan[0]["count"]]
    designs = [art.verse_page(v, ref, random.Random(rng.random())) for v, ref in verses]
    pages += single_sided(designs)
    return finish(pages, [], book), len(verses)


def art_verse(book):
    rng = random.Random(book.seed + 4)

    def fn(c, x, y, s):
        art.draw_mandala(c, x + s / 2, y + s / 2, s * 0.47, rng, bold=1.8)
        c.setFillColor(white)
        c.roundRect(x + s * 0.12, y + s * 0.36, s * 0.76, s * 0.28, 12, stroke=0, fill=1)
        art.draw_outline_text(c, ["BE STILL"], SERIF, s * 0.12, x + s / 2, y + s * 0.6)
    return fn


# ================================================================ 7. memory games

def build_memory(book):
    rng = random.Random(book.seed)
    pages = front(book, ["This book has rounds of gentle brain games: memory lists, number patterns, missing vowels, "
                         "finishing sayings, odd one out, mental math and word scrambles.",
                         "There is no time limit. Do a round a day, alone or with a friend.",
                         "For memory rounds, study the word list, turn the page, then write what you remember.",
                         "All answers are in the back."])
    mem_pages, blocks = pz.memory_pages(rng, book.plan[0]["count"])
    pages += mem_pages
    return finish(pages, compose._text_solutions(blocks, book), book), book.plan[0]["count"]


def art_memory(book):
    def fn(c, x, y, s):
        words = ["APPLE", "PIANO", "ROBIN", "TULIP", "KETTLE", "MAPLE"]
        cw, ch = s / 2, s / 3
        for i, w in enumerate(words):
            col, r = i % 2, i // 2
            bx, by = x + col * cw, y + s - (r + 1) * ch
            c.setStrokeColor(HexColor("#999999"))
            c.setLineWidth(2)
            c.roundRect(bx + 6, by + 6, cw - 12, ch - 12, 10)
            c.setFillColor(DARK)
            c.setFont(BOLD, s * 0.075)
            c.drawCentredString(bx + cw / 2, by + ch / 2 - s * 0.025, w)
    return fn


# ================================================================ 8-10, 14. text books for kids

def build_riddles(book):
    pages = front(book, ["Read each riddle and try to guess the answer before you peek.",
                         "Answers are printed upside down at the bottom of each page.",
                         "Try them on your family and friends!"])
    per = 4
    for k in range(0, len(RIDDLES), per):
        group = RIDDLES[k:k + per]

        def fn(c, box, n, group=group, start=k + 1):
            step = (box.h - 0.7 * INCH) / per
            for i, (q, a) in enumerate(group):
                y = box.y1 - i * step
                c.setFillColor(HexColor("#2E86C1"))
                c.setFont(SERIF, 30)
                c.drawString(box.x0, y - 30, "?")
                c.setFillColor(DARK)
                c.setFont(SERIF, 15)
                c.drawString(box.x0 + 26, y - 16, f"Riddle {start + i}")
                draw_paragraphs(c, [q], box.x0 + 26, y - 24, box.w - 26, SANS, 14, gap=0)
                c.setStrokeColor(GREY)
                c.line(box.x0, y - step + 8, box.x1, y - step + 8)
            # answers, upside down at the foot of the page
            c.saveState()
            c.translate(box.x1, box.y0 + 6)
            c.rotate(180)
            c.setFont(SANS, 10)
            c.setFillColor(DARK)
            for i, (q, a) in enumerate(group):
                c.drawString(0, -12 * (len(group) - i) + 4, f"{start + i}. {a}")
            c.restoreState()
        pages.append(fn)
    return finish(pages, [], book), len(RIDDLES)


def build_jokes(book):
    pages = front(book, ["Find a friend, pick a joke, and start with \"Knock knock!\"",
                         "Your friend says \"Who's there?\" and the fun begins.",
                         "Warning: some of these will make grown-ups groan."])
    per = 4
    for k in range(0, len(KNOCK_KNOCK), per):
        group = KNOCK_KNOCK[k:k + per]

        def fn(c, box, n, group=group):
            y = box.y1
            step = box.h / per
            for who, punch in group:
                c.setFillColor(DARK)
                lines = [("Knock, knock!", BOLD), ("Who's there?", SANS), (f"{who}.", BOLD), (f"{who} who?", SANS)]
                yy = y - 13
                for txt, f in lines:
                    c.setFont(f, 12.5)
                    c.drawString(box.x0, yy, txt)
                    yy -= 15.5
                for ln in wrap(punch, BOLD, 12.5, box.w):
                    c.setFont(BOLD, 12.5)
                    c.setFillColor(HexColor("#B03A2E"))
                    c.drawString(box.x0, yy, ln)
                    yy -= 15.5
                c.setStrokeColor(GREY)
                c.line(box.x0, y - step + 6, box.x1, y - step + 6)
                y -= step
        pages.append(fn)
    return finish(pages, [], book), len(KNOCK_KNOCK)


def build_wyr(book):
    pages = front(book, ["Read each question out loud and pick one answer. You have to choose!",
                         "Tick a box, then explain why. There are no wrong answers.",
                         "Great for car rides, sleepovers, dinner tables and rainy days."])
    per = 5
    for k in range(0, len(WOULD_YOU_RATHER), per):
        group = WOULD_YOU_RATHER[k:k + per]

        def fn(c, box, n, group=group, start=k + 1):
            step = box.h / per
            y = box.y1
            for i, q in enumerate(group):
                a, b = q.rstrip("?").split(" OR ")
                c.setFillColor(DARK)
                c.setFont(BOLD, 12)
                c.drawString(box.x0, y - 13, f"{start + i}. Would you rather...")
                yy = y - 32
                for opt in (a, b + "?"):
                    c.setFont(SANS, 12)
                    for j, ln in enumerate(wrap(opt, SANS, 12, box.w - 22)):
                        if j == 0:
                            c.rect(box.x0 + 2, yy - 2, 10, 10)
                        c.drawString(box.x0 + 20, yy, ln)
                        yy -= 14
                    if opt == a:
                        c.setFont(BOLD, 11)
                        c.drawString(box.x0 + 20, yy, "OR")
                        yy -= 14
                c.setStrokeColor(GREY)
                c.line(box.x0, y - step + 4, box.x1, y - step + 4)
                y -= step
        pages.append(fn)
    return finish(pages, [], book), len(WOULD_YOU_RATHER)


def build_stories(book):
    import re
    pages = front(book, ["Don't read the story first! Ask a friend for each word on the left-hand page and write it in.",
                         "Then read the story out loud, filling each numbered blank with the word you wrote.",
                         "Need help? A noun is a person, place or thing. A verb is an action word. "
                         "An adjective describes something (fuzzy, huge). An adverb tells how (quickly, loudly)."])
    for title, text in FILL_IN_STORIES:
        prompts = re.findall(r"\{([^}]+)\}", text)
        counter = iter(range(1, len(prompts) + 1))
        story = re.sub(r"\{[^}]+\}", lambda m: f"__({next(counter)})__", text)

        def left(c, box, n, title=title, prompts=prompts):
            y = heading(c, box, title, 20)
            c.setFont(SANS, 11)
            c.drawCentredString(box.cx, y - 4, "Fill in these words first:")
            step = min((y - 20 - box.y0) / len(prompts), 30)
            yy = y - 30
            for i, pr in enumerate(prompts, 1):
                c.setFont(SANS, 12)
                c.setFillColor(DARK)
                c.drawString(box.x0, yy, f"{i}.")
                c.setStrokeColor(GREY)
                c.line(box.x0 + 22, yy - 2, box.x1 - 1.4 * INCH, yy - 2)
                c.setFont(SANS, 9)
                c.drawString(box.x1 - 1.35 * INCH, yy, f"({pr})")
                yy -= step

        def right(c, box, n, title=title, story=story):
            y = heading(c, box, title, 20)
            draw_paragraphs(c, [story], box.x0, y - 6, box.w, SANS, 12.5, leading=21)
        pages += [left, right]
    return finish(pages, [], book), len(FILL_IN_STORIES)


def art_text(kind):
    def fn(c, x, y, s):
        c.setFillColor(DARK)
        if kind == "riddles":
            c.setFont(SERIF, s * 0.5)
            c.setFillColor(HexColor("#2E86C1"))
            c.drawCentredString(x + s / 2, y + s * 0.38, "?")
            c.setFillColor(DARK)
            c.setFont(BOLD, s * 0.065)
            c.drawCentredString(x + s / 2, y + s * 0.2, "What has keys but")
            c.drawCentredString(x + s / 2, y + s * 0.12, "can't open locks?")
        elif kind == "jokes":
            for i, (txt, dx) in enumerate((("Knock, knock!", 0.08), ("Who's there?", 0.3), ("Lettuce.", 0.08), ("Lettuce who?", 0.3))):
                yy = y + s * (0.82 - i * 0.2)
                c.setStrokeColor(DARK)
                c.setLineWidth(2)
                c.roundRect(x + s * dx, yy - s * 0.06, s * 0.6, s * 0.14, s * 0.05)
                c.setFont(BOLD, s * 0.065)
                c.drawCentredString(x + s * (dx + 0.3), yy - s * 0.01, txt)
        elif kind == "wyr":
            c.setLineWidth(3)
            c.setStrokeColor(DARK)
            c.roundRect(x + s * 0.05, y + s * 0.55, s * 0.9, s * 0.3, 14)
            c.roundRect(x + s * 0.05, y + s * 0.08, s * 0.9, s * 0.3, 14)
            c.setFont(BOLD, s * 0.07)
            c.drawCentredString(x + s / 2, y + s * 0.68, "Fly like a bird")
            c.drawCentredString(x + s / 2, y + s * 0.21, "Swim like a fish")
            c.setFont(SERIF, s * 0.12)
            c.setFillColor(HexColor("#C0392B"))
            c.drawCentredString(x + s / 2, y + s * 0.42, "OR")
        else:  # stories
            c.setFont(SANS, s * 0.06)
            y0 = y + s * 0.85
            for txt in ("Once upon a time, a", "______ (adjective)", "______ (animal) ate a", "______ (food) and said",
                        "\"______!\" (silly word)"):
                c.drawString(x + s * 0.06, y0, txt)
                y0 -= s * 0.16
    return fn


# ================================================================ 11. pencil control

def build_trace(book):
    pages = front(book, ["Hold the pencil gently. Start at the big dot and follow the dashed line.",
                         "Go slowly. It's fine to go over the line a little, and practice makes it easier.",
                         "Pages go from straight lines to curves, loops, spirals and shapes."], belongs=True)
    kinds = ["horizontal", "vertical", "diagonal", "zigzag", "castle", "bumps", "arches", "waves", "spikes", "loops"]
    shapes = ["circle", "square", "triangle", "diamond", "heart", "star", "spiral"]
    reps = book.plan[0].get("reps", 3)
    for k in kinds:
        for _ in range(reps):
            pages.append(art.trace_rows(k, rows=5 if _ % 2 == 0 else 4))
    for sh in shapes:
        for _ in range(2):
            pages.append(art.trace_shapes(sh))
    return finish(pages, [], book), len(kinds) * reps + len(shapes) * 2


def art_trace(book):
    def fn(c, x, y, s):
        c.setStrokeColor(DARK)
        c.setLineWidth(4)
        c.setDash(12, 9)
        c.setLineCap(1)
        for r, amp in enumerate((0.1, 0.07, 0.1)):
            yc = y + s * (0.8 - r * 0.3)
            p = c.beginPath()
            p.moveTo(x + s * 0.06, yc)
            seg = s * 0.22
            xs = x + s * 0.06
            while xs + seg <= x + s * 0.96:
                if r == 1:
                    p.lineTo(xs + seg / 2, yc + s * amp); p.lineTo(xs + seg, yc)
                else:
                    p.curveTo(xs + seg / 4, yc + s * amp, xs + seg / 4, yc + s * amp, xs + seg / 2, yc)
                    p.curveTo(xs + 3 * seg / 4, yc - s * amp, xs + 3 * seg / 4, yc - s * amp, xs + seg, yc)
                xs += seg
            c.drawPath(p, stroke=1, fill=0)
        c.setDash()
        c.setLineCap(0)
    return fn


# ================================================================ 12. scissor skills

def build_cut(book):
    rng = random.Random(book.seed)
    pages = front(book, ["Always use child-safe scissors, with a grown-up nearby.",
                         "Cut along the dashed lines, starting at the scissors. Each activity has a blank back.",
                         "Start with straight lines, then move to zigzags, waves, curves, spirals and shapes."], belongs=True)
    order = ["straight"] * 3 + ["zigzag"] * 3 + ["steps"] * 3 + ["waves"] * 3 + ["curves"] * 3 + ["mixed"] * 4 + \
            ["spiral"] * 3 + ["shapes"] * 6
    designs = [art.cut_page(k, random.Random(rng.random())) for k in order]
    pages += single_sided(designs)
    return finish(pages, [], book), len(order)


def art_cut(book):
    def fn(c, x, y, s):
        c.setStrokeColor(DARK)
        c.setLineWidth(4)
        c.setDash(14, 10)
        for r in range(3):
            yc = y + s * (0.8 - r * 0.3)
            p = c.beginPath()
            p.moveTo(x + s * 0.2, yc)
            if r == 0:
                p.lineTo(x + s * 0.95, yc)
            elif r == 1:
                xs, up = x + s * 0.2, True
                while xs < x + s * 0.9:
                    xs += s * 0.08
                    p.lineTo(xs, yc + (s * 0.06 if up else -s * 0.06)); up = not up
            else:
                p.curveTo(x + s * 0.4, yc + s * 0.15, x + s * 0.6, yc - s * 0.15, x + s * 0.95, yc)
            c.drawPath(p, stroke=1, fill=0)
            c.setDash()
            c.setFont(SANS, s * 0.12)
            c.setFillColor(DARK)
            c.drawString(x + s * 0.02, yc - s * 0.04, "✂")
            c.setDash(14, 10)
        c.setDash()
    return fn


# ================================================================ 13. 2027 planner

def us_holidays(year: int) -> dict:
    def nth(month, weekday, n):
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)

    def last(month, weekday):
        d = dt.date(year, month, calendar.monthrange(year, month)[1])
        return d - dt.timedelta(days=(d.weekday() - weekday) % 7)
    # Easter (anonymous Gregorian algorithm)
    a = year % 19; b = year // 100; cc = year % 100; d_ = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d_ - g + 15) % 30
    i = cc // 4; k = cc % 4; l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return {
        dt.date(year, 1, 1): "New Year's Day", nth(1, 0, 3): "Martin Luther King Jr. Day",
        dt.date(year, 2, 14): "Valentine's Day", nth(2, 0, 3): "Presidents' Day", dt.date(year, 3, 17): "St. Patrick's Day",
        dt.date(year, month, day): "Easter", nth(5, 6, 2): "Mother's Day", last(5, 0): "Memorial Day",
        dt.date(year, 6, 19): "Juneteenth", nth(6, 6, 3): "Father's Day", dt.date(year, 7, 4): "Independence Day",
        nth(9, 0, 1): "Labor Day", nth(10, 0, 2): "Columbus / Indigenous Peoples' Day", dt.date(year, 10, 31): "Halloween",
        dt.date(year, 11, 11): "Veterans Day", nth(11, 3, 4): "Thanksgiving", dt.date(year, 12, 24): "Christmas Eve",
        dt.date(year, 12, 25): "Christmas Day", dt.date(year, 12, 31): "New Year's Eve",
    }


def _mini_month(c, x, y_top, w, year, month, fs=8):
    c.setFillColor(DARK)
    c.setFont(BOLD, fs + 2)
    c.drawCentredString(x + w / 2, y_top - fs - 2, calendar.month_name[month])
    cw = w / 7
    c.setFont(BOLD, fs)
    for i, dn in enumerate("MTWTFSS"):
        c.drawCentredString(x + cw * (i + 0.5), y_top - 2 * fs - 8, dn)
    c.setFont(SANS, fs)
    for r, week in enumerate(calendar.Calendar(0).monthdayscalendar(year, month)):
        for i, d in enumerate(week):
            if d:
                c.drawCentredString(x + cw * (i + 0.5), y_top - (3 + r) * fs * 1.35 - 8, str(d))


def year_page(year):
    def fn(c, box, n):
        y = heading(c, box, f"{year} at a Glance", 26)
        cw, ch = box.w / 3, (y - box.y0) / 4
        for m in range(1, 13):
            col, r = (m - 1) % 3, (m - 1) // 3
            _mini_month(c, box.x0 + col * cw + 6, y - r * ch, cw - 12, year, m, fs=9)
    return fn


def build_planner(book):
    year = book.plan[0]["year"]
    hol = us_holidays(year)
    pages = [render.title_page(f"{year} Weekly Planner", book.subtitle.split(" - ")[0], book.author),
             render.copyright_page(book.author), belongs_page, year_page(year), year_page(year + 1)]

    def holidays_page(c, box, n):
        y = heading(c, box, f"{year} Holidays & Important Dates", 22)
        c.setFont(SANS, 12)
        for d, name in sorted(hol.items()):
            c.drawString(box.x0, y - 14, d.strftime("%a, %b %d").replace(" 0", " "))
            c.drawString(box.x0 + 1.6 * INCH, y - 14, name)
            y -= 19
        y -= 20
        c.setFont(BOLD, 13)
        c.drawString(box.x0, y, "Birthdays & anniversaries")
        c.setStrokeColor(GREY)
        y -= 26
        while y > box.y0 + 10:
            c.line(box.x0, y, box.x1, y)
            y -= 24
    pages.append(holidays_page)

    def goals_page(c, box, n):
        y = heading(c, box, f"My Goals for {year}", 24)
        for sec in ("Health", "Family & friends", "Work & money", "Fun & learning"):
            c.setFont(BOLD, 14)
            c.setFillColor(DARK)
            c.drawString(box.x0, y - 18, sec)
            c.setStrokeColor(GREY)
            yy = y - 42
            for _ in range(5):
                c.line(box.x0, yy, box.x1, yy)
                yy -= 24
            y = yy - 8
    pages.append(goals_page)
    while len(pages) % 2:
        pages.append(render.blank_page)

    def month_page(m):
        def fn(c, box, n):
            y = heading(c, box, f"{calendar.month_name[m]} {year}", 28)
            weeks = calendar.Calendar(0).monthdatescalendar(year, m)
            cw = box.w / 7
            c.setFont(BOLD, 10)
            for i, dn in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
                c.drawCentredString(box.x0 + cw * (i + 0.5), y - 12, dn)
            top = y - 20
            ch = (top - box.y0) / len(weeks)
            c.setStrokeColor(DARK)
            c.setLineWidth(0.8)
            for r, week in enumerate(weeks):
                for i, d in enumerate(week):
                    x0, y0 = box.x0 + i * cw, top - (r + 1) * ch
                    c.rect(x0, y0, cw, ch)
                    if d.month == m:
                        c.setFont(BOLD, 11)
                        c.setFillColor(DARK)
                        c.drawString(x0 + 4, y0 + ch - 13, str(d.day))
                        if d in hol:
                            c.setFont(SANS, 6.5)
                            for j, ln in enumerate(wrap(hol[d], SANS, 6.5, cw - 6)[:2]):
                                c.drawString(x0 + 3, y0 + 4 + (1 - j) * 8, ln)
        return fn

    def month_notes(m):
        def fn(c, box, n):
            y = heading(c, box, f"{calendar.month_name[m]} Notes & Goals", 22)
            c.setStrokeColor(GREY)
            yy = y - 20
            while yy > box.y0 + 10:
                c.line(box.x0, yy, box.x1, yy)
                yy -= 24
        return fn

    def week_page(days, left: bool):
        def fn(c, box, n):
            mon = days[0]
            c.setFillColor(DARK)
            c.setFont(SERIF, 16)
            title = f"Week of {mon.strftime('%B')} {mon.day}" if left else f"{days[0].strftime('%B %Y')}"
            c.drawString(box.x0, box.y1 - 16, title)
            slots = days + (["notes"] if left else [])
            top = box.y1 - 26
            sh = (top - box.y0) / len(slots)
            for i, d in enumerate(slots):
                y0 = top - (i + 1) * sh
                c.setStrokeColor(DARK)
                c.setLineWidth(1)
                c.rect(box.x0, y0, box.w, sh)
                c.setFillColor(HexColor("#EEEEEE"))
                c.rect(box.x0, y0 + sh - 18, box.w, 18, stroke=0, fill=1)
                c.setFillColor(DARK)
                c.setFont(BOLD, 11)
                if d == "notes":
                    c.drawString(box.x0 + 6, y0 + sh - 13, "Notes & to-do")
                else:
                    c.drawString(box.x0 + 6, y0 + sh - 13, d.strftime("%A, %B ") + str(d.day))
                    if d in hol:
                        c.setFont(SANS, 9)
                        c.drawRightString(box.x1 - 6, y0 + sh - 13, hol[d])
                c.setStrokeColor(HexColor("#CCCCCC"))
                c.setLineWidth(0.5)
                yy = y0 + sh - 18 - 20
                while yy > y0 + 4:
                    c.line(box.x0 + 6, yy, box.x1 - 6, yy)
                    yy -= 20
        return fn

    # weeks starting on Mondays, covering the whole year
    start = dt.date(year, 1, 1) - dt.timedelta(days=dt.date(year, 1, 1).weekday())
    weeks = []
    d = start
    while d <= dt.date(year, 12, 31):
        weeks.append([d + dt.timedelta(days=k) for k in range(7)])
        d += dt.timedelta(days=7)
    wi = 0
    for m in range(1, 13):
        pages += [month_page(m), month_notes(m)]
        while wi < len(weeks) and (weeks[wi][0].month == m and weeks[wi][0].year == year or (m == 1 and weeks[wi][0].year < year)):
            w = weeks[wi]
            pages += [week_page(w[:3], True), week_page(w[3:], False)]
            wi += 1
    pages += [render.notes_page, render.notes_page]
    return pages, len(weeks)


def art_planner(book):
    year = book.plan[0]["year"]

    def fn(c, x, y, s):
        _mini_month(c, x + s * 0.05, y + s * 0.95, s * 0.9, year, 1, fs=s * 0.05)
    return fn


# ================================================================ 15. brain games variety (uses compose)

BUILDERS = {
    "logic": (build_logic, art_logic),
    "crimews": (build_crime, art_crime),
    "sudoku500": (build_sudoku500, art_sudoku),
    "coloring": (build_coloring, art_coloring),
    "cbn": (build_cbn, art_cbn),
    "verse": (build_verse, art_verse),
    "memory": (build_memory, art_memory),
    "riddles": (build_riddles, lambda b: art_text("riddles")),
    "jokes": (build_jokes, lambda b: art_text("jokes")),
    "wyr": (build_wyr, lambda b: art_text("wyr")),
    "stories": (build_stories, lambda b: art_text("stories")),
    "trace": (build_trace, art_trace),
    "cut": (build_cut, art_cut),
    "planner": (build_planner, art_planner),
}
