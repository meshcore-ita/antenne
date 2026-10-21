"""Minimal NEC-2 card-deck reader driving PyNEC.

Supports the cards commonly used in amateur models: CM CE SY GW GS GE EK GN
EX LD TL NT FR (RP PT PL XQ NE NH EN are accepted and ignored). SY variables
and arithmetic (including 4nec2's `^` power) are evaluated in every numeric
field, as 4nec2 does. Unsupported geometry cards and references to missing
wires or segments raise DeckError instead of being silently ignored.
"""
import ast
import math
import operator
import re
from dataclasses import dataclass, field

import numpy as np
from PyNEC import nec_context

FUNCS = {k: getattr(math, k) for k in ("sin", "cos", "tan", "atan", "sqrt", "log", "log10", "exp")}
FUNCS.update(abs=abs)
CONSTS = {"pi": math.pi}
_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow, ast.Mod: operator.mod}
_UNOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
IGNORED = ("RP", "PT", "PL", "XQ", "NE", "NH")


class DeckError(ValueError):
    pass


@dataclass(frozen=True)
class Wire:
    tag: int
    segs: int
    p1: tuple                                      # (x, y, z) in metri, scala GS già applicata
    p2: tuple
    r: float                                       # raggio in metri
    line: int                                      # riga del GW nel file, da 1

    def point(self, t):
        """Punto a frazione t (0..1) del filo."""
        return tuple(a + (b - a) * t for a, b in zip(self.p1, self.p2))


@dataclass
class Deck:
    comments: list = field(default_factory=list)
    wires: list = field(default_factory=list)      # Wire
    gpflag: int = 0
    ek: bool = False
    ground: tuple = (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)   # argomenti di gn_card
    ex: tuple = None                               # (type, tag, seg)
    loads: list = field(default_factory=list)      # (type, tag, segf, segl, zlr, zli, zlc)
    networks: list = field(default_factory=list)   # ("TL"|"NT", tag1, seg1, tag2, seg2, 6 reali)
    freq: float = None


def _eval(node, sym):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in sym:
            return sym[node.id]
        if node.id in CONSTS:
            return CONSTS[node.id]
        raise ValueError(f"variabile '{node.id}' non definita")
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval(node.left, sym), _eval(node.right, sym))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNOPS:
        return _UNOPS[type(node.op)](_eval(node.operand, sym))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCS
            and not node.keywords):
        return float(FUNCS[node.func.id](*(_eval(a, sym) for a in node.args)))
    raise ValueError("espressione non ammessa")


def _ev(tok, sym, line):
    try:                                           # ^ = potenza come in 4nec2, con la stessa precedenza di **
        return float(_eval(ast.parse(tok.replace("^", "**"), mode="eval").body, sym))
    except (SyntaxError, ValueError, TypeError, ArithmeticError) as e:
        raise DeckError(f"valore non valido '{tok}' ({e}) nella riga: {line}") from e


def _fields(rest):
    return [t for t in re.split(r"[,\s]+", rest.split("'")[0].strip()) if t]


def _sy(rest, sym, line):
    """Valuta una scheda SY, aggiorna sym e restituisce [(nome, valore)]."""
    out = []
    for part in rest.split("'")[0].split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            sym[k.strip()] = _ev(v.strip(), sym, line)
            out.append((k.strip(), sym[k.strip()]))
    return out


def _card(line):
    return line[:2].upper(), line[2:]


def parse(text):
    d, sym = Deck(), {}
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line[0] in "'!":
            continue
        card, rest = _card(line)
        if card in ("CM", "CE"):
            if rest.strip():
                d.comments.append(rest.strip())
            continue
        if card == "SY":
            _sy(rest, sym, line)
            continue
        f = _fields(rest)
        n = lambda i, default=0.0: _ev(f[i], sym, line) if i < len(f) else default
        if card == "GW":
            if len(f) < 9:
                raise DeckError(f"GW con meno di 9 campi: {line}")
            w = Wire(int(n(0)), int(n(1)), (n(2), n(3), n(4)), (n(5), n(6), n(7)), n(8), no)
            if w.segs < 1 or w.r <= 0 or math.dist(w.p1, w.p2) == 0:
                raise DeckError(f"filo non valido (segmenti, raggio o lunghezza nulli): {line}")
            d.wires.append(w)
        elif card == "GS":                         # come in NEC: scala i fili già definiti
            s = n(2, 1.0)
            d.wires = [Wire(w.tag, w.segs, tuple(v * s for v in w.p1), tuple(v * s for v in w.p2), w.r * s, w.line)
                       for w in d.wires]
        elif card == "GE":
            d.gpflag = int(n(0))
        elif card == "EK":
            d.ek = int(n(0)) != -1
        elif card == "GN":
            t = int(n(0))
            d.ground = (t, int(n(1)), *(n(i) for i in range(4, 10))) if t != -1 else Deck.ground
        elif card == "EX":
            if d.ex is not None:
                raise DeckError(f"una sola sorgente EX supportata: {line}")
            d.ex = (int(n(0)), int(n(1)), int(n(2)))
            if d.ex[0] not in (0, 5):
                raise DeckError(f"solo sorgenti in tensione (EX 0 o 5) supportate: {line}")
        elif card == "LD":
            d.loads.append((int(n(0)), int(n(1)), int(n(2)), int(n(3)), n(4), n(5), n(6)))
        elif card in ("TL", "NT"):
            d.networks.append((card, int(n(0)), int(n(1)), int(n(2)), int(n(3)), *(n(i) for i in range(4, 10))))
        elif card == "FR":
            d.freq = n(4)
        elif card == "EN":
            break
        elif card not in IGNORED:
            raise DeckError(f"scheda {card} non supportata: {line}")
    if not d.wires:
        raise DeckError("nessun filo (GW) nel modello")
    if d.ex is None:
        raise DeckError("nessuna sorgente (EX) nel modello")
    segment(d, d.ex[1], d.ex[2], "EX")
    for ld in d.loads:
        if ld[0] != -1 and ld[1] != 0:
            segment(d, ld[1], ld[2] or 1, "LD")
    for nw in d.networks:
        segment(d, nw[1], nw[2], nw[0])
        segment(d, nw[3], nw[4], nw[0])
    return d


