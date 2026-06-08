"""Couche données : télécharge l'OHLCV journalier (yfinance) et le met en cache (Parquet).

Le cache disque est essentiel : il évite de re-télécharger à chaque exécution, ce qui
rend indolore le passage de 10 à 500 tickers (on ne télécharge chaque ticker qu'une fois).
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf

from . import config


def _cache_path(ticker: str, start: str, end: str | None):
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tag = f"{ticker}_{start}_{end or 'latest'}.parquet"
    return config.CACHE_DIR / tag


def get_ohlcv(
    ticker: str,
    start: str = config.START,
    end: str | None = config.END,
    refresh: bool = False,
) -> pd.DataFrame:
    """Renvoie un DataFrame OHLCV journalier (index = Date).

    Colonnes : Open, High, Low, Close, Volume. Prix ajustés (dividendes/splits).
    Utilise le cache Parquet si présent, sauf si refresh=True.
    """
    path = _cache_path(ticker, start, end)
    if path.exists() and not refresh:
        return pd.read_parquet(path)

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df is None or df.empty:
        raise ValueError(f"Aucune donnée téléchargée pour {ticker}")

    # yfinance renvoie un MultiIndex de colonnes ; on l'aplatit.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index.name = "Date"
    df.to_parquet(path)
    return df
