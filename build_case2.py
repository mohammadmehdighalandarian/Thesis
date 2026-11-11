"""Case 2 (s fixed, t free): longest path that must start at a given cell s.

For every T graph in case 1 and every cell s of it, find the longest path
starting at s and ending anywhere. This is the "charging dock" question.
For a mirror-symmetric T only the left half (and middle column) is searched;
the right half is copied from the mirror cell.

Output: dataset/case2_s_fixed_t_free.csv

Usage: python3 build_case2.py [max_cells] [seconds_per_start]   (defaults 60, 30)
"""
import csv
import os
import sys
import time
from multiprocessing import Pool

from tgraph import t_cells, check_path, is_black
from exact import Solver, Timeout

MAX_CELLS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
TIME_LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 30
CASE1 = "dataset/case1_s_free_t_free.csv"
OUT = "dataset/case2_s_fixed_t_free.csv"


def solve_graph(row):
    params = tuple(int(row[k]) for k in ("W", "H1", "w", "H2", "left"))
    W = params[0]
    cells = t_cells(*params)
    symmetric = int(row["left"]) == int(row["right"])
    out = {}
    for c in cells:
        if symmetric and c[1] > (W - 1) / 2:
            continue
        s = Solver(*params, time_limit=TIME_LIMIT)
        si = s.index[c]
        bound = s._component_bound(si, 0)
        t0 = time.perf_counter()
        status = "optimal"
        try:
            L, path = s.longest_from(c)
        except Timeout:
            L, path = s.best_len, [s.cells[i] for i in s.best_path]
            status = "timeout"
        dt = time.perf_counter() - t0
        assert check_path(path, cells, start=c) and len(path) == L
        out[c] = (bound, L, path[-1], status, dt)
    if symmetric:
        for c in cells:
            m = (c[0], W - 1 - c[1])
            if c not in out:
                b, L, end, st, _ = out[m]
                out[c] = (b, L, (end[0], W - 1 - end[1]), st, 0.0)
    rows = []
    for c in cells:
        bound, L, end, status, dt = out[c]
        rows.append(dict(
            id=row["id"], W=row["W"], H1=row["H1"], w=row["w"], H2=row["H2"],
            left=row["left"], right=row["right"], n_cells=len(cells),
            s_r=c[0], s_c=c[1], s_color="black" if is_black(c) else "white",
            bound_from_s=bound,
            longest_from_s=L if status == "optimal" else "",
            best_found=L,
            deficit=bound - L if status == "optimal" else "",
            covers_all=(L == len(cells)),
            t_r=end[0], t_c=end[1],
            status=status, time_sec=round(dt, 4)))
    return rows


def main():
    graphs = [r for r in csv.DictReader(open(CASE1)) if int(r["n_cells"]) <= MAX_CELLS]
    graphs.sort(key=lambda r: int(r["n_cells"]))
    all_rows = []
    t0 = time.time()
    with Pool(os.cpu_count()) as pool:
        for i, rows in enumerate(pool.imap(solve_graph, graphs)):
            all_rows.extend(rows)
            to = sum(r["status"] == "timeout" for r in rows)
            print(f"[{i + 1}/{len(graphs)}] {rows[0]['id']:20s} n={rows[0]['n_cells']:3d} "
                  f"timeouts={to} elapsed={time.time() - t0:.0f}s", flush=True)
    with open(OUT, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        wr.writeheader()
        wr.writerows(all_rows)
    print("rows", len(all_rows), "timeouts", sum(r["status"] == "timeout" for r in all_rows))


if __name__ == "__main__":
    main()
