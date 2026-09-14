#!/usr/bin/env python3
"""Render each unique plywood panel outline as a dimensioned TikZ figure.

Input:  ply_outlines.json — top-face outlines of every 3/8 in body in the Fusion
        model, harvested over the Fusion MCP (coordinates in inches relative to
        each panel's own corner).
Output: ply_patterns.tex — \\input by cut_list.tex.

    ./ply_patterns.py            # regenerate ply_patterns.tex
"""
import json, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SC = 0.105  # cm per inch

def frac(v):
    v = round(v * 8) / 8; w = int(v); f = v - w
    m = {0: '', 0.125: '⅛', 0.25: '¼', 0.375: '⅜', 0.5: '½', 0.625: '⅝', 0.75: '¾', 0.875: '⅞'}
    return (str(w) if (w or not f) else '') + m[f]

def notches(poly, d):
    """Horizontal polygon edges strictly inside the panel are notch bottoms.
    An L-shaped cut shows up twice (two inner edges) — keep the deeper one."""
    found = {}
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if y1 == y2 and 0 < y1 < d:
            lo, hi = sorted((x1, x2))
            side = 'front' if y1 < d / 2 else 'back'
            depth = y1 if side == 'front' else d - y1
            key = (side, lo, hi - lo)
            found[key] = max(found.get(key, 0), depth)
    return sorted(((s, x, w, dp) for (s, x, w), dp in found.items()), key=lambda t: (t[0] != 'front', t[1]))

sheets = json.load(open(os.path.join(HERE, 'ply_outlines.json')))
T = lambda poly: tuple(tuple(p) for p in poly)
shapes = OrderedDict()
for s in sheets:
    outer = T([l for l in s['loops'] if l['outer']][0]['poly'])
    shapes.setdefault((s['w'], s['d'], outer), []).append(s)

items = []
for (w, d, outer), ss in shapes.items():
    ss = sorted(ss, key=lambda s: (s['z'], s['x']))
    items.append(dict(w=w, d=d, outer=outer, n=len(ss), name=ss[0]['comp'],
                      where=[(s['x'], s['z']) for s in ss], notch=notches(outer, d)))
items.sort(key=lambda it: (-it['w'], it['name']))

out = ["% generated from ply_outlines.json by ply_patterns.py — do not hand-edit\n"]
for it in items:
    w, d = it['w'], it['d']
    short = it['name'].replace('Ply 3/8 x ', '').replace(' notch ', ' · notch ')
    where = ' · '.join(f"z\\,{frac(z)} @ x\\,{frac(x)}" for x, z in it['where'])
    pts = ' -- '.join(f"({x},{y})" for x, y in it['outer'])
    out.append(r"\begin{minipage}[t]{0.33\textwidth}\centering" "\n")
    out.append(r"{\small\bfseries " + short + r"}\quad{\footnotesize\textcolor{ink2}{×" + str(it['n']) + r"}}\\[2pt]" "\n")
    out.append(f"\\begin{{tikzpicture}}[x={SC}cm,y={SC}cm,baseline]\n")
    out.append(f"  \\fill[ply] {pts} -- cycle;\n  \\draw[ink,line width=0.5pt] {pts} -- cycle;\n")
    out.append(f"  \\draw[ink2,|-|,line width=0.3pt] (0,-3.2) -- ({w},-3.2) node[midway,below,font=\\scriptsize\\ttfamily,text=ink] {{{frac(w)}}};\n")
    out.append(f"  \\draw[ink2,|-|,line width=0.3pt] ({w}+3.2,0) -- ({w}+3.2,{d}) node[midway,right,font=\\scriptsize\\ttfamily,text=ink] {{{frac(d)}}};\n")
    for side, x0, nw, dp in it['notch']:
        y = -1.3 if side == 'front' else d + 1.3
        anchor = 'above' if side == 'back' else 'below'
        out.append(f"  \\node[font=\\tiny\\ttfamily,text=ink,{anchor}=-2pt] at ({x0 + nw / 2},{y}) {{{frac(x0)}\\,+\\,{frac(nw)}}};\n")
    depths = sorted({dp for _, _, _, dp in it['notch']})
    if depths:
        out.append(f"  \\node[font=\\tiny,text=ink2] at ({w / 2},{d / 2}) {{notches {' / '.join(frac(dp) for dp in depths)} in deep}};\n")
    out.append("\\end{tikzpicture}\\\\[1pt]\n")
    out.append(r"{\scriptsize\textcolor{ink2}{" + where + r"}}" "\n")
    out.append("\\end{minipage}\n")
open(os.path.join(HERE, 'ply_patterns.tex'), 'w').write(''.join(out))
print(len(items), 'patterns ->', os.path.join(HERE, 'ply_patterns.tex'))
