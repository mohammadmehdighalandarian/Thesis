"""Case 1 (s free, t free): build a longest path of an odd-sized T directly.

No search. The path is put together from simple pieces (straight lines, snakes
and one Hamiltonian cycle of a rectangle), so the running time is linear in the
number of vertices.

Key fact: in an odd-sized T exactly one of the two rectangles (bar, stem) has an
odd area, so the two colours differ by exactly one and the colour bound is n.
A longest path of length n is a Hamiltonian path.

Length rule (found from the dataset, see dataset/README.md):
  1. H1 = 1 and w = 1                         -> n - min(left, right, H2)
  2. H1 = 1, w >= 2, W even                   -> n - 1
  3. w = 1, H1 odd, W odd, left odd           -> n - 1
  4. every other odd-sized T                  -> n   (Hamiltonian path)

Usage: python3 construct.py W H1 w H2 left
"""
import sys


def longest_length(W, H1, w, H2, left):
    """Length (in vertices) of a longest path, by the rule above."""
    right = W - w - left
    n = W * H1 + w * H2
    if H1 == 1 and w == 1:
        return n - min(left, right, H2)
    if H1 == 1 and W % 2 == 0:
        return n - 1
    if w == 1 and H1 % 2 == 1 and W % 2 == 1 and left % 2 == 1:
        return n - 1
    return n


# ---------- pieces, all in local coordinates (row 0 at the top) ----------

def vsnake(R, cols, down_first=True):
    """Go through the given columns one by one, alternating down and up."""
    out = []
    for i, c in enumerate(cols):
        rows = range(R) if (i % 2 == 0) == down_first else range(R - 1, -1, -1)
        out += [(r, c) for r in rows]
    return out


def hsnake(rows, C, right_first=True):
    """Go through the given rows one by one, alternating right and left."""
    out = []
    for i, r in enumerate(rows):
        cols = range(C) if (i % 2 == 0) == right_first else range(C - 1, -1, -1)
        out += [(r, c) for c in cols]
    return out


def cycle(R, C):
    """Hamiltonian cycle of an R x C rectangle (R, C >= 2, R*C even)."""
    if R % 2 == 1:
        return [(r, c) for c, r in cycle(C, R)]
    out = [(0, c) for c in range(C)]
    for r in range(1, R):
        cols = range(C - 1, 0, -1) if r % 2 == 1 else range(1, C)
        out += [(r, c) for c in cols]
    out += [(r, 0) for r in range(R - 1, 0, -1)]
    return out


def cycle_from(R, C, start):
    """Hamiltonian path of an even-area rectangle that starts at any cell."""
    cyc = cycle(R, C)
    i = cyc.index(start)
    return cyc[i:] + cyc[:i]


def odd_rect_from_bottom(R, C, c):
    """Hamiltonian path of an odd x odd rectangle from bottom-row cell (R-1, c), c even."""
    if c == 0:
        out = [(r, 0) for r in range(R - 1, -1, -1)]
    else:
        out = [(R - 1, j) for j in range(c, -1, -1)]          # bottom row to the left
        for j in range(c):                                    # rows above it, columns 0..c-1
            rows = range(R - 2, -1, -1) if j % 2 == 0 else range(R - 1)
            out += [(r, j) for r in rows]
        out += [(r, c) for r in range(R - 2, -1, -1)]         # up column c
    return out + vsnake(R, range(c + 1, C), down_first=True)


def top_left_to_top_right(R, C):
    """Path in an R x C rectangle from (0,0) to (0,C-1), as long as possible.

    Covers every cell, except when C is odd and R is even: then one cell is left out.
    """
    if C % 2 == 0:
        return vsnake(R, range(C), down_first=True)
    if R % 2 == 1:
        return hsnake(range(R), C - 1) + [(r, C - 1) for r in range(R - 1, -1, -1)]
    out = vsnake(R, range(C - 3), down_first=True)
    out += [(r, C - 3) for r in range(R)]
    for r in range(R - 1, 0, -1):
        pair = [(r, C - 2), (r, C - 1)]
        out += pair if (R - 1 - r) % 2 == 0 else pair[::-1]
    return out + [(0, C - 1)]                                 # cell (0, C-2) is left out


def shift(path, dr, dc):
    return [(r + dr, c + dc) for r, c in path]


# ---------- the algorithm ----------

def longest_path(W, H1, w, H2, left):
    """Return a longest path of the odd-sized T as a list of (row, col) cells."""
    right = W - w - left
    assert left >= 1 and right >= 1 and (W * H1 + w * H2) % 2 == 1
    a, b = left, left + w - 1                                 # first and last stem column

    if H1 == 1:
        left_arm = [(0, c) for c in range(a)]                 # ends next to the stem
        right_arm = [(0, c) for c in range(b + 1, W)]         # starts next to the stem
        if w == 1:                                            # rule 1: three arms, take two
            stem = [(r, a) for r in range(H2, 0, -1)]         # ends next to the junction
            arms = sorted([left_arm, right_arm[::-1], stem], key=len)
            return arms[2] + [(0, a)] + arms[1][::-1]
        middle = shift(top_left_to_top_right(H2 + 1, w), 0, a)    # rules 2 and 4
        return left_arm + middle + right_arm

    if w == 1 and H1 % 2 == 1 and W % 2 == 1 and left % 2 == 1:   # rule 3
        out = [(r, a) for r in range(H1 + H2 - 1, H1 - 1, -1)]    # up the stem
        out += [(H1 - 1, j) for j in range(a, -1, -1)]            # bar bottom row to the left
        for j in range(a + 1):
            rows = range(H1 - 2, -1, -1) if j % 2 == 0 else range(H1 - 1)
            out += [(r, j) for r in rows]
        out += [(r, a + 1) for r in range(H1 - 2, -1, -1)]        # cell (H1-1, a+1) is left out
        return out + vsnake(H1, range(a + 2, W), down_first=True)

    # rule 4: cover the whole bar, cross once at column c, cover the whole stem
    bar_odd = (W * H1) % 2 == 1
    if not bar_odd or w == 1:
        c = a
    elif H2 == 1:
        c = a if a % 2 == 0 else b
    else:
        c = a if a % 2 == 0 else a + 1

    if bar_odd:
        bar = odd_rect_from_bottom(H1, W, c)
    else:
        bar = cycle_from(H1, W, (H1 - 1, c))

    k = c - a
    if w == 1:
        stem = [(r, 0) for r in range(H2)]
    elif H2 == 1:
        stem = [(0, j) for j in (range(w) if k == 0 else range(w - 1, -1, -1))]
    elif (w * H2) % 2 == 0:
        stem = cycle_from(H2, w, (0, k))
    else:
        stem = hsnake(range(H2), w)
    return bar[::-1] + shift(stem, H1, a)


if __name__ == "__main__":
    p = tuple(int(x) for x in sys.argv[1:6])
    path = longest_path(*p)
    print("vertices:", p[0] * p[1] + p[2] * p[3], " longest path:", len(path))
    print(" -> ".join(f"({r},{c})" for r, c in path))
