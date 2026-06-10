"""Stratégie : support / résistance HORIZONTAUX (canaux de Donchian) — 2 variantes.

- Résistance = plus-haut des N derniers jours ; Support = plus-bas des N derniers jours.
- Variante "breakout" (CASSURE = suiveur de tendance) : on achète quand la clôture
  franchit la résistance d'un TAMPON (anti fausse cassure / chasse au stop) ; on sort
  quand elle repasse sous le plus-bas d'une fenêtre de sortie plus courte.
- Variante "bounce" (REBOND = retour à la moyenne) : on achète quand le cours vient
  TOUCHER le support puis repart à la hausse ; on sort à la résistance, ou stop si le
  support est cassé (avec tampon, des DEUX côtés).

Le `buffer` (tampon de confirmation) est appliqué symétriquement au support ET à la
résistance, car la « chasse au stop » des gros acteurs se produit aux deux niveaux.
Tout est déterministe et reproductible ; les paramètres (n, buffer) sont balayables en
walk-forward. Niveaux OBLIQUES (lignes de tendance) = extension v2 (plus subjective).
"""
from __future__ import annotations

import pandas as pd

from ..trade import Trade

N_DEFAULT = 20      # fenêtre du canal (jours)
BUFFER = 0.005      # tampon de confirmation (0,5 %) anti fausse cassure
EXIT_N = 10         # fenêtre de sortie (canal plus court) pour la cassure


def _channels(close: pd.Series, n: int):
    """Résistance (plus-haut N j) et support (plus-bas N j), décalés d'un jour (causal)."""
    upper = close.rolling(n).max().shift(1)
    lower = close.rolling(n).min().shift(1)
    return upper, lower


def detect_trades(
    df: pd.DataFrame,
    *,
    variant: str = "breakout",
    n: int = N_DEFAULT,
    buffer: float = BUFFER,
    exit_n: int = EXIT_N,
    **_,
) -> list[Trade]:
    close = df["Close"]
    idx = df.index
    vals = close.to_numpy()
    up, lo = _channels(close, n)
    up_a, lo_a = up.to_numpy(), lo.to_numpy()
    lo_exit = close.rolling(exit_n).min().shift(1).to_numpy()
    breakout = variant == "breakout"

    trades: list[Trade] = []
    in_pos = False
    entry_date = entry_price = None
    for i in range(len(vals)):
        c = vals[i]
        if breakout:
            if not in_pos:
                if up_a[i] == up_a[i] and c > up_a[i] * (1 + buffer):  # cassure résistance
                    in_pos, entry_date, entry_price = True, idx[i], c
            elif lo_exit[i] == lo_exit[i] and c < lo_exit[i]:           # sortie de canal
                trades.append(Trade(entry_date, entry_price, idx[i], float(c), 1))
                in_pos = False
        else:  # bounce (rebond sur support)
            if not in_pos:
                # hier près du support (tampon) ET aujourd'hui ça remonte -> rebond
                if i > 0 and lo_a[i] == lo_a[i] and vals[i - 1] <= lo_a[i] * (1 + buffer) and c > vals[i - 1]:
                    in_pos, entry_date, entry_price = True, idx[i], c
            else:
                hit_resist = up_a[i] == up_a[i] and c >= up_a[i] * (1 - buffer)  # objectif = résistance
                broke_support = lo_a[i] == lo_a[i] and c < lo_a[i] * (1 - buffer)  # stop = support cassé
                if hit_resist or broke_support:
                    trades.append(Trade(entry_date, entry_price, idx[i], float(c), 1))
                    in_pos = False
    return trades


def open_entry(df: pd.DataFrame, **_):
    """On ne compte que les trades clôturés (stats propres)."""
    return None


def indicators(df: pd.DataFrame, *, n: int = N_DEFAULT, **_) -> pd.DataFrame:
    """Trace le canal : résistance (plus-haut N j) et support (plus-bas N j)."""
    upper, lower = _channels(df["Close"], n)
    return pd.DataFrame({f"Résist. {n}j": upper, f"Support {n}j": lower})
