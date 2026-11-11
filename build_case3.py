"""Case 3 (s fixed, t fixed): longest path from a given cell s to a given cell t.

This is the longest (s,t)-path problem studied for rectangular, L-, C- and
O-shaped grid graphs. For every T graph up to max_cells and every unordered pair
{s, t} of distinct cells, find the longest path between them. A path from s to t
reversed is a path from t to s, so each pair is stored once (s before t in the
cell order: top-to-bottom, left-to-right).

Bound for a pair (from the chessboard colouring):
  s, t same colour       : 2*min(n_same - 1, n_other) + 1
  s, t different colours : 2*min(n_black, n_white)
deficit = bound - longest.

Output: dataset/case3_s_fixed_t_fixed.csv

Usage: python3 build_case3.py [max_cells] [seconds_per_pair]   (defaults 45, 5)
"""
import csv
import os
import sys
import time
from itertools import combinations
from multiprocessing import Pool

from tgraph import t_cells, check_path, is_black
from exact import SolverST, Timeout

MAX_CELLS = int(sys.argv[1]) if len(sys.argv) > 1 else 45
TIME_LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 5
CASE1 = "dataset/case1_s_free_t_free.csv"
OUT = "dataset/case3_s_fixed_t_fixed.csv"


def solve_graph(row):
    params = tuple(int(row[k]) for k in ("W", "H1", "w", "H2", "left"))
    W = params[0]
    cells = t_cells(*params)
    n = len(cells)
    symmetric = int(row["left"]) == int(row["right"])
    order = {c: i for i, c in enumerate(cells)}

    def mirror(c):
        return (c[0], W - 1 - c[1])

    def key(a, b):
        return (a, b) if order[a] < order[b] else (b, a)

    done = {}
    for s, t in combinations(cells, 2):
        if symmetric:
            mk = key(mirror(s), mirror(t))
            if mk in done:
                b, L, st, _ = done[mk]
                done[(s, t)] = (b, L, st, 0.0)
                continue
        solver = SolverST(*params, time_limit=TIME_LIMIT)
        t0 = time.perf_counter()
        status = "optimal"
        try:
            L, path, bound = solver.longest_st(s, t)
        except Timeout:
            L, path = solver.best_len, [solver.cells[i] for i in solver.best_path]
            bound = solver._st_bound(solver.index[s], 0, solver.index[t])
            status = "timeout"
        dt = time.perf_counter() - t0
        assert L == 0 or (check_path(path, cells, start=s) and path[-1] == t and len(path) == L)
        done[(s, t)] = (bound, L, status, dt)

    rows = []
    for s, t in combinations(cells, 2):
        bound, L, status, dt = done[(s, t)]
        rows.append(dict(
            id=row["id"], W=row["W"], H1=row["H1"], w=row["w"], H2=row["H2"],
            left=row["left"], right=row["right"], n_cells=n,
            s_r=s[0], s_c=s[1], t_r=t[0], t_c=t[1],
            s_color="black" if is_black(s) else "white",
            t_color="black" if is_black(t) else "white",
            same_color=(is_black(s) == is_black(t)),
            bound_st=bound,
            longest_st=L if status == "optimal" else "",
            best_found=L,
            deficit=bound - L if status == "optimal" else "",
            hamiltonian=(L == n),
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
                  f"pairs={len(rows)} timeouts={to} elapsed={time.time() - t0:.0f}s", flush=True)
    with open(OUT, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        wr.writeheader()
        wr.writerows(all_rows)
    print("rows", len(all_rows), "timeouts", sum(r["status"] == "timeout" for r in all_rows))


if __name__ == "__main__":
    main()
