"""Construit la matiere premiere du BLOC 3 : rendements quotidiens par SECTEUR.

Pourquoi le secteur (et pas chaque action) ? Etudier les liens entre 503 actions = 503x503
paires (>250 000) : illisible et instable. On agrege au SECTEUR (11 series) : unite la plus
INTERPRETABLE pour parler de "relations entre morceaux du marche", et openable dans Excel.
On ajoute une colonne MARCHE = moyenne de toutes les actions (proxy de l'indice).

Sortie : bloc3/01_donnees/rendements_secteurs.csv  (1 ligne = 1 jour, 1 colonne = 1 secteur)
Lance :  backend/.venv/Scripts/python.exe bloc3/01_donnees/construire_base.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from charts import data, universe  # noqa: E402

OUT = Path(__file__).resolve().parent / "rendements_secteurs.csv"


def main() -> None:
    tickers = universe.load_sp500()
    sec_of = universe.load_sectors()

    # 1) rendements quotidiens de chaque action (matrice date x action)
    cols = {}
    for tk in tickers:
        try:
            df = data.get_ohlcv(tk)
        except Exception:  # noqa: BLE001
            continue
        cols[tk] = df["Close"].pct_change()
    R = pd.DataFrame(cols)
    print("actions chargees :", R.shape[1])

    # 2) agregation par secteur (moyenne des actions du secteur, chaque jour)
    secteurs = sorted({sec_of.get(t, "?") for t in R.columns} - {"?"})
    S = pd.DataFrame({
        s: R[[t for t in R.columns if sec_of.get(t) == s]].mean(axis=1)
        for s in secteurs
    })
    S["MARCHE"] = R.mean(axis=1)            # proxy indice = moyenne de toutes les actions

    # 3) on garde la periode ou TOUTES les series existent (matrice propre, sans trous)
    S = S.dropna()
    S.index.name = "date"
    S.to_csv(OUT, encoding="utf-8")
    print("%d jours x %d colonnes -> %s" % (S.shape[0], S.shape[1], OUT))
    print("colonnes :", list(S.columns))
    print("periode  :", S.index.min().date(), "->", S.index.max().date())


if __name__ == "__main__":
    main()
