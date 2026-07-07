"""ETAPE 3 (Bloc 2) — LE SENS DU SIGNAL EST-IL LIE A L'ISSUE ?  (khi-deux d'independance)

QUESTION : le SENS annonce par le signal (Congres achat/vente, resultat beat/miss,
           regulation significative/standard) est-il LIE a l'ISSUE observee du titre
           (a-t-il monte ou baisse en anormal : CAR>0 vs CAR<0) ? Autrement dit, le
           signal "predit"-il la direction mieux que le hasard ?

DEMARCHE (methode de cours) :
  - Pour chaque signal, table de contingence  SENS x ISSUE(CAR>0 / CAR<=0).
  - TEST DU KHI-DEUX d'independance (H0 : sens et issue independants).
  - V DE CRAMER : intensite du lien (0 = nul, 1 = parfait) — car a grand n le khi-deux
    devient significatif pour des liens minuscules ; le V dit s'ils sont EXPLOITABLES.

Meme patron que bloc1/02_methodes/etape3_chi2.py (coherence entre blocs).

Entree :  bloc2/01_donnees/evenements.csv  (+ prix)
Sortie :  bloc2/03_resultats/etape3_chi2.txt
Lance  :  python bloc2/02_methodes/etape3_chi2.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

from _moteur import charger_evenements, marche, table_cars

OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape3_chi2.txt"
ALPHA = 0.05


def cramer_v(conf: np.ndarray) -> float:
    chi2 = st.chi2_contingency(conf, correction=False)[0]
    n = conf.sum()
    k = min(conf.shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if n and k else float("nan")


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    tab = table_cars(ev, rmkt)
    tab["issue"] = np.where(tab["CAR"] > 0, "hausse", "baisse")

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 80)
    out("ETAPE 3 (Bloc 2) - LE SENS DU SIGNAL EST-IL LIE A L'ISSUE ? (khi-deux + V de Cramer)")
    out("Issue = signe du CAR (hausse si CAR>0, baisse sinon). H0 : sens et issue independants.")
    out("=" * 80)

    for sig in sorted(tab["signal"].unique()):
        sub = tab[tab["signal"] == sig]
        # il faut au moins 2 sens distincts pour croiser
        if sub["sens"].nunique() < 2:
            out("\n[%s] un seul sens ('%s') -> pas de croisement possible (n=%d)."
                % (sig, sub["sens"].iloc[0], len(sub)))
            continue
        conf = pd.crosstab(sub["sens"], sub["issue"])
        chi2, p, dof, _ = st.chi2_contingency(conf.to_numpy(), correction=False)
        v = cramer_v(conf.to_numpy())
        out("\n[%s]  n=%d" % (sig, len(sub)))
        out(conf.to_string())
        force = ("negligeable" if v < 0.1 else "faible" if v < 0.2
                 else "moyen" if v < 0.3 else "fort")
        verdict = "LIEN" if p < ALPHA else "independant"
        out("  chi2=%.2f  dof=%d  p=%.3g  V_Cramer=%.3f (%s)  -> %s"
            % (chi2, dof, p, v, force, verdict))

    out("\n" + "-" * 80)
    out("Lecture : p<0.05 => lien statistique entre le sens du signal et la direction du")
    out("          rendement anormal. MAIS le V de Cramer dit s'il est EXPLOITABLE :")
    out("          <0.1 negligeable, 0.1-0.2 faible, >0.3 fort. Un lien 'significatif mais")
    out("          negligeable' (grand n) n'a pas de valeur pratique de trading.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
