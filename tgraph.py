"""T-shaped rectangular grid graphs: generation, coloring bound, path checking.

A T is defined by five integers:
  W     width of the top bar
  H1    height of the top bar
  w     width of the stem
  H2    height of the stem
  left  number of bar columns to the left of the stem
right = W - w - left. A real T needs left >= 1 and right >= 1.
Rows are numbered from the top (0), columns from the left (0).
"""

from itertools import product


def t_cells(W, H1, w, H2, left):
    cells = [(r, c) for r in range(H1) for c in range(W)]
    cells += [(r, c) for r in range(H1, H1 + H2) for c in range(left, left + w)]
    return cells


def build(W, H1, w, H2, left):
    """Return (cells, index, adj) where adj[i] is a list of neighbour indices."""
    cells = t_cells(W, H1, w, H2, left)
    index = {cell: i for i, cell in enumerate(cells)}
    adj = [[] for _ in cells]
    for i, (r, c) in enumerate(cells):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            j = index.get((r + dr, c + dc))
            if j is not None:
                adj[i].append(j)
    return cells, index, adj


def is_black(cell):
    r, c = cell
    return (r + c) % 2 == 0


def color_counts(cells):
    b = sum(1 for x in cells if is_black(x))
    return b, len(cells) - b


def color_bound(n_black, n_white):
    """Max number of vertices of any simple path in a bipartite graph."""
    lo, hi = min(n_black, n_white), max(n_black, n_white)
    return 2 * lo + 1 if hi > lo else 2 * lo


def check_path(path, cells, start=None):
    """True if path is a simple path inside the T moving only to neighbours."""
    cellset = set(cells)
    if not path:
        return False
    if len(set(path)) != len(path):
        return False
    if any(p not in cellset for p in path):
        return False
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
    if start is not None and path[0] != start:
        return False
    return True


def all_odd_t(max_W, max_H1, max_H2, max_cells):
    """Yield parameter tuples of all odd-sized T graphs, one per mirror pair."""
    for W, H1, H2 in product(range(3, max_W + 1), range(1, max_H1 + 1), range(1, max_H2 + 1)):
        for w in range(1, W - 1):
            for left in range(1, W - w):
                right = W - w - left
                if left > right:  # keep one of each mirror pair
                    continue
                n = W * H1 + w * H2
                if n % 2 == 1 and n <= max_cells:
                    yield (W, H1, w, H2, left)


def instance_id(W, H1, w, H2, left):
    return f"T_{W}_{H1}_{w}_{H2}_{left}"
