"""ETAPE 7 (Bloc 2) — CARTOGRAPHIE FINE : quels couples A -> B sont les plus contagieux ?

QUESTION : les etapes 5-6 ont montre que, EN MOYENNE, les actifs lies a A reagissent a un
           signal sur A. Ici on descend au niveau du COUPLE : pour chaque titre-source A et
           chaque cible B (pair correle ou theme/matiere premiere), de combien B bouge-t-il
           en moyenne quand A recoit un signal, et est-ce significatif ? On en tire :
             (1) un CLASSEMENT des couples A->B les plus contagieux ;
             (2) une CARTE DE CHALEUR source x cible (CAR moyen de B autour des signaux de A).

DEMARCHE :
  - Pour chaque A (titres qui recoivent le plus de signaux) et chaque cible B associee,
    on moyenne le CAR de B sur toutes les dates de signal de A (moteur d'etude d'evenement).
  - Test de Student (H0: CAR moyen de B = 0) ; on retient n>=10 pour la fiabilite.
  - Sortie : tableau trie + heatmap PNG (lignes = sources A, colonnes = cibles B).

Entree :  bloc2/01_donnees/evenements.csv (+ prix, + liens_thematiques.py)
Sortie :  bloc2/03_resultats/etape7_carte_contagion.txt + etape7_heatmap.png
Lance  :  python bloc2/02_methodes/etape7_carte_contagion.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from _moteur import car_evenement, charger_evenements, marche

ICI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ICI / "01_donnees"))
import liens_thematiques as LT  # noqa: E402
from etape5_contagion import top_pairs_correles

OUT_TXT = ICI / "03_resultats" / "etape7_carte_contagion.txt"
OUT_PNG = ICI / "03_resultats" / "etape7_heatmap.png"
N_MIN = 10          # min d'observations (couples date x cible) pour un couple fiable
K_PAIRS = 3


def car_couple(dates, b, rmkt):
    """CAR moyen de la cible B sur toutes les dates de signal de A (+ n, p-value)."""
    cars = []
    for d in dates:
        res = car_evenement(b, d, rmkt)
        if res is not None:
            cars.append(res[0])
    cars = np.array(cars)
    if len(cars) < N_MIN:
        return None
    p = st.ttest_1samp(cars, 0.0).pvalue
    return float(cars.mean()), len(cars), float(p)


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    univers = sorted(ev["ticker"].unique())
    sources = (ev.groupby("ticker").size().sort_values(ascending=False)
               .head(10).index.tolist())

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 92)
    out("ETAPE 7 (Bloc 2) - CARTOGRAPHIE FINE DE LA CONTAGION : couples A -> B")
    out("CAR moyen de la cible B autour des dates de signal sur A (n>=%d)." % N_MIN)
    out("=" * 92)

    couples = []          # (A, B, type, CAR_moy, n, p)
    heat = {}             # heat[A][B] = CAR_moy (pour la carte)
    cibles_ordre = []     # colonnes de la heatmap (ordre stable)

    for a in sources:
        dates = sorted(ev[ev["ticker"] == a]["date"].unique())
        pairs = [p for p, _ in top_pairs_correles(a, univers, K_PAIRS)]
        themes = LT.themes_de(a)
        heat[a] = {}
        for b, typ in [(x, "pair") for x in pairs] + [(x, "theme") for x in themes]:
            res = car_couple(dates, b, rmkt)
            if res is None:
                continue
            car_moy, n, p = res
            couples.append((a, b, typ, car_moy, n, p))
            heat[a][b] = car_moy
            if b not in cibles_ordre:
                cibles_ordre.append(b)

    # --- classement des couples les plus contagieux (|CAR| eleve ET significatif) ---
    signif = [c for c in couples if c[5] < 0.05]
    signif.sort(key=lambda c: -abs(c[3]))
    out("\nTOP couples A -> B contagieux et significatifs (p<0.05), tries par |CAR| :")
    out("%-6s %-6s %-7s %10s %6s %9s" % ("source", "cible", "type", "CAR_moy", "n", "p"))
    out("-" * 60)
    for a, b, typ, car, n, p in signif[:20]:
        fleche = "monte" if car > 0 else "baisse"
        out("%-6s %-6s %-7s %+9.3f%% %6d %9.2g   B %s"
            % (a, b, typ, car * 100, n, p, fleche))
    if not signif:
        out("  (aucun couple significatif a p<0.05)")

    out("\nTotal couples testes : %d | significatifs : %d" % (len(couples), len(signif)))

    # --- carte de chaleur A (lignes) x B (colonnes) ---
    if heat and cibles_ordre:
        M = np.full((len(sources), len(cibles_ordre)), np.nan)
        for i, a in enumerate(sources):
            for j, b in enumerate(cibles_ordre):
                if b in heat.get(a, {}):
                    M[i, j] = heat[a][b] * 100
        lim = np.nanmax(np.abs(M)) if np.isfinite(M).any() else 1.0
        plt.figure(figsize=(max(8, len(cibles_ordre) * 0.5), max(5, len(sources) * 0.5)))
        im = plt.imshow(M, cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="auto")
        plt.colorbar(im, label="CAR moyen de la cible (%)")
        plt.xticks(range(len(cibles_ordre)), cibles_ordre, rotation=90, fontsize=8)
        plt.yticks(range(len(sources)), sources, fontsize=8)
        plt.xlabel("cible B (pair correle ou theme)")
        plt.ylabel("source A (recoit le signal)")
        plt.title("Contagion : CAR moyen de B quand A recoit un signal")
        plt.tight_layout()
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(OUT_PNG, dpi=110)
        out("\n-> carte de chaleur : %s" % OUT_PNG)

    out("\n" + "-" * 92)
    out("Lecture : une case rouge = quand A recoit un signal, la cible B monte en moyenne ;")
    out("          bleue = elle baisse. Les couples du classement sont les canaux de")
    out("          contagion les plus nets (ex. entre valeurs de defense, ou vers un ETF")
    out("          sectoriel). |CAR| donne l'ampleur, p la fiabilite. A confirmer decale")
    out("          (etape 6) avant d'en faire un signal exploitable.")

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    out("-> ecrit dans %s" % OUT_TXT)


if __name__ == "__main__":
    main()
