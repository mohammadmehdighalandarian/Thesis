"""Exact longest path in T-shaped grid graphs by backtracking with pruning.

Pruning:
  1. Global stop: once a path reaches the coloring bound, nothing longer exists.
  2. Component bound: from the current cell, only unvisited cells in its
     connected part can still be used, and the path alternates colours, so
     the remaining length is limited by the colour counts of that part.
  3. Start cells: for the free-endpoint version, a path that reaches the
     bound must start on the majority colour when the counts differ; and for
     a mirror-symmetric T only starts in the left half are needed.
"""

import sys
import time

from tgraph import build, color_counts, color_bound, is_black

sys.setrecursionlimit(10000)


class Timeout(Exception):
    pass


class Solver:
    def __init__(self, W, H1, w, H2, left, time_limit=None):
        self.cells, self.index, self.adj = build(W, H1, w, H2, left)
        self.n = len(self.cells)
        self.black = [is_black(c) for c in self.cells]
        nb, nw = color_counts(self.cells)
        self.bound = color_bound(nb, nw)
        self.symmetric = (left == W - w - left)
        self.W = W
        self.time_limit = time_limit
        self.nodes = 0

    # bound for a path that starts at `cur` and may use only unvisited cells
    def _component_bound(self, cur, visited):
        same = other = 0
        stack = [cur]
        seen = visited | (1 << cur)
        cur_black = self.black[cur]
        same = 1
        while stack:
            v = stack.pop()
            for u in self.adj[v]:
                if not (seen >> u) & 1:
                    seen |= 1 << u
                    stack.append(u)
                    if self.black[u] == cur_black:
                        same += 1
                    else:
                        other += 1
        # path c,o,c,o,...: uses ceil(L/2) of colour c and floor(L/2) of o
        return 2 * other + 1 if same > other else 2 * same

    def _dfs(self, cur, visited, length, path, target):
        self.nodes += 1
        if self.time_limit and (self.nodes & 4095) == 0:
            if time.perf_counter() - self.t0 > self.time_limit:
                raise Timeout
        if length > self.best_len:
            self.best_len = length
            self.best_path = list(path)
            if self.best_len >= target:
                return True
        if length - 1 + self._component_bound(cur, visited) <= self.best_len:
            return False
        for u in self.adj[cur]:
            if not (visited >> u) & 1:
                path.append(u)
                if self._dfs(u, visited | (1 << u), length + 1, path, target):
                    return True
                path.pop()
        return False

    def _run_from(self, s, target):
        self._dfs(s, 1 << s, 1, [s], target)

    def longest_free(self):
        """Longest path with free endpoints. Returns (length, path_cells)."""
        self.t0 = time.perf_counter()
        self.best_len, self.best_path = 0, []
        nb = sum(self.black)
        nw = self.n - nb
        starts = list(range(self.n))
        if self.symmetric:
            mid = (self.W - 1) / 2
            starts = [i for i in starts if self.cells[i][1] <= mid]
        # starts on the majority colour first (only they can reach the bound)
        if nb != nw:
            maj_black = nb > nw
            starts.sort(key=lambda i: self.black[i] != maj_black)
        for s in starts:
            self._run_from(s, self.bound)
            if self.best_len >= self.bound:
                break
        return self.best_len, [self.cells[i] for i in self.best_path]

    def longest_from(self, start_cell):
        """Longest path that must start at start_cell (charging dock)."""
        self.t0 = time.perf_counter()
        self.best_len, self.best_path = 0, []
        s = self.index[start_cell]
        target = self._component_bound(s, 0)
        self._run_from(s, target)
        return self.best_len, [self.cells[i] for i in self.best_path]


class SolverST(Solver):
    """Case 3: longest path that starts at s and ends at t (both fixed)."""

    def _st_bound(self, cur, visited, t):
        """Upper bound on a path from cur to t that uses only unvisited cells.
        Returns -1 if t is no longer reachable from cur."""
        same = 1
        other = 0
        stack = [cur]
        seen = visited | (1 << cur)
        cur_black = self.black[cur]
        reach_t = (cur == t)
        while stack:
            v = stack.pop()
            for u in self.adj[v]:
                if not (seen >> u) & 1:
                    seen |= 1 << u
                    stack.append(u)
                    if u == t:
                        reach_t = True
                    if self.black[u] == cur_black:
                        same += 1
                    else:
                        other += 1
        if not reach_t:
            return -1
        if self.black[t] == cur_black:
            # path c,o,c,...,c: k+1 cells of colour c and k of the other
            return 2 * min(same - 1, other) + 1
        # path c,o,...,o: k cells of each colour
        return 2 * min(same, other)

    def _dfs_st(self, cur, visited, length, path, t, target):
        self.nodes += 1
        if self.time_limit and (self.nodes & 4095) == 0:
            if time.perf_counter() - self.t0 > self.time_limit:
                raise Timeout
        if cur == t:
            if length > self.best_len:
                self.best_len = length
                self.best_path = list(path)
            return self.best_len >= target
        b = self._st_bound(cur, visited, t)
        if b < 0 or length - 1 + b <= self.best_len:
            return False
        for u in self.adj[cur]:
            if not (visited >> u) & 1:
                path.append(u)
                if self._dfs_st(u, visited | (1 << u), length + 1, path, t, target):
                    return True
                path.pop()
        return False

    def longest_st(self, s_cell, t_cell):
        """Longest s-t path. Returns (length, path_cells, bound)."""
        self.t0 = time.perf_counter()
        self.best_len, self.best_path = 0, []
        s, t = self.index[s_cell], self.index[t_cell]
        target = self._st_bound(s, 0, t)
        self._dfs_st(s, 1 << s, 1, [s], t, target)
        return self.best_len, [self.cells[i] for i in self.best_path], target


def brute_force_st(W, H1, w, H2, left, s_cell, t_cell):
    """Plain exhaustive s-t search with no pruning. Only for tiny graphs."""
    cells, index, adj = build(W, H1, w, H2, left)
    s, t = index[s_cell], index[t_cell]
    best = [0]

    def go(cur, visited, length):
        if cur == t:
            best[0] = max(best[0], length)
            return
        for u in adj[cur]:
            if not (visited >> u) & 1:
                go(u, visited | (1 << u), length + 1)

    go(s, 1 << s, 1)
    return best[0]


def brute_force_free(W, H1, w, H2, left):
    """Plain exhaustive search with no pruning. Only for tiny graphs."""
    cells, _, adj = build(W, H1, w, H2, left)
    best = [0]

    def go(cur, visited, length):
        best[0] = max(best[0], length)
        for u in adj[cur]:
            if not (visited >> u) & 1:
                go(u, visited | (1 << u), length + 1)

    for s in range(len(cells)):
        go(s, 1 << s, 1)
    return best[0]
