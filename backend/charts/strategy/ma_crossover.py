"""Stratégie : croisement de moyennes mobiles (golden cross / death cross).

- MM courte passe AU-DESSUS de la MM longue -> golden cross -> achat.
- MM courte passe EN-DESSOUS -> death cross -> vente.

Détection 100% déterministe (comparaison de nombres) -> reproductible -> stats valides.
"""
from __future__ import annotations

import pandas as pd

from .. import config
from ..trade import Trade


def indicators(df: pd.DataFrame, short: int = config.MA_SHORT, long: int = config.MA_LONG, **_) -> pd.DataFrame:
    """Renvoie les deux moyennes mobiles (utile pour le tracé)."""
    close = df["Close"]
    return pd.DataFrame(
        {
            f"MM{short}": close.rolling(short).mean(),
            f"MM{long}": close.rolling(long).mean(),
        }
    )


def detect_trades(df: pd.DataFrame, short: int = config.MA_SHORT, long: int = config.MA_LONG, **_) -> list[Trade]:
    """Détecte les trades : achat au golden cross, vente au death cross suivant."""
    close = df["Close"]
    ma_short = close.rolling(short).mean()
    ma_long = close.rolling(long).mean()

    # État visé : 1 si MM courte > MM longue (on veut être en position), sinon 0.
    state = (ma_short > ma_long).astype(int)
    # Un croisement = un changement d'état : +1 golden cross, -1 death cross.
    cross = state.diff()

    trades: list[Trade] = []
    entry_date = None
    entry_price = None
    for date, c in cross.items():
        if c == 1:  # golden cross -> on achète
            entry_date = date
            entry_price = float(close.loc[date])
        elif c == -1 and entry_date is not None:  # death cross -> on vend
            trades.append(Trade(entry_date, entry_price, date, float(close.loc[date])))
            entry_date = None
            entry_price = None

    # Note : si une position est encore ouverte à la fin de l'historique, on ne la
    # comptabilise pas (trade non clôturé). Choix volontaire pour des stats propres.
    return trades


def open_entry(df: pd.DataFrame, short: int = config.MA_SHORT, long: int = config.MA_LONG, **_):
    """Renvoie (date, prix) de la dernière entrée NON clôturée, ou None.

    C'est le golden cross le plus récent sans death cross derrière : la position
    est encore ouverte en fin d'historique. Exclue des stats (pas de rendement),
    mais on l'affiche sur le graphique pour qu'il colle aux moyennes mobiles.
    """
    close = df["Close"]
    ma_short = close.rolling(short).mean()
    ma_long = close.rolling(long).mean()
    cross = (ma_short > ma_long).astype(int).diff()

    last_entry = None
    for date, c in cross.items():
        if c == 1:
            last_entry = (date, float(close.loc[date]))
        elif c == -1:
            last_entry = None
    return last_entry
