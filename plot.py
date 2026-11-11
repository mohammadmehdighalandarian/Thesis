"""Draw T graphs and their case-1 longest paths (s free, t free).

Usage:
  python3 plot.py                     overview figure -> dataset/overview.png
  python3 plot.py T_7_3_3_4_2         one instance    -> figures/T_7_3_3_4_2.png
  python3 plot.py --all               every instance  -> figures/<id>.png
"""
import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tgraph import t_cells, is_black

ROWS = {r["id"]: r for r in csv.DictReader(open("dataset/case1_s_free_t_free.csv"))}
PATHS = {}
for line in open("dataset/case1_s_free_t_free_paths.jsonl"):
    d = json.loads(line)
    PATHS[d["id"]] = d


def draw(ax, iid):
    r = ROWS[iid]
    params = [int(r[k]) for k in ("W", "H1", "w", "H2", "left")]
    path = [tuple(x) for x in PATHS[iid]["path"]]
    for rr, cc in t_cells(*params):
        colour = "#cfe8e0" if is_black((rr, cc)) else "#eeeeee"
        ax.add_patch(plt.Rectangle((cc, -rr - 1), 1, 1, fc=colour, ec="#999", lw=0.5))
    ax.plot([c + 0.5 for _, c in path], [-r_ - 0.5 for r_, _ in path], color="#d85a30", lw=2)
    ax.plot(path[0][1] + 0.5, -path[0][0] - 0.5, "o", color="#d85a30", ms=8)
    ax.set_aspect("equal")
    ax.axis("off")
    longest = r["longest"] or f"{r['best_found']} (timeout)"
    ax.set_title(f"{iid}\nn={r['n_cells']}  bound={r['color_bound']}  longest={longest}", fontsize=10)


def one(iid):
    os.makedirs("figures", exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    draw(ax, iid)
    plt.tight_layout()
    out = f"figures/{iid}.png"
    plt.savefig(out, dpi=130)
    plt.close(fig)
    return out


def overview():
    ex = ["T_7_3_3_4_2", "T_3_3_1_4_1", "T_9_4_3_5_1"]
    fig, axs = plt.subplots(1, 4, figsize=(18, 5), gridspec_kw={"width_ratios": [1, 1, 1, 1.4]})
    for ax, iid in zip(axs, ex):
        draw(ax, iid)
    rs = list(ROWS.values())
    xs = [int(r["n_cells"]) for r in rs]
    ys = [max(float(r["time_sec"]), 1e-4) for r in rs]
    cs = ["#3b6dd8" if r["reaches_bound"] == "True" else "#d85a30" for r in rs]
    axs[3].scatter(xs, ys, c=cs, s=12)
    axs[3].set_yscale("log")
    axs[3].set_xlabel("number of cells")
    axs[3].set_ylabel("exact solver time (s, log)")
    axs[3].set_title("blue: reaches colour bound   orange: below bound", fontsize=10)
    plt.tight_layout()
    plt.savefig("dataset/overview.png", dpi=130)
    print("wrote dataset/overview.png")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        overview()
    elif sys.argv[1] in ("--all", "all", "-all"):
        for iid in ROWS:
            one(iid)
        print(f"wrote {len(ROWS)} figures to figures/")
    else:
        for iid in sys.argv[1:]:
            if iid not in ROWS:
                print(f"'{iid}' is not a graph id. Use an id from dataset/case1_s_free_t_free.csv, "
                      "for example T_7_3_3_4_2, or 'all' to draw every graph.")
                continue
            print("wrote", one(iid))
