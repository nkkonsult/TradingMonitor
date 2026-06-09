"""Scan batch : transforme (tickers × stratégies) en lignes de détection enrichies.

Une ligne = un trade clôturé, avec tout ce qu'il faut pour les tests statistiques
ultérieurs SANS recalcul (cf. menu d'analyses) :
- return_net (stratégie, coûts déduits) ET bh_return_window (buy & hold sur la MÊME
  fenêtre, même titre) -> test APPARIÉ stratégie vs buy&hold ;
- regime_entry (haussier/baissier) -> ANOVA stratégie×régime ;
- sector -> analyse par secteur ;
- trade_drawdown -> dimension risque (pas que le rendement).

Tout est calculé sur les données DÉJÀ EN CACHE -> pur calcul, rapide même sur 500 titres.
"""
from __future__ import annotations

import pandas as pd

from . import config, data, regime as regime_mod
from .registry import PARAMS_VERSION, STRATEGIES


def _bh_return_window(close: pd.Series, entry_date, exit_date) -> float:
    """Rendement BRUT du buy & hold du titre sur la fenêtre exacte du trade (apparié)."""
    return float(close.loc[exit_date] / close.loc[entry_date] - 1.0)


def _trade_drawdown(close: pd.Series, entry_date, exit_date, direction: int) -> float:
    """Pire creux (peak-to-trough) de la POSITION pendant le trade. <= 0."""
    seg = close.loc[entry_date:exit_date]
    if len(seg) < 2:
        return 0.0
    base = float(seg.iloc[0])
    # Valeur de la position : monte avec le prix en long, baisse en short.
    path = 1.0 + direction * (seg / base - 1.0)
    peak = path.cummax()
    return float((path / peak - 1.0).min())


def scan_ticker(
    ticker: str,
    reg: pd.Series,
    sectors: dict[str, str],
    cost: float = config.COST_PER_SIDE,
) -> list[dict]:
    """Toutes les stratégies sur un titre -> liste de lignes (1 par trade clôturé)."""
    df = data.get_ohlcv(ticker)
    close = df["Close"]
    sector = sectors.get(ticker, "?")
    rows: list[dict] = []

    for key, (strat, _label, params) in STRATEGIES.items():
        call = {"short": config.MA_SHORT, "long": config.MA_LONG, **params}
        for t in strat.detect_trades(df, **call):
            rows.append(
                {
                    "ticker": ticker,
                    "sector": sector,
                    "strategy": key,
                    "params_version": PARAMS_VERSION,
                    "direction": t.direction,
                    "entry_date": t.entry_date.strftime("%Y-%m-%d"),
                    "exit_date": t.exit_date.strftime("%Y-%m-%d"),
                    "holding_days": t.holding_days,
                    "entry_price": round(t.entry_price, 4),
                    "exit_price": round(t.exit_price, 4),
                    "return_gross": round(t.return_pct, 6),
                    "return_net": round(t.net_return(cost), 6),
                    "bh_return_window": round(_bh_return_window(close, t.entry_date, t.exit_date), 6),
                    "trade_drawdown": round(_trade_drawdown(close, t.entry_date, t.exit_date, t.direction), 6),
                    "regime_entry": regime_mod.regime_at(reg, t.entry_date),
                }
            )
    return rows


def scan_universe(
    tickers: list[str],
    cost: float = config.COST_PER_SIDE,
    log_every: int = 50,
) -> pd.DataFrame:
    """Scan complet -> DataFrame (1 ligne/trade). Un titre en échec est ignoré."""
    from . import universe

    reg = regime_mod.regime_series()
    sectors = universe.load_sectors()
    rows: list[dict] = []
    failed: list[str] = []
    total = len(tickers)
    for i, tk in enumerate(tickers, 1):
        try:
            rows.extend(scan_ticker(tk, reg, sectors, cost))
        except Exception as e:  # noqa: BLE001
            failed.append(f"{tk}: {e}")
        if log_every and (i % log_every == 0 or i == total):
            print(f"[scan] {i}/{total} — {len(rows)} trades, {len(failed)} échecs", flush=True)
    if failed:
        print(f"[scan] échecs : {failed[:10]}{' …' if len(failed) > 10 else ''}", flush=True)
    return pd.DataFrame(rows)
