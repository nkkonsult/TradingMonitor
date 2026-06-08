"""Statistiques : agrège les résultats d'un backtest en métriques de comparaison.

Ce sont ces métriques qui, plus tard, alimenteront les tests (ANOVA/Welch/chi2)
pour comparer les stratégies entre elles.
"""
from __future__ import annotations

import pandas as pd


def summarize(trades_df: pd.DataFrame) -> dict:
    """Résume une table de trades en métriques clés."""
    if trades_df.empty:
        return {"n_trades": 0}

    r = trades_df["return_pct"]
    return {
        "n_trades": int(len(r)),
        "taux_reussite": round(float((r > 0).mean()), 4),
        "rendement_moyen": round(float(r.mean()), 4),
        "rendement_median": round(float(r.median()), 4),
        "rendement_total_cumule": round(float((1 + r).prod() - 1), 4),
        "meilleur": round(float(r.max()), 4),
        "pire": round(float(r.min()), 4),
        "duree_moyenne_jours": round(float(trades_df["holding_days"].mean()), 1),
    }
