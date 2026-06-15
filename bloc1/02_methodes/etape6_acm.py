"""ETAPE 6 — ACM : analyse des correspondances MULTIPLES (plusieurs variables qualitatives).

QUESTION : l'AFC (etape 5) croise DEUX variables qualitatives ; l'ACM en croise PLUSIEURS
           d'un coup et place toutes les MODALITES sur une meme carte. Ici :
           strategie + regime + secteur + issue (gagnant/perdant). On regarde quelles
           modalites se regroupent -- en particulier : 'gagnant' est-il pres de certaines
           strategies / regimes ?

DEMARCHE (methode de cours) :
  1) TABLEAU DISJONCTIF COMPLET (indicatrices 0/1 : une colonne par modalite).
  2) ACM = analyse des correspondances appliquee a ce tableau disjonctif.
  3) INERTIE des axes + coordonnees des MODALITES (colonnes) sur le plan factoriel.
  4) Proximite de deux modalites = elles apparaissent souvent ENSEMBLE.

Entree :  bloc1/01_donnees/trades.csv
Sorties:  bloc1/03_resultats/etape6_acm.txt   (+ etape6_acm.png si matplotlib dispo)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape6_acm.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape6_acm.png"
VARS = ["strategy", "regime_entry", "sector", "issue"]


def ca(N: np.ndarray):
    """Analyse des correspondances (cf. etape5). Applique au tableau disjonctif = ACM."""
    N = N.astype(float)
    P = N / N.sum()
    r = P.sum(axis=1)
    c = P.sum(axis=0)
    dr, dc = 1 / np.sqrt(r), 1 / np.sqrt(c)
    S = dr[:, None] * (P - np.outer(r, c)) * dc[None, :]
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    inertia = sv ** 2
    col = (dc[:, None] * Vt.T) * sv[None, :]   # coordonnees des modalites (colonnes)
    return col, inertia


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["return_net"]).copy()
    df["issue"] = np.where(df["win"] == 1, "gagnant", "perdant")

    # tableau disjonctif complet : une colonne 0/1 par modalite, en gardant la variable d'origine
    parts, labels, varof = [], [], []
    for v in VARS:
        d = pd.get_dummies(df[v].astype(str))
        parts.append(d)
        for mod in d.columns:
            labels.append("%s = %s" % (v, mod))
            varof.append(v)
    Z = pd.concat(parts, axis=1).to_numpy(dtype=float)

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 74)
    out("ETAPE 6 - ACM : strategie + regime + secteur + issue")
    out("Entree: trades.csv (%d trades, %d modalites)" % (len(df), len(labels)))
    out("Variables : %s" % ", ".join(VARS))
    out("=" * 74)

    col, inertia = ca(Z)
    ratio = inertia / inertia.sum()
    out("\nInertie expliquee : axe1 = %.1f %%, axe2 = %.1f %% (cumul %.1f %%)" %
        (100 * ratio[0], 100 * ratio[1], 100 * (ratio[0] + ratio[1])))

    out("\nCoordonnees des modalites (axe1, axe2) :")
    for lab, (x, y) in zip(labels, col[:, :2]):
        out("    %-34s (%+.3f, %+.3f)" % (lab, x, y))

    # focus rapport : qui est le plus proche de 'gagnant' ?
    i_gain = labels.index("issue = gagnant")
    g = col[i_gain, :2]
    dist = np.sqrt(((col[:, :2] - g) ** 2).sum(axis=1))
    ordre = np.argsort(dist)
    out("\nModalites les plus PROCHES de 'gagnant' (hors issue) :")
    shown = 0
    for k in ordre:
        if varof[k] == "issue":
            continue
        out("    %-34s  distance %.3f" % (labels[k], dist[k]))
        shown += 1
        if shown == 6:
            break
    out("\nLecture : proximite = co-occurrence. Les modalites listees apparaissent")
    out("          relativement plus souvent avec les trades gagnants.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        palette = {"strategy": "#1f77b4", "regime_entry": "#2ca02c",
                   "sector": "#7f7f7f", "issue": "#d62728"}
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.axhline(0, color="#ddd", lw=0.8); ax.axvline(0, color="#ddd", lw=0.8)
        for lab, v, (x, y) in zip(labels, varof, col[:, :2]):
            big = v == "issue"
            ax.scatter(x, y, c=palette[v], s=90 if big else 35,
                       marker="D" if big else "o", zorder=3 if big else 2)
            ax.annotate(lab.split(" = ")[1], (x, y), fontsize=9 if big else 7,
                        color=palette[v], weight="bold" if big else "normal")
        handles = [plt.Line2D([], [], marker="o", ls="", color=palette[v], label=v) for v in VARS]
        ax.legend(handles=handles, fontsize=8)
        ax.set_xlabel("Axe 1 (%.0f %%)" % (100 * ratio[0]))
        ax.set_ylabel("Axe 2 (%.0f %%)" % (100 * ratio[1]))
        ax.set_title("ACM - modalites (issue en rouge)")
        fig.tight_layout(); fig.savefig(PNG, dpi=110)
        out("-> carte : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : carte non generee)")


if __name__ == "__main__":
    main()
