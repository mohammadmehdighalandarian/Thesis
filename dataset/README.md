# Odd-sized T-shaped grid graphs: exact longest paths (v0.2)

Exact longest simple paths in every odd-sized T-shaped rectangular grid graph in a fixed parameter range,
for three versions of the problem. Built for the M.Sc. thesis "Longest Path in T-Shaped Rectangular Grid Graphs
of Odd Size" (Amirkabir University of Technology).

## The three cases

| Case | s (start) | t (end) | Persian name | Files |
|---|---|---|---|---|
| 1 | free | free | حالت ۱: s نامشخص، t نامشخص | `case1_s_free_t_free.csv`, `case1_s_free_t_free_paths.jsonl` |
| 2 | fixed | free | حالت ۲: s مشخص، t نامشخص | `case2_s_fixed_t_free.csv` |
| 3 | fixed | fixed | حالت ۳: s مشخص، t مشخص (طولانی‌ترین مسیر s-t) | `case3_s_fixed_t_fixed.csv` |

`dataset.xlsx` holds the same three tables, one sheet per case, plus a `Guide` sheet with summary counts.

## How a T is defined

Five integers: `W` (bar width), `H1` (bar height), `w` (stem width), `H2` (stem height), `left` (bar columns left of the stem).
`right = W - w - left`. Rows are counted from the top, columns from the left, both from 0.
Bar cells: rows `0..H1-1`, columns `0..W-1`. Stem cells: rows `H1..H1+H2-1`, columns `left..left+w-1`.
Two cells are adjacent if they share a side.

**Odd size** means the total number of vertices `W*H1 + w*H2` is odd.

Included: `3 <= W <= 9`, `1 <= H1 <= 4`, `1 <= H2 <= 6`, `left >= 1`, `right >= 1`, odd size, at most 60 vertices.
Mirror images are removed (only `left <= right` is kept), since they have the same answers.
Graph id: `T_W_H1_w_H2_left`.

## Colour bounds

Cells are coloured like a chessboard (black if row + column is even). Every edge joins black to white, so a path alternates colours.

- Case 1: `color_bound = 2*min(black, white) + 1` (always `+1` here, since the size is odd).
- Case 2: `bound_from_s` = the same idea for a path that starts on the colour of `s`.
- Case 3: if `s` and `t` have the same colour, `bound_st = 2*min(n_same - 1, n_other) + 1`; otherwise `2*min(black, white)`.

`deficit = bound - longest`. A deficit of 0 means the colour bound is reached.

## Columns

Case 1, one row per graph: `id, W, H1, w, H2, left, right, n_cells, n_black, n_white, color_bound, longest, best_found,
deficit, reaches_bound, path_start_r/c, path_end_r/c, status, method, time_sec, search_nodes, split`.
`split` is a train/val/test split for a learning-based method (the largest 15% are always test).

Case 2, one row per graph and start cell `s`: `id, shape columns, n_cells, s_r, s_c, s_color, bound_from_s, longest_from_s,
best_found, deficit, covers_all, t_r, t_c, status, time_sec`. `t_r, t_c` is where the best path found ends.

Case 3, one row per graph and unordered pair `{s, t}`: `id, shape columns, n_cells, s_r, s_c, t_r, t_c, s_color, t_color,
same_color, bound_st, longest_st, best_found, deficit, hamiltonian, status, time_sec`.
A path from `t` to `s` is the same path reversed, so each pair is stored once (`s` comes first in top-to-bottom, left-to-right order).

In all tables: `status = optimal` means the value is exact; `timeout` means the time limit was reached and `best_found`
is only a lower bound (the exact columns are then empty). `time_sec = 0` marks a result copied from the mirror image of a symmetric T.

## How the answers were computed

Backtracking search in `exact.py`, with pruning that never changes the answer:
1. stop as soon as a path reaches the colour bound;
2. at each step, bound the remaining length by the colour counts of the unvisited cells that can still be reached
   (for case 3, also stop if `t` can no longer be reached);
3. case 1 tries majority-colour starts first and, for a symmetric T, only left-half starts.

Checks against plain exhaustive search with no pruning, all with zero mismatches:

| Script | Case | Checked |
|---|---|---|
| `verify_case1.py` | 1 | 159 graphs up to 17 vertices |
| `verify_case2.py` | 2 | 518 (graph, s) pairs up to 15 vertices |
| `verify_case3.py` | 3 | 3,154 (graph, s, t) triples up to 15 vertices |

Every stored path was also re-checked to be a simple path inside its T.

## Summary of v0.2

Case 2 and case 3 tables are being built; numbers will be added here.

## Reproduce

```
python3 verify_case1.py && python3 verify_case2.py && python3 verify_case3.py
python3 build_case1.py 60          # case 1, 60 s per graph
python3 build_case2.py 60 30       # case 2, all graphs, 30 s per start cell
python3 build_case3.py 45 5        # case 3, graphs up to 45 vertices, 5 s per pair
python3 make_excel.py              # dataset.xlsx
```

## Figures

```
python3 plot.py                 # overview -> dataset/overview.png
python3 plot.py T_7_3_3_4_2     # one graph and its case-1 path -> figures/T_7_3_3_4_2.png
python3 plot.py all             # all graphs -> figures/
```

Python 3, standard library only (matplotlib for figures, openpyxl for the Excel file).
