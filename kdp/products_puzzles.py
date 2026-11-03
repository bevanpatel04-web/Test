"""Murder-mystery logic cases, crime word searches and memory games."""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field

from reportlab.lib.colors import HexColor, black, white

from . import render, sudoku, wordsearch
from .render import BOLD, DARK, SANS, SERIF, Box, draw_paragraphs, fit_lines, wrap
from .specs import INCH
from .text_content import (CATEGORIES, CRIME_MESSAGES, PROVERBS, SETTINGS, SUSPECTS, VICTIMS, WEAPONS)

GREY = HexColor("#9E9E9E")

# ================================================================ logic grid mysteries


@dataclass
class Case:
    num: int
    setting: str
    victim: str
    suspects: list[tuple[str, str]]
    weapons: list[str]
    places: list[str]
    weapon_of: list[int]      # suspect i had weapons[weapon_of[i]]
    place_of: list[int]       # suspect i was in places[place_of[i]]
    clues: list[str] = field(default_factory=list)
    body_place: int = 0

    @property
    def killer(self) -> int:
        return self.place_of.index(self.body_place)


def _consistent(atoms, w, l) -> bool:
    for kind, a, b, truth in atoms:
        if kind == "sw":
            ok = (w[a] == b)
        elif kind == "sl":
            ok = (l[a] == b)
        else:  # "wl": weapon a was in place b  ->  the suspect holding weapon a is in place b
            s = w.index(a)
            ok = (l[s] == b)
        if ok != truth:
            return False
    return True


def _count(atoms, n) -> int:
    perms = list(itertools.permutations(range(n)))
    found = 0
    for w in perms:
        for l in perms:
            if _consistent(atoms, w, l):
                found += 1
                if found > 1:
                    return found
    return found


