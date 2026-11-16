"""Draw the path built by construct.py for a few T graphs.

Usage: python3 plot_construct.py            (four examples, one per rule)
       python3 plot_construct.py W H1 w H2 left
Output: figures/construct_*.png
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tgraph import t_cells, is_black
from construct import longest_path


def draw(ax, p, title):
    cells = t_cells(*p)
    path = longest_path(*p)
    on = set(path)
    for r, c in cells:
        face = "#d9d9d9" if is_black((r, c)) else "white"
        ax.add_patch(plt.Rectangle((c, -r - 1), 1, 1, facecolor=face, edgecolor="#888888", lw=0.6))
        if (r, c) not in on:
            ax.plot(c + 0.5, -r - 0.5, marker="x", color="#c0392b", ms=9, mew=2)
    xs = [c + 0.5 for r, c in path]
    ys = [-r - 0.5 for r, c in path]
    ax.plot(xs, ys, color="#1f5fa8", lw=2)
    ax.plot(xs[0], ys[0], "o", color="#2e8b57", ms=8)
    ax.plot(xs[-1], ys[-1], "s", color="#c0392b", ms=8)
    ax.set_title(f"{title}\nT{p}: {len(path)} of {len(cells)} vertices", fontsize=9)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale()


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    if len(sys.argv) > 5:
        p = tuple(int(x) for x in sys.argv[1:6])
        fig, ax = plt.subplots(figsize=(6, 6))
        draw(ax, p, "")
        out = "figures/construct_" + "_".join(map(str, p)) + ".png"
    else:
        ex = [((7, 1, 1, 4, 2), "Rule 1: three arms, two are used"),
              ((8, 1, 3, 3, 2), "Rule 2: one cell left out"),
              ((7, 3, 1, 4, 3), "Rule 3: one cell left out"),
              ((9, 3, 4, 4, 2), "Rule 4: every cell visited")]
        fig, axes = plt.subplots(1, 4, figsize=(17, 5))
        for ax, (p, t) in zip(axes, ex):
            draw(ax, p, t)
        out = "figures/construct_examples.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    print("wrote", out)
