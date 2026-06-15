"""ETAPE 2 — Les strategies different-elles entre elles ?  (ANOVA + Tukey)

QUESTION : au lieu de comparer les strategies deux a deux (risque de tests multiples),
           l'ANOVA compare les 10 D'UN COUP : "au moins une strategie a-t-elle un edge
           moyen different des autres ?".

DEMARCHE (methodes de cours) :
  1) ANOVA a 1 facteur : edge ~ strategie. F eleve + p petit => les moyennes ne sont
     pas toutes egales (au moins une strategie se demarque).
  2) post-hoc TUKEY HSD : SI l'ANOVA est significative, Tukey dit QUELLES PAIRES de
     strategies different reellement (il corrige deja les comparaisons multiples).
  3) ANOVA a 2 facteurs : edge ~ strategie * regime. Le terme d'INTERACTION teste le
     resultat phare : "le classement des strategies s'inverse-t-il selon que le marche
     est haussier ou baissier ?".

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape2_anova.txt
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats as st
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape2_anova.txt"
ALPHA = 0.05


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 78)
    out("ETAPE 2 - LES STRATEGIES DIFFERENT-ELLES ?  (ANOVA + Tukey)")
    out("Entree: trades.csv (%d trades)" % len(df))
    out("=" * 78)

    # 1) ANOVA a 1 facteur : edge ~ strategie
    groupes = [g["edge"].to_numpy() for _, g in df.groupby("strategy")]
    F, p = st.f_oneway(*groupes)
    out("\n[1] ANOVA 1 facteur  H0: toutes les strategies ont le meme edge moyen")
    out("    F = %.2f    p = %.3g  ->  %s" %
        (F, p, "les strategies DIFFERENT" if p < ALPHA else "pas de difference detectee"))

    # 2) Tukey HSD : quelles paires different
    out("\n[2] Tukey HSD (paires significatives apres correction)")
    tuk = pairwise_tukeyhsd(df["edge"].to_numpy(), df["strategy"].to_numpy(), alpha=ALPHA)
    res = pd.DataFrame(tuk.summary().data[1:], columns=tuk.summary().data[0])
    signif = res[res["reject"].astype(str) == "True"]
    out("    %d paires sur %d different significativement. Detail des paires sign. :" %
        (len(signif), len(res)))
    for _, r in signif.iterrows():
        out("      %-13s vs %-13s  ecart=%+8.4f  p=%s" %
            (r["group1"], r["group2"], float(r["meandiff"]), r["p-adj"]))

    # 3) ANOVA a 2 facteurs : edge ~ strategie * regime (interaction = resultat phare)
    out("\n[3] ANOVA 2 facteurs : edge ~ strategie * regime")
    modele = ols("edge ~ C(strategy) * C(regime_entry)", data=df).fit()
    tab = anova_lm(modele, typ=2)
    out(tab.round(4).to_string())
    p_inter = tab.loc["C(strategy):C(regime_entry)", "PR(>F)"]
    out("\n    Interaction strategie x regime : p = %.3g  ->  %s" %
        (p_inter, "le classement DEPEND du regime (effet phare !)" if p_inter < ALPHA
         else "pas d'inversion significative selon le regime"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
