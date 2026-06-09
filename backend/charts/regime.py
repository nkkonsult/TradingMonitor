"""Régime de marché : étiquette chaque date en « haussier » ou « baissier ».

Défini QUANTITATIVEMENT (pas par le LLM) et de façon CAUSALE : haussier si l'indice
S&P 500 clôture au-dessus de sa moyenne mobile longue (MM200), baissier sinon. La MM200
à la date t n'utilise que le passé -> aucun biais de look-ahead.

Régime UNIQUE par date, partagé par tous les titres -> idéal pour l'ANOVA stratégie×régime.
Enrichissements possibles plus tard : terciles de volatilité, Markov-switching (Hamilton).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data

INDEX_TICKER = "^GSPC"  # indice S&P 500
REGIME_MA = 200


def regime_series(ma: int = REGIME_MA) -> pd.Series:
    """Série datée du régime de marché : 'haussier' / 'baissier' (ou 'indetermine')."""
    df = data.get_ohlcv(INDEX_TICKER)
    close = df["Close"]
    mm = close.rolling(ma).mean()
    reg = pd.Series(np.where(close > mm, "haussier", "baissier"), index=close.index)
    reg[mm.isna()] = "indetermine"  # avant que la MM200 soit calculable
    return reg


def regime_at(reg: pd.Series, date) -> str:
    """Régime CONNU à la date donnée (dernière valeur <= date) -> causal."""
    try:
        val = reg.asof(date)
    except Exception:  # noqa: BLE001
        return "indetermine"
    return str(val) if val is not None and not pd.isna(val) else "indetermine"
