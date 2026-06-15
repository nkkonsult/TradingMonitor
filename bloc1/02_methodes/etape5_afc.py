"""ETAPE 5 — AFC : analyse factorielle des correspondances (variables qualitatives).

QUESTION : le khi-deux (etape 3) dit s'il y a un LIEN entre deux variables qualitatives ;
           l'AFC en fait la CARTE : elle place les modalites sur un plan et montre
           lesquelles s'ATTIRENT. Ici : strategie x tranche de rendement
           (perte / gain modere / gain fort) -> quelle strategie va avec quel resultat ?

DEMARCHE (methode de cours) :
  1) Tableau de CONTINGENCE (effectifs croises strategie x tranche).
  2) ANALYSE DES CORRESPONDANCES : on centre le tableau par rapport a l'independance
     (P - r.c^T), on le normalise par les masses, puis SVD -> axes factoriels.
  3) INERTIE de chaque axe (= variance qualitative expliquee) + coordonnees des
     modalites (lignes ET colonnes dans le meme plan = carte symetrique).
  4) Proximite sur la carte = association (s'attirent) ; opposes = se repoussent.

Entree :  bloc1/01_donnees/trades.csv
Sorties:  bloc1/03_resultats/etape5_afc.txt   (+ etape5_afc.png si matplotlib dispo)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape5_afc.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape5_afc.png"


def ca(N: np.ndarray):
    """Analyse des correspondances d'un tableau de contingence N (effectifs).
    Renvoie (coord_lignes, coord_colonnes, inertie_par_axe). L'axe trivial des marges
    est deja retire par le centrage (P - r.c^T)."""
    N = N.astype(float)
    P = N / N.sum()
    r = P.sum(axis=1)                 # masses des lignes
    c = P.sum(axis=0)                 # masses des colonnes
    dr, dc = 1 / np.sqrt(r), 1 / np.sqrt(c)
    S = dr[:, None] * (P - np.outer(r, c)) * dc[None, :]
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    inertia = sv ** 2
    row = (dr[:, None] * U) * sv[None, :]          # coordonnees principales lignes
    col = (dc[:, None] * Vt.T) * sv[None, :]       # coordonnees principales colonnes
    return row, col, inertia


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["return_net"])
    # tranche de rendement (variable qualitative construite a partir du rendement net)
    df["tranche"] = pd.cut(df["return_net"], [-np.inf, 0, 0.10, np.inf],
                           labels=["perte", "gain_modere", "gain_fort"])
    table = pd.crosstab(df["strategy"], df["tranche"])
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 74)
    out("ETAPE 5 - AFC : strategie x tranche de rendement")
    out("Entree: trades.csv (%d trades)" % len(df))
    out("=" * 74)
    out("\nTableau de contingence (effectifs) :")
    out(table.to_string())

    row, col, inertia = ca(table.to_numpy())
    ratio = inertia / inertia.sum()
    out("\nInertie expliquee : axe1 = %.1f %%, axe2 = %.1f %% (cumul %.1f %%)" %
        (100 * ratio[0], 100 * ratio[1], 100 * (ratio[0] + ratio[1])))

    out("\nCoordonnees (axe1, axe2) :")
    out("  -- strategies (lignes) --")
    for name, (x, y) in zip(table.index, row[:, :2]):
        out("    %-14s (%+.3f, %+.3f)" % (name, x, y))
    out("  -- tranches de rendement (colonnes) --")
    for name, (x, y) in zip(table.columns, col[:, :2]):
        out("    %-14s (%+.3f, %+.3f)" % (name, x, y))
    out("\nLecture : une strategie PROCHE d'une tranche y est sur-representee.")
    out("          Ex. une strategie pres de 'gain_fort' produit relativement plus")
    out("          de gros gains que la moyenne ; pres de 'perte' = l'inverse.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.axhline(0, color="#ccc", lw=0.8); ax.axvline(0, color="#ccc", lw=0.8)
        ax.scatter(row[:, 0], row[:, 1], c="#1f77b4", s=30)
        for name, (x, y) in zip(table.index, row[:, :2]):
            ax.annotate(name, (x, y), fontsize=8, color="#1f77b4")
        ax.scatter(col[:, 0], col[:, 1], c="#d62728", s=80, marker="D")
        for name, (x, y) in zip(table.columns, col[:, :2]):
            ax.annotate(name, (x, y), fontsize=10, color="#d62728", weight="bold")
        ax.set_xlabel("Axe 1 (%.0f %%)" % (100 * ratio[0]))
        ax.set_ylabel("Axe 2 (%.0f %%)" % (100 * ratio[1]))
        ax.set_title("AFC - strategie (bleu) x tranche de rendement (rouge)")
        fig.tight_layout(); fig.savefig(PNG, dpi=110)
        out("-> carte : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : carte non generee)")


if __name__ == "__main__":
    main()
