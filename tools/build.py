"""Simulate every antenne/*/antenna.nec and write a static gallery to site/."""
import cmath
import html
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import markdown
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import nec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "antenne"
OUT = ROOT / "site"
DOCS = ROOT / "docs"
GUIDE_MD = DOCS / "guida.md"
GUIDE = "guida"                    # cartella della guida sotto site/
F0 = 869.618                       # preset MeshCore ITA
SITE = "https://meshcore-ita.github.io/"   # sito principale della community
F0_IT = "869,618"                  # stesso valore, formato italiano (virgola) per i testi
BAND = (869.4, 869.65)             # sub-banda 500 mW ERP
ERP_MAX = 27.0                     # dBm, 500 mW ERP
TX_CAP = 30.0                      # dBm, limite tipico di un modulo LoRa
SWEEP = np.arange(855.0, 885.01, 1.0)
SWEEP_IT = f"{SWEEP[0]:g}–{SWEEP[-1]:g}"
MOUNTS = ("Verticale", "Orizzontale")
PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")

CSS = """
@font-face{font-family:Geist;src:url(ROOT/fonts/geist-300-700-latin.woff2) format('woff2');font-weight:300 700;font-display:swap}
@font-face{font-family:'JetBrains Mono';src:url(ROOT/fonts/jetbrains-mono-400-latin.woff2) format('woff2');font-display:swap}
:root{--bg:#000;--fg:#fafafa;--muted:#adadad;--dim:#7d7d7d;--line:rgba(255,255,255,.10);
--line-strong:rgba(255,255,255,.22);--accent:#22c55e;--accent-2:#e11d48;--panel:rgba(255,255,255,.03);
--sans:Geist,ui-sans-serif,system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace}
*{box-sizing:border-box}
html{background:var(--bg);color:var(--fg);color-scheme:dark}
body{font:16px/1.6 var(--sans);max-width:1180px;margin:0 auto;padding:2.5rem clamp(1.25rem,4vw,3rem) 4rem}
a{color:var(--fg);text-decoration-color:var(--accent);text-underline-offset:3px}a:hover{color:var(--accent)}
h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.1;letter-spacing:-.03em;font-weight:600;margin:.4rem 0 1rem}
h2{font-size:1.4rem;letter-spacing:-.02em;font-weight:600;margin:3rem 0 1rem}
.eyebrow{font:500 .75rem var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--accent)}
.eyebrow a{color:inherit;text-decoration:none}.eyebrow a:hover{text-decoration:underline}
.lede{color:var(--muted);font-size:1.1rem;max-width:48rem}
.back{font:.85rem var(--mono);color:var(--muted);text-decoration:none}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:2rem 0}
.stat{background:var(--bg);padding:1rem 1.2rem}.stat b{display:block;font:600 1.6rem var(--mono);letter-spacing:-.02em;white-space:nowrap}
.stat b.sm{font-size:1.15rem;line-height:2.1rem}
.stat span{font:.72rem var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--dim)}
.stat b.ok{color:var(--accent)}.stat b.warn{color:#facc15}.stat b.bad{color:var(--accent-2)}
.stat span a{color:inherit;text-decoration:none;border-bottom:1px dotted var(--dim)}
.stat span a:hover{color:var(--accent);border-color:var(--accent)}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border-bottom:1px solid var(--line);padding:.7rem .6rem;text-align:left}th{font:500 .75rem var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
td.n{text-align:right;font:1rem var(--mono)}tr:hover td{background:var(--panel)}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.tag{font:.75rem var(--mono);border:1px solid var(--line-strong);border-radius:999px;padding:.15rem .7rem;color:var(--muted)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1rem}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1rem}
figure{margin:0}figcaption{font-size:.82rem;color:var(--dim);margin-top:.5rem}
figcaption a{color:var(--accent);text-decoration-color:var(--accent)}
svg{width:100%;height:auto;display:block}svg text{fill:var(--dim);font-family:var(--mono)}
.photos{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1rem}
img.photo{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;border-radius:10px;border:1px solid var(--line);cursor:zoom-in;transition:border-color .15s}
.photos a:hover img.photo,.photos a:focus-visible img.photo{border-color:var(--accent)}
dialog.lightbox{border:0;padding:0;background:transparent;max-width:100vw;max-height:100vh;width:100vw;height:100vh;color:var(--text,#eee)}
dialog.lightbox::backdrop{background:rgba(0,0,0,.92)}
.lightbox figure{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3.5rem 4rem 1.5rem}
.lightbox img{max-width:100%;max-height:calc(100vh - 9rem);object-fit:contain;border-radius:6px}
.lightbox figcaption{margin-top:.8rem;text-align:center;max-width:44rem}
.lightbox button{position:absolute;font:1.6rem var(--mono);line-height:1;color:var(--muted);background:rgba(0,0,0,.55);border:1px solid var(--line-strong);border-radius:999px;width:2.8rem;height:2.8rem;cursor:pointer}
.lightbox button:hover{color:#fff}.lightbox .lb-close{top:1rem;right:1rem}
.lightbox .lb-prev{left:.8rem;top:50%}.lightbox .lb-next{right:.8rem;top:50%}
.v3d{margin:1.5rem 0 0}
.v3d:fullscreen{display:flex;flex-direction:column;gap:.6rem;padding:.8rem;background:var(--bg);overflow:auto}
.v3d:fullscreen .viewer{flex:1;height:auto;min-height:0;border-radius:10px}
.vtools{display:flex;flex-wrap:wrap;gap:.45rem .9rem;margin:0 0 .6rem}
.vgrp{display:flex;flex-wrap:wrap;gap:.3rem}
.vtools button{font:.74rem/1.3 var(--mono);color:var(--muted);padding:.34rem .7rem;border:1px solid var(--line-strong);background:rgba(255,255,255,.04);border-radius:999px;cursor:pointer}
.vtools button:hover{color:var(--fg);border-color:var(--muted)}
.vtools button[aria-pressed=true]{color:#000;background:var(--accent);border-color:var(--accent)}
.vtools button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.vtools button:disabled{opacity:.4;cursor:default}
.viewer{position:relative;height:min(70vh,36rem);border:1px solid var(--line);border-radius:14px;overflow:hidden;
background:radial-gradient(ellipse at 50% 40%,#0d1f14 0%,#050806 55%,#000 100%);touch-action:none;cursor:grab}
.viewer canvas{width:100%;height:100%;display:block}
.vlabels{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.vlab{position:absolute;left:0;top:0;font:.68rem/1 var(--mono);color:#e5e7eb;white-space:nowrap;text-shadow:0 0 4px #000,0 0 2px #000;will-change:transform}
.vlab.dim{color:var(--dim)}.vlab.lobe{color:#fff;background:rgba(0,0,0,.6);border:1px solid var(--line-strong);padding:.2rem .45rem;border-radius:6px}
.vtip{position:absolute;left:0;top:0;z-index:3;pointer-events:none;font:.72rem/1.5 var(--mono);color:var(--muted);background:rgba(10,12,11,.92);border:1px solid var(--line-strong);border-radius:8px;padding:.45rem .65rem;max-width:15rem;box-shadow:0 4px 18px rgba(0,0,0,.5)}
.vtip b{display:block;color:var(--fg);font-weight:500}.vtip i{display:inline-block;width:.6rem;height:.6rem;border-radius:50%;margin-right:.4rem;vertical-align:-.05rem}
.vtip small{display:block;color:var(--dim);font-size:.66rem}
.vleg{position:absolute;right:.8rem;bottom:.8rem;display:flex;flex-direction:column;gap:.4rem;align-items:flex-end;font:.66rem var(--mono);color:var(--muted);pointer-events:none}
.vleg div{display:flex;align-items:center;gap:.45rem}.vleg b{font-weight:500;color:var(--dim)}
.vleg i{display:block;width:7rem;height:.4rem;border-radius:99px}
.vfail{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:1.5rem;color:var(--muted);margin:0}
.viewer[hidden],.vtip[hidden],.vfail[hidden],.vleg[hidden],.vleg div[hidden]{display:none}
@media (max-width:600px){.vleg i{width:5rem}.vlab{font-size:.62rem}.vtools{gap:.35rem .6rem}.vtools button{font-size:.7rem;padding:.3rem .55rem}}
.note{font-size:.85rem;color:var(--dim)}code{font-family:var(--mono);background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:0 .3rem}
.prose{max-width:48rem;color:var(--muted)}.prose strong{color:var(--fg)}
.btn{display:inline-block;font:500 .85rem var(--mono);color:#000;background:var(--accent);padding:.55rem 1rem;border-radius:999px;text-decoration:none}
.btn:hover{color:#000;filter:brightness(1.1)}
.guide-note{font-size:.9rem;color:var(--muted);margin:.6rem 0 1.6rem}
.guide-note a{color:var(--accent)}
.guide-wrap{display:flex;gap:2.5rem;align-items:flex-start;margin-top:1.5rem}
.guide-toc{flex:0 0 14rem;position:sticky;top:1.2rem;font-size:.82rem;line-height:1.8;border-right:1px solid var(--line);padding-right:1.2rem;max-height:calc(100vh - 2.4rem);overflow-y:auto}
.guide-toc ul{list-style:none;margin:0;padding:0}
.guide-toc ul ul{padding-left:1rem}
.guide-toc a{color:var(--muted);text-decoration:none}
.guide-toc a:hover{color:var(--accent)}
.guide-content{min-width:0;flex:1 1 auto;max-width:44rem}
.guide-content h2{scroll-margin-top:1.2rem}
@media (max-width:860px){.guide-wrap{flex-direction:column}.guide-toc{position:static;max-height:none;border-right:none;border-bottom:1px solid var(--line);padding:0 0 1rem;width:100%}}
.insights{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin:1.5rem 0 2.5rem}
.insight{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.2rem}
.insight h3{margin:0 0 .5rem;font-size:.95rem}
.insight h3 a{color:var(--fg);text-decoration-color:var(--accent)}
.insight p{margin:0;font-size:.92rem;color:var(--muted)}
.insight p.warn{color:#facc15}
.insight table.erp{margin:.8rem 0 .3rem;font-size:.85rem}
.insight table.erp th,.insight table.erp td{padding:.35rem .5rem}
.insight .note{margin-top:.5rem}
.btn.alt{background:transparent;color:var(--fg);border:1px solid var(--line-strong)}
.btn.alt:hover{color:var(--accent);border-color:var(--accent);filter:none}
button.btn{cursor:pointer;border:0}button.btn.alt{border:1px solid var(--line-strong)}
.files{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem}.copy-msg{font:.8rem var(--mono);color:var(--accent)}
.nec-key{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font:.72rem var(--mono);color:var(--dim);margin:.8rem 0}
.k{font-family:var(--mono);font-weight:600}
.k-com{color:var(--dim);font-weight:400}.k-sy{color:#38bdf8}.k-geo{color:var(--accent)}.k-src{color:#fb923c}.k-ctl{color:#c084fc}.k-ign{color:#7d7d7d;text-decoration:line-through;text-decoration-color:rgba(255,255,255,.3)}
.t-c{color:var(--dim);font-style:italic}.t-n{color:#facc15}.t-def{color:#38bdf8;font-weight:600}.t-var{color:#a5d8ff}.t-fn{color:#c4b5fd}.t-op{color:var(--dim)}
.nec{border:1px solid var(--line);border-radius:12px;background:var(--panel);overflow:hidden;font:.8rem/1.6 var(--mono);padding:.4rem 0}
.nl{display:grid;grid-template-columns:3.6rem minmax(0,1.3fr) minmax(0,1fr);gap:0 1rem;align-items:baseline;padding:.1rem 1rem .1rem 0;border-left:3px solid transparent;scroll-margin-top:30vh}
.nl:hover{background:rgba(255,255,255,.035)}
.nl.c-geo,.nl.c-src{border-left-color:rgba(255,255,255,.12)}
.nl.c-geo[data-tag]:hover,.nl.c-src[data-tag]:hover{cursor:pointer}
.nl.c-blank{line-height:.7rem}
.nl .ln{text-align:right;padding-right:.3rem;color:var(--dim);text-decoration:none;user-select:none}
.nl .ln:hover{color:var(--accent)}
.nl .src{background:none;border:0;padding:0;font:inherit;color:var(--fg);white-space:pre-wrap;overflow-wrap:anywhere;tab-size:4}
.nl .why{font:.82rem/1.45 var(--sans);color:var(--muted)}
.nl.c-com .why{font-size:.74rem;color:var(--dim)}
.nl .to3d{font:.7rem var(--mono);margin-left:.3rem;color:var(--accent);text-decoration:none;white-space:nowrap;opacity:0}
.nl:hover .to3d,.nl:focus-within .to3d,.nl:focus .to3d{opacity:1}
.nl:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.nl.hl{background:rgba(103,232,249,.10);border-left-color:#67e8f9}
.nl.sel{background:rgba(34,197,94,.13);border-left-color:var(--accent)}
.nl.flash{animation:nlflash 1.8s ease-out}
@keyframes nlflash{0%,30%{background:rgba(34,197,94,.45)}100%{background:rgba(34,197,94,.13)}}
.nec details.run>summary{cursor:pointer;list-style:none;padding:.45rem 1rem .45rem 4.6rem;font:.78rem var(--mono);color:var(--accent);background:rgba(34,197,94,.06);border-block:1px dashed var(--line-strong)}
.nec details.run>summary::-webkit-details-marker{display:none}
.nec details.run>summary::before{content:"▸ "}.nec details.run[open]>summary::before{content:"▾ "}
.nec details.run>summary:hover{background:rgba(34,197,94,.12)}
@media (max-width:820px){.nl{grid-template-columns:2.6rem minmax(0,1fr)}.nl .why{grid-column:2;padding-bottom:.4rem}
.nec details.run>summary{padding-left:3.2rem}.nl .to3d{opacity:1}}
@media (prefers-reduced-motion:reduce){.nl.flash{animation:none}}
details.help{margin:.8rem 0 0;border:1px solid var(--line);border-radius:10px;padding:.2rem .9rem}
details.help summary{cursor:pointer;padding:.7rem 0;font:500 .85rem var(--mono);color:var(--muted)}
details.help[open] summary{color:var(--fg)}
details.help .help-body p{color:var(--muted);font-size:.9rem;margin:.6rem 0}
"""


