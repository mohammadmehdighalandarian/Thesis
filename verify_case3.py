"""Case 3 check: SolverST (with pruning) against plain exhaustive s-t search."""
from itertools import product, combinations
from tgraph import t_cells, check_path
from exact import SolverST, brute_force_st

pairs = bad = 0
for W, H1, H2 in product(range(3, 6), range(1, 4), range(1, 4)):
    for w in range(1, W - 1):
        for left in range(1, W - w):
            cells = t_cells(W, H1, w, H2, left)
            if len(cells) > 15:
                continue
            for s, t in combinations(cells, 2):
                L, p, _ = SolverST(W, H1, w, H2, left).longest_st(s, t)
                ok = check_path(p, cells, start=s) and p[-1] == t and len(p) == L
                pairs += 1
                if L != brute_force_st(W, H1, w, H2, left, s, t) or not ok:
                    bad += 1
                    print("MISMATCH", (W, H1, w, H2, left), s, t, L)
print("s-t pairs checked", pairs, "mismatches", bad)
