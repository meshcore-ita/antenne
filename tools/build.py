"""Simulate every antenne/*/antenna.nec and write a static gallery to site/."""
import html
import json
import math
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
F0 = 869.618                       # preset MeshCore ITA
BAND = (869.4, 869.65)             # sub-banda 500 mW ERP
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
.lede{color:var(--muted);font-size:1.1rem;max-width:48rem}
.back{font:.85rem var(--mono);color:var(--muted);text-decoration:none}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:2rem 0}
.stat{background:var(--bg);padding:1rem 1.2rem}.stat b{display:block;font:600 1.6rem var(--mono);letter-spacing:-.02em;white-space:nowrap}
.stat b.sm{font-size:1.15rem;line-height:2.1rem}
.stat span{font:.72rem var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--dim)}
.stat b.ok{color:var(--accent)}.stat b.warn{color:#facc15}.stat b.bad{color:var(--accent-2)}
table{border-collapse:collapse;width:100%;margin:1rem 0}
th,td{border-bottom:1px solid var(--line);padding:.7rem .6rem;text-align:left}th{font:500 .75rem var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
td.n{text-align:right;font:1rem var(--mono)}tr:hover td{background:var(--panel)}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}.tag{font:.75rem var(--mono);border:1px solid var(--line-strong);border-radius:999px;padding:.15rem .7rem;color:var(--muted)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1rem}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(16rem,1fr));gap:1rem}
figure{margin:0}figcaption{font-size:.82rem;color:var(--dim);margin-top:.5rem}
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
"""


def page(title, body, root="..", head=""):
    return (f"<!doctype html><html lang=it><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>"
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
    return ("<div class=viewer id=viewer3d role=img aria-label='Diagramma di irradiazione 3D e geometria dell&apos;antenna'>"
            "<p class=modes><button data-mode=both aria-pressed=true>Tutto</button>"
            "<button data-mode=pattern aria-pressed=false>Diagramma</button>"
            "<button data-mode=geom aria-pressed=false>Antenna</button></p>"
            f"<div class=legend><span>−30 dB</span><i></i><span>{r['gmax']:.1f} dBi</span></div></div>"
            "<p class=note>Trascina per ruotare, rotella o pizzico per lo zoom. Il punto verde è l'alimentazione; "
            "la geometria è ingrandita per stare dentro il diagramma.</p>"
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
        f"<figure class=card>{svg_line(SWEEP, [(sw, '#e11d48')], 'ROS', 1, 5, BAND)}<figcaption>ROS su 50 Ω, 855–885 MHz. In verde la sub-banda 869,4–869,65</figcaption></figure>"
        f"<figure class=card>{svg_line(SWEEP, [(R, '#22c55e'), (X, '#facc15')], 'impedenza', mark=BAND)}<figcaption>Impedenza: <span style=color:#22c55e>R</span> e <span style=color:#facc15>X</span> in Ω</figcaption></figure>"
        f"<figure class=card>{az}<figcaption>Taglio conico a θ = {r['theta']}°, dB rispetto al massimo</figcaption></figure>"
        f"<figure class=card>{el}<figcaption>Taglio verticale a φ = {r['phi']}° (θ = 0 in alto)</figcaption></figure>"
        "</div>")


def fmt_z(z):
    return f"{z.real:.1f} {'+' if z.imag >= 0 else '−'} j{abs(z.imag):.1f} Ω"


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(Path(__file__).parent / "viewer.js", OUT / "viewer.js")
    shutil.copytree(Path(__file__).parent / "vendor" / "three", OUT / "vendor" / "three")
    shutil.copytree(Path(__file__).parent / "vendor" / "fonts", OUT / "fonts")
    rows, errors = [], []
    for d in sorted(p for p in SRC.iterdir() if (p / "antenna.nec").exists()):
        meta = json.loads((d / "meta.json").read_text())
        try:
            deck = nec.parse((d / "antenna.nec").read_text())
            r = simulate(deck)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{d.name}: {e}")
            continue
        dst = OUT / d.name
        dst.mkdir()
        for f in d.iterdir():
            if f.suffix.lower() in (".nec", ".jpg", ".jpeg", ".png", ".webp", ".s1p"):
                shutil.copy(f, dst / f.name)
        notes = markdown.markdown((d / "README.md").read_text(), extensions=["tables"]) if (d / "README.md").exists() else ""
        photos = "".join(f"<figure><img class=photo loading=lazy src='{html.escape(p['file'])}' alt='{html.escape(p['alt'])}'>"
                         f"<figcaption>{html.escape(p['alt'])}</figcaption></figure>" for p in meta.get("photos", []))
        gnd = "spazio libero" if not nec.has_ground(deck) else "sopra il terreno definito nel file"
        cls = "ok" if r["swr"] < 1.5 else "warn" if r["swr"] < 2 else "bad"
        stat = lambda v, label, c="": f"<div class=stat><b class='{c}'>{v}</b><span>{label}</span></div>"
        summary = ("<div class=stats>"
                   + stat(f"{r['gmax']:.1f}", "guadagno dBi")
                   + stat(f"{r['fb']:.1f}", "avanti/dietro dB")
                   + stat(f"{r['swr']:.2f}", f"ROS a {F0}", cls)
                   + stat(fmt_z(r["z"]).replace(" Ω", ""), "impedenza Ω", "sm")
                   + stat(f"{r['fres']:.0f}", "ROS minimo MHz")
                   + "</div>")
        tags = "".join(f"<span class=tag>{html.escape(t)}</span>" for t in
                       (meta["type"], meta.get("status", ""), f"di {meta['author']}", gnd) if t)
        body = (f"<a class=back href='../'>← Tutte le antenne</a>"
                f"<p class=eyebrow>Antenne MeshCore ITA</p><h1>{html.escape(meta['title'])}</h1>"
                f"<p class=lede>{html.escape(meta.get('description', ''))}</p><div class=meta>{tags}</div>"
                f"{summary}{viewer(deck, r)}"
                f"<h2>Adattamento e diagrammi</h2>{charts(r)}"
                f"<p class=note>Simulazione NEC-2 (PyNEC) a {F0} MHz, {gnd}. I valori reali cambiano con supporto, cavo e ostacoli.</p>"
                + (f"<h2>Foto</h2><div class=photos>{photos}</div>" if photos else "")
                + (f"<div class=prose>{notes}</div>" if notes else "")
                + "<h2>File del modello</h2><p><a class=btn href='antenna.nec' download>Scarica antenna.nec</a></p>"
                "<p class=note>Si apre con xnec2c, 4nec2 o EZNEC.</p>")
        (dst / "index.html").write_text(page(meta["title"], body, head=IMPORTMAP))
        rows.append((d.name, meta, r))
        print(f"{d.name}: Z={fmt_z(r['z'])} ROS={r['swr']:.2f} G={r['gmax']:.1f} dBi F/B={r['fb']:.1f} dB")

    table = "".join(
        f"<tr><td><a href='{n}/'>{html.escape(m['title'])}</a></td><td>{html.escape(m['author'])}</td>"
        f"<td class=n>{r['gmax']:.1f}</td><td class=n>{r['fb']:.1f}</td><td class=n>{r['swr']:.2f}</td></tr>"
        for n, m, r in rows)
    body = ("<p class=eyebrow>MeshCore ITA</p><h1>Antenne della community</h1>"
            f"<p class=lede>Modelli NEC-2 condivisi dalla community, simulati automaticamente a {F0} MHz, "
            "il preset italiano. Ogni scheda ha la vista 3D, i grafici e il file <code>.nec</code> da scaricare.</p>"
            "<table><tr><th>Antenna</th><th>Autore</th><th style=text-align:right>Guadagno dBi</th>"
            "<th style=text-align:right>Avanti/dietro dB</th><th style=text-align:right>ROS</th></tr>"
            f"{table}</table>"
            "<p class=note>Simulazioni in NEC-2: indicano la tendenza, non sostituiscono una misura con un VNA.</p>")
    (OUT / "index.html").write_text(page("Antenne della community", body, root="."))
    if errors:
        print("\n".join(["ERRORI:"] + errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()
