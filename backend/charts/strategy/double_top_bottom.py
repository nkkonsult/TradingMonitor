"""Stratégie : double sommet / double creux — figure chartiste à 3 pivots.

Deux variantes via `direction` :
- "top"    (double SOMMET) : 2 pics à hauteur proche encadrant un creux ; cassure de la
  ligne de cou VERS LE BAS -> baissier -> trade SHORT (direction=-1).
- "bottom" (double CREUX)  : 2 creux à niveau proche encadrant un pic ; cassure VERS LE
  HAUT -> haussier -> trade LONG (direction=+1).

Même esprit déterministe que l'épaule-tête-épaule (extrema locaux + conditions chiffrées),
mais 3 pivots au lieu de 5. Le reste de la chaîne (backtest/stats/overlay/random) le
récupère via le contrat detect_trades / open_entry / indicators / shapes.
"""
from __future__ import annotations

import pandas as pd

from ..trade import Trade

PIVOT_WINDOW = 10       # un extremum doit dominer +/- 10 jours
LEVEL_TOL = 0.04        # les 2 sommets (ou creux) à <= 4 % l'un de l'autre
MIN_DEPTH = 0.04        # le creux (ou pic) central à au moins 4 % des extrêmes
BREAK_HORIZON = 60      # jours max après le 2e extrême pour voir la cassure
TRADE_HORIZON = 252     # jours max après la cassure pour atteindre objectif/stop


def _pivots(vals, w: int) -> list[tuple[int, int]]:
    """Extrema locaux -> (position, kind) +1 sommet / -1 creux, alternance nettoyée."""
    raw: list[tuple[int, int]] = []
    n = len(vals)
    for i in range(w, n - w):
        seg = vals[i - w : i + w + 1]
        if vals[i] == seg.max() and seg.argmax() == w:
            raw.append((i, 1))
        elif vals[i] == seg.min() and seg.argmin() == w:
            raw.append((i, -1))
    clean: list[tuple[int, int]] = []
    for p in raw:
        if clean and clean[-1][1] == p[1]:
            prev = clean[-1]
            more = (p[1] == 1 and vals[p[0]] > vals[prev[0]]) or (
                p[1] == -1 and vals[p[0]] < vals[prev[0]]
            )
            if more:
                clean[-1] = p
        else:
            clean.append(p)
    return clean


def _scan(df, direction, pivot_window, level_tol, min_depth, break_horizon, trade_horizon):
    vals = df["Close"].to_numpy()
    idx = df.index
    n = len(vals)
    bottom = direction == "bottom"
    d = 1 if bottom else -1
    start_kind = -1 if bottom else 1  # bottom: creux,pic,creux ; top: pic,creux,pic

    piv = _pivots(vals, pivot_window)
    out: list[dict] = []
    last_exit = -1

    for k in range(len(piv) - 2):
        window = piv[k : k + 3]
        if window[0][1] != start_kind:
            continue
        (e1, _), (mid, _), (e2, _) = window
        p_e1, p_mid, p_e2 = vals[e1], vals[mid], vals[e2]

        # Les deux extrêmes (sommets ou creux) à niveau proche.
        if abs(p_e1 - p_e2) > level_tol * max(p_e1, p_e2):
            continue
        # Le pivot central assez éloigné (profondeur du creux / hauteur du pic).
        if bottom:
            if (p_mid - p_e1) / p_mid < min_depth or (p_mid - p_e2) / p_mid < min_depth:
                continue
        else:
            if (p_e1 - p_mid) / p_e1 < min_depth or (p_e2 - p_mid) / p_e2 < min_depth:
                continue

        neck = float(p_mid)  # ligne de cou horizontale au niveau du pivot central
        amp = abs((p_e1 + p_e2) / 2.0 - neck)  # amplitude figure (measured move)

        # Cassure de la ligne de cou après le 2e extrême.
        break_pos = None
        for pos in range(e2 + 1, min(e2 + 1 + break_horizon, n)):
            if (bottom and vals[pos] > neck) or (not bottom and vals[pos] < neck):
                break_pos = pos
                break
        if break_pos is None or break_pos <= last_exit:
            continue

        entry_price = float(vals[break_pos])
        target = entry_price + d * amp
        stop = float(p_e1 if bottom else max(p_e1, p_e2))  # creux (bottom) / sommets (top)
        if bottom:
            stop = float(min(p_e1, p_e2))

        exit_pos = None
        for pos in range(break_pos + 1, min(break_pos + 1 + trade_horizon, n)):
            c = vals[pos]
            hit_target = (bottom and c >= target) or (not bottom and c <= target)
            hit_stop = (bottom and c <= stop) or (not bottom and c >= stop)
            if hit_target or hit_stop:
                exit_pos = pos
                break
        if exit_pos is None:
            continue

        out.append(
            {
                "direction": d,
                "entry_pos": break_pos,
                "entry_price": entry_price,
                "exit_pos": exit_pos,
                "exit_price": float(vals[exit_pos]),
                "target": float(target),
                "neck": neck,
                "first": e1,
                "extremes": [(e1, float(p_e1)), (e2, float(p_e2))],
            }
        )
        last_exit = exit_pos
    return out


def detect_trades(
    df,
    *,
    direction: str = "bottom",
    pivot_window: int = PIVOT_WINDOW,
    level_tol: float = LEVEL_TOL,
    min_depth: float = MIN_DEPTH,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[Trade]:
    idx = df.index
    recs = _scan(df, direction, pivot_window, level_tol, min_depth, break_horizon, trade_horizon)
    return [
        Trade(idx[r["entry_pos"]], r["entry_price"], idx[r["exit_pos"]], r["exit_price"], direction=r["direction"])
        for r in recs
    ]


def shapes(
    df,
    *,
    direction: str = "bottom",
    pivot_window: int = PIVOT_WINDOW,
    level_tol: float = LEVEL_TOL,
    min_depth: float = MIN_DEPTH,
    break_horizon: int = BREAK_HORIZON,
    trade_horizon: int = TRADE_HORIZON,
    **_,
) -> list[dict]:
    idx = df.index
    fmt = lambda pos: idx[pos].strftime("%Y-%m-%d")  # noqa: E731
    recs = _scan(df, direction, pivot_window, level_tol, min_depth, break_horizon, trade_horizon)
    out = []
    for r in recs:
        out.append(
            {
                "neckline": [
                    {"date": fmt(r["first"]), "price": round(r["neck"], 2)},
                    {"date": fmt(r["exit_pos"]), "price": round(r["neck"], 2)},
                ],
                "target": {
                    "price": round(r["target"], 2),
                    "from": fmt(r["entry_pos"]),
                    "to": fmt(r["exit_pos"]),
                },
                "head": None,  # pas de « tête » dans un double sommet/creux
                "shoulders": [{"date": fmt(p), "price": round(v, 2)} for p, v in r["extremes"]],
            }
        )
    return out


def open_entry(df, **_):
    return None


def indicators(df, **_) -> pd.DataFrame:
    return pd.DataFrame(index=df.index)
