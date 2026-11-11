from itertools import product
from tgraph import build
from exact import Solver
def bf_from(adj, s):
    best=[0]
    def go(c,v,l):
        best[0]=max(best[0],l)
        for u in adj[c]:
            if not (v>>u)&1: go(u,v|(1<<u),l+1)
    go(s,1<<s,1); return best[0]
bad=n_=0
for W,H1,H2 in product(range(3,6),range(1,3),range(1,4)):
    for w in range(1,W-1):
        for left in range(1,W-w):
            cells,_,adj=build(W,H1,w,H2,left)
            if len(cells)>15: continue
            for i,c in enumerate(cells):
                L,_=Solver(W,H1,w,H2,left).longest_from(c)
                n_+=1
                if L!=bf_from(adj,i): bad+=1
print("start checks",n_,"mismatches",bad)
