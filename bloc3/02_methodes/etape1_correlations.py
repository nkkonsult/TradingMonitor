"""ETAPE 1 (Bloc 3) — Quels secteurs bougent ENSEMBLE ?  (matrice de correlation)

QUESTION : les rendements des secteurs sont-ils lies ? A quel point le marche bouge-t-il
           "d'un seul bloc" (risque systematique) plutot que secteur par secteur ?

DEMARCHE (cours) :
  - COEFFICIENT DE CORRELATION de Pearson entre chaque paire de secteurs (matrice 11x11).
    +1 = bougent exactement pareil, 0 = independants, -1 = opposes.
  - correlation moyenne hors-diagonale = degre de "couplage" global du marche.
  - correlation de chaque secteur avec MARCHE = son exposition au risque systematique.

Entree :  bloc3/01_donnees/rendements_secteurs.csv
Sorties:  bloc3/03_resultats/etape1_correlations.txt  (+ .png si matplotlib)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "rendements_secteurs.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1_correlations.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1_correlations.png"


def main() -> None:
    df = pd.read_csv(CSV, index_col="date", parse_dates=True)
    secteurs = [c for c in df.columns if c != "MARCHE"]
    C = df[secteurs].corr()                       # matrice de correlation 11x11
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 76)
    out("ETAPE 1 (Bloc 3) - CORRELATIONS ENTRE SECTEURS")
    out("Entree: rendements_secteurs.csv (%d jours, %d secteurs)" % (len(df), len(secteurs)))
    out("=" * 76)

    out("\nMatrice de correlation (arrondie) :")
    out(C.round(2).to_string())

    # couplage global = moyenne des correlations hors-diagonale
    m = C.to_numpy()
    off = m[~np.eye(len(secteurs), dtype=bool)]
    out("\nCorrelation moyenne entre secteurs (hors diagonale) : %.2f" % off.mean())
    out("  -> proche de 1 = le marche bouge 'd'un bloc' (risque systematique dominant).")

    # paires extremes
    pairs = [(secteurs[i], secteurs[j], m[i, j])
             for i in range(len(secteurs)) for j in range(i + 1, len(secteurs))]
    pairs.sort(key=lambda p: p[2])
    out("\nPaires les MOINS correlees (les plus 'diversifiantes') :")
    for a, b, v in pairs[:3]:
        out("    %-24s %-24s  r=%.2f" % (a, b, v))
    out("Paires les PLUS correlees :")
    for a, b, v in pairs[-3:]:
        out("    %-24s %-24s  r=%.2f" % (a, b, v))

    # exposition de chaque secteur au marche
    out("\nCorrelation de chaque secteur avec le MARCHE (exposition systematique) :")
    beta = df[secteurs].corrwith(df["MARCHE"]).sort_values(ascending=False)
    for s, v in beta.items():
        out("    %-24s  %.2f" % (s, v))

    out("\nLecture : des correlations elevees signifient qu'il est difficile de 'diversifier'")
    out("          le risque ; les secteurs defensifs (Utilities, Staples) sont en general")
    out("          moins correles au marche que les cycliques (Tech, Conso discretionnaire).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 7))
        im = ax.imshow(C.to_numpy(), cmap="RdYlGn", vmin=0, vmax=1)
        ax.set_xticks(range(len(secteurs))); ax.set_yticks(range(len(secteurs)))
        ax.set_xticklabels(secteurs, rotation=90, fontsize=7)
        ax.set_yticklabels(secteurs, fontsize=7)
        for i in range(len(secteurs)):
            for j in range(len(secteurs)):
                ax.text(j, i, "%.2f" % m[i, j], ha="center", va="center", fontsize=6)
        fig.colorbar(im, ax=ax, shrink=0.8, label="correlation")
        ax.set_title("Correlation des rendements par secteur")
        fig.tight_layout(); fig.savefig(PNG, dpi=110)
        out("-> carte de chaleur : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : carte non generee)")


if __name__ == "__main__":
    main()
