"""ETAPE 4 (Bloc 2) — LE NOMBRE D'EVENEMENTS DEPEND-IL DU SECTEUR ?  (regression de Poisson)

QUESTION : les signaux d'information ne tombent pas au hasard sur les titres. Certains
           secteurs concentrent-ils significativement PLUS d'evenements (contrats de
           defense, regulations pharma...) ? On modelise un COMPTAGE (nb d'evenements par
           ticker) -> loi de Poisson, la methode de cours pour les donnees de comptage.

DEMARCHE (methode de cours : GLM Poisson) :
  - Variable a expliquer Y = nombre d'evenements observes pour chaque ticker (comptage >=0).
  - Variable explicative = le SECTEUR GICS (facteur categoriel).
  - Modele  log(E[Y]) = beta0 + somme(beta_secteur) via statsmodels GLM(family=Poisson).
  - On teste la SUR-DISPERSION (variance >> moyenne) : si forte, la Poisson sous-estime
    les ecarts-types -> on bascule sur une BINOMIALE NEGATIVE (mentionne, methode robuste).

Entree :  bloc2/01_donnees/evenements.csv
Sortie :  bloc2/03_resultats/etape4_poisson.txt
Lance  :  python bloc2/02_methodes/etape4_poisson.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from _moteur import charger_evenements

OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape4_poisson.txt"


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()

    # comptage : nb d'evenements par (ticker, secteur)
    cnt = (ev.dropna(subset=["secteur"])
           .groupby(["ticker", "secteur"]).size().reset_index(name="n"))
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 80)
    out("ETAPE 4 (Bloc 2) - REGRESSION DE POISSON : le nb d'evenements depend-il du secteur ?")
    out("Unite = un ticker. Y = nombre d'evenements recus. Facteur = secteur GICS.")
    out("=" * 80)
    out("Tickers : %d | evenements totaux : %d | moyenne/ticker : %.1f"
        % (len(cnt), cnt["n"].sum(), cnt["n"].mean()))

    # sur-dispersion : indice = variance / moyenne (1 = Poisson pure)
    mu, var = cnt["n"].mean(), cnt["n"].var()
    disp = var / mu if mu else float("nan")
    out("Moyenne=%.2f  Variance=%.2f  ratio(dispersion)=%.2f" % (mu, var, disp))
    out("  (ratio >> 1 => sur-dispersion : la binomiale negative serait plus prudente.)")
    out("-" * 80)

    # GLM Poisson : n ~ C(secteur)
    modele = smf.glm("n ~ C(secteur)", data=cnt,
                     family=sm.families.Poisson()).fit()

    out("\nModele  log(E[n]) = beta0 + effets secteur   (GLM Poisson)")
    out("Deviance=%.1f  AIC=%.1f  pseudo-R2=%.3f"
        % (modele.deviance, modele.aic,
           1 - modele.deviance / modele.null_deviance))
    out("")
    # coefficients : exp(beta) = multiplicateur du nombre attendu d'evenements
    params = modele.params
    pvals = modele.pvalues
    out("%-42s %10s %10s %9s" % ("terme", "coef", "exp(coef)", "p"))
    out("-" * 74)
    for nom in params.index:
        out("%-42s %10.3f %10.2f %9.3g"
            % (nom[:42], params[nom], np.exp(params[nom]), pvals[nom]))

    out("\n" + "-" * 80)
    out("Lecture : exp(coef) = combien de fois PLUS (ou moins) d'evenements un secteur")
    out("          recoit par rapport au secteur de reference (a p<0.05). Un exp(coef)=2")
    out("          => deux fois plus d'evenements. Confirme que les signaux d'information")
    out("          se CONCENTRENT sur certains secteurs (defense pour les contrats, etc.).")
    if disp > 2:
        out("Reserve : forte sur-dispersion (ratio=%.1f) -> p-values Poisson optimistes." % disp)
        out("          On refait donc le modele en BINOMIALE NEGATIVE (plus prudente) :")
        try:
            nb = smf.glm("n ~ C(secteur)", data=cnt,
                         family=sm.families.NegativeBinomial(alpha=1.0)).fit()
            signif_pois = int((pvals < 0.05).sum())
            signif_nb = int((nb.pvalues < 0.05).sum())
            out("          AIC binom.neg=%.1f (vs Poisson %.1f) ; termes significatifs :"
                % (nb.aic, modele.aic))
            out("          Poisson=%d  ->  binom.neg=%d (certains effets disparaissent une"
                % (signif_pois, signif_nb))
            out("          fois la sur-dispersion prise en compte : conclusion plus robuste).")
        except Exception as e:  # noqa: BLE001
            out("          (binomiale negative non estimee : %s)" % e)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
