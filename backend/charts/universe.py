"""Univers de tickers : liste du S&P 500 (source gratuite) + cache disque.

Passage du prototype (10 valeurs) à l'étude statistique (~500). La liste est mise en
cache pour ne pas dépendre du réseau à chaque exécution.

⚠️ BIAIS DU SURVIVANT à signaler dans le rapport : on récupère les constituants
ACTUELS du S&P 500. Les sociétés sorties de l'indice (faillite, rachat, relégation)
manquent → l'échantillon est biaisé vers les survivantes. Pour une étude rigoureuse il
faudrait l'historique des constituants à chaque date ; ici on l'assume et on le mentionne.
"""
from __future__ import annotations

import io

import httpx
import pandas as pd

from . import config

# Source gratuite, sans clé : constituants S&P 500 maintenus sur datahub (GitHub).
SP500_CSV_URL = (
    "https://raw.githubusercontent.com/datasets/"
    "s-and-p-500-companies/main/data/constituents.csv"
)


def _cache_file():
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return config.CACHE_DIR / "sp500_constituents.csv"


def load_sp500(refresh: bool = False) -> list[str]:
    """Liste des tickers du S&P 500 (mise en cache disque).

    Convertit la notation des actions à classes (ex. BRK.B) vers celle de yfinance
    (BRK-B). `refresh=True` force le re-téléchargement de la liste.
    """
    path = _cache_file()
    if path.exists() and not refresh:
        df = pd.read_csv(path)
    else:
        resp = httpx.get(SP500_CSV_URL, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        df.to_csv(path, index=False)

    syms = df["Symbol"].astype(str).str.strip().str.replace(".", "-", regex=False)
    return sorted(s for s in syms if s and s.lower() != "nan")


def load_sectors() -> dict[str, str]:
    """Mappe chaque ticker -> son secteur GICS (colonne du CSV des constituants).

    Sert à l'analyse PAR SECTEUR (la figure marche-t-elle mieux dans la tech, l'énergie… ?).
    """
    path = _cache_file()
    if not path.exists():
        load_sp500()  # télécharge et cache le CSV
    df = pd.read_csv(path)
    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.replace(".", "-", regex=False)
    # Colonne secteur selon la source : « GICS Sector » (Wikipédia/datahub) ou « Sector ».
    sector_col = next(
        (c for c in ("GICS Sector", "Sector", "sector") if c in df.columns),
        None,
    )
    if sector_col is None:
        return {}
    return dict(zip(df["Symbol"], df[sector_col].astype(str)))