def segment(d, tag, seg, card="EX"):
    """(filo, segmento locale da 1) indicati da tag/segmento come li conta NEC.

    Con tag 0 il segmento è il numero assoluto; altrimenti è l'n-esimo segmento
    fra tutti i fili con quel tag, nell'ordine del file.
    """
    count = 0
    for w in d.wires:
        if tag == 0 or w.tag == tag:
            if seg <= count + w.segs:
                if seg >= 1:
                    return w, seg - count
                break
            count += w.segs
    raise DeckError(f"{card}: segmento {seg} del filo {tag} inesistente")


def segment_center(d, tag, seg):
    w, k = segment(d, tag, seg)
    return w.point((k - 0.5) / w.segs)


def _ranges(tags):
    out, tags = [], sorted(set(tags))
    for t in tags:
        if out and t == out[-1][1] + 1:
            out[-1][1] = t
        else:
            out.append([t, t])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def lint(d, f):
    """Avvisi sulla segmentazione, non bloccanti: segmenti più lunghi di λ/20 (la regola della
    guida) o più corti di 8 volte il raggio (2 con EK), il limite indicato dal manuale NEC-2."""
    lam = 299.792458 / f
    ratio = 2 if d.ek else 8
    long_, short = [], []
    for w in d.wires:
        seg = math.dist(w.p1, w.p2) / w.segs
        if seg > lam / 20:
            long_.append(w.tag)
        if seg < ratio * w.r:
            short.append(w.tag)
    out = []
    if long_:
        out.append(f"fili {_ranges(long_)}: segmenti più lunghi di λ/20 ({lam / 20 * 1000:.1f} mm), aumenta i segmenti")
    if short:
        out.append(f"fili {_ranges(short)}: segmenti più corti di {ratio} volte il raggio"
                   + ("" if d.ek else " (con EK il limite scende a 2)"))
    return out


def _context(d, f):
    c = nec_context()
    g = c.get_geometry()
    for w in d.wires:
        g.wire(w.tag, w.segs, *w.p1, *w.p2, w.r, 1.0, 1.0)
    c.geometry_complete(d.gpflag)
    if d.ek:
        c.set_extended_thin_wire_kernel(True)
    for ld in d.loads:
        c.ld_card(*ld)
    c.gn_card(*d.ground)
    for card, *args in d.networks:
        (c.tl_card if card == "TL" else c.nt_card)(*args)
    c.ex_card(d.ex[0], d.ex[1], d.ex[2], 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f, 0)
    return c


def has_ground(d):
    return d.ground[0] != -1


def impedance(d, f):
    c = _context(d, f)
    c.xq_card(0)
    return complex(c.get_input_parameters(0).get_impedance()[0])


def far_field(d, f, step=5):
    """Guadagno totale (dBi) su una griglia theta x phi (solo emisfero superiore sopra il terreno)
    e corrente complessa di ogni segmento, nell'ordine di segments()."""
    c = _context(d, f)
    nth = (90 if has_ground(d) else 180) // step + 1
    nph = 360 // step
    c.rp_card(0, nth, nph, 0, 5, 0, 0, 0, 0, step, step, 0, 0)
    g = np.array(c.get_radiation_pattern(0).get_gain()).reshape(nth, nph)
    currents = np.array(c.get_structure_currents(0).get_current(), dtype=complex)
    return np.arange(nth) * step, np.arange(nph) * step, np.maximum(g, -40.0), currents


