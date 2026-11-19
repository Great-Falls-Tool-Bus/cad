#!/usr/bin/env -S uv run --quiet --with scipy --with numpy python
"""Cutting-stock optimizer for the port-side shelves cut list.

    ./cutstock.py          # 8 ft stock only (default)
    ./cutstock.py --all    # compare 8/10/12/16 ft and mixed stock
    ./cutstock.py --json   # machine-readable plan
    ./cutstock.py --three-up  # three shelves up instead of four

Exact ILP over every maximal cut pattern that fits a board, 1/8 in kerf,
minimising total purchased length. Cut demands are the part counts from
the Fusion model (see cut_list.tex).
"""
import json, sys
from collections import Counter
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
KERF=0.125
STOCK={96:8,120:10,144:12,192:16}

def patterns(lengths, stock):
    """Return patterns that fit the stock and leave no room for another cut."""
    out=set()
    def rec(i, cur, used):
        if i==len(lengths):
            out.add(tuple(cur)); return
        L=lengths[i]
        maxn = 0
        earlier_cuts = sum(cur)
        while used + (maxn + 1) * L + KERF * (earlier_cuts + maxn) <= stock + 1e-9:
            maxn += 1
        for n in range(maxn,-1,-1):
            rec(i+1, cur+[n], used+n*L)
    rec(0,[],0)
    res = []
    for p in out:
        count = sum(p)
        if count == 0:
            continue
        used = sum(n * L for n, L in zip(p, lengths)) + KERF * (count - 1)
        if all(used + L + KERF > stock + 1e-9 for L in lengths):
            res.append(p)
    return res

def solve(cuts, stocks, objective='length'):
    lengths=sorted(cuts, reverse=True); demand=np.array([cuts[L] for L in lengths])
    cols=[]; costs=[]; meta=[]
    for s in stocks:
        for p in patterns(lengths, s):
            cols.append(p); meta.append(s)
            costs.append(s if objective=='length' else 1)
    A=np.array(cols).T  # rows=lengths, cols=patterns
    c=np.array(costs,dtype=float)
    res=milp(c, constraints=LinearConstraint(A, lb=demand, ub=np.inf), integrality=np.ones(len(c)), bounds=Bounds(0,np.inf))
    x=np.round(res.x).astype(int)
    plan=[]
    for i,n in enumerate(x):
        if n>0: plan.append((meta[i], {L:k for L,k in zip(lengths,cols[i]) if k}, int(n)))
    return plan

def show(name, cuts, stocks):
    plan=solve(cuts, stocks)
    total=sum(s*n for s,p,n in plan); boards=sum(n for s,p,n in plan)
    used=sum(L*k for L,k in cuts.items())
    buy=Counter()
    for s,p,n in plan: buy[STOCK[s]]+=n
    print(f"\n{name} | allowed {[STOCK[s] for s in stocks]} ft -> buy {dict(sorted(buy.items()))} = {boards} boards, {total/12:.0f} lf, waste {(total-used)/total*100:.1f}%")
    for s,p,n in sorted(plan, key=lambda t:(-t[0], sorted(t[1].items(), reverse=True))):
        cutstr=' + '.join(f"{L:g}" + (f"×{k}" if k>1 else '') for L,k in sorted(p.items(), reverse=True))
        off=s-sum(L*k for L,k in p.items())-KERF*(sum(p.values())-1)
        print(f"   {n:2d} × {STOCK[s]}ft : {cutstr}   (offcut {off:.2f}\")")
    return {"buy":dict(buy),"boards":boards,"lf":total/12,"waste_pct":round((total-used)/total*100,1),"plan":[(STOCK[s],p,n) for s,p,n in plan]}

cuts_2x4 = {29.0:52, 31.0:2, 72.0:16}
cuts_2x6 = {72.0:2, 62.5:6, 50.5:2, 30.5:4, 25.0:2, 18.5:2}
if '--three-up' in sys.argv:
    # Removing the two z78 frames removes four rails and ten cross members.
    cuts_2x4 = {29.0:42, 31.0:2, 72.0:12}
out={}
# The local yard carries 8 ft stock.
OPTIONS = [[96]] if '--all' not in sys.argv else [[96],[120],[144],[192],[96,120],[96,120,144],[96,120,144,192]]
for name,cuts in [("2x4",cuts_2x4),("2x6",cuts_2x6)]:
    print("="*72); print(name, "cuts:", cuts, f"= {sum(L*n for L,n in cuts.items())/12:.1f} lf net")
    out[name]={}
    for stocks in OPTIONS:
        key='+'.join(str(STOCK[s]) for s in stocks)
        out[name][key]=show(name, cuts, stocks)
if '--json' in sys.argv: json.dump(out, sys.stdout, indent=1)
