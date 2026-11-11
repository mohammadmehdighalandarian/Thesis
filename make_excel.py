"""Put the three case tables into one Excel workbook, one sheet per case.

Output: dataset/dataset.xlsx
  Guide                  what each case means, column meanings, summary counts
  Case1_sFree_tFree      s free,  t free  (one row per graph)
  Case2_sFixed_tFree     s fixed, t free  (one row per graph and start cell s)
  Case3_sFixed_tFixed    s fixed, t fixed (one row per graph and pair {s, t})

Usage: python3 make_excel.py
"""
import csv

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Font, PatternFill

FILES = [
    ("Case1_sFree_tFree", "dataset/case1_s_free_t_free.csv"),
    ("Case2_sFixed_tFree", "dataset/case2_s_fixed_t_free.csv"),
    ("Case3_sFixed_tFixed", "dataset/case3_s_fixed_t_fixed.csv"),
]
HEAD_FONT = Font(name="Arial", size=10, bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", start_color="3B5998")
FONT = Font(name="Arial", size=10)
BOLD = Font(name="Arial", size=10, bold=True)
TITLE = Font(name="Arial", size=13, bold=True)


def value(x):
    if x == "":
        return None
    if x in ("True", "False"):
        return x == "True"
    for cast in (int, float):
        try:
            return cast(x)
        except ValueError:
            pass
    return x


def data_sheet(wb, name, path):
    ws = wb.create_sheet(name)
    ws.freeze_panes = "B2"
    rows = csv.reader(open(path))
    header = next(rows)
    for i, h in enumerate(header):
        ws.column_dimensions[chr(65 + i) if i < 26 else "A" + chr(65 + i - 26)].width = max(9, len(h) + 2)
    cells = []
    for h in header:
        c = WriteOnlyCell(ws, value=h)
        c.font, c.fill = HEAD_FONT, HEAD_FILL
        cells.append(c)
    ws.append(cells)
    n = 0
    for r in rows:
        ws.append([value(x) for x in r])
        n += 1
    return header, n


GUIDE = [
    ("Case 1: s free, t free", "حالت ۱: s نامشخص، t نامشخص",
     "Longest path anywhere in the graph. One row per T graph. Sheet Case1_sFree_tFree."),
    ("Case 2: s fixed, t free", "حالت ۲: s مشخص، t نامشخص",
     "Longest path that must start at cell s (s_r, s_c) and may end anywhere. "
     "One row per graph and start cell. Sheet Case2_sFixed_tFree."),
    ("Case 3: s fixed, t fixed", "حالت ۳: s مشخص، t مشخص (مسئله طولانی‌ترین مسیر s-t)",
     "Longest path from cell s to cell t. One row per graph and unordered pair {s, t}; "
     "the path t to s is the same path reversed. Sheet Case3_sFixed_tFixed."),
]

COLUMNS = [
    ("id", "Graph id T_W_H1_w_H2_left"),
    ("W, H1", "Width and height of the top bar"),
    ("w, H2", "Width and height of the stem"),
    ("left, right", "Bar columns to the left and right of the stem"),
    ("n_cells", "Number of vertices (always odd)"),
    ("s_r, s_c / t_r, t_c", "Row and column of s and t; rows from the top, columns from the left, both from 0"),
    ("*_color", "Chessboard colour: black if row + column is even"),
    ("color_bound / bound_from_s / bound_st", "Upper bound on the path length from the chessboard colouring"),
    ("longest / longest_from_s / longest_st", "Exact longest path length in vertices (empty if the search timed out)"),
    ("best_found", "Longest path found (equals the exact value when status is optimal)"),
    ("deficit", "Bound minus exact longest length"),
    ("covers_all / hamiltonian", "TRUE if the path visits every vertex"),
    ("status", "optimal = exact answer; timeout = time limit reached, best_found is a lower bound"),
    ("time_sec", "Search time in seconds (0 for a result copied from the mirror image)"),
]


def guide_sheet(wb, headers):
    from openpyxl.utils import get_column_letter

    def col(sheet, h):
        L = get_column_letter(headers[sheet].index(h) + 1)
        return f"'{sheet}'!{L}:{L}"

    ws = wb.create_sheet("Guide", 0)
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 44
    ws.column_dimensions["C"].width = 90
    ws.column_dimensions["D"].width = 14

    def put(row, items, font=FONT):
        out = []
        for x in items:
            c = WriteOnlyCell(ws, value=x)
            c.font = font
            c.alignment = Alignment(wrap_text=True, vertical="top")
            out.append(c)
        ws.append(out)

    put(0, ["Longest paths in odd-sized T-shaped grid graphs"], TITLE)
    put(0, ["Odd size = the total number of vertices W*H1 + w*H2 is odd."])
    put(0, [])
    put(0, ["Case", "نام فارسی", "Meaning"], BOLD)
    for row in GUIDE:
        put(0, row)
    put(0, [])
    put(0, ["Summary (formulas)", "", "", "Value"], BOLD)
    s1, s2, s3 = (n for n, _ in FILES)
    summary = [
        ("Case 1 graphs", f"=COUNTA({col(s1, 'id')})-1"),
        ("Case 1 exact answers", f'=COUNTIF({col(s1, "status")},"optimal")'),
        ("Case 1 graphs below the bound (deficit > 0)", f'=COUNTIF({col(s1, "deficit")},">0")'),
        ("Case 2 rows (graph, s)", f"=COUNTA({col(s2, 'id')})-1"),
        ("Case 2 exact answers", f'=COUNTIF({col(s2, "status")},"optimal")'),
        ("Case 2 rows covering all vertices", f"=COUNTIF({col(s2, 'covers_all')},TRUE)"),
        ("Case 3 rows (graph, s, t)", f"=COUNTA({col(s3, 'id')})-1"),
        ("Case 3 exact answers", f'=COUNTIF({col(s3, "status")},"optimal")'),
        ("Case 3 Hamiltonian s-t pairs", f"=COUNTIF({col(s3, 'hamiltonian')},TRUE)"),
        ("Case 3 largest graph included (vertices)", f"=MAX({col(s3, 'n_cells')})"),
    ]
    for label, f in summary:
        put(0, [label, "", "", f])
    put(0, [])
    put(0, ["Column", "", "Meaning"], BOLD)
    for name, meaning in COLUMNS:
        put(0, [name, "", meaning])


def main():
    wb = Workbook(write_only=True)
    counts = {}
    headers = {}
    for name, path in FILES:
        headers[name], counts[name] = data_sheet(wb, name, path)
    guide_sheet(wb, headers)
    wb.save("dataset/dataset.xlsx")
    print("wrote dataset/dataset.xlsx", counts)


if __name__ == "__main__":
    main()
