# Odd-sized T-shaped grid graphs: exact longest paths (v0.1)

Exact longest simple paths for every odd-sized T-shaped rectangular grid graph in a fixed parameter range.
Built for the M.Sc. thesis "Longest Path in T-Shaped Rectangular Grid Graphs of Odd Size" (Amirkabir University of Technology).

## How a T is defined

Five integers: `W` (bar width), `H1` (bar height), `w` (stem width), `H2` (stem height), `left` (bar columns left of the stem).
`right = W - w - left`. Rows are counted from the top, columns from the left.
Bar cells: rows `0..H1-1`, columns `0..W-1`. Stem cells: rows `H1..H1+H2-1`, columns `left..left+w-1`.
Two cells are adjacent if they share a side.

Included: `3 <= W <= 9`, `1 <= H1 <= 4`, `1 <= H2 <= 6`, `left >= 1`, `right >= 1`, odd number of cells, at most 60 cells.
Mirror images are removed (only `left <= right` is kept), since they have the same answer.

## Files

`instances.csv`, one row per T (475 rows):

| column | meaning |
|---|---|
| `id` | `T_W_H1_w_H2_left` |
| `W, H1, w, H2, left, right` | shape parameters |
| `n_cells, n_black, n_white` | size and chessboard colour counts (black if row+col is even) |
| `color_bound` | upper bound from the bipartite colouring: `2*min+1` (or `2*min` if equal) |
| `longest` | exact longest path length in vertices (empty if the search timed out) |
| `best_found` | longest path found (equals `longest` when status is optimal) |
| `reaches_bound` | whether the best path reaches `color_bound` |
| `status` | `optimal` or `timeout` |
| `method`, `time_sec`, `search_nodes` | solver used, wall time, search tree size |
| `split` | `train` / `val` / `test` (all largest instances are in `test`) |

`paths.jsonl`: one JSON object per T with the best path as a list of `[row, col]` cells.

`start_cells.csv`: for every T with at most 35 cells, and every cell of it, the longest path that must start at that cell
(`longest_from_start`) and whether it covers the whole T (`covers_all`). This supports the charging-dock question.

`overview.png`: three example paths and the solver time per instance.

## How the answers were computed

Backtracking search (`exact.py`) with three prunings:
1. stop when a path reaches the colour bound;
2. at each step, bound the remaining length by the colour counts of the unvisited cells still reachable;
3. for the free-endpoint version, try majority-colour start cells first, and only left-half starts for symmetric T.

Checks: the solver was compared with plain exhaustive search on 159 T graphs up to 17 cells (free endpoints)
and 518 (T, start cell) pairs up to 15 cells. No mismatch. Every stored path was re-checked to be a simple path inside its T.
Time limit: 60 s per instance.

## Summary of v0.1

- 475 instances, 5 to 57 cells.
- 473 solved exactly, 2 timed out (`T_8_4_5_5_1`, `T_9_4_7_3_1`, best found 56 of bound 57).
- 395 reach the colour bound; 78 solved instances are strictly below it (mostly width-1 stems).
- Split: 290 train, 56 val, 129 test (random seed 42).
- 7,981 rows in `start_cells.csv`.

## Reproduce

```
python3 verify.py          # solver vs brute force
python3 verify_start.py    # fixed-start solver vs brute force
python3 build_dataset.py 60
```
Python 3, standard library only (matplotlib for the figure).

## Figures

```
python3 plot.py                 # overview -> dataset/overview.png
python3 plot.py T_7_3_3_4_2     # one T and its path -> figures/T_7_3_3_4_2.png
python3 plot.py --all           # all 475 -> figures/
```
