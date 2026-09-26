"""Minimal NEC-2 card-deck reader driving PyNEC.

Supports the cards commonly used in amateur models: CM CE SY GW GS GE EK GN
EX LD FR RP PT EN. SY variables and arithmetic are evaluated in every
numeric field, as 4nec2 does. Unsupported geometry cards raise an error
instead of being silently ignored.
"""
import math
import re
from dataclasses import dataclass, field

import numpy as np
from PyNEC import nec_context

SAFE = {k: getattr(math, k) for k in ("sin", "cos", "tan", "atan", "sqrt", "log", "log10", "exp", "pi")}
SAFE.update(abs=abs)


class DeckError(ValueError):
    pass


@dataclass
class Deck:
    comments: list = field(default_factory=list)
    wires: list = field(default_factory=list)      # (tag, segs, x1, y1, z1, x2, y2, z2, radius)
    scale: float = 1.0
    gpflag: int = 0
    ek: bool = False
    ground: tuple = (-1, 0, 0.0, 0.0)             # (type, nradl, epse, sig)
    ex: tuple = None                               # (type, tag, seg)
    loads: list = field(default_factory=list)      # (type, tag, segf, segl, zlr, zli, zlc)
    freq: float = None


def _ev(tok, sym, line):
    try:
        return float(eval(tok, {"__builtins__": {}}, {**SAFE, **sym}))
    except Exception as e:
        raise DeckError(f"valore non valido '{tok}' nella riga: {line}") from e


def _fields(rest):
    return [t for t in re.split(r"[,\s]+", rest.strip()) if t]


