from itertools import product
from tgraph import t_cells, check_path, instance_id
from exact import Solver, brute_force_free

checked = mism = 0
for W, H1, H2 in product(range(3, 7), range(1, 4), range(1, 5)):
    for w in range(1, W - 1):
        for left in range(1, W - w):
            n = W * H1 + w * H2
            if n > 17: continue
            s = Solver(W, H1, w, H2, left)
            L, path = s.longest_free()
            bf = brute_force_free(W, H1, w, H2, left)
            cells = t_cells(W, H1, w, H2, left)
            ok = check_path(path, cells) and len(path) == L
            for cell in cells[:3]:
                Ls, ps = Solver(W, H1, w, H2, left).longest_from(cell)
                ok &= check_path(ps, cells, start=cell) and len(ps) == Ls
            checked += 1
            if L != bf or not ok:
                mism += 1
                print("MISMATCH", instance_id(W,H1,w,H2,left), L, bf, ok)
print("checked", checked, "mismatches", mism)
