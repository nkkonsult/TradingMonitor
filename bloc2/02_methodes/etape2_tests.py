"""ETAPE 2 (Bloc 2) — LE SIGNAL BAT-IL LE HASARD, SELON SON SENS ?  (tests d'hypothese)

QUESTION : l'etape 1 a teste chaque signal globalement. Mais un signal a un SENS
           (le Congres ACHETE ou VEND ; un resultat BEAT ou MISS ; une regulation est
           SIGNIFICATIVE ou standard). On teste ici, POUR CHAQUE (signal, sens), si le
           CAR moyen est significativement different de 0 -> le sens porte-t-il un edge ?

DEMARCHE (methodes de cours, 1 echantillon) :
  - SHAPIRO-WILK : normalite du CAR (documentee ; rejetee a grand n => on s'appuie sur le TCL).
  - STUDENT 1-echantillon bilateral (H0: CAR moyen = 0).
  - WILCOXON (rangs signes) en controle non-parametrique.
  - BONFERRONI sur le nombre de couples (signal, sens) testes (tests multiples).

Entree :  bloc2/01_donnees/evenements.csv  (+ prix)
Sortie :  bloc2/03_resultats/etape2_tests.txt
Lance  :  python bloc2/02_methodes/etape2_tests.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
from scipy import stats as st

from _moteur import charger_evenements, marche, table_cars

OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape2_tests.txt"
ALPHA = 0.05
SHAPIRO_MAX = 5000


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    tab = table_cars(ev, rmkt)
    rng = np.random.default_rng(2026)

    couples = (tab.groupby(["signal", "sens"]).size()
               .reset_index(name="n").query("n >= 5"))
    seuil = ALPHA / max(len(couples), 1)
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 92)
    out("ETAPE 2 (Bloc 2) - LE SIGNAL BAT-IL LE HASARD SELON SON SENS ? (H0: CAR moyen = 0)")
    out("Evenements exploitables : %d | couples (signal,sens) testes : %d | Bonferroni=%.4f"
        % (len(tab), len(couples), seuil))
    out("=" * 92)
    out("%-12s %-12s %7s %10s %11s %11s %11s %7s" %
        ("signal", "sens", "n", "CAR_moy", "p_shapiro", "p_student", "p_wilcox", "verdict"))
    out("-" * 92)

    for _, c in couples.iterrows():
        car = tab[(tab["signal"] == c["signal"]) & (tab["sens"] == c["sens"])]["CAR"].to_numpy()
        s = car if len(car) <= SHAPIRO_MAX else rng.choice(car, SHAPIRO_MAX, replace=False)
        p_shapiro = st.shapiro(s).pvalue
        t, p_student = st.ttest_1samp(car, 0.0)
        try:
            p_wilcox = st.wilcoxon(car).pvalue
        except ValueError:
            p_wilcox = float("nan")
        verdict = "OUI" if p_student < seuil else "non"
        out("%-12s %-12s %7d %10.4f %11.2g %11.2g %11.2g %7s" %
            (c["signal"], c["sens"], len(car), car.mean(),
             p_shapiro, p_student, p_wilcox, verdict))

    out("-" * 92)
    out("Lecture : verdict=OUI => pour ce (signal, sens), le CAR moyen est significativement")
    out("          != 0 APRES Bonferroni. CAR_moy>0 = le titre sur-performe apres le signal ;")
    out("          CAR_moy<0 = il sous-performe. p_shapiro quasi nul = non-normalite (TCL).")
    out("Rappel  : un edge significatif reste a confirmer hors-echantillon et net de frais.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