def parse(text):
    d, sym = Deck(), {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line[0] in "'!":
            continue
        card, rest = line[:2].upper(), line[2:]
        if card in ("CM", "CE"):
            if rest.strip():
                d.comments.append(rest.strip())
            continue
        if card == "SY":
            for part in rest.split(","):
                if "=" in part:
                    k, v = part.split("=", 1)
                    sym[k.strip()] = _ev(v.split("'")[0].strip(), sym, line)
            continue
        f = _fields(rest.split("'")[0])
        n = lambda i, default=0.0: _ev(f[i], sym, line) if i < len(f) else default
        if card == "GW":
            d.wires.append((int(n(0)), int(n(1)), *[n(i) for i in range(2, 9)]))
        elif card == "GS":
            d.scale = n(2, 1.0)
        elif card == "GE":
            d.gpflag = int(n(0))
        elif card == "EK":
            d.ek = int(n(0)) != -1
        elif card == "GN":
            t = int(n(0))
            d.ground = (t, int(n(1)), n(4), n(5)) if t != -1 else (-1, 0, 0.0, 0.0)
        elif card == "EX":
            d.ex = (int(n(0)), int(n(1)), int(n(2)))
        elif card == "LD":
            d.loads.append((int(n(0)), int(n(1)), int(n(2)), int(n(3)), n(4), n(5), n(6)))
        elif card == "FR":
            d.freq = n(4)
        elif card in ("RP", "PT", "PL", "XQ", "NE", "NH", "EN"):
            if card == "EN":
                break
        else:
            raise DeckError(f"scheda {card} non supportata: {line}")
    if not d.wires:
        raise DeckError("nessun filo (GW) nel modello")
    if d.ex is None:
        raise DeckError("nessuna sorgente (EX) nel modello")
    return d


def _context(d, f):
    c = nec_context()
    g = c.get_geometry()
    for tag, segs, x1, y1, z1, x2, y2, z2, r in d.wires:
        g.wire(tag, segs, x1, y1, z1, x2, y2, z2, r, 1.0, 1.0)
    if d.scale != 1.0:
        g.scale(d.scale)
    c.geometry_complete(d.gpflag)
    if d.ek:
        c.set_extended_thin_wire_kernel(True)
    for ld in d.loads:
        c.ld_card(*ld)
    t, nr, eps, sig = d.ground
    c.gn_card(t, nr, eps, sig, 0, 0, 0, 0)
    c.ex_card(d.ex[0], d.ex[1], d.ex[2], 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f, 0)
    return c


def has_ground(d):
    return d.ground[0] != -1


def impedance(d, f):
    c = _context(d, f)
    c.xq_card(0)
    return complex(c.get_input_parameters(0).get_impedance()[0])


def pattern(d, f, step=5):
    """Total gain (dBi) on a theta x phi grid; upper hemisphere only over ground."""
    c = _context(d, f)
    nth = (90 if has_ground(d) else 180) // step + 1
    nph = 360 // step
    c.rp_card(0, nth, nph, 0, 5, 0, 0, 0, 0, step, step, 0, 0)
    g = np.array(c.get_radiation_pattern(0).get_gain()).reshape(nth, nph)
    th = np.arange(nth) * step
    ph = np.arange(nph) * step
    return th, ph, np.maximum(g, -40.0)


def swr(z, z0=50.0):
    rho = abs((z - z0) / (z + z0))
    return (1 + rho) / (1 - rho) if rho < 1 else float("inf")



def explain_lines(text, scale=1.0):
    """Per-line Italian explanation of a raw .nec deck, for the annotated listing.

    Mirrors the card handling in parse() but never raises: unknown or malformed
    lines get a generic note instead of aborting. `scale` should be the final
    Deck.scale (from parse()) so GW coordinates are shown in the mm actually
    used by the simulation, regardless of where a GS card sits in the file.
    Returns a list of {"raw": line, "note": str} dicts, one per source line.
    """
    out = []
    sym = {}
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            out.append({"raw": line, "note": ""})
            continue
        if stripped[0] in "'!":
            out.append({"raw": line, "note": "Commento (ignorato dal simulatore)."})
            continue
        card, rest = stripped[:2].upper(), stripped[2:]
        note = ""
        try:
            if card == "CM":
                note = "Commento descrittivo del modello (ignorato dal simulatore)."
            elif card == "CE":
                note = "Fine dei commenti: da qui iniziano le schede di geometria."
            elif card == "SY":
                parts = []
                for part in rest.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        k = k.strip()
                        val = _ev(v.split("'")[0].strip(), sym, line)
                        sym[k] = val
                        parts.append(f"{k} = {val:g}")
                note = ("Variabile " + ", ".join(parts) + "." if parts else "Variabile (nessun valore riconosciuto).")
            elif card in ("GW", "GS", "GE", "EK", "GN", "EX", "LD", "FR"):
                f = _fields(rest.split("'")[0])
                n = lambda i, default=0.0: _ev(f[i], sym, line) if i < len(f) else default
                if card == "GW":
                    tag, segs = int(n(0)), int(n(1))
                    x1, y1, z1, x2, y2, z2, r = (n(i) for i in range(2, 9))
                    p1 = (x1 * scale * 1000, y1 * scale * 1000, z1 * scale * 1000)
                    p2 = (x2 * scale * 1000, y2 * scale * 1000, z2 * scale * 1000)
                    length_mm = math.dist(p1, p2)
                    note = (f"Filo {tag}: {segs} segmenti, da ({p1[0]:.0f}, {p1[1]:.0f}, {p1[2]:.0f}) mm "
                            f"a ({p2[0]:.0f}, {p2[1]:.0f}, {p2[2]:.0f}) mm — diametro {r * scale * 2000:.1f} mm, "
                            f"lunghezza {length_mm:.0f} mm.")
                elif card == "GS":
                    note = f"Fattore di scala delle coordinate: ×{n(2, 1.0):g} (già applicato ai fili qui sopra)."
                elif card == "GE":
                    note = "Fine della geometria." + (
                        " Indica un piano di massa nell'origine (immagine speculare)." if int(n(0)) == 1 else "")
                elif card == "EK":
                    note = "Kernel per fili spessi (extended thin-wire kernel): più preciso quando il diametro non è trascurabile."
                elif card == "GN":
                    t = int(n(0))
                    if t == -1:
                        note = "Nessun terreno: simulazione in spazio libero."
                    elif t == 0:
                        note = "Terreno reale (dielettrico con perdite)."
                    elif t == 1:
                        note = "Terreno modellato come conduttore perfetto."
                    else:
                        note = f"Terreno tipo {t}."
                elif card == "EX":
                    note = f"Alimentazione: sul filo {int(n(1))}, segmento {int(n(2))}."
                elif card == "LD":
                    note = f"Carico elettrico (tipo {int(n(0))}) sul filo {int(n(1))}: modella una perdita (es. conducibilità reale del metallo)."
                elif card == "FR":
                    note = (f"Frequenza nel file originale: {n(4):g} MHz — la galleria la ignora e simula sempre "
                            "a 869,618 MHz (preset italiano), con una scansione 855–885 MHz.")
            elif card in ("RP", "PT", "PL", "XQ", "NE", "NH"):
                note = "Ignorata dalla galleria: il diagramma di irradiazione lo calcola il generatore del sito."
            elif card == "EN":
                note = "Fine del file."
            else:
                note = "Scheda non riconosciuta da questo lettore."
        except Exception:
            note = "Riga non interpretabile automaticamente."
        out.append({"raw": line, "note": note})
    return out
