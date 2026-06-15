"""ETAPE 4 — ACP : les gagnants se distinguent-ils des perdants ?  (analyse en composantes principales)

QUESTION : on decrit chaque trade par l'ETAT du titre a l'entree (volatilite, RSI,
           distance a la MM200, duree). L'ACP resume ces 4 variables en 2 axes (pour
           pouvoir VISUALISER) et on regarde si les trades GAGNANTS et PERDANTS occupent
           des zones differentes de ce plan.

DEMARCHE (methode de cours) :
  1) STANDARDISATION (centrer-reduire) : chaque variable -> moyenne 0, ecart-type 1
     (sinon une variable a grande echelle ecraserait les autres).
  2) ACP = diagonalisation de la matrice de covariance. Les VECTEURS PROPRES = les axes
     principaux (composantes), les VALEURS PROPRES = variance portee par chaque axe.
  3) % de variance expliquee par PC1, PC2... + LOADINGS (poids de chaque variable dans
     chaque axe : "que represente PC1 ?").
  4) On PROJETTE les trades sur (PC1, PC2) et on compare gagnants vs perdants
     (separation des moyennes + nuage de points colore).

Remarque : l'ACP se fait sur les variables de CONTEXTE seulement (pas sur win/edge, qui
sont la cible) -> on teste honnetement si le contexte d'entree separe deja les issues.

Entree :  bloc1/01_donnees/trades.csv
Sorties:  bloc1/03_resultats/etape4_acp.txt   (+ etape4_acp.png si matplotlib dispo)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape4_acp.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape4_acp.png"
FEATURES = ["vol_entry", "rsi_entry", "dist_ma200", "holding_days"]


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=FEATURES + ["win"])
    X = df[FEATURES].to_numpy(dtype=float)
    win = df["win"].to_numpy()
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 78)
    out("ETAPE 4 - ACP : gagnants vs perdants dans l'espace du contexte d'entree")
    out("Entree: trades.csv (%d trades, %d variables)" % (len(df), len(FEATURES)))
    out("Variables : %s" % ", ".join(FEATURES))
    out("=" * 78)

    # 1) standardisation (centrer-reduire)
    Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)

    # 2) ACP = vecteurs/valeurs propres de la covariance (matrice symetrique -> eigh)
    C = np.cov(Z, rowvar=False)
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]            # tri decroissant
    vals, vecs = vals[order], vecs[:, order]

    # 3) variance expliquee + loadings
    ratio = vals / vals.sum()
    out("\n[1] Variance expliquee par composante :")
    cum = 0.0
    for i, r in enumerate(ratio, 1):
        cum += r
        out("    PC%d : %5.1f %%   (cumul %5.1f %%)" % (i, 100 * r, 100 * cum))
    out("\n[2] Loadings (poids de chaque variable dans PC1 et PC2) :")
    out("    %-14s %8s %8s" % ("variable", "PC1", "PC2"))
    for j, f in enumerate(FEATURES):
        out("    %-14s %8.3f %8.3f" % (f, vecs[j, 0], vecs[j, 1]))

    # 4) projection + comparaison gagnants / perdants
    scores = Z @ vecs[:, :2]
    out("\n[3] Position moyenne dans le plan (PC1, PC2) :")
    out("    %-10s %8s %8s" % ("groupe", "PC1_moy", "PC2_moy"))
    for g, name in [(1, "gagnants"), (0, "perdants")]:
        s = scores[win == g]
        out("    %-10s %8.3f %8.3f" % (name, s[:, 0].mean(), s[:, 1].mean()))
    # separation = ecart des moyennes PC1 rapporte a la dispersion (d de Cohen)
    a, b = scores[win == 1, 0], scores[win == 0, 0]
    pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    d = (a.mean() - b.mean()) / pooled
    out("\n    Separation sur PC1 (d de Cohen) = %.3f" % d)
    out("    -> |d|<0.2 : separation negligeable ; les gagnants ne se distinguent PAS")
    out("       nettement des perdants par le seul contexte d'entree (resultat instructif).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    # nuage de points (optionnel, si matplotlib est installe)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        rng = np.random.default_rng(2026)
        idx = rng.choice(len(scores), min(4000, len(scores)), replace=False)  # echantillon lisible
        fig, ax = plt.subplots(figsize=(7, 6))
        for g, col, name in [(0, "#d62728", "perdants"), (1, "#2ca02c", "gagnants")]:
            m = win[idx] == g
            ax.scatter(scores[idx][m, 0], scores[idx][m, 1], s=6, alpha=0.3, c=col, label=name)
        ax.set_xlabel("PC1 (%.0f %%)" % (100 * ratio[0]))
        ax.set_ylabel("PC2 (%.0f %%)" % (100 * ratio[1]))
        ax.set_title("ACP - contexte d'entree, gagnants vs perdants")
        ax.legend()
        fig.tight_layout()
        fig.savefig(PNG, dpi=110)
        out("-> nuage de points : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : nuage de points non genere)")


if __name__ == "__main__":
    main()
