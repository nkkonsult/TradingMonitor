"""ETAPE 4 (Bloc 3) — Peut-on PREVOIR le marche avec son propre passe ?  (ARIMA)

QUESTION : une serie temporelle (ici le rendement du marche) contient-elle de l'AUTO-
           CORRELATION exploitable pour prevoir le lendemain ? Ou est-elle un "bruit blanc"
           (imprevisible a partir de son passe) ? C'est le test de l'efficience faible.

DEMARCHE (cours, serie temporelle) :
  1) STATIONNARITE - test de DICKEY-FULLER augmente (ADF) :
     - sur le PRIX : non stationnaire (marche aleatoire, racine unitaire) ;
     - sur le RENDEMENT (prix differencie) : stationnaire -> on modelise le rendement.
  2) ACF / PACF : autocorrelations. Si elles sont quasi nulles, peu de structure.
  3) ARIMA(p,d,q) ajuste sur le rendement ; on lit l'AIC et les coefficients.
  4) Conclusion : autocorrelation faible => predictibilite faible (marche quasi-efficient).

Entree :  bloc3/01_donnees/rendements_secteurs.csv   (colonne MARCHE)
Sorties:  bloc3/03_resultats/etape4_arima.txt  (+ .png ACF/PACF si matplotlib)
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, adfuller, pacf

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "rendements_secteurs.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape4_arima.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape4_arima.png"


def main() -> None:
    warnings.filterwarnings("ignore")
    df = pd.read_csv(CSV, index_col="date", parse_dates=True)
    r = df["MARCHE"].dropna()
    prix = (1.0 + r).cumprod()                    # reconstruit un niveau de 'prix' du marche
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 72)
    out("ETAPE 4 (Bloc 3) - ARIMA SUR LE RENDEMENT DU MARCHE")
    out("Entree: rendements_secteurs.csv colonne MARCHE (%d jours)" % len(r))
    out("=" * 72)

    # 1) stationnarite (ADF). H0 : 'non stationnaire' (racine unitaire). p<0.05 => stationnaire.
    p_prix = adfuller(prix)[1]
    p_rend = adfuller(r)[1]
    out("\n[1] Test de Dickey-Fuller augmente (ADF) :")
    out("    PRIX     : p = %.3g  -> %s" % (p_prix, "stationnaire" if p_prix < 0.05 else "NON stationnaire (marche aleatoire)"))
    out("    RENDEMENT: p = %.3g  -> %s" % (p_rend, "stationnaire" if p_rend < 0.05 else "non stationnaire"))
    out("    => on modelise le RENDEMENT (le prix doit etre differencie une fois : d=1).")

    # 2) autocorrelations
    a = acf(r, nlags=10)
    out("\n[2] Autocorrelations du rendement (ACF, retards 1..10) :")
    out("    " + "  ".join("%+.2f" % v for v in a[1:11]))
    out("    -> proches de 0 = tres peu de memoire d'un jour sur l'autre.")

    # 3) ARIMA(1,0,1) sur le rendement
    out("\n[3] ARIMA(1,0,1) sur le rendement :")
    fit = ARIMA(r, order=(1, 0, 1)).fit()
    out("    AIC = %.0f" % fit.aic)
    for name, val, pval in zip(fit.param_names, fit.params, fit.pvalues):
        out("    %-12s coef=%+.4f  (p=%.2g)" % (name, val, pval))

    out("\n[4] Conclusion :")
    out("    Le prix est une marche aleatoire (ADF non significatif), le rendement est")
    out("    stationnaire mais quasi sans autocorrelation : sa propre histoire ne permet")
    out("    guere de prevoir le lendemain. C'est l'EFFICIENCE FAIBLE du marche -> il faudra")
    out("    des signaux EXTERNES (blocs 1 et 2) pour esperer predire, pas la serie seule.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        p = pacf(r, nlags=10)
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))
        a1.bar(range(1, 11), a[1:11], color="#1f77b4"); a1.axhline(0, color="#999", lw=0.8)
        a1.set_title("ACF du rendement marche"); a1.set_xlabel("retard (jours)")
        a2.bar(range(1, 11), p[1:11], color="#2ca02c"); a2.axhline(0, color="#999", lw=0.8)
        a2.set_title("PACF du rendement marche"); a2.set_xlabel("retard (jours)")
        for ax in (a1, a2):
            ci = 1.96 / np.sqrt(len(r))
            ax.axhline(ci, color="red", ls="--", lw=0.8); ax.axhline(-ci, color="red", ls="--", lw=0.8)
        fig.tight_layout(); fig.savefig(PNG, dpi=110)
        out("-> ACF/PACF : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : graphique non genere)")


if __name__ == "__main__":
    main()
