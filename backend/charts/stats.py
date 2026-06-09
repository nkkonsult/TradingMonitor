"""Statistiques : agrège les résultats d'un backtest en métriques de comparaison.

Deux familles de métriques, deux sources de données différentes :
- `summarize(trades_df)` : métriques AU NIVEAU TRADE (liste des trades) — win rate,
  rendement moyen, profit factor, expectancy.
- `summarize_equity(equity)` : métriques AU NIVEAU SÉRIE TEMPORELLE (courbe d'equity
  jour par jour) — CAGR, volatilité, Sharpe, Sortino, Calmar, Max Drawdown, VaR.
  Ces ratios annualisés/ajustés du risque EXIGENT la trajectoire dans le temps, ils
  ne sont pas calculables à partir des seuls trades.

Ce sont ces métriques qui, plus tard, alimenteront les tests (ANOVA/Welch/chi2)
pour comparer les stratégies entre elles.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

# Conventions (standards, modifiables) : jours de bourse/an, taux sans risque, niveau VaR.
TRADING_DAYS = 252
RISK_FREE_ANNUAL = 0.0
VAR_LEVEL = 0.05  # VaR historique à 95 % = quantile 5 % des rendements quotidiens


def summarize(trades_df: pd.DataFrame) -> dict:
    """Résume une table de trades en métriques de NIVEAU TRADE."""
    if trades_df.empty:
        return {"n_trades": 0}

    r = trades_df["return_pct"]
    gains = float(r[r > 0].sum())
    losses = float(-r[r < 0].sum())  # somme des pertes, en positif
    # Profit factor = gains bruts / pertes brutes (>1 = profitable). None si aucune perte.
    profit_factor = round(gains / losses, 3) if losses > 0 else None
    return {
        "n_trades": int(len(r)),
        "taux_reussite": round(float((r > 0).mean()), 4),
        "rendement_moyen": round(float(r.mean()), 4),
        "rendement_median": round(float(r.median()), 4),
        "rendement_total_cumule": round(float((1 + r).prod() - 1), 4),
        "meilleur": round(float(r.max()), 4),
        "pire": round(float(r.min()), 4),
        "duree_moyenne_jours": round(float(trades_df["holding_days"].mean()), 1),
        "profit_factor": profit_factor,
        # Expectancy = espérance de gain par trade (= rendement_moyen, exposé explicitement).
        "expectancy": round(float(r.mean()), 4),
    }


def _r(x: float, n: int = 4) -> float | None:
    """Arrondi sûr : None si non-fini (NaN/inf), pour un JSON propre."""
    if x is None or not math.isfinite(x):
        return None
    return round(float(x), n)


def summarize_equity(
    equity,
    periods_per_year: int = TRADING_DAYS,
    risk_free_annual: float = RISK_FREE_ANNUAL,
    var_level: float = VAR_LEVEL,
) -> dict:
    """Métriques de NIVEAU SÉRIE TEMPORELLE depuis une courbe d'equity jour par jour.

    `equity` = suite de valeurs du portefeuille (base 100), alignée sur les jours de
    bourse. Jours hors position = valeur plate (rendement 0) : c'est la stratégie
    vue comme une ALLOCATION (cash quand pas en position), la comparaison honnête
    face au buy & hold (toujours investi).
    """
    eq = pd.Series(list(equity), dtype="float64").dropna()
    if len(eq) < 2:
        return {}

    daily = eq.pct_change().dropna()
    n_years = len(eq) / periods_per_year

    # CAGR = taux de croissance annuel composé.
    total_growth = float(eq.iloc[-1] / eq.iloc[0])
    cagr = total_growth ** (1.0 / n_years) - 1.0 if n_years > 0 and total_growth > 0 else float("nan")

    sd = float(daily.std(ddof=1))
    vol_annual = sd * math.sqrt(periods_per_year) if sd > 0 else float("nan")

    rf_daily = risk_free_annual / periods_per_year
    excess = daily - rf_daily
    # Sharpe = rendement excédentaire / risque total, annualisé.
    sharpe = (excess.mean() / sd) * math.sqrt(periods_per_year) if sd > 0 else float("nan")

    # Sortino = idem mais ne pénalise que la volatilité À LA BAISSE (downside deviation).
    downside = daily[daily < 0]
    dd_std = math.sqrt(float((downside ** 2).mean())) if len(downside) > 0 else 0.0
    sortino = (excess.mean() / dd_std) * math.sqrt(periods_per_year) if dd_std > 0 else float("nan")

    # Max Drawdown = pire perte depuis un plus-haut (sur la courbe d'equity).
    cummax = eq.cummax()
    drawdown = eq / cummax - 1.0
    max_dd = float(drawdown.min())

    # Calmar = CAGR / |Max DD| : rendement rapporté au pire creux subi.
    calmar = cagr / abs(max_dd) if max_dd < 0 and math.isfinite(cagr) else float("nan")

    # VaR historique : perte quotidienne au quantile (négatif), sur les jours actifs.
    active = daily[daily != 0.0]
    var = float(np.quantile(active, var_level)) if len(active) > 0 else float("nan")

    return {
        "cagr": _r(cagr),
        "volatilite_annuelle": _r(vol_annual),
        "sharpe": _r(sharpe, 3),
        "sortino": _r(sortino, 3),
        "calmar": _r(calmar, 3),
        "max_drawdown": _r(max_dd),
        "var_95": _r(var),
    }
