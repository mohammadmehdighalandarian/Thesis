"""Build dataset v0.1 of odd-sized T-shaped grid graphs with exact longest paths."""
import csv, json, os, sys, time, random
from tgraph import all_odd_t, t_cells, color_counts, color_bound, check_path, instance_id
from exact import Solver, Timeout

MAX_W, MAX_H1, MAX_H2 = 9, 4, 6
MAX_CELLS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
TIME_LIMIT = 60          # seconds per instance, free-endpoint version
START_TABLE_MAX = 35     # per-start (dock) table only for small T
OUT = "dataset"
os.makedirs(OUT, exist_ok=True)

rows, paths, starts = [], [], []
for params in all_odd_t(MAX_W, MAX_H1, MAX_H2, MAX_CELLS):
    W, H1, w, H2, left = params
    cells = t_cells(*params)
    nb, nw = color_counts(cells)
    bound = color_bound(nb, nw)
    s = Solver(*params, time_limit=TIME_LIMIT)
    t0 = time.perf_counter()
    status = "optimal"
    try:
        L, path = s.longest_free()
    except Timeout:
        L, path = s.best_len, [s.cells[i] for i in s.best_path]
        status = "timeout"
    dt = time.perf_counter() - t0
    assert check_path(path, cells) and len(path) == L
    iid = instance_id(*params)
    rows.append(dict(id=iid, W=W, H1=H1, w=w, H2=H2, left=left, right=W - w - left,
                     n_cells=len(cells), n_black=nb, n_white=nw, color_bound=bound,
                     longest=L if status == "optimal" else "", best_found=L,
                     reaches_bound=(L == bound), status=status, method="backtracking",
                     time_sec=round(dt, 4), search_nodes=s.nodes))
    paths.append(dict(id=iid, length=L, status=status, path=path))
    if len(cells) <= START_TABLE_MAX and status == "optimal":
        for c in cells:
            Ls, ps = Solver(*params).longest_from(c)
            assert check_path(ps, cells, start=c) and len(ps) == Ls
            starts.append(dict(id=iid, start_r=c[0], start_c=c[1], longest_from_start=Ls,
                               covers_all=(Ls == len(cells))))
    print(f"{iid:20s} n={len(cells):3d} bound={bound:3d} L={L:3d} {status} {dt:.2f}s", flush=True)

# split: test = all instances with the largest sizes + random 15%; val 15%; rest train
random.seed(42)
ns = sorted(r["n_cells"] for r in rows)
big = ns[int(0.85 * len(ns))]
for r in rows:
    if r["n_cells"] > big:
        r["split"] = "test"
    else:
        x = random.random()
        r["split"] = "train" if x < 0.70 else ("val" if x < 0.85 else "test")

with open(f"{OUT}/instances.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader(); wr.writerows(rows)
with open(f"{OUT}/paths.jsonl", "w") as f:
    for p in paths:
        f.write(json.dumps(p) + "\n")
with open(f"{OUT}/start_cells.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(starts[0].keys()))
    wr.writeheader(); wr.writerows(starts)
print("instances", len(rows), "start rows", len(starts),
      "timeouts", sum(r["status"] == "timeout" for r in rows))
