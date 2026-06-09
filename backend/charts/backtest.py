"""Backtest : transforme une liste de Trade en table analysable (1 ligne / trade).

Totalement indépendant de la stratégie — il ne connaît que le type Trade.
"""
from __future__ import annotations

import pandas as pd

from .trade import Trade


def to_dataframe(trades: list[Trade], cost_per_side: float = 0.0) -> pd.DataFrame:
    """Convertit la liste de Trade en DataFrame (une ligne par trade).

    `return_pct` est NET de coûts (colonne utilisée par les stats) ; `gross_return_pct`
    conserve le brut pour référence. cost_per_side=0 -> net == brut.
    """
    rows = [
        {
            "entry_date": t.entry_date,
            "exit_date": t.exit_date,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "return_pct": t.net_return(cost_per_side),
            "gross_return_pct": t.return_pct,
            "holding_days": t.holding_days,
        }
        for t in trades
    ]
    return pd.DataFrame(rows)
