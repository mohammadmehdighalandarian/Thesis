"""Check construct.py (the direct algorithm for case 1).

1. Against the dataset: the built path must be a valid path and exactly as long
   as the exact answer found by exhaustive search.
2. On many more T graphs (all left values, larger sizes): the built path must be
   valid and as long as the rule says.
3. Speed on a few large graphs.
"""
import csv
import time

from tgraph import t_cells, check_path
from construct import longest_path, longest_length

# 1. dataset
rows = list(csv.DictReader(open("dataset/case1_s_free_t_free.csv")))
bad = 0
exact = 0
for r in rows:
    p = tuple(int(r[k]) for k in ("W", "H1", "w", "H2", "left"))
    path = longest_path(*p)
    ok = check_path(path, t_cells(*p))
    if r["status"] == "optimal":
        exact += 1
        ok = ok and len(path) == int(r["longest"])
    else:
        ok = ok and len(path) >= int(r["best_found"])
    if not ok:
        bad += 1
        print("MISMATCH", r["id"], len(path), r["longest"])
print(f"dataset: {len(rows)} graphs ({exact} with exact answers), mismatches: {bad}")

# 2. wider range, both mirror images
count = bad2 = 0
for W in range(3, 21):
    for H1 in range(1, 10):
        for H2 in range(1, 12):
            for w in range(1, W - 1):
                for left in range(1, W - w):
                    if (W * H1 + w * H2) % 2 == 0:
                        continue
                    p = (W, H1, w, H2, left)
                    path = longest_path(*p)
                    count += 1
                    if not check_path(path, t_cells(*p)) or len(path) != longest_length(*p):
                        bad2 += 1
                        print("BAD", p, len(path), longest_length(*p))
print(f"wider range: {count} graphs, invalid or wrong length: {bad2}")

# 3. speed
for p in [(101, 51, 41, 60, 30), (1001, 301, 500, 400, 200), (2001, 1001, 999, 1000, 500)]:
    t0 = time.perf_counter()
    path = longest_path(*p)
    dt = time.perf_counter() - t0
    n = p[0] * p[1] + p[2] * p[3]
    print(f"T{p}: n={n:,} path={len(path):,} valid={check_path(path, t_cells(*p))} time={dt:.2f}s")