def make_case(rng: random.Random, num: int, n: int) -> Case:
    setting, rooms = rng.choice(SETTINGS)
    sus = rng.sample(SUSPECTS, n)
    weps = rng.sample(WEAPONS, n)
    places = rng.sample(rooms, n)
    w = list(range(n))
    l = list(range(n))
    rng.shuffle(w)
    rng.shuffle(l)
    case = Case(num, setting, rng.choice(VICTIMS), sus, weps, places, w, l)
    case.body_place = rng.randrange(n)
    # pool of true atoms; negatives are favoured so the solver has to reason
    pool = []
    for i in range(n):
        for j in range(n):
            pool.append(("sw", i, j, w[i] == j))
            pool.append(("sl", i, j, l[i] == j))
            s = w.index(i)
            pool.append(("wl", i, j, l[s] == j))
    rng.shuffle(pool)
    pool.sort(key=lambda a: a[3])  # negatives first
    negs = [a for a in pool if not a[3]]
    poss = [a for a in pool if a[3]]
    rng.shuffle(negs)
    rng.shuffle(poss)
    ordered = negs[: len(negs) * 2 // 3] + poss[:2] + negs[len(negs) * 2 // 3:] + poss[2:]
    atoms = []
    for a in ordered:
        atoms.append(a)
        if _count(atoms, n) == 1:
            break
    # drop clues that are not needed
    for a in list(atoms):
        trial = [x for x in atoms if x is not a]
        if _count(trial, n) == 1:
            atoms = trial
    rng.shuffle(atoms)
    case.atoms = atoms
    case.clues = [_phrase(rng, case, a) for a in atoms]
    return case


def _short(name: str) -> str:
    return name


def _phrase(rng, case: Case, atom) -> str:
    kind, a, b, truth = atom
    S = lambda i: case.suspects[i][0]
    W = lambda i: "the " + case.weapons[i]
    P = lambda i: "the " + case.places[i]
    if kind == "sw":
        if truth:
            return rng.choice([f"{S(a)} was carrying {W(b)}.", f"{W(b).capitalize()} was found with {S(a)}'s fingerprints."])
        return rng.choice([f"{S(a)} never touched {W(b)}.", f"{S(a)} did not have {W(b)}.",
                           f"{W(b).capitalize()} did not belong to {S(a)}."])
    if kind == "sl":
        if truth:
            return rng.choice([f"{S(a)} was seen in {P(b)}.", f"A witness placed {S(a)} in {P(b)}."])
        return rng.choice([f"{S(a)} was not in {P(b)}.", f"{S(a)} has never set foot in {P(b)}.",
                           f"{S(a)} has an alibi: nowhere near {P(b)}."])
    if truth:
        return rng.choice([f"{W(a).capitalize()} turned up in {P(b)}.", f"Someone spotted {W(a)} in {P(b)}."])
    return rng.choice([f"Nobody took {W(a)} into {P(b)}.", f"There was no sign of {W(a)} in {P(b)}."])


def draw_logic_grid(c, x, y_top, case: Case, cell: float) -> float:
    """Classic logic grid: suspects x (weapons | places), weapons x places. Returns bottom y."""
    n = len(case.suspects)
    label_w = 1.55 * INCH
    head_h = 1.25 * INCH
    fs = min(11, cell * 0.42)
    gx, gy = x + label_w, y_top - head_h
    # column headers (rotated)
    cols = case.weapons + case.places
    c.setFont(SANS, fs)
    c.setFillColor(DARK)
    for k, name in enumerate(cols):
        c.saveState()
        c.translate(gx + k * cell + cell * 0.65, gy + 4)
        c.rotate(60)
        c.drawString(0, 0, name)
        c.restoreState()
    rows = [s[0] for s in case.suspects] + case.weapons
    for r, name in enumerate(rows):
        yy = gy - (r + 1) * cell + cell * 0.32
        c.drawRightString(gx - 4, yy, name)
    c.setStrokeColor(black)
    # suspect rows: all 2n columns
    def box(x0, y0, ncols, nrows):
        c.setLineWidth(0.5)
        for i in range(ncols + 1):
            c.line(x0 + i * cell, y0, x0 + i * cell, y0 - nrows * cell)
        for j in range(nrows + 1):
            c.line(x0, y0 - j * cell, x0 + ncols * cell, y0 - j * cell)
        c.setLineWidth(1.8)
        c.rect(x0, y0 - nrows * cell, ncols * cell, nrows * cell)
    box(gx, gy, n, n)
    box(gx + n * cell, gy, n, n)
    box(gx + n * cell, gy - n * cell, n, n)
    return gy - 2 * n * cell


def logic_case_page(case: Case, label: str):
    def fn(c, box: Box, page_no: int) -> None:
        n = len(case.suspects)
        c.setFillColor(DARK)
        size, lines = fit_lines(f"{label}: Murder at {case.setting}", SERIF, 20, box.w, 2, 12)
        y = box.y1 - size
        c.setFont(SERIF, size)
        for ln in lines:
            c.drawString(box.x0, y, ln)
            y -= size * 1.15
        intro = (f"{case.victim.capitalize()} has been found dead in the {case.places[case.body_place]}. "
                 f"Each suspect had exactly one weapon and was in exactly one place. "
                 f"Who did it, with what, and where?")
        y = draw_paragraphs(c, [intro], box.x0, y - 2, box.w, SANS, 12.5, gap=4)
        fs = 13.5 if len(case.clues) <= 14 else 12
        c.setFont(BOLD, fs)
        c.drawString(box.x0, y - 10, "Suspects")
        yy = y - 26
        c.setFont(SANS, fs)
        for name, desc in case.suspects:
            for k, ln in enumerate(wrap(f"{name}, {desc}", SANS, fs, box.w)):
                c.drawString(box.x0 + (0 if k == 0 else 12), yy, ln)
                yy -= fs * 1.3
        c.setFont(BOLD, fs)
        c.drawString(box.x0, yy - 6, "Clues")
        yy -= 22
        c.setFont(SANS, fs)
        for i, cl in enumerate(case.clues, 1):
            for k, ln in enumerate(wrap(cl, SANS, fs, box.w - 22)):
                c.drawString(box.x0 + 22, yy, ln)
                if k == 0:
                    c.drawRightString(box.x0 + 16, yy, f"{i}.")
                yy -= fs * 1.3
        for head, items in (("Possible weapons", case.weapons), ("Possible places", case.places)):
            c.setFont(BOLD, fs)
            c.drawString(box.x0, yy - 8, head)
            yy -= 8 + fs * 1.4
            c.setFont(SANS, fs)
            for ln in wrap(", ".join(items), SANS, fs, box.w):
                c.drawString(box.x0, yy, ln)
                yy -= fs * 1.3
        c.setFont(BOLD, fs)
        c.drawString(box.x0, yy - 10, "Detective's notes")
        c.setStrokeColor(HexColor("#BBBBBB"))
        yy -= 34
        while yy > box.y0 + 10:
            c.line(box.x0, yy, box.x1, yy)
            yy -= 24
    return fn


def logic_grid_page(case: Case, label: str):
    """Right-hand page of the spread: a full-size grid to mark, plus the answer line."""
    def fn(c, box: Box, page_no: int) -> None:
        n = len(case.suspects)
        c.setFillColor(DARK)
        c.setFont(SERIF, 18)
        c.drawString(box.x0, box.y1 - 18, f"{label}: Logic Grid")
        c.setFont(SANS, 11)
        c.drawString(box.x0, box.y1 - 36, "Mark X for impossible, O for certain. The clues are on the facing page.")
        cell = min(0.55 * INCH, (box.w - 1.7 * INCH) / (2 * n))
        bottom = draw_logic_grid(c, box.x0, box.y1 - 0.75 * INCH, case, cell)
        c.setFont(BOLD, 12)
        y = bottom - 0.6 * INCH
        for lab in ("Killer:", "Weapon:", "Place:"):
            c.drawString(box.x0, y, lab)
            c.setStrokeColor(DARK)
            c.line(box.x0 + 0.9 * INCH, y - 2, box.x0 + 4 * INCH, y - 2)
            y -= 0.45 * INCH
    return fn


def logic_solution_text(case: Case, label: str) -> tuple[str, list[str]]:
    k = case.killer
    lines = [f"{case.suspects[k][0]} with the {case.weapons[case.weapon_of[k]]} in the {case.places[case.place_of[k]]}."]
    for i, (name, _) in enumerate(case.suspects):
        if i != k:
            lines.append(f"{name}: {case.weapons[case.weapon_of[i]]}, {case.places[case.place_of[i]]}")
    return label, lines


# ================================================================ crime word search

CLUE_WORDS = ["ALIBI", "MOTIVE", "WITNESS", "FOOTPRINT", "FINGERPRINT", "SUSPECT", "DETECTIVE", "EVIDENCE",
              "MAGNIFIER", "CLUE", "VICTIM", "INSPECTOR", "SECRET", "LOCKED DOOR", "TORN NOTE", "MUDDY BOOT",
              "SCREAM", "MIDNIGHT", "SHADOW", "DIARY"]


@dataclass
class CrimeSearch:
    title: str
    intro: str
    statements: list[str]
    ws: wordsearch.WordSearch
    message: str
    killer: str


def _surname(name: str) -> str:
    parts = [p for p in name.replace(".", "").split() if p not in ("Dr", "Mr", "Mrs", "Ms", "Miss", "Lady", "Lord",
             "Captain", "Baroness", "Chef", "Professor", "Sergeant", "Madame", "Brother", "Coach", "Agent", "Duke",
             "Nurse", "Reverend", "Signor", "Admiral", "Mayor", "Doctor", "Maestro", "Granny", "Countess", "Inspector",
             "Farmer", "Archdeacon")]
    return parts[-1].upper()


def make_crime_search(rng: random.Random, num: int, size: int = 15) -> CrimeSearch:
    setting, rooms = rng.choice(SETTINGS)
    sus = rng.sample(SUSPECTS, 4)
    places = rng.sample(rooms, 4)
    weps = rng.sample(WEAPONS, 3)
    killer_i = rng.randrange(4)
    room = places[killer_i].upper()
    msg_words = rng.choice(CRIME_MESSAGES) + " " + room
    message = "".join(ch for ch in msg_words if ch.isalpha())
    words = [_surname(s[0]) for s in sus] + [p.upper() for p in places] + [w.upper() for w in weps]
    words += rng.sample(CLUE_WORDS, 4)
    words = [w for w in words if len(w.replace(" ", "")) <= size]
    for _ in range(200):
        grid = [["" for _ in range(size)] for _ in range(size)]
        placements = []
        chosen = []
        for w in sorted(words, key=lambda w: -len(w.replace(" ", ""))):
            k = wordsearch._key(w)
            if any(k in wordsearch._key(o) or wordsearch._key(o) in k for o in chosen):
                continue
            p = wordsearch._place(rng, grid, w, wordsearch.DIRS_ALL)
            if p is None:
                break
            placements.append(p)
            chosen.append(w)
        else:
            empties = [(r, c) for r in range(size) for c in range(size) if not grid[r][c]]
            if len(empties) < len(message):
                continue
            for (r, c), ch in zip(empties, message):
                grid[r][c] = ch
            for r, c in empties[len(message):]:
                grid[r][c] = rng.choice(wordsearch.FILL)
            if all(wordsearch._occurrences(grid, wordsearch._key(p.word)) == 1 for p in placements):
                ws = wordsearch.WordSearch(f"Case {num}", grid, placements)
                statements = [f"Witnesses saw {s[0]} in the {pl}." for s, pl in zip(sus, places)]
                intro = (f"A {rng.choice(['jewel', 'will', 'priceless painting', 'secret recipe'])} has vanished from "
                         f"{setting}, and {rng.choice(VICTIMS)} lies unconscious beside the empty case.")
                return CrimeSearch(f"Case {num}: {setting.title() if setting[0].islower() else setting}", intro,
                                   statements, ws, msg_words, sus[killer_i][0])
    raise RuntimeError("crime search failed")


def crime_page(cs: CrimeSearch):
    def fn(c, box: Box, n: int) -> None:
        c.setFillColor(DARK)
        size, lines = fit_lines(cs.title, SERIF, 20, box.w, 2, 12)
        y = box.y1 - size
        c.setFont(SERIF, size)
        for ln in lines:
            c.drawCentredString(box.cx, y, ln)
            y -= size * 1.15
        y = draw_paragraphs(c, [cs.intro + " " + " ".join(cs.statements)], box.x0, y, box.w, SANS, 10, gap=2)
        words = cs.ws.words
        cols = 3
        rows = -(-len(words) // cols)
        list_h = rows * 14 + 64
        gsize = min(box.w * 0.9, y - box.y0 - list_h - 10)
        gy = y - gsize - 8
        render.draw_wordsearch(c, box.cx - gsize / 2, gy, gsize, cs.ws)
        c.setFont(SANS, 10.5)
        colw = box.w / cols
        for i, w in enumerate(words):
            col, r = divmod(i, rows)
            c.drawString(box.x0 + col * colw + 6, gy - 22 - r * 14, "□ " + w)
        yb = gy - 22 - rows * 14 - 6
        c.setFont(BOLD, 10)
        c.drawString(box.x0, yb, "Secret clue: read the unused letters left to right, top to bottom:")
        c.setStrokeColor(DARK)
        nlet = len(cs.message.replace(" ", ""))
        cw = min(14, box.w / nlet)
        for i in range(nlet):
            c.line(box.x0 + i * cw + 1, yb - 18, box.x0 + i * cw + cw - 2, yb - 18)
        c.setFont(SANS, 10)
        c.drawString(box.x0, yb - 34, "So the culprit is: _______________________________")
    return fn


# ================================================================ memory & brain games (large print)

def _seq(rng):
    t = rng.randrange(6)
    if t == 0:
        a, d = rng.randint(1, 20), rng.randint(2, 9)
        s = [a + d * i for i in range(6)]
    elif t == 1:
        a, r = rng.randint(1, 4), rng.choice([2, 3])
        s = [a * r ** i for i in range(6)]
    elif t == 2:
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        s = [a, b]
        while len(s) < 6:
            s.append(s[-1] + s[-2])
    elif t == 3:
        k = rng.randint(1, 4)
        s = [(i + k) ** 2 for i in range(6)]
    elif t == 4:
        a, d1, d2 = rng.randint(10, 40), rng.randint(2, 6), rng.randint(1, 4)
        s = [a]
        for i in range(5):
            s.append(s[-1] + (d1 if i % 2 == 0 else -d2))
    else:
        a, d = rng.randint(60, 99), rng.randint(3, 8)
        s = [a - d * i for i in range(6)]
    return s[:5], s[5]


def memory_pages(rng: random.Random, n_rounds: int):
    """Return (pages, solution_blocks). Each round is a set of themed pages."""
    pages, sols = [], []
    cats = list(CATEGORIES.items())
    for r in range(1, n_rounds + 1):
        kind = (r - 1) % 7
        title = ""
        if kind == 0:  # memory list: study page then recall page
            words = rng.sample([w for _, ws in cats for w in ws], 12)
            decoys = rng.sample([w for _, ws in cats for w in ws if w not in words], 4)
            pages.append(_study_page(r, words))
            pages.append(_recall_page(r, words, decoys, rng))
            sols.append((f"Round {r}: Memory list", [", ".join(words)]))
            continue
        if kind == 1:
            title = "What Comes Next?"
            items = [_seq(rng) for _ in range(8)]
            lines = [", ".join(map(str, s)) + ",  ____" for s, _ in items]
            sols.append((f"Round {r}: {title}", [", ".join(str(a) for _, a in items)]))
            pages.append(_list_page(r, title, "Find the pattern and write the next number.", lines))
        elif kind == 2:
            title = "Missing Vowels"
            cat, words = rng.choice(cats)
            ws = rng.sample(words, min(8, len(words)))
            lines = ["".join("_" if ch in "AEIOU" else ch for ch in w) for w in ws]
            sols.append((f"Round {r}: {title} ({cat})", [", ".join(ws)]))
            pages.append(_list_page(r, title, f"Every word is from the category: {cat}. Fill in the missing vowels.", lines, spaced=True))
        elif kind == 3:
            title = "Finish the Saying"
            ps = rng.sample(PROVERBS, 8)
            lines = [f"{a} ..." for a, _ in ps]
            sols.append((f"Round {r}: {title}", [f"{a} {b}." for a, b in ps]))
            pages.append(_list_page(r, title, "Complete each well-known saying.", lines, answer_line=True))
        elif kind == 4:
            title = "Odd One Out"
            lines, ans = [], []
            for _ in range(7):
                (c1, w1), (c2, w2) = rng.sample(cats, 2)
                group = rng.sample(w1, 4)
                odd = rng.choice(w2)
                row = group + [odd]
                rng.shuffle(row)
                lines.append("   ".join(row))
                ans.append(f"{odd} (the others are {c1.lower()})")
            sols.append((f"Round {r}: {title}", ans))
            pages.append(_list_page(r, title, "Circle the word that does not belong with the others.", lines))
        elif kind == 5:
            title = "Mental Math Chains"
            lines, ans = [], []
            for _ in range(6):
                v = rng.randint(2, 12)
                steps = [f"Start with {v}"]
                for _ in range(3):
                    op = rng.choice(["add", "sub", "dbl"])
                    if op == "add":
                        k = rng.randint(2, 9); v += k; steps.append(f"add {k}")
                    elif op == "sub" and v > 5:
                        k = rng.randint(1, v - 2); v -= k; steps.append(f"take away {k}")
                    else:
                        v *= 2; steps.append("double it")
                lines.append(", ".join(steps) + ".  = ____")
                ans.append(str(v))
            sols.append((f"Round {r}: {title}", [", ".join(ans)]))
            pages.append(_list_page(r, title, "Work it out in your head, then write the answer.", lines))
        else:
            title = "Word Scramble"
            cat, words = rng.choice(cats)
            ws = rng.sample(words, 8)
            from .puzzles import scramble_word
            lines = [scramble_word(rng, w) + "   ________" for w in ws]
            sols.append((f"Round {r}: {title} ({cat})", [", ".join(ws)]))
            pages.append(_list_page(r, title, f"Unscramble these {cat.lower()}.", lines))
    return pages, sols


def _round_head(c, box, r, title):
    c.setFillColor(DARK)
    c.setFont(SERIF, 26)
    c.drawCentredString(box.cx, box.y1 - 26, f"Round {r}: {title}")


def _study_page(r, words):
    def fn(c, box, n):
        _round_head(c, box, r, "Remember These")
        c.setFont(SANS, 16)
        c.drawCentredString(box.cx, box.y1 - 60, "Study these 12 words for 2 minutes. Then turn the page.")
        cw, ch = box.w / 3, 1.25 * INCH
        for i, w in enumerate(words):
            col, row = i % 3, i // 3
            x = box.x0 + col * cw
            y = box.y1 - 1.4 * INCH - row * ch
            c.setStrokeColor(GREY)
            c.setLineWidth(1.5)
            c.roundRect(x + 8, y - ch + 18, cw - 16, ch - 18, 10)
            c.setFont(BOLD, 22)
            c.setFillColor(DARK)
            c.drawCentredString(x + cw / 2, y - ch / 2 + 2, w)
    return fn


def _recall_page(r, words, decoys, rng):
    def fn(c, box, n):
        _round_head(c, box, r, "What Do You Remember?")
        c.setFont(SANS, 16)
        c.setFillColor(DARK)
        c.drawCentredString(box.cx, box.y1 - 60, "Without looking back, write down as many words as you can.")
        c.setStrokeColor(GREY)
        for i in range(12):
            col, row = i % 2, i // 2
            x = box.x0 + col * box.w / 2 + 10
            y = box.y1 - 1.3 * INCH - row * 0.6 * INCH
            c.setFont(SANS, 16)
            c.drawString(x, y, f"{i + 1}.")
            c.line(x + 30, y - 2, x + box.w / 2 - 30, y - 2)
        c.setFont(BOLD, 16)
        yb = box.y1 - 5.3 * INCH
        c.drawString(box.x0, yb, "Bonus: circle the words that were on the list.")
        mix = rng.sample(words, 4) + decoys
        rng.shuffle(mix)
        c.setFont(SANS, 18)
        for i, w in enumerate(mix):
            col, row = i % 4, i // 4
            c.drawString(box.x0 + col * box.w / 4 + 6, yb - 40 - row * 40, w)
    return fn


def _list_page(r, title, instr, lines, spaced=False, answer_line=False):
    def fn(c, box, n):
        _round_head(c, box, r, title)
        c.setFillColor(DARK)
        y = draw_paragraphs(c, [instr], box.x0, box.y1 - 48, box.w, SANS, 16)
        step = min((y - box.y0) / len(lines), 1.0 * INCH)
        for i, ln in enumerate(lines, 1):
            yy = y - step * (i - 0.4)
            c.setFont(BOLD, 18)
            c.drawString(box.x0, yy, f"{i}.")
            txt = " ".join(ln) if spaced else ln
            fs = 18
            while render.pdfmetrics.stringWidth(txt, SANS, fs) > box.w - 36 and fs > 11:
                fs -= 1
            c.setFont(SANS, fs)
            c.drawString(box.x0 + 34, yy, txt)
            if answer_line:
                c.setStrokeColor(GREY)
                c.line(box.x0 + 34, yy - step * 0.42, box.x1, yy - step * 0.42)
    return fn