def swr(z, z0=50.0):
    rho = abs((z - z0) / (z + z0))
    return (1 + rho) / (1 - rho) if rho < 1 else float("inf")


def _mm(p):
    return f"({p[0] * 1000:.1f}, {p[1] * 1000:.1f}, {p[2] * 1000:.1f}) mm".replace(".0,", ",").replace(".0)", ")")


def explain_lines(text, deck, f0_label, sweep_label):
    """Spiegazione in italiano di ogni riga di un file .nec già letto da parse().

    Non solleva mai eccezioni: righe sconosciute o malformate ricevono una nota
    generica. Le coordinate dei GW vengono da `deck`, quindi sono quelle usate
    davvero dalla simulazione (scala GS compresa). Restituisce una lista di
    {"n", "raw", "card", "note", "tag"}, una per riga del file.
    """
    out, sym = [], {}
    wires = {w.line: w for w in deck.wires}
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        item = {"n": no, "raw": line, "card": "", "note": "", "tag": None}
        out.append(item)
        if not stripped:
            continue
        if stripped[0] in "'!":
            item.update(card="'", note="Commento (ignorato dal simulatore).")
            continue
        card, rest = _card(stripped)
        item["card"] = card
        try:
            f = _fields(rest)
            n = lambda i, default=0.0: _ev(f[i], sym, line) if i < len(f) else default
            if card == "CM":
                note = "Commento descrittivo del modello (ignorato dal simulatore)."
            elif card == "CE":
                note = "Fine dei commenti: da qui iniziano le schede di geometria."
            elif card == "SY":
                parts = [f"{k} = {v:g}" for k, v in _sy(rest, sym, line)]
                note = "Variabile " + ", ".join(parts) + "." if parts else "Variabile (nessun valore riconosciuto)."
            elif card == "GW" and no in wires:
                w = wires[no]
                item["tag"] = w.tag
                note = (f"Filo {w.tag}: {w.segs} segment{'o' if w.segs == 1 else 'i'}, da {_mm(w.p1)} a {_mm(w.p2)}"
                        f" — diametro {w.r * 2000:.1f} mm, lunghezza {math.dist(w.p1, w.p2) * 1000:.1f} mm.")
            elif card == "GS":
                note = f"Fattore di scala ×{n(2, 1.0):g} applicato ai fili definiti sopra."
            elif card == "GE":
                note = "Fine della geometria." + (
                    " I fili che toccano z = 0 sono collegati al terreno." if int(n(0)) == 1 else "")
            elif card == "EK":
                note = "Kernel per fili spessi (extended thin-wire kernel): più preciso quando il diametro non è trascurabile."
            elif card == "GN":
                note = {-1: "Nessun terreno: simulazione in spazio libero.",
                        0: "Terreno reale (dielettrico con perdite), approssimazione di riflessione.",
                        1: "Terreno modellato come conduttore perfetto.",
                        2: "Terreno reale con il metodo di Sommerfeld/Norton."}.get(int(n(0)), f"Terreno tipo {int(n(0))}.")
            elif card == "EX":
                item["tag"] = int(n(1))
                note = f"Alimentazione: sul filo {int(n(1))}, segmento {int(n(2))} — qui si collega il cavo."
            elif card == "LD":
                kind = {0: "R-L-C in serie", 1: "R-L-C in parallelo", 4: "impedenza fissa",
                        5: "conducibilità del metallo"}.get(int(n(0)), f"tipo {int(n(0))}")
                where = f"sul filo {int(n(1))}" if int(n(1)) else "su tutti i fili"
                note = f"Carico ({kind}) {where}" + (f": σ = {n(4):.3g} S/m." if int(n(0)) == 5 else ".")
            elif card == "TL":
                note = (f"Linea di trasmissione da {abs(n(4)):g} Ω fra filo {int(n(0))} seg. {int(n(1))} e filo "
                        f"{int(n(2))} seg. {int(n(3))}" + (f", lunga {n(5) * 1000:.1f} mm." if n(5) else
                                                          ", lunga quanto la distanza fra i due segmenti."))
            elif card == "NT":
                note = f"Rete a due porte fra filo {int(n(0))} seg. {int(n(1))} e filo {int(n(2))} seg. {int(n(3))}."
            elif card == "FR":
                note = (f"Frequenza nel file originale: {n(4):g} MHz — la galleria la ignora e simula sempre "
                        f"a {f0_label} MHz (preset italiano), con una scansione {sweep_label} MHz.")
            elif card in IGNORED:
                note = "Ignorata dalla galleria: il diagramma di irradiazione lo calcola il generatore del sito."
            elif card == "EN":
                note = "Fine del file."
            else:
                note = "Scheda non riconosciuta da questo lettore."
        except Exception:  # noqa: BLE001
            note = "Riga non interpretabile automaticamente."
        item["note"] = note
    return out
