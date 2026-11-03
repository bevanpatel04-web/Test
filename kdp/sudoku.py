"""Sudoku generator: every puzzle has exactly one solution.

Grids are lists of 81 ints, 0 = empty. Difficulty is set by how many clues
remain; cells are removed in symmetric pairs so puzzles look like the ones in
newspapers.
"""
from __future__ import annotations

import random

ALL = 0x3FE  # bits 1..9

ROW = [i // 9 for i in range(81)]
COL = [i % 9 for i in range(81)]
BOX = [(i // 27) * 3 + (i % 9) // 3 for i in range(81)]

# Target clue counts. Fewer clues = harder.
LEVELS = {"easy": 40, "medium": 32, "hard": 27}


def _bits(x: int):
    while x:
        low = x & -x
        yield low.bit_length() - 1
        x ^= low


def count_solutions(grid: list[int], limit: int = 2) -> int:
    """Count solutions up to `limit` using bitmask backtracking (fewest options first)."""
    g = list(grid)
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for i, v in enumerate(g):
        if v:
            b = 1 << v
            if rows[ROW[i]] & b or cols[COL[i]] & b or boxes[BOX[i]] & b:
                return 0
            rows[ROW[i]] |= b
            cols[COL[i]] |= b
            boxes[BOX[i]] |= b
    empties = [i for i in range(81) if not g[i]]
    found = 0

    def solve(k: int) -> None:
        nonlocal found
        if k == len(empties):
            found += 1
            return
        # choose the empty cell with the fewest candidates
        best, best_opts, best_n = k, 0, 10
        for j in range(k, len(empties)):
            i = empties[j]
            opts = ALL & ~(rows[ROW[i]] | cols[COL[i]] | boxes[BOX[i]])
            n = bin(opts).count("1")
            if n < best_n:
                best, best_opts, best_n = j, opts, n
                if n <= 1:
                    break
        if best_n == 0:
            return
        empties[k], empties[best] = empties[best], empties[k]
        i = empties[k]
        r, c, bx = ROW[i], COL[i], BOX[i]
        for d in _bits(best_opts):
            b = 1 << d
            rows[r] |= b
            cols[c] |= b
            boxes[bx] |= b
            solve(k + 1)
            rows[r] &= ~b
            cols[c] &= ~b
            boxes[bx] &= ~b
            if found >= limit:
                break
        empties[k], empties[best] = empties[best], empties[k]

    solve(0)
    return found


def solve(grid: list[int]) -> list[int] | None:
    """Return the solution of a puzzle (first one found), or None."""
    g = list(grid)

    def ok(i: int, d: int) -> bool:
        for j in range(81):
            if g[j] == d and (ROW[j] == ROW[i] or COL[j] == COL[i] or BOX[j] == BOX[i]):
                return False
        return True

    def bt(pos: int) -> bool:
        while pos < 81 and g[pos]:
            pos += 1
        if pos == 81:
            return True
        for d in range(1, 10):
            if ok(pos, d):
                g[pos] = d
                if bt(pos + 1):
                    return True
        g[pos] = 0
        return False

    return g if bt(0) else None


def full_grid(rng: random.Random) -> list[int]:
    g = [0] * 81

    def bt(pos: int) -> bool:
        if pos == 81:
            return True
        digits = list(range(1, 10))
        rng.shuffle(digits)
        for d in digits:
            if all(
                g[j] != d
                for j in range(81)
                if ROW[j] == ROW[pos] or COL[j] == COL[pos] or BOX[j] == BOX[pos]
            ):
                g[pos] = d
                if bt(pos + 1):
                    return True
        g[pos] = 0
        return False

    bt(0)
    return g


def make_puzzle(rng: random.Random, level: str, tries: int = 12) -> tuple[list[int], list[int]]:
    """Return (puzzle, solution) with a unique solution, as close to the level's clue target as found."""
    target = LEVELS[level]
    best = None
    for _ in range(tries):
        puzzle, solution = _dig(rng, target)
        if best is None or clue_count(puzzle) < clue_count(best[0]):
            best = (puzzle, solution)
        if clue_count(puzzle) <= target + 1:
            break
    return best


def _dig(rng: random.Random, target: int) -> tuple[list[int], list[int]]:
    solution = full_grid(rng)
    puzzle = list(solution)
    cells = list(range(41))  # 0..40 paired with 80..40 (centre pairs with itself)
    rng.shuffle(cells)
    clues = 81
    for i in cells:
        if clues <= target:
            break
        j = 80 - i
        pair = {i, j}
        saved = {k: puzzle[k] for k in pair}
        for k in pair:
            puzzle[k] = 0
        if count_solutions(puzzle) == 1:
            clues -= len(pair)
        else:
            for k, v in saved.items():
                puzzle[k] = v
    return puzzle, solution


def clue_count(grid: list[int]) -> int:
    return sum(1 for v in grid if v)
