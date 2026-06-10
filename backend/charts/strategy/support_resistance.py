"""Stratégie : VRAIS supports / résistances HORIZONTAUX (droites), par touches répétées.

Principe attendu par un trader (≠ canaux glissants) : on repère les sommets et les creux
locaux, et lorsque PLUSIEURS d'entre eux tombent au MÊME prix (à une tolérance près), on
trace une DROITE HORIZONTALE = une résistance (sommets) ou un support (creux). Plus il y a
de « touches », plus le niveau est crédible.

Deux usages (mêmes droites) :
- "breakout" (CASSURE = tendance) : on achète quand le cours franchit une RÉSISTANCE
  d'un tampon de confirmation (anti fausse cassure / chasse au stop).
- "bounce" (REBOND = retour à la moyenne) : on achète quand le cours vient TOUCHER un
  SUPPORT et repart ; objectif = la résistance, stop = sous le support (tampon des 2 côtés).

Niveaux OBLIQUES (lignes de tendance) = extension v2 (plus subjective).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..trade import Trade

PIVOT_WINDOW = 10     # un sommet/creux doit dominer +/- 10 jours
LEVEL_TOL = 0.02      # 2 % : deux touches « au même prix » si à <= 2 % l'une de l'autre
MIN_TOUCHES = 3       # nombre de touches pour valider un niveau (>= 3 = niveau crédible)
BUFFER = 0.005        # tampon de confirmation (anti chasse-au-stop), des 2 côtés
TARGET = 0.10         # objectif de sortie (+/- 10 %)
BREAK_HORIZON = 120   # jours max après validation du niveau pour le signal
TRADE_HORIZON = 252   # jours max pour atteindre objectif/stop


def _pivots(vals, w):
    """Renvoie (positions des sommets, positions des creux) locaux."""
    highs, lows = [], []
    for i in range(w, len(vals) - w):
        seg = vals[i - w : i + w + 1]
        if vals[i] == seg.max() and seg.argmax() == w:
            highs.append(i)
        elif vals[i] == seg.min() and seg.argmin() == w:
            lows.append(i)
    return highs, lows


def _levels(vals, positions, tol, min_touches, kind):
    """Regroupe des pivots de MÊME prix (à `tol` près) en niveaux horizontaux.

    `kind` = +1 (résistance, sommets) / -1 (support, creux). Condition supplémentaire :
    entre les touches qui valident le niveau, le cours ne doit PAS traverser la droite
    (sinon le niveau a déjà été cassé → invalide).
    """
    pts = sorted(positions, key=lambda p: vals[p])  # tri par prix
    out, i = [], 0
    while i < len(pts):
        group = [pts[i]]
        base = vals[pts[i]]
        j = i + 1
        while j < len(pts) and vals[pts[j]] <= base * (1 + tol):
            group.append(pts[j])
            j += 1
        if len(group) >= min_touches:
            touches = sorted(group)  # chronologique
            conf = touches[:min_touches]               # les touches qui valident
            price = float(np.mean([vals[p] for p in group]))
            span = vals[conf[0] : conf[-1] + 1]        # entre 1re et N-ième touche
            no_cross = span.max() <= price * (1 + tol) if kind == 1 else span.min() >= price * (1 - tol)
            if no_cross:
                out.append({"price": price, "activate": conf[-1], "touches": touches})
        i = j
    return out


def _scan(df, variant, pivot_window, tol, min_touches, buffer, target, break_horizon, trade_horizon):
    vals = df["Close"].to_numpy()
    n = len(vals)
    highs, lows = _pivots(vals, pivot_window)
    is_break = variant == "breakout"
    levels = _levels(vals, highs if is_break else lows, tol, min_touches, 1 if is_break else -1)
    levels.sort(key=lambda L: L["activate"])

    recs, last_exit = [], -1
    for L in levels:
        price, act = L["price"], L["activate"]
        # signal d'entrée après validation du niveau
        entry = None
        for i in range(max(act + 1, last_exit + 1), min(act + 1 + break_horizon, n)):
            if is_break:
                if vals[i] > price * (1 + buffer):       # cassure de la résistance
                    entry = i
                    break
            else:
                if i > 0 and vals[i - 1] <= price * (1 + buffer) and vals[i] > vals[i - 1]:  # rebond sur support
                    entry = i
                    break
        if entry is None:
            continue
        ep = float(vals[entry])
        tgt = ep * (1 + target)
        stop = price * (1 - buffer) if not is_break else price  # sous le support / retour sous la résistance
        exit_i = None
        for i in range(entry + 1, min(entry + 1 + trade_horizon, n)):
            if vals[i] >= tgt or vals[i] <= stop:
                exit_i = i
                break
        if exit_i is None:
            continue
        recs.append({
            "entry_pos": entry, "entry_price": ep, "exit_pos": exit_i, "exit_price": float(vals[exit_i]),
            "level": price, "target": tgt,
            "touches": L["touches"], "act": act,
        })
        last_exit = exit_i
    return recs


def detect_trades(
    df,
    *,
    variant: str = "breakout",
    pivot_window: int = PIVOT_WINDOW,
    tol: float = LEVEL_TOL,
    min_touches: int = MIN_TOUCHES,
    buffer: float = BUFFER,
    target: float = TARGET,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[Trade]:
    idx = df.index
    recs = _scan(df, variant, pivot_window, tol, min_touches, buffer, target, break_horizon, trade_horizon)
    return [Trade(idx[r["entry_pos"]], r["entry_price"], idx[r["exit_pos"]], r["exit_price"], 1) for r in recs]


def shapes(
    df,
    *,
    variant: str = "breakout",
    pivot_window: int = PIVOT_WINDOW,
    tol: float = LEVEL_TOL,
    min_touches: int = MIN_TOUCHES,
    buffer: float = BUFFER,
    target: float = TARGET,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[dict]:
    """Chaque niveau = une DROITE HORIZONTALE (de la 1re touche à la sortie) + les touches."""
    idx = df.index
    fmt = lambda p: idx[p].strftime("%Y-%m-%d")  # noqa: E731
    recs = _scan(df, variant, pivot_window, tol, min_touches, buffer, target, break_horizon, trade_horizon)
    out = []
    for r in recs:
        lvl = round(r["level"], 2)
        out.append({
            "neckline": [{"date": fmt(r["touches"][0]), "price": lvl}, {"date": fmt(r["exit_pos"]), "price": lvl}],
            "target": {"price": round(r["target"], 2), "from": fmt(r["entry_pos"]), "to": fmt(r["exit_pos"])},
            "head": None,
            "shoulders": [{"date": fmt(p), "price": lvl} for p in r["touches"]],
        })
    return out


def open_entry(df, **_):
    return None


def indicators(df, **_) -> pd.DataFrame:
    """Pas d'overlay continu : les niveaux sont des DROITES (via shapes)."""
    return pd.DataFrame(index=df.index)
