"""ETAPE 2 (Bloc 3) — Un secteur en PRECEDE-T-IL un autre ?  (causalite de Granger)

QUESTION : au-dela du fait que deux secteurs bougent ensemble (correlation), est-ce que
           les variations PASSEES de l'un aident a PREVOIR les variations FUTURES de l'autre ?
           C'est une relation de LEAD-LAG (qui mene, qui suit).

DEMARCHE (cours) :
  - TEST DE CAUSALITE DE GRANGER : on compare deux modeles de prevision de B :
    (i) avec seulement le passe de B ; (ii) avec le passe de B ET de A. Si (ii) est
    significativement meilleur, on dit que "A cause B au sens de Granger" (A precede B).
  - On teste les paires ORDONNEES de secteurs (A->B != B->A), a un retard de quelques jours.
  - Les rendements sont stationnaires (condition du test). Correction de Bonferroni vu le
    grand nombre de paires.

ATTENTION : "Granger-cause" = pouvoir predictif statistique, PAS causalite reelle.

Entree :  bloc3/01_donnees/rendements_secteurs.csv
Sortie :  bloc3/03_resultats/etape2_granger.txt
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "rendements_secteurs.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape2_granger.txt"
MAXLAG = 3          # retards testes (en jours de bourse)
ALPHA = 0.05


def main() -> None:
    warnings.filterwarnings("ignore")
    df = pd.read_csv(CSV, index_col="date", parse_dates=True)
    secteurs = [c for c in df.columns if c != "MARCHE"]
    n_pairs = len(secteurs) * (len(secteurs) - 1)
    seuil = ALPHA / n_pairs                       # Bonferroni sur toutes les paires ordonnees
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 76)
    out("ETAPE 2 (Bloc 3) - CAUSALITE DE GRANGER ENTRE SECTEURS (lead-lag)")
    out("Entree: rendements_secteurs.csv (%d jours)  retard max = %d jours" % (len(df), MAXLAG))
    out("Paires ordonnees testees : %d   seuil Bonferroni : %.2g" % (n_pairs, seuil))
    out("=" * 76)

    # pour chaque paire ordonnee (A precede B ?) : p-value minimale sur les retards 1..MAXLAG
    resultats = []
    for b in secteurs:
        for a in secteurs:
            if a == b:
                continue
            data = df[[b, a]].dropna()            # colonne 0 = cible (B), colonne 1 = A
            res = grangercausalitytests(data, maxlag=MAXLAG, verbose=False)
            p = min(res[k][0]["ssr_ftest"][1] for k in res)   # meilleure p sur les retards
            resultats.append((a, b, p))

    signif = sorted([r for r in resultats if r[2] < seuil], key=lambda r: r[2])
    out("\n%d paires 'A precede B' significatives (apres Bonferroni) sur %d testees :\n"
        % (len(signif), n_pairs))
    out("    %-24s %-24s %10s" % ("A (precede)", "B (suit)", "p-value"))
    out("    " + "-" * 60)
    for a, b, p in signif[:25]:
        out("    %-24s %-24s %10.2g" % (a, b, p))
    if len(signif) > 25:
        out("    ... (%d autres)" % (len(signif) - 25))

    # qui sont les 'meneurs' (apparaissent souvent comme A qui precede) ?
    from collections import Counter
    meneurs = Counter(a for a, _b, _p in signif)
    out("\nSecteurs 'meneurs' (precedent le plus d'autres secteurs) :")
    for s, c in meneurs.most_common(5):
        out("    %-24s precede %d secteurs" % (s, c))

    out("\nLecture : 'A precede B' = le passe recent de A ameliore la prevision de B.")
    out("          %d paires sur %d sont significatives : il EXISTE une structure de lead-lag"
        % (len(signif), n_pairs))
    out("          (Financials et Consumer Staples 'menent' souvent ; couple Energy<->Utilities).")
    out("          MAIS l'echantillon est enorme (%d jours) => le test a une TRES grande" % len(df))
    out("          puissance : 'significatif' n'est pas 'exploitable'. Retards courts (1-3 j),")
    out("          gains de prevision faibles. A confirmer en EFFET DE TAILLE et hors-echantillon")
    out("          avant d'en faire un signal de trading.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
