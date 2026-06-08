"""Stratégie : RSI (Relative Strength Index) — retour à la moyenne.

Idée : le RSI mesure si un titre est en SURVENTE (<seuil bas) ou SURACHAT (>seuil haut).
- Achat quand le RSI REPASSE AU-DESSUS du seuil bas (il sort de la survente).
- Vente quand le RSI REPASSE SOUS le seuil haut (il sort du surachat).

Un seul module paramétrable -> trois variantes déclarées dans le registre de
`app/analysis.py` (le reste de la chaîne backtest/stats/render ne change pas) :
- RSI 30/70   (classique)
- RSI 20/80   (seuils stricts, moins de trades)
- RSI 30/70 + filtre MM : on n'achète QUE si le cours est au-dessus de sa MM longue
  (évite d'attraper un couteau qui tombe en plein marché baissier).

Détection 100% déterministe (comparaison de nombres) -> reproductible -> stats valides.
Le calcul du RSI utilise le lissage de Wilder (EMA, alpha = 1/period), la convention standard.
"""
from __future__ import annotations

import pandas as pd

from .. import config
from ..trade import Trade


def rsi_series(close: pd.Series, period: int = config.RSI_PERIOD) -> pd.Series:
    """RSI de Wilder. Renvoie une série 0-100 (NaN tant que la fenêtre n'est pas pleine)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    # Lissage de Wilder = moyenne mobile exponentielle avec alpha = 1/period.
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100.0 - 100.0 / (1.0 + rs)
    # avg_loss == 0 (que des hausses) -> rs = inf -> rsi = 100 : pandas le gère déjà.
    return rsi


def _signals(
    df: pd.DataFrame,
    lower: float,
    upper: float,
    trend_ma: int | None,
    period: int,
):
    """Génère les bascules d'état (0 hors position / 1 en position) pas à pas.

    Renvoie un itérable (date, action) où action vaut +1 (entrée) ou -1 (sortie).
    Centralise la logique pour que detect_trades et open_entry restent cohérents.
    """
    close = df["Close"]
    rsi = rsi_series(close, period)
    prev = rsi.shift(1)

    # Filtre de tendance optionnel : autorise l'achat seulement au-dessus de la MM.
    if trend_ma is not None:
        trend_ok = close > close.rolling(trend_ma).mean()
    else:
        trend_ok = pd.Series(True, index=close.index)

    # Entrée : le RSI repasse au-dessus du seuil bas (sortie de survente).
    cross_up = (prev <= lower) & (rsi > lower) & trend_ok
    # Sortie : le RSI repasse sous le seuil haut (sortie de surachat).
    cross_down = (prev >= upper) & (rsi < upper)

    in_pos = False
    for date in close.index:
        if not in_pos and bool(cross_up.get(date, False)):
            in_pos = True
            yield date, 1
        elif in_pos and bool(cross_down.get(date, False)):
            in_pos = False
            yield date, -1


def detect_trades(
    df: pd.DataFrame,
    *,
    lower: float = 30.0,
    upper: float = 70.0,
    trend_ma: int | None = None,
    period: int = config.RSI_PERIOD,
    **_,
) -> list[Trade]:
    """Trades clôturés : achat en sortie de survente, vente en sortie de surachat."""
    close = df["Close"]
    trades: list[Trade] = []
    entry_date = entry_price = None
    for date, action in _signals(df, lower, upper, trend_ma, period):
        if action == 1:
            entry_date = date
            entry_price = float(close.loc[date])
        elif action == -1 and entry_date is not None:
            trades.append(Trade(entry_date, entry_price, date, float(close.loc[date])))
            entry_date = entry_price = None
    # Position encore ouverte en fin d'historique -> non comptabilisée (stats propres).
    return trades


def open_entry(
    df: pd.DataFrame,
    *,
    lower: float = 30.0,
    upper: float = 70.0,
    trend_ma: int | None = None,
    period: int = config.RSI_PERIOD,
    **_,
):
    """(date, prix) de la dernière entrée NON clôturée, ou None."""
    close = df["Close"]
    last_entry = None
    for date, action in _signals(df, lower, upper, trend_ma, period):
        if action == 1:
            last_entry = (date, float(close.loc[date]))
        elif action == -1:
            last_entry = None
    return last_entry


def oscillator(
    df: pd.DataFrame,
    *,
    lower: float = 30.0,
    upper: float = 70.0,
    period: int = config.RSI_PERIOD,
    **_,
) -> dict:
    """Données du panneau RSI séparé (échelle 0-100) : courbe + seuils à tracer.

    Le RSI n'est PAS traçable sur l'axe des prix -> le front l'affiche dans un
    panneau dédié sous le cours, avec les droites horizontales `lower`/`upper`.
    """
    rsi = rsi_series(df["Close"], period)
    return {
        "name": f"RSI{period}",
        "data": [None if pd.isna(v) else round(float(v), 2) for v in rsi],
        "lower": lower,
        "upper": upper,
    }


def indicators(
    df: pd.DataFrame,
    *,
    lower: float = 30.0,
    upper: float = 70.0,
    trend_ma: int | None = None,
    period: int = config.RSI_PERIOD,
    **_,
) -> pd.DataFrame:
    """Overlays à tracer sur l'axe des PRIX.

    Le RSI est un oscillateur 0-100 (autre échelle) -> pas traçable sur l'axe du cours,
    on ne renvoie donc que la MM de tendance quand la variante l'utilise. Sinon vide :
    le graphique montre les repères d'achat/vente, suffisant pour cette stratégie.
    """
    if trend_ma is not None:
        return pd.DataFrame({f"MM{trend_ma}": df["Close"].rolling(trend_ma).mean()})
    return pd.DataFrame(index=df.index)
