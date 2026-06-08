"""Configuration centrale : tickers et paramètres.

La liste de tickers est un PARAMÈTRE, jamais codée en dur ailleurs. Passer du
prototype (10 valeurs) au S&P 500 = remplacer cette liste, rien d'autre.
"""
from __future__ import annotations

from pathlib import Path

# --- Répertoires (créés au runtime) ---
ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "data_cache"      # cache Parquet des données téléchargées
OUTPUT_DIR = ROOT / "output"         # graphiques + résultats

# --- Univers ---
# Prototype : 10 valeurs liquides. Plus tard : une fonction load_sp500().
TICKERS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AMD", "NFLX", "JPM"]

# --- Période d'historique (daily) ---
START = "2010-01-01"
END = None  # None = jusqu'à aujourd'hui

# --- Paramètres stratégie croisement de moyennes mobiles ---
MA_SHORT = 50   # moyenne mobile courte (réagit vite)
MA_LONG = 200   # moyenne mobile longue (tendance de fond)

# --- Paramètres stratégie RSI (Relative Strength Index) ---
RSI_PERIOD = 14   # fenêtre standard de Wilder (jours)
