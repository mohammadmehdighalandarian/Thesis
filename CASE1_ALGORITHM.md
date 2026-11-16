# Case 1 (s free, t free): rule and direct algorithm

`construct.py` builds a longest path of an odd-sized T without any search.
`verify_construct.py` checks it against the dataset.

## Starting point

A rectangle with an even area has the same number of black and white cells.
A rectangle with an odd area has one extra cell of its corner colour.
In an odd-sized T exactly one of the two rectangles (bar, stem) has an odd area.
So the two colours always differ by exactly one, and the colour bound is `n`.
The question is only: does the T have a Hamiltonian path or not?

A Hamiltonian path here must start and end on the majority colour.
A cell with only one neighbour (a dead end) must be an end of the path.

## Rule

`n = W*H1 + w*H2`, `right = W - w - left`.

| # | Condition | Longest path |
|---|---|---|
| 1 | `H1 = 1` and `w = 1` | `n - min(left, right, H2)` |
| 2 | `H1 = 1`, `w >= 2`, `W` even | `n - 1` |
| 3 | `w = 1`, `H1` odd, `W` odd, `left` odd | `n - 1` |
| 4 | everything else | `n` |

## Why the path cannot be longer (rules 1 to 3)

1. The T is three straight arms joined at one cell. A path can use at most two arms.
2. The bar is one row, so `(0,0)` and `(0,W-1)` are dead ends and both must be ends of a
   Hamiltonian path. With `W` even they have different colours, but both ends must have
   the majority colour. So there is no Hamiltonian path.
3. The bottom cell of the stem is a dead end, so it must be an end of the path.
   The bar is odd x odd, so black (the corner colour) is the majority.
   With `H1` odd, `H2` even and `left` odd that bottom cell is white. So there is no Hamiltonian path.

## How the path is built

- Rule 1: the two longest arms, joined through the junction cell.
- Rules 2 and 4 with `H1 = 1`: left arm, then the block under the bar from its top-left
  to its top-right cell (a snake), then the right arm. In rule 2 the snake skips one cell.
- Rule 3: up the stem, left along the bottom row of the bar, snake back over the left part,
  then the right part. The cell right of the stem in the bottom row is skipped.
- Rule 4 with `H1 >= 2`: cover the whole bar and stop above the stem at a column `c`,
  step down, cover the whole stem. A rectangle with an even area has a Hamiltonian cycle,
  so its path can start at any cell. For the odd rectangle `c` is chosen so that the
  crossing cell has the majority colour.

Each cell is written once, so the running time is linear in `n`.

## Checks (`python3 verify_construct.py`)

- All 475 dataset graphs: the built path is valid and has exactly the exact length.
- 44,985 odd-sized T graphs with `W <= 20`, `H1 <= 9`, `H2 <= 11` (both mirror images):
  the built path is valid and has the length given by the rule.
- A T with 3,002,001 vertices is solved in about one second.

The two 57-vertex graphs that timed out in the dataset are Hamiltonian by rule 4;
a longer exact run (10 minutes each) confirmed 57 for both.

## Status

The rule was found from the data. The constructions prove "at least this long" for every size,
and the arguments above give "at most this long" for rules 1 to 3. The proof still has to be
written out in full and checked.