PAGES = []                         # (url, lastmod) per la sitemap


def lastmod(*paths):
    """Data dell'ultimo commit che tocca i percorsi (serve fetch-depth 0 in CI); oggi se non disponibile."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *map(str, paths)],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return out or date.today().isoformat()
    except (OSError, subprocess.CalledProcessError):
        return date.today().isoformat()


def page(title, body, root="..", head="", url=None, desc="", mod=None):
    meta = ""
    if url:
        PAGES.append((url, mod or date.today().isoformat()))
        meta += f"<link rel=canonical href='{url}'>"
    if desc:
        meta += f"<meta name=description content='{html.escape(desc, quote=True)}'>"
    return (f"<!doctype html><html lang=it><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>{meta}"
            f"<title>{html.escape(title)} · MeshCore ITA</title><style>{CSS.replace('ROOT', root)}</style>{head}"
            f"<body>{body}</body></html>")


def simulate(deck):
    zs = [nec.impedance(deck, f) for f in SWEEP]
    z0 = nec.impedance(deck, F0)
    th, ph, g, cur = nec.far_field(deck, F0)
    i, j = np.unravel_index(np.argmax(g), g.shape)
    gmax = float(g[i, j])
    step = int(th[1] - th[0])
    # direzione opposta: (180-theta, phi+180); sopra il suolo resta nello stesso emisfero
    bi = min(len(th) - 1, int(round((180 - th[i]) / step))) if not nec.has_ground(deck) else i
    bj = (j + len(ph) // 2) % len(ph)
    fb = gmax - float(g[bi, bj])
    k = int(np.argmin([nec.swr(z) for z in zs]))
    return dict(z=z0, swr=nec.swr(z0), gmax=gmax, fb=fb, theta=int(th[i]), phi=int(ph[j]),
                fres=float(SWEEP[k]), sweep=zs, th=th, ph=ph, g=g, imax=i, jmax=j, currents=cur)


def svg_line(xs, series, ylabel, ymin=None, ymax=None, mark=None):
    W, H, L, R, T, B = 320, 200, 42, 10, 10, 28
    ys = np.concatenate([s for s, _ in series])
    lo = ymin if ymin is not None else float(np.floor(ys.min() / 10) * 10)
    hi = ymax if ymax is not None else float(np.ceil(ys.max() / 10) * 10)
    hi = hi if hi > lo else lo + 1
    X = lambda x: L + (x - xs[0]) / (xs[-1] - xs[0]) * (W - L - R)
    Y = lambda y: T + (1 - (min(max(y, lo), hi) - lo) / (hi - lo)) * (H - T - B)
    out = [f"<svg viewBox='0 0 {W} {H}' role=img aria-label='{ylabel}'>"]
    if mark:
        out.append(f"<rect x='{X(mark[0]):.1f}' y='{T}' width='{max(X(mark[1]) - X(mark[0]), 1.5):.1f}' "
                   f"height='{H - T - B}' fill='#22c55e' opacity='.14'/>")
    for t in np.linspace(lo, hi, 5):
        out.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' stroke='rgba(255,255,255,.08)'/>"
                   f"<text x='{L - 4}' y='{Y(t) + 4:.1f}' font-size='10' text-anchor='end'>{t:g}</text>")
    for t in xs[::10]:
        out.append(f"<text x='{X(t):.1f}' y='{H - 10}' font-size='10' text-anchor='middle'>{t:g}</text>")
    for s, color in series:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(xs, s))
        out.append(f"<polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2'/>")
    out.append("</svg>")
    return "".join(out)


def svg_polar(angles_deg, gains, gmax, zero_at_top=True):
    W = 240; C = W / 2; Rr = C - 14; floor = -30.0
    rad = lambda v: Rr * (max(v - gmax, floor) - floor) / -floor
    out = [f"<svg viewBox='0 0 {W} {W}' role=img aria-label='diagramma polare'>"]
    for db in (0, -10, -20):
        out.append(f"<circle cx='{C}' cy='{C}' r='{rad(gmax + db):.1f}' fill='none' stroke='rgba(255,255,255,.14)'/>"
                   f"<text x='{C + 2}' y='{C - rad(gmax + db) + 10:.1f}' font-size='9'>{db}</text>")
    out.append(f"<line x1='{C}' x2='{C}' y1='14' y2='{W - 14}' stroke='rgba(255,255,255,.08)'/>"
               f"<line y1='{C}' y2='{C}' x1='14' x2='{W - 14}' stroke='rgba(255,255,255,.08)'/>")
    pts = []
    for a, v in zip(angles_deg, gains):
        t = math.radians(a)
        r = rad(v)
        x, y = (C + r * math.sin(t), C - r * math.cos(t)) if zero_at_top else (C + r * math.cos(t), C - r * math.sin(t))
        pts.append(f"{x:.1f},{y:.1f}")
    out.append(f"<polygon points='{' '.join(pts)}' fill='#22c55e' fill-opacity='.14' stroke='#22c55e' stroke-width='2'/>")
    out.append("</svg>")
    return "".join(out)


LIGHTBOX = (
    "<dialog class=lightbox aria-label='Foto ingrandita'><figure><img alt=''><figcaption></figcaption></figure>"
    "<button class=lb-close aria-label=Chiudi>&times;</button>"
    "<button class=lb-prev aria-label=Precedente>&lsaquo;</button>"
    "<button class=lb-next aria-label=Successiva>&rsaquo;</button></dialog>"
    "<script>(()=>{const d=document.querySelector('dialog.lightbox'),L=[...document.querySelectorAll('a[data-lb]')],"
    "im=d.querySelector('img'),cp=d.querySelector('figcaption');let i=0;"
    "const show=n=>{i=(n+L.length)%L.length;im.src=L[i].href;im.alt=cp.textContent=L[i].firstChild.alt};"
    "L.forEach((a,n)=>a.addEventListener('click',e=>{e.preventDefault();show(n);d.showModal()}));"
    "d.querySelector('.lb-close').onclick=()=>d.close();"
    "d.querySelector('.lb-prev').onclick=()=>show(i-1);d.querySelector('.lb-next').onclick=()=>show(i+1);"
    "d.addEventListener('click',e=>{if(e.target===d||e.target.tagName==='FIGURE')d.close()});"
    "d.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)});"
    "})()</script>")
IMPORTMAP = ("<script type=importmap>{\"imports\":{\"three\":\"../vendor/three/three.module.min.js\","
             "\"three/addons/\":\"../vendor/three/\"}}</script>")


def viewer_data(deck, r):
    """Dati per viewer.js. Fili: [x1, y1, z1, x2, y2, z2, raggio, tag, segmenti, riga del GW];
    cur: [ampiezza normalizzata 0..1, fase in gradi] per ogni segmento, nell'ordine di NEC
    (i segmenti di un filo sono uguali, il viewer li ricostruisce dai fili)."""
    p = lambda v: [round(float(c), 5) for c in v]
    cur = r["currents"]
    peak = float(np.abs(cur).max()) or 1.0
    return dict(
        th=r["th"].tolist(), ph=r["ph"].tolist(), g=np.round(r["g"], 2).tolist(), gmax=round(r["gmax"], 2),
        theta=r["theta"], phi=r["phi"], ground=nec.has_ground(deck), f0=F0,
        wires=[[*p(w.p1), *p(w.p2), round(w.r, 6), w.tag, w.segs, w.line] for w in deck.wires],
        cur=[[round(abs(i) / peak, 3), round(math.degrees(cmath.phase(i)))] for i in cur],
        feed=p(nec.segment_center(deck, deck.ex[1], deck.ex[2])),
        nets=[[*p(nec.segment_center(deck, n[1], n[2])), *p(nec.segment_center(deck, n[3], n[4])), n[0]]
              for n in deck.networks])


def viewer(deck, r):
    data = viewer_data(deck, r)
    help_body = (
        "<div class=help-body>"
        "<p><b>Diagramma.</b> Il raggio della superficie colorata, in ogni direzione, è proporzionale al guadagno: "
        "più si allontana dal centro, più energia irradia l'antenna verso quel punto. I colori seguono la legenda "
        f"in basso a destra, dal blu (−30 dB sotto il massimo) al rosso ({r['gmax']:.1f} dBi, il massimo di questo "
        "modello). I lobi sono le \"bolle\": il lobo principale è dove punta l'antenna (la freccia bianca, con il "
        "guadagno), gli altri sono energia irradiata altrove — <a href='../guida/#diagramma'>vedi il diagramma di "
        "irradiazione</a>. Passa il mouse (o tocca) sulla superficie per leggere θ, φ, guadagno e dB sotto il massimo.</p>"
        "<p><b>Scala.</b> <em>dB</em> comprime la dinamica e mostra anche i lobi deboli; <em>Lineare</em> usa la "
        "potenza: i lobi secondari quasi spariscono e resta il fascio principale. La griglia sul piano dell'orizzonte "
        "ha raggi ogni 30° e cerchi con i livelli indicati.</p>"
        "<p><b>Correnti.</b> Ogni segmento dei fili è colorato in base all'intensità della corrente: grigio-blu quasi "
        "zero, arancio e giallo massima. <em>Fase</em> anima la corrente nel tempo: i tratti sfasati pulsano in "
        "momenti diversi. Il punto verde è l'alimentazione, dove si collega il cavo; le linee tratteggiate, se "
        "presenti, sono linee di trasmissione.</p>"
        "<p><b>Tagli 2D.</b> I due anelli sulla superficie sono i tagli dei grafici qui sotto: il taglio conico "
        "(azimut, a θ fisso) e quello verticale (elevazione, nel piano del lobo principale).</p>"
        "<p><b>Antenna e file NEC.</b> Passa sopra un filo per vedere numero di filo, riga e corrente; un clic ti "
        "porta alla sua riga nel file NEC spiegato più in basso, e viceversa passando o cliccando sulle righe GW o EX "
        "il filo si illumina nel 3D. La geometria è ingrandita per stare dentro il diagramma.</p>"
        "<p><b>Comandi.</b> Trascina per ruotare, rotella o pizzico per lo zoom, tasto destro per spostare. "
        "I pulsanti cambiano punto di vista (di fronte e di lato sono rispetto al lobo principale), fermano la "
        "rotazione, azzerano la vista o aprono lo schermo intero.</p>"
        "</div>")

    def btn(label, **attrs):
        a = "".join(f" {k.replace('_', '-')}={v}" for k, v in attrs.items())
        return f"<button type=button{a}>{label}</button>"

    tools = (
        "<div class=vtools role=toolbar aria-label='Controlli della vista 3D'>"
        "<div class=vgrp role=group aria-label='Cosa mostrare'>"
        + btn("Tutto", data_mode="both", aria_pressed="true") + btn("Diagramma", data_mode="pattern", aria_pressed="false")
        + btn("Antenna", data_mode="geom", aria_pressed="false") + "</div>"
        "<div class=vgrp role=group aria-label='Punto di vista'>"
        + btn("3D", data_view="iso") + btn("Dall'alto", data_view="top") + btn("Di fronte", data_view="front")
        + btn("Di lato", data_view="side") + "</div>"
        "<div class=vgrp role=group aria-label='Scala del diagramma'>"
        + btn("dB", data_scale="db", aria_pressed="true") + btn("Lineare", data_scale="lin", aria_pressed="false") + "</div>"
        "<div class=vgrp role=group aria-label='Opzioni'>"
        + btn("Correnti", data_toggle="cur", aria_pressed="true") + btn("Fase", data_toggle="phase", aria_pressed="false")
        + btn("Tagli 2D", data_toggle="cuts", aria_pressed="false") + btn("Rotazione", data_toggle="rot", aria_pressed="true")
        + "</div>"
        "<div class=vgrp role=group aria-label='Vista'>"
        + btn("Reset", data_act="reset") + btn("Schermo intero", data_act="fs", aria_pressed="false", hidden="") + "</div>"
        "</div>")
    stage = (
        "<div class=viewer id=viewer3d role=group aria-label='Diagramma di irradiazione 3D e geometria dell&apos;antenna'>"
        "<div class=vlabels></div><div class=vtip hidden></div>"
        "<div class=vleg><div id=lg-cur><b>Corrente</b><span>0</span><i></i><span>max</span></div>"
        f"<div id=lg-pat><b>Guadagno</b><span>−30 dB</span><i></i><span>{r['gmax']:.1f} dBi</span></div></div>"
        "<p class=vfail hidden>La vista 3D richiede WebGL, che questo browser non offre o ha disattivato. "
        "I grafici e il file NEC qui sotto funzionano comunque.</p></div>")
    return (f"<div class=v3d id=v3d>{tools}{stage}</div>"
            "<p class=note>Trascina per ruotare, rotella o pizzico per lo zoom. Il punto verde è l'alimentazione; "
            "la geometria è ingrandita per stare dentro il diagramma"
            + (" e il disco è il terreno (l'altezza reale dal suolo non è in scala)" if data["ground"] else "") + ".</p>"
            f"<details class=help><summary>Come leggere la vista 3D</summary>{help_body}</details>"
            f"<script type=application/json id=antenna-data>{json.dumps(data, separators=(',', ':'))}</script>"
            "<script type=module src='../viewer.js'></script>")


def charts(r):
    sw = np.array([min(nec.swr(z), 5.0) for z in r["sweep"]])
    R = np.array([z.real for z in r["sweep"]]); X = np.array([z.imag for z in r["sweep"]])
    th, ph, g, i, j = r["th"], r["ph"], r["g"], r["imax"], r["jmax"]
    # taglio "azimut": tutti i phi alla theta del massimo
    az = svg_polar(ph, g[i, :], r["gmax"])
    # taglio "elevazione": piano verticale che contiene il massimo (phi e phi+180)
    jb = (j + len(ph) // 2) % len(ph)
    ang = list(th) + [360 - t for t in th[::-1]]
    val = list(g[:, j]) + list(g[::-1, jb])
    el = svg_polar(ang, val, r["gmax"])
    return (
        "<div class=charts>"
        f"<figure class=card>{svg_line(SWEEP, [(sw, '#e11d48')], 'ROS', 1, 5, BAND)}<figcaption>"
        f"<a href='../guida/#ros'>ROS</a> su 50 Ω, 855–885 MHz. In verde la sub-banda 869,4–869,65 — "
        "la curva deve toccare il minimo dentro la fascia verde.</figcaption></figure>"
        f"<figure class=card>{svg_line(SWEEP, [(R, '#22c55e'), (X, '#facc15')], 'impedenza', mark=BAND)}<figcaption>"
        f"<a href='../guida/#impedenza'>Impedenza</a>: <span style=color:#22c55e>R</span> e "
        "<span style=color:#facc15>X</span> in Ω — nella fascia verde R deve avvicinarsi a 50 Ω e X a "
        "0.</figcaption></figure>"
        f"<figure class=card>{az}<figcaption>Taglio conico a θ = {r['theta']}°, dB rispetto al massimo — "
        f"quanto è largo il lobo principale girando intorno all'antenna (<a href='../guida/#diagramma'>"
        "diagramma</a>).</figcaption></figure>"
        f"<figure class=card>{el}<figcaption>Taglio verticale a φ = {r['phi']}° (θ = 0 in alto) — "
        "quanto il lobo principale punta verso l'orizzonte o verso il cielo.</figcaption></figure>"
        "</div>")


def fmt_z(z):
    return f"{z.real:.1f} {'+' if z.imag >= 0 else '−'} j{abs(z.imag):.1f} Ω"


def polarization(deck):
    """'Verticale' o 'Orizzontale', dalla direzione del filo che contiene il segmento alimentato."""
    w, _ = nec.segment(deck, deck.ex[1], deck.ex[2])
    dx, dy, dz = (abs(b - a) for a, b in zip(w.p1, w.p2))
    return "Verticale" if dz >= dx and dz >= dy else "Orizzontale"


def check_meta(d, meta):
    """Errori di meta.json: campi obbligatori, montaggio e foto esistenti."""
    errs = [f"manca il campo '{k}'" for k in ("title", "author", "type", "description", "license")
            if not str(meta.get(k, "")).strip()]
    if meta.get("montaggio") not in (None, *MOUNTS):
        errs.append(f"montaggio '{meta['montaggio']}' non valido (ammessi: {', '.join(MOUNTS)})")
    for p in meta.get("photos", []):
        if not p.get("file") or not p.get("alt"):
            errs.append("ogni foto vuole 'file' e 'alt'")
        elif Path(p["file"]).suffix.lower() not in PHOTO_EXT or not (d / p["file"]).is_file():
            errs.append(f"foto '{p['file']}' mancante o di formato non ammesso")
    return errs


def erp_table(dbd):
    rows = []
    for loss in (0, 1, 2):
        raw = ERP_MAX - dbd + loss
        capped = min(raw, TX_CAP)
        star = "*" if raw > TX_CAP else ""
        mw = 10 ** (capped / 10)
        rows.append(f"<tr><td class=n>{loss}</td><td class=n>{capped:.1f}{star}</td><td class=n>{mw:.0f}</td></tr>")
    return "".join(rows)


def insights(deck, r, mounted=None):
    g, fb, swr, z, fres = r["gmax"], r["fb"], r["swr"], r["z"], r["fres"]
    dbd = g - 2.15
    dipole_ratio = 10 ** (dbd / 10)
    rho = abs((z - 50) / (z + 50))
    refl_pct = rho * rho * 100
    mismatch_db = -10 * math.log10(max(1 - rho * rho, 1e-9))
    if swr < 1.5:
        swr_verdict, swr_extra = "ottimo", "."
    elif swr < 2:
        swr_verdict, swr_extra = "accettabile", "."
    else:
        swr_verdict = "da migliorare"
        swr_extra = " — vedi come <a href='../guida/#adattamento'>adattare l'antenna</a>."

    x = z.imag
    if abs(x) < 0.5:
        z_note = "la parte reattiva è quasi zero: qui l'antenna è già in risonanza."
    elif x > 0:
        z_note = ("la reattanza è positiva (induttiva): l'antenna è elettricamente più lunga della risonanza. "
                   f"Per avvicinare la risonanza a {F0_IT} MHz prova ad <strong>accorciare</strong> leggermente i conduttori.")
    else:
        z_note = ("la reattanza è negativa (capacitiva): l'antenna è elettricamente più corta della risonanza. "
                   f"Per avvicinare la risonanza a {F0_IT} MHz prova ad <strong>allungare</strong> leggermente i conduttori.")

    if fb < 3:
        fb_note = (f"{fb:.1f} dB: differenza minima. Su questo asse l'antenna irradia quasi allo stesso modo "
                    "avanti e indietro — di fatto <strong>omnidirezionale</strong>. Il rapporto avanti/dietro ha "
                    "senso solo per antenne direttive.")
    else:
        fb_factor = 10 ** (fb / 10)
        fb_note = (f"{fb:.1f} dB, cioè circa <strong>{fb_factor:.1f} volte</strong> più potenza avanti che "
                    "indietro. Vale solo per antenne direttive: orienta il lato \"avanti\" verso il nodo che vuoi raggiungere.")

    pol = polarization(deck)
    if mounted and mounted != pol:
        pol_note = (f"nel file il filo alimentato è {pol.lower()}, ma l'antenna reale è montata ruotata di 90°: "
                    f"polarizzazione <strong>{mounted.lower()}</strong>. Guadagno, ROS e forma del diagramma "
                    "non cambiano: il diagramma 3D qui sopra va solo immaginato ruotato.")
        pol_cls = "" if mounted == "Verticale" else " warn"
    elif pol == "Verticale":
        pol_note = ("il filo alimentato è prevalentemente verticale (asse z): polarizzazione verticale, la "
                     "stessa di quasi tutti i nodi MeshCore.")
        pol_cls = ""
    else:
        pol_note = ("il filo alimentato è prevalentemente orizzontale: polarizzazione orizzontale. "
                     "<strong>Attenzione</strong>: quasi tutti i nodi MeshCore sono verticali. Incrociare le "
                     "polarizzazioni fa perdere molto segnale: monta l'antenna ruotata di 90° (elementi verticali) "
                     "oppure usala solo se anche l'altro capo è orizzontale.")
        pol_cls = " warn"

    return (
        "<h2>Cosa dicono questi numeri</h2>"
        "<div class=insights>"
        f"<div class=insight><h3><a href='../guida/#guadagno'>Guadagno</a></h3><p>{g:.1f} dBi = "
        f"<a href='../guida/#dbi-dbd'>{dbd:.1f} dBd</a>: nella direzione migliore questa antenna concentra "
        f"circa <strong>{dipole_ratio:.1f} volte</strong> la potenza di un <a href='../guida/#dipolo'>dipolo "
        "a mezz'onda</a> alimentato allo stesso modo.</p></div>"
        f"<div class=insight><h3><a href='../guida/#avanti-dietro'>Avanti/dietro</a></h3><p>{fb_note}</p></div>"
        f"<div class=insight><h3><a href='../guida/#ros'>ROS</a></h3><p>ROS {swr:.2f}: circa "
        f"<strong>{refl_pct:.1f}%</strong> della potenza torna indietro verso il trasmettitore invece di "
        f"irradiare (perdita per disadattamento {mismatch_db:.2f} dB). Verdetto: <strong>{swr_verdict}</strong>"
        f"{swr_extra}</p></div>"
        f"<div class=insight><h3><a href='../guida/#impedenza'>Impedenza</a></h3><p>Z = {fmt_z(z)} a {F0_IT} MHz: "
        f"{z_note} La frequenza di minimo <a href='../guida/#ros'>ROS</a> di questo modello è a "
        f"<strong>{fres:.0f} MHz</strong>.</p></div>"
        f"<div class=insight><h3><a href='../guida/#polarizzazione'>Polarizzazione</a></h3>"
        f"<p class='{pol_cls.strip()}'>{pol}: {pol_note}</p></div>"
        f"<div class=insight><h3><a href='../guida/#erp'>ERP e potenza TX</a></h3>"
        f"<p>In Italia il preset MeshCore limita l'<a href='../guida/#erp'>ERP</a> a "
        f"<strong>{ERP_MAX:.0f} dBm (500 mW)</strong>. Con {dbd:.1f} dBd di guadagno, questa è la potenza "
        "massima da impostare sul trasmettitore (prima del cavo) per restare nel limite:</p>"
        "<table class=erp><tr><th>Perdita cavo</th><th>TX max</th><th>TX max</th></tr>"
        f"<tr><th>dB</th><th>dBm</th><th>mW</th></tr>{erp_table(dbd)}</table>"
        f"<p class=note>* supererebbe {TX_CAP:.0f} dBm: i moduli LoRa non arrivano così in alto (un SX1262, il "
        "più diffuso, si ferma a 22 dBm). Restare entro l'ERP consentito è comunque responsabilità di chi "
        "gestisce il nodo — vedi la <a href='https://meshcore-ita.github.io/normativa/'>normativa</a>.</p></div>"
        "</div>")


NEC_CAT = {"CM": "com", "CE": "com", "SY": "sy",
           "GW": "geo", "GS": "geo", "GE": "geo", "GA": "geo", "GM": "geo", "GR": "geo", "GX": "geo",
           "SP": "geo", "SC": "geo",
           "EX": "src", "LD": "src", "TL": "src", "NT": "src",
           "GN": "ctl", "EK": "ctl", "FR": "ctl", "EN": "ctl"}
NEC_TOKEN = re.compile(r"(?P<id>[A-Za-z_][A-Za-z0-9_]*)|(?P<num>(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)"
                       r"|(?P<ws>\s+)|(?P<op>.)")
NEC_RUN_MIN = 12                   # oltre questa soglia una serie di GW consecutivi si comprime
NEC_RUN_EDGE = 3                   # righe GW lasciate visibili a inizio e fine della serie


def nec_hl(raw, card):
    """Riga NEC in HTML con la sintassi colorata; ogni frammento passa da html.escape."""
    esc = html.escape
    body = raw.lstrip()
    if not body:
        return ""
    if card == "'":
        return f"<span class=t-c>{esc(raw)}</span>"
    lead, mnem, rest = raw[:len(raw) - len(body)], body[:2], body[2:]
    head = f"{esc(lead)}<span class='k k-{NEC_CAT.get(card, 'ign')}'>{esc(mnem)}</span>"
    if card in ("CM", "CE"):
        return head + f"<span class=t-c>{esc(rest)}</span>"
    expr, quote, comment = rest.partition("'")
    out, defining = [], card == "SY"
    for m in NEC_TOKEN.finditer(expr):
        tok = m.group()
        if m.lastgroup == "id":
            kind = ("fn" if tok in nec.FUNCS else "def" if defining else "var")
            if kind == "def":
                defining = False
        elif m.lastgroup == "num":
            kind = "n"
        elif m.lastgroup == "op":
            kind = "op"
            defining = defining or (card == "SY" and tok == ",")
        else:
            kind = ""
        out.append(f"<span class=t-{kind}>{esc(tok)}</span>" if kind else esc(tok))
    if quote:
        out.append(f"<span class=t-c>{esc(quote + comment)}</span>")
    return head + "".join(out)


def nec_row(l, ex, prev_note):
    card = l["card"]
    cat = "blank" if not l["raw"].strip() else "com" if card in ("'", "CM", "CE") else NEC_CAT.get(card, "ign")
    note = l["note"]
    if card == "'" or (cat == "com" and note == prev_note):
        note = ""                  # i commenti si spiegano da soli; CM/CE solo alla prima riga della serie
    attrs = f"id=L{l['n']} data-line={l['n']}"
    link = ""
    if l["tag"] is not None:
        attrs += f" data-card={card} data-tag={l['tag']} tabindex=0"
        if card == "EX":
            attrs += f" data-seg={ex[2]}"
        link = (f" <a class=to3d href='#v3d' aria-label='Mostra la riga {l['n']} nella vista 3D'>↑ 3D</a>")
    return (f"<div class='nl c-{cat}' {attrs}>"
            f"<a class=ln href='#L{l['n']}' aria-label='riga {l['n']}'>{l['n']}</a>"
            f"<code class=src>{nec_hl(l['raw'], card)}</code>"
            f"<span class=why>{html.escape(note)}{link}</span></div>"), l["note"]


def nec_explained(deck, text):
    lines = nec.explain_lines(text, deck, F0_IT, SWEEP_IT)
    out, i, prev = [], 0, None
    while i < len(lines):
        j = i
        while j < len(lines) and lines[j]["card"] == "GW" and lines[j]["tag"] is not None:
            j += 1
        if j - i > NEC_RUN_MIN:    # serie di fili: restano visibili i primi e gli ultimi, il resto si espande
            hidden = lines[i + NEC_RUN_EDGE:j - NEC_RUN_EDGE]
            run = []
            for l in lines[i:i + NEC_RUN_EDGE]:
                row, prev = nec_row(l, deck.ex, prev)
                out.append(row)
            for l in hidden:
                row, prev = nec_row(l, deck.ex, prev)
                run.append(row)
            out.append(
                f"<details class=run><summary>… altri {len(hidden)} fili (tag {hidden[0]['tag']}–{hidden[-1]['tag']}, "
                f"righe {hidden[0]['n']}–{hidden[-1]['n']}): mostra</summary>{''.join(run)}</details>")
            for l in lines[j - NEC_RUN_EDGE:j]:
                row, prev = nec_row(l, deck.ex, prev)
                out.append(row)
            i = j
            continue
        row, prev = nec_row(lines[i], deck.ex, prev)
        out.append(row)
        i += 1
    key = "".join(f"<span class='k k-{c}'>{label}</span>" for c, label in (
        ("com", "commenti"), ("sy", "variabili SY"), ("geo", "geometria"),
        ("src", "alimentazione e carichi"), ("ctl", "controllo"), ("ign", "ignorate")))
    return (
        "<h2>Il file NEC spiegato</h2>"
        "<p class=lede>Il modello NEC-2 di questa antenna, riga per riga. Per il significato generale delle "
        "schede (variabili <code>SY</code>, fili <code>GW</code>, alimentazione <code>EX</code>...) vedi la "
        "<a href='../guida/#schede-nec'>guida alle schede NEC</a>. Passa il mouse su un filo o sull'alimentazione "
        "per vederli evidenziati nella vista 3D.</p>"
        f"<p class=nec-key>{key}</p>"
        f"<div class=nec id=nec role=region aria-label='File NEC con spiegazione riga per riga'>{''.join(out)}</div>")


SEARCH = []                        # chunk per la ricerca del sito principale


def _plain(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def index_html(fragment, url, page_label, intro_title, slug):
    """Divide un frammento HTML sugli <h2> e aggiunge un chunk per sezione a SEARCH.
    Formato uguale a search-index.json del sito: id, page, title, url, text."""
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", fragment, flags=re.S)
    title, anchor, buf = intro_title, "", parts[0]
    def flush():
        text = _plain(buf)
        if text:
            SEARCH.append({"id": f"antenne--{slug}--{anchor or 'intro'}", "page": page_label,
                           "title": title, "url": url + (f"#{anchor}" if anchor else ""), "text": text[:1200]})
    for k in range(1, len(parts), 2):
        flush()
        h = parts[k]
        m = re.search(r"id=[\"']?([^\"' >]+)", h)
        anchor, title, buf = (m.group(1) if m else ""), _plain(h), parts[k + 1]
    flush()


def render_guide():
    if not GUIDE_MD.exists():
        print(f"ERRORE: {GUIDE_MD} non trovato (la guida è gestita a parte).", file=sys.stderr)
        sys.exit(1)
    md = markdown.Markdown(extensions=["tables", "attr_list", "toc", "fenced_code"],
                            extension_configs={"toc": {"toc_depth": "2-3", "anchorlink": False, "permalink": False}})
    content_html = md.convert(GUIDE_MD.read_text())
    index_html(content_html, f"{SITE}antenne/{GUIDE}/", "Antenne · Guida", "Guida alle antenne", GUIDE)
    return content_html, md.toc


def build_guide():
    content_html, toc_html = render_guide()
    body = ("<a class=back href='../'>← Tutte le antenne</a>"
            f"<p class=eyebrow><a href='{SITE}'>MeshCore ITA</a> · Antenne</p>"
            "<div class=guide-wrap>"
            f"<nav class=guide-toc aria-label='Indice della guida'>{toc_html}</nav>"
            f"<div class='guide-content prose'>{content_html}</div>"
            "</div>")
    (OUT / GUIDE).mkdir(parents=True, exist_ok=True)
    (OUT / GUIDE / "index.html").write_text(page(
        "Guida alle antenne", body, root="..", url=f"{SITE}antenne/{GUIDE}/", mod=lastmod(GUIDE_MD),
        desc="Guida per chi inizia: lunghezza d'onda, dipolo, polarizzazione, dBi e dBd, ROS, impedenza, "
             "adattamento a 50 Ω, ERP a 869,618 MHz e schede NEC."))


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(Path(__file__).parent / "viewer.js", OUT / "viewer.js")
    shutil.copytree(Path(__file__).parent / "vendor" / "three", OUT / "vendor" / "three")
    shutil.copytree(Path(__file__).parent / "vendor" / "fonts", OUT / "fonts")
    build_guide()
    rows, errors = [], []
    for d in sorted(p for p in SRC.iterdir() if (p / "antenna.nec").exists()):
        try:
            meta = json.loads((d / "meta.json").read_text())
            if bad := check_meta(d, meta):
                raise ValueError("meta.json: " + "; ".join(bad))
            nec_text = (d / "antenna.nec").read_text()
            deck = nec.parse(nec_text)
            r = simulate(deck)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{d.name}: {e}")
            continue
        for w in nec.lint(deck, F0):
            print(f"AVVISO {d.name}: {w}", file=sys.stderr)
        mounted = meta.get("montaggio")
        pol = mounted or polarization(deck)
        dst = OUT / d.name
        dst.mkdir()
        for f in d.iterdir():
            if f.suffix.lower() in (*PHOTO_EXT, ".nec", ".s1p"):
                shutil.copy(f, dst / f.name)
        notes = (markdown.markdown((d / "README.md").read_text(), extensions=["tables", "toc"])
                 if (d / "README.md").exists() else "")
        url = f"{SITE}antenne/{d.name}/"
        SEARCH.append({"id": f"antenne--{d.name}--scheda", "page": "Antenne", "title": meta["title"], "url": url,
                       "text": f"{meta.get('description', '')} {meta['type']}. Autore {meta['author']}. "
                               f"Guadagno {r['gmax']:.1f} dBi, avanti/dietro {r['fb']:.1f} dB, ROS {r['swr']:.2f} "
                               f"a {F0_IT} MHz, impedenza {fmt_z(r['z'])}, polarizzazione {pol.lower()}."})
        index_html(notes, url, f"Antenne · {meta['title']}", meta["title"], d.name)
        photos = "".join(f"<figure><a href='{html.escape(p['file'])}' data-lb>"
                         f"<img class=photo loading=lazy src='{html.escape(p['file'])}' alt='{html.escape(p['alt'])}'></a>"
                         f"<figcaption>{html.escape(p['alt'])}</figcaption></figure>" for p in meta.get("photos", []))
        gnd = "spazio libero" if not nec.has_ground(deck) else "sopra il terreno definito nel file"
        cls = "ok" if r["swr"] < 1.5 else "warn" if r["swr"] < 2 else "bad"
        def stat(v, label, c="", anchor=None):
            span = f"<a href='../{GUIDE}/#{anchor}'>{label}</a>" if anchor else label
            return f"<div class=stat><b class='{c}'>{v}</b><span>{span}</span></div>"
        summary = ("<div class=stats>"
                   + stat(f"{r['gmax']:.1f}", "guadagno dBi", anchor="guadagno")
                   + stat(f"{r['fb']:.1f}", "avanti/dietro dB", anchor="avanti-dietro")
                   + stat(f"{r['swr']:.2f}", f"ROS a {F0_IT}", cls, anchor="ros")
                   + stat(fmt_z(r["z"]).replace(" Ω", ""), "impedenza Ω", "sm", anchor="impedenza")
                   + stat(f"{r['fres']:.0f}", "ROS minimo MHz", anchor="ros")
                   + "</div>")
        tags = "".join(f"<span class=tag>{html.escape(t)}</span>" for t in
                       (meta["type"], meta.get("status", ""), f"di {meta['author']}", gnd, pol) if t)
        body = (f"<a class=back href='../'>← Tutte le antenne</a>"
                f"<p class=eyebrow><a href='{SITE}'>MeshCore ITA</a> · Antenne</p><h1>{html.escape(meta['title'])}</h1>"
                f"<p class=lede>{html.escape(meta.get('description', ''))}</p>"
                f"<p class=guide-note>Nuovo alle antenne? <a href='../{GUIDE}/'>Leggi la guida</a> per capire "
                "guadagno, ROS, impedenza e polarizzazione.</p>"
                f"<div class=meta>{tags}</div>"
                f"{summary}{insights(deck, r, mounted)}{viewer(deck, r)}"
                f"<h2>Adattamento e diagrammi</h2>{charts(r)}"
                f"<p class=note>Simulazione NEC-2 (PyNEC) a {F0_IT} MHz, {gnd}. I valori reali cambiano con supporto, cavo e ostacoli.</p>"
                + (f"<h2>Foto</h2><div class=photos>{photos}</div>{LIGHTBOX}" if photos else "")
                + (f"<div class=prose>{notes}</div>" if notes else "")
                + nec_explained(deck, nec_text)
                + "<h2>File del modello</h2><p class=files><a class=btn href='antenna.nec' download>Scarica antenna.nec</a>"
                "<button class='btn alt' type=button id=copy-nec>Copia</button>"
                "<span class=copy-msg id=copy-msg role=status></span></p>"
                "<p class=note>Si apre con xnec2c, 4nec2 o EZNEC.</p>")
        (dst / "index.html").write_text(page(meta["title"], body, head=IMPORTMAP, url=url,
                                             desc=meta.get("description", ""), mod=lastmod(d)))
        rows.append((d.name, meta, r, pol))
        print(f"{d.name}: Z={fmt_z(r['z'])} ROS={r['swr']:.2f} G={r['gmax']:.1f} dBi F/B={r['fb']:.1f} dB pol={pol}")

    table = "".join(
        f"<tr><td><a href='{n}/'>{html.escape(m['title'])}</a></td><td>{html.escape(m['type'])}</td>"
        f"<td>{html.escape(pol)}</td><td>{html.escape(m['author'])}</td>"
        f"<td class=n>{r['gmax']:.1f}</td><td class=n>{r['fb']:.1f}</td><td class=n>{r['swr']:.2f}</td></tr>"
        for n, m, r, pol in rows)
    body = (f"<p class=eyebrow><a href='{SITE}'>MeshCore ITA</a> · <a href='{SITE}blog/galleria-antenne/'>com'è nata</a></p>"
            "<h1>Antenne della community</h1>"
            f"<p class=lede>Modelli NEC-2 condivisi dalla community, simulati automaticamente a {F0_IT} MHz, "
            "il preset italiano. Ogni scheda ha la vista 3D, i grafici e il file <code>.nec</code> da scaricare.</p>"
            f"<p class=guide-note>Nuovo alle antenne? <a href='{GUIDE}/'>Leggi la guida</a> prima di scegliere "
            "un modello: spiega guadagno, ROS, impedenza, polarizzazione ed ERP con parole semplici.</p>"
            "<table><tr><th>Antenna</th><th>Tipo</th><th>Polarizzazione</th><th>Autore</th>"
            "<th style=text-align:right>Guadagno dBi</th>"
            "<th style=text-align:right>Avanti/dietro dB</th><th style=text-align:right>ROS</th></tr>"
            f"{table}</table>"
            "<p class=note>Simulazioni in NEC-2: indicano la tendenza, non sostituiscono una misura con un VNA.</p>")
    (OUT / "index.html").write_text(page(
        "Antenne della community", body, root=".", url=f"{SITE}antenne/", mod=lastmod(SRC, GUIDE_MD),
        desc=f"Antenne per MeshCore condivise dalla community, simulate in NEC-2 a {F0_IT} MHz: vista 3D, "
             "ROS, impedenza, potenza massima ERP e istruzioni di costruzione."))
    (OUT / "search-index.json").write_text(json.dumps(SEARCH, ensure_ascii=False, separators=(",", ":")))
    urls = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{m}</lastmod>\n  </url>\n"
                   for u, m in sorted(PAGES, key=lambda p: (p[0].count("/"), p[0])))
    (OUT / "sitemap.xml").write_text("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                                     "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
                                     f"{urls}</urlset>\n")
    if errors:
        print("\n".join(["ERRORI:"] + errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()
