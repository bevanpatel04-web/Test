"""Extra puzzle generators: mazes, 6x6 Sudoku, word scrambles, cryptograms."""
from __future__ import annotations

import random
import string
from collections import deque
from dataclasses import dataclass, field


# ---------------------------------------------------------------- mazes

@dataclass
class Maze:
    cols: int
    rows: int
    open: set = field(default_factory=set)  # frozenset({(c, r), (c2, r2)}) passages

    def is_open(self, a, b) -> bool:
        return frozenset((a, b)) in self.open

    def solution(self) -> list[tuple[int, int]]:
        start, end = (0, 0), (self.cols - 1, self.rows - 1)
        prev = {start: None}
        q = deque([start])
        while q:
            cur = q.popleft()
            if cur == end:
                break
            c, r = cur
            for nb in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if nb not in prev and self.is_open(cur, nb):
                    prev[nb] = cur
                    q.append(nb)
        path, node = [], end
        while node is not None:
            path.append(node)
            node = prev[node]
        return path[::-1]


def make_maze(rng: random.Random, cols: int, rows: int) -> Maze:
    """Perfect maze (exactly one path between any two cells) by randomized depth-first search."""
    m = Maze(cols, rows)
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        c, r = stack[-1]
        nbs = [(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
               if 0 <= c + dc < cols and 0 <= r + dr < rows and (c + dc, r + dr) not in seen]
        if not nbs:
            stack.pop()
            continue
        nb = rng.choice(nbs)
        m.open.add(frozenset(((c, r), nb)))
        seen.add(nb)
        stack.append(nb)
    return m


# ---------------------------------------------------------------- 6x6 sudoku

def _peers6(i: int) -> list[int]:
    r, c = divmod(i, 6)
    br, bc = r // 2 * 2, c // 3 * 3
    out = set()
    for k in range(6):
        out.add(r * 6 + k)
        out.add(k * 6 + c)
    for rr in range(br, br + 2):
        for cc in range(bc, bc + 3):
            out.add(rr * 6 + cc)
    out.discard(i)
    return sorted(out)


PEERS6 = [_peers6(i) for i in range(36)]


def _count6(g: list[int], limit: int = 2) -> int:
    try:
        i = g.index(0)
    except ValueError:
        return 1
    used = {g[p] for p in PEERS6[i]}
    n = 0
    for d in range(1, 7):
        if d not in used:
            g[i] = d
            n += _count6(g, limit - n)
            g[i] = 0
            if n >= limit:
                break
    return n


def make_sudoku6(rng: random.Random, clues: int = 14) -> tuple[list[int], list[int]]:
    """6x6 Sudoku (2x3 boxes, digits 1-6) with a unique solution."""
    g = [0] * 36

    def fill(i: int) -> bool:
        if i == 36:
            return True
        ds = list(range(1, 7))
        rng.shuffle(ds)
        used = {g[p] for p in PEERS6[i]}
        for d in ds:
            if d not in used:
                g[i] = d
                if fill(i + 1):
                    return True
        g[i] = 0
        return False

    fill(0)
    solution = list(g)
    puzzle = list(g)
    cells = list(range(36))
    rng.shuffle(cells)
    count = 36
    for i in cells:
        if count <= clues:
            break
        v = puzzle[i]
        puzzle[i] = 0
        if _count6(list(puzzle)) == 1:
            count -= 1
        else:
            puzzle[i] = v
    return puzzle, solution


# ---------------------------------------------------------------- word scramble

@dataclass
class Scramble:
    title: str
    words: list[str]       # answers, display form
    scrambled: list[str]   # letters only, scrambled


def scramble_word(rng: random.Random, word: str) -> str:
    letters = [ch for ch in word.upper() if ch.isalpha()]
    plain = "".join(letters)
    for _ in range(50):
        rng.shuffle(letters)
        s = "".join(letters)
        if s != plain and s != plain[::-1]:
            return s
    return "".join(letters)


def make_scramble(rng: random.Random, title: str, words: list[str], count: int = 12, max_len: int = 12) -> Scramble:
    pool = [w for w in words if 4 <= sum(ch.isalpha() for ch in w) <= max_len and len(set(w.replace(" ", ""))) > 2]
    chosen = rng.sample(pool, min(count, len(pool)))
    return Scramble(title, chosen, [scramble_word(rng, w) for w in chosen])


# ---------------------------------------------------------------- cryptogram

@dataclass
class Cryptogram:
    quote: str
    source: str
    key: dict           # plain letter -> cipher letter
    hints: dict         # cipher letter -> plain letter given to the solver

    @property
    def cipher(self) -> str:
        return "".join(self.key.get(ch, ch) for ch in self.quote.upper())


def make_cryptogram(rng: random.Random, quote: str, source: str, hints: int = 2) -> Cryptogram:
    letters = list(string.ascii_uppercase)
    while True:
        shuffled = letters[:]
        rng.shuffle(shuffled)
        if all(a != b for a, b in zip(letters, shuffled)):
            break
    key = dict(zip(letters, shuffled))
    # give away the most common letters first
    freq: dict[str, int] = {}
    for ch in quote.upper():
        if ch.isalpha():
            freq[ch] = freq.get(ch, 0) + 1
    top = sorted(freq, key=lambda ch: (-freq[ch], ch))[:hints]
    return Cryptogram(quote, source, key, {key[ch]: ch for ch in top})
