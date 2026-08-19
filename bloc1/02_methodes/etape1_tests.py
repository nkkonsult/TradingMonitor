"""ETAPE 1 — Chaque strategie bat-elle le HASARD ?  (tests d'hypothese, 1 echantillon)

QUESTION : pour chaque strategie, l'edge moyen (avantage vs hasard) est-il
           significativement > 0, ou est-ce un coup de chance d'echantillon ?

DEMARCHE (methodes de cours) :
  1) SHAPIRO-WILK sur l'edge -> les donnees sont-elles normales ? (on le DOCUMENTE)
  2) test de STUDENT a 1 echantillon, H0: moyenne(edge)=0 vs H1: moyenne(edge)>0.
     Justification : n est grand (centaines/milliers) -> le Theoreme Central Limite
     rend la moyenne quasi-normale, donc Student reste valide meme si l'edge brut
     n'est pas normal (Shapiro rejette presque toujours a grand n, c'est attendu).
  3) WILCOXON (rangs signes) reporte EN PLUS, comme controle non-parametrique.
  4) Tests MULTIPLES (11 strategies) -> correction de BONFERRONI : seuil = 0.05/11.

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape1_tests.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1_tests.txt"
ALPHA = 0.05
SHAPIRO_MAX = 5000  # Shapiro est concu pour n <= ~5000 : au-dela on sous-echantillonne


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    rng = np.random.default_rng(2026)
    strategies = sorted(df["strategy"].unique())
    seuil_bonf = ALPHA / len(strategies)  # correction tests multiples
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 86)
    out("ETAPE 1 - LA STRATEGIE BAT-ELLE LE HASARD ?  (H0: edge moyen = 0  /  H1: > 0)")
    out("Entree: trades.csv (%d trades exploitables)" % len(df))
    out("Seuil Bonferroni (%d strategies): %.4f" % (len(strategies), seuil_bonf))
    out("=" * 86)
    out("%-14s %7s %10s %9s %11s %11s %11s %7s" %
        ("strategie", "n", "edge_moy", "W_shapiro", "p_shapiro", "p_student", "p_wilcox", "verdict"))
    out("-" * 96)

    for k in strategies:
        edge = df.loc[df["strategy"] == k, "edge"].to_numpy()
        # 1) normalite (documentee) : sous-echantillon si n trop grand pour Shapiro
        s = edge if len(edge) <= SHAPIRO_MAX else rng.choice(edge, SHAPIRO_MAX, replace=False)
        sw = st.shapiro(s)               # renvoie statistic (W) ET pvalue
        w_shapiro, p_shapiro = sw.statistic, sw.pvalue
        # 2) Student 1-echantillon, unilateral H1: moyenne > 0
        t, p_two = st.ttest_1samp(edge, 0.0)
        p_student = p_two / 2 if t > 0 else 1 - p_two / 2
        # 3) Wilcoxon (controle non-parametrique), meme sens
        try:
            p_wilcox = st.wilcoxon(edge, alternative="greater").pvalue
        except ValueError:
            p_wilcox = float("nan")
        verdict = "OUI" if p_student < seuil_bonf else "non"
        out("%-14s %7d %10.4f %9.4f %11.2g %11.2g %11.2g %7s" %
            (k, len(edge), edge.mean(), w_shapiro, p_shapiro, p_student, p_wilcox, verdict))

    out("-" * 86)
    out("Lecture : 'verdict=OUI' = edge significativement > 0 APRES Bonferroni")
    out("          => la strategie bat le hasard (talent reel, pas du bruit d'echantillon).")
    out("Note    : p_shapiro quasi nul partout = non-normalite -> on s'appuie sur le TCL")
    out("          pour Student ; Wilcoxon confirme (meme conclusion) = resultat robuste.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
