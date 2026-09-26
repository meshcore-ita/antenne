"""Simulate every antenne/*/antenna.nec and write a static gallery to site/."""
import html
import subprocess
from datetime import date
import json
import math
import re
import shutil
import sys
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
img.photo{width:100%;max-height:32rem;object-fit:cover;border-radius:10px;border:1px solid var(--line)}
.viewer{position:relative;height:min(70vh,36rem);border:1px solid var(--line);border-radius:14px;overflow:hidden;
background:radial-gradient(ellipse at 50% 40%,#0d1f14 0%,#050806 55%,#000 100%);touch-action:none;cursor:grab}
.viewer canvas{width:100%;height:100%;display:block}
.viewer .modes{position:absolute;top:.8rem;left:.8rem;display:flex;gap:.4rem;margin:0}
.modes button{font:.75rem var(--mono);color:var(--muted);padding:.35rem .7rem;border:1px solid var(--line-strong);background:rgba(0,0,0,.55);border-radius:999px;cursor:pointer;backdrop-filter:blur(6px)}
.modes button[aria-pressed=true]{color:#000;background:var(--accent);border-color:var(--accent)}
.legend{position:absolute;right:.9rem;bottom:.9rem;font:.7rem var(--mono);color:var(--muted);display:flex;align-items:center;gap:.5rem}
.legend i{display:block;width:9rem;height:.45rem;border-radius:99px;background:linear-gradient(90deg,#1e3a8a,#22c55e 45%,#facc15 75%,#e11d48)}
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
table.necdump td:first-child{font-family:var(--mono);font-size:.8rem;white-space:pre;color:var(--fg)}
table.necdump td:last-child{color:var(--muted);font-size:.88rem}
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
    th, ph, g = nec.pattern(deck, F0)
    i, j = np.unravel_index(np.argmax(g), g.shape)
    gmax = float(g[i, j])
    # direzione opposta: (180-theta, phi+180); sopra il suolo resta nello stesso emisfero
    bi = min(len(th) - 1, int(round((180 - th[i]) / 5))) if not nec.has_ground(deck) else i
    bj = (j + len(ph) // 2) % len(ph)
    fb = gmax - float(g[bi, bj])
    k = int(np.argmin([nec.swr(z) for z in zs]))
    return dict(z=z0, swr=nec.swr(z0), gmax=gmax, fb=fb, theta=int(th[i]), phi=int(ph[j]),
                fres=float(SWEEP[k]), sweep=zs, th=th, ph=ph, g=g, imax=i, jmax=j)


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


IMPORTMAP = ("<script type=importmap>{\"imports\":{\"three\":\"../vendor/three/three.module.min.js\","
             "\"three/addons/\":\"../vendor/three/\"}}</script>")


def viewer(deck, r):
    s = deck.scale
    wires = [[round(v * s, 5) for v in w[2:9]] for w in deck.wires]
    feed = next((k for k, w in enumerate(deck.wires) if w[0] == deck.ex[1]), None)
    data = dict(th=r["th"].tolist(), ph=r["ph"].tolist(), g=np.round(r["g"], 2).tolist(),
                gmax=round(r["gmax"], 2), wires=wires, feed=feed)
    help_body = (
        "<div class=help-body>"
        "<p>Il raggio della superficie colorata, in ogni direzione, è proporzionale al guadagno: più il "
        "diagramma si allontana dal centro in una direzione, più energia irradia l'antenna verso quel punto.</p>"
        f"<p>I colori seguono la legenda in basso a destra: dal blu (−30 dB sotto il massimo) al verde, al "
        f"giallo, fino al rosso ({r['gmax']:.1f} dBi, il massimo di questo modello).</p>"
        "<p>I lobi sono le \"bolle\" del diagramma. Il lobo principale è la direzione in cui punta l'antenna; "
        "i lobi laterali e posteriori, più piccoli, sono energia irradiata altrove — <a href='../guida/#diagramma'>"
        "vedi il diagramma di irradiazione</a>.</p>"
        "<p>Il punto verde sui fili è il punto di alimentazione, dove si collega il cavo.</p>"
        "<p>La griglia orizzontale rappresenta il piano dell'orizzonte, con cerchi ogni 10 dB e raggi ogni 30°: "
        "aiuta a capire quanto il lobo principale è inclinato verso il suolo o verso il cielo.</p>"
        "</div>")
    return ("<div class=viewer id=viewer3d role=img aria-label='Diagramma di irradiazione 3D e geometria dell&apos;antenna'>"
            "<p class=modes><button data-mode=both aria-pressed=true>Tutto</button>"
            "<button data-mode=pattern aria-pressed=false>Diagramma</button>"
            "<button data-mode=geom aria-pressed=false>Antenna</button></p>"
            f"<div class=legend><span>−30 dB</span><i></i><span>{r['gmax']:.1f} dBi</span></div></div>"
            "<p class=note>Trascina per ruotare, rotella o pizzico per lo zoom. Il punto verde è l'alimentazione; "
            "la geometria è ingrandita per stare dentro il diagramma.</p>"
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
    """('Verticale'|'Orizzontale', asse) dedotti dalla direzione dominante del filo alimentato."""
    wire = next((w for w in deck.wires if w[0] == deck.ex[1]), deck.wires[0])
    dx, dy, dz = abs(wire[5] - wire[2]), abs(wire[6] - wire[3]), abs(wire[7] - wire[4])
    if dz >= dx and dz >= dy:
        return "Verticale", "z"
    return "Orizzontale", "x/y"


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

    pol, axis = polarization(deck)
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


def nec_explained(deck, text):
    lines = nec.explain_lines(text, deck.scale)
    rows = "".join(
        f"<tr><td><code>{html.escape(l['raw']) if l['raw'].strip() else '&nbsp;'}</code></td>"
        f"<td>{html.escape(l['note'])}</td></tr>"
        for l in lines)
    return (
        "<h2>Il file NEC spiegato</h2>"
        "<p class=lede>Il modello NEC-2 di questa antenna, riga per riga. Per il significato generale delle "
        "schede (variabili <code>SY</code>, fili <code>GW</code>, alimentazione <code>EX</code>...) vedi la "
        "<a href='../guida/#schede-nec'>guida alle schede NEC</a>.</p>"
        f"<table class=necdump><tr><th>Riga</th><th>Cosa fa</th></tr>{rows}</table>")


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
        meta = json.loads((d / "meta.json").read_text())
        nec_text = (d / "antenna.nec").read_text()
        try:
            deck = nec.parse(nec_text)
            r = simulate(deck)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{d.name}: {e}")
            continue
        pol, _axis = polarization(deck)
        mounted = meta.get("montaggio")
        if mounted:
            pol = mounted
        dst = OUT / d.name
        dst.mkdir()
        for f in d.iterdir():
            if f.suffix.lower() in (".nec", ".jpg", ".jpeg", ".png", ".webp", ".s1p"):
                shutil.copy(f, dst / f.name)
        notes = (markdown.markdown((d / "README.md").read_text(), extensions=["tables", "toc"])
                 if (d / "README.md").exists() else "")
        url = f"{SITE}antenne/{d.name}/"
        SEARCH.append({"id": f"antenne--{d.name}--scheda", "page": "Antenne", "title": meta["title"], "url": url,
                       "text": f"{meta.get('description', '')} {meta['type']}. Autore {meta['author']}. "
                               f"Guadagno {r['gmax']:.1f} dBi, avanti/dietro {r['fb']:.1f} dB, ROS {r['swr']:.2f} "
                               f"a {F0_IT} MHz, impedenza {fmt_z(r['z'])}, polarizzazione {pol.lower()}."})
        index_html(notes, url, f"Antenne · {meta['title']}", meta["title"], d.name)
        photos = "".join(f"<figure><img class=photo loading=lazy src='{html.escape(p['file'])}' alt='{html.escape(p['alt'])}'>"
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
                + (f"<h2>Foto</h2><div class=photos>{photos}</div>" if photos else "")
                + (f"<div class=prose>{notes}</div>" if notes else "")
                + nec_explained(deck, nec_text)
                + "<h2>File del modello</h2><p><a class=btn href='antenna.nec' download>Scarica antenna.nec</a></p>"
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
