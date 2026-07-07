"""MOTEUR d'etude d'evenement — briques communes reutilisees par etape1..4.

On isole ici ce qui est partage (calcul des rendements anormaux / CAR par evenement)
pour ne pas le reecrire dans chaque etape. Chaque `etape*.py` importe ce moteur puis
applique SA methode statistique (test, chi2, Poisson).

Concept (cours) : modele de marche sur une fenetre d'estimation -> rendement anormal
sur la fenetre d'evenement -> CAR (rendement anormal cumule).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parents[1]        # .../bloc2
sys.path.insert(0, str(ICI.parents[0] / "backend"))
from charts import data  # noqa: E402

EST_DEB, EST_FIN = -250, -11     # fenetre d'estimation
EVT_DEB, EVT_FIN = -1, 5         # fenetre d'evenement
MIN_EST = 60


def marche() -> pd.Series:
    """Rendement quotidien du marche : colonne MARCHE du Bloc 3, sinon SPY."""
    ref = ICI.parents[0] / "bloc3" / "01_donnees" / "rendements_secteurs.csv"
    if ref.exists():
        m = pd.read_csv(ref, index_col="date", parse_dates=True)["MARCHE"]
        m.index = m.index.tz_localize(None)
        return m
    spy = data.get_ohlcv("SPY")["Close"].pct_change()
    spy.index = pd.to_datetime(spy.index).tz_localize(None)
    return spy


_CACHE: dict[str, pd.Series | None] = {}


def _rendements(ticker: str) -> pd.Series | None:
    if ticker not in _CACHE:
        try:
            r = data.get_ohlcv(ticker)["Close"].pct_change()
            r.index = pd.to_datetime(r.index).tz_localize(None)
            _CACHE[ticker] = r
        except Exception:  # noqa: BLE001
            _CACHE[ticker] = None
    return _CACHE[ticker]


def car_evenement(ticker: str, date: pd.Timestamp, rmkt: pd.Series):
    """(CAR, AR par jour) pour un evenement via le modele de marche, ou None si infaisable."""
    r = _rendements(ticker)
    if r is None:
        return None
    df = pd.DataFrame({"r": r, "m": rmkt}).dropna()
    if date not in df.index:
        futurs = df.index[df.index >= date]
        if len(futurs) == 0:
            return None
        date = futurs[0]
    pos = df.index.get_loc(date)
    if isinstance(pos, slice):
        pos = pos.start
    e0, e1 = pos + EST_DEB, pos + EST_FIN
    if e0 < 0 or e1 <= e0:
        return None
    est = df.iloc[e0:e1]
    if len(est) < MIN_EST:
        return None
    beta, alpha = np.polyfit(est["m"].to_numpy(), est["r"].to_numpy(), 1)
    v0, v1 = pos + EVT_DEB, pos + EVT_FIN + 1
    if v0 < 0 or v1 > len(df):
        return None
    evt = df.iloc[v0:v1]
    ar = evt["r"].to_numpy() - (alpha + beta * evt["m"].to_numpy())
    if len(ar) != (EVT_FIN - EVT_DEB + 1):
        return None
    return float(ar.sum()), ar


def table_cars(evenements: pd.DataFrame, rmkt: pd.Series) -> pd.DataFrame:
    """Ajoute une colonne CAR a chaque evenement exploitable (les autres sont ecartes).

    Renvoie un DataFrame (signal, ticker, date, sens, secteur, intensite, CAR).
    """
    out = []
    for _, row in evenements.iterrows():
        res = car_evenement(str(row["ticker"]), row["date"], rmkt)
        if res is None:
            continue
        d = row.to_dict()
        d["CAR"] = res[0]
        out.append(d)
    return pd.DataFrame(out)


def charger_evenements() -> pd.DataFrame:
    csv = ICI / "01_donnees" / "evenements.csv"
    return pd.read_csv(csv, parse_dates=["date"])
