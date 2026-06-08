"""Benchmark de référence : « acheter et garder » (buy & hold).

La comparaison qui donne du sens à toute stratégie : si rester investi sans rien
faire rapporte autant ou plus, alors les signaux de la stratégie n'apportent rien.

On compare « 1$ investi via la stratégie » vs « 1$ investi le 1er jour et gardé ».
Nuance : la stratégie n'est en position qu'une partie du temps (le reste en cash à 0%),
tandis que le buy & hold est investi en permanence. C'est la comparaison honnête.
"""
from __future__ import annotations

import pandas as pd


def buy_and_hold(df: pd.DataFrame, end: pd.Timestamp | None = None) -> dict:
    """Rendement total d'un achat au premier jour, gardé jusqu'au dernier.

    Si `end` est fourni, on tronque l'historique à cette date — utile pour comparer
    à période ÉGALE avec la stratégie (en retirant la dernière évolution non clôturée).
    """
    close = df["Close"].dropna()
    if end is not None:
        close = close[close.index <= end]
    if close.empty:
        return {}
    start_price = float(close.iloc[0])
    end_price = float(close.iloc[-1])
    return {
        "start_date": close.index[0].strftime("%Y-%m-%d"),
        "end_date": close.index[-1].strftime("%Y-%m-%d"),
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "total_return": round(end_price / start_price - 1.0, 4),
    }
