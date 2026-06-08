"""Point d'entrée : lance la chaîne complète sur 1 ticker, ou sur toute la liste.

Usage :
    python -m charts.run AAPL        # un ticker, avec graphique
    python -m charts.run --all       # tous les tickers de config.TICKERS (tableau)
"""
from __future__ import annotations

import argparse

import pandas as pd

from . import backtest, config, data, render, stats
from .strategy import ma_crossover


def run_one(ticker: str, plot: bool = True):
    """Chaîne complète pour un ticker : data -> détection -> backtest -> stats -> tracé."""
    df = data.get_ohlcv(ticker)
    trades = ma_crossover.detect_trades(df)
    trades_df = backtest.to_dataframe(trades)
    metrics = stats.summarize(trades_df)
    chart = render.plot_ma_crossover(ticker, df, trades) if plot else None
    return metrics, chart, trades_df


def run_all(tickers: list[str] | None = None) -> pd.DataFrame:
    """Backtest sur toute la liste -> un DataFrame récapitulatif (1 ligne/ticker)."""
    tickers = tickers or config.TICKERS
    rows = []
    for tk in tickers:
        try:
            metrics, _, _ = run_one(tk, plot=False)
            metrics["ticker"] = tk
            rows.append(metrics)
        except Exception as e:  # noqa: BLE001
            print(f"[!] {tk} ignoré : {e}")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest croisement de moyennes mobiles")
    parser.add_argument("ticker", nargs="?", default="AAPL", help="Ticker (défaut: AAPL)")
    parser.add_argument("--all", action="store_true", help="Lancer sur toute la liste")
    args = parser.parse_args()

    if args.all:
        recap = run_all()
        cols = ["ticker", "n_trades", "taux_reussite", "rendement_moyen", "rendement_total_cumule"]
        print(recap[cols].to_string(index=False))
    else:
        metrics, chart, _ = run_one(args.ticker)
        print(f"\n=== {args.ticker} : croisement MM{config.MA_SHORT}/MM{config.MA_LONG} ===")
        for k, v in metrics.items():
            print(f"  {k:24s}: {v}")
        print(f"  {'graphique':24s}: {chart}")
