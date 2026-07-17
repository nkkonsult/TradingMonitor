"""ETAPE 8 (Bloc 2) — LES DEUX PORTES DE LA DEPENDANCE : le verdict corrige.

QUESTION : les tests des etapes 1-3 supposent des observations INDEPENDANTES. Or :
  (1) une regulation est dupliquee sur un panier de ~5 tickers -> 5 CAR mecaniquement
      correles (meme jour, meme secteur) comptes comme 5 observations (pseudo-replication) ;
  (2) les evenements arrivent en grappes dans le temps -> les CAR d'un meme mois
      partagent le choc de marche (facteur commun ~73 %, cf. Bloc 3).
  Meme discipline que le Bloc 1 (etape1c) : on ferme les deux portes et on re-teste.

DEMARCHE (miroir de bloc1/02_methodes/etape1c_agregation.py) :
  - PORTE A « un evenement = un vote » : le CAR d'un evenement = MOYENNE des CAR de son
    panier (via evenement_id). Une regle dupliquee sur 5 tickers ne vote plus qu'une fois.
    -> Student sur les CAR par evenement.
  - PORTE B « un mois = un vote » : moyenne des CAR (dedupliques) par MOIS d'evenement.
    Les evenements simultanes fondent en un seul vote. -> Student sur les moyennes
    mensuelles + autocorrelation lag-1 en diagnostic (les fenetres CAR font 7 jours,
    l'independance entre mois est plausible ; on le VERIFIE au lieu de l'affirmer).
  - VERDICT : un signal n'est retenu que s'il passe LES DEUX portes (Bonferroni).

Entree :  bloc2/01_donnees/evenements.csv (+ prix)
Sortie :  bloc2/03_resultats/etape8_portes_dependance.txt
Lance  :  python bloc2/02_methodes/etape8_portes_dependance.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

from _moteur import charger_evenements, marche, table_cars

OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape8_portes_dependance.txt"
ALPHA = 0.05


def _student(x: np.ndarray) -> tuple[float, float]:
    """(t, p bilaterale) du test H0: moyenne = 0 ; (nan, nan) si n < 5."""
    if len(x) < 5:
        return float("nan"), float("nan")
    t, p = st.ttest_1samp(x, 0.0)
    return float(t), float(p)


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    tab = table_cars(ev, rmkt)                       # 1 ligne = 1 (evenement, ticker) + CAR

    # unites testees : chaque signal, + le Congres eclate par sens (achat/vente)
    tab["unite"] = np.where(tab["signal"].eq("congres"),
                            "congres_" + tab["sens"].astype(str), tab["signal"])
    unites = sorted(tab["unite"].unique())
    seuil = ALPHA / len(unites)
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 110)
    out("ETAPE 8 (Bloc 2) - LES DEUX PORTES : un evenement = un vote (A), un mois = un vote (B)")
    out("Lignes brutes exploitables : %d   Seuil Bonferroni (%d unites) : %.4f"
        % (len(tab), len(unites), seuil))
    out("=" * 110)
    out("%-22s %7s | %8s %10s %8s %9s | %7s %10s %8s %9s %7s | %8s" %
        ("signal", "lignes", "n_evts", "CAR_moy_A", "t_A", "p_A",
         "n_mois", "CAR_moy_B", "t_B", "p_B", "ACF1", "verdict"))
    out("-" * 110)

    for u in unites:
        sub = tab[tab["unite"] == u]
        # PORTE A : dedup par evenement (CAR du panier = moyenne)
        par_evt = (sub.groupby("evenement_id")
                   .agg(CAR=("CAR", "mean"), date=("date", "first")).reset_index())
        tA, pA = _student(par_evt["CAR"].to_numpy())
        # PORTE B : un mois = un vote (sur les CAR deja dedupliques)
        par_evt["mois"] = pd.to_datetime(par_evt["date"]).dt.to_period("M")
        par_mois = par_evt.groupby("mois")["CAR"].mean().sort_index()
        tB, pB = _student(par_mois.to_numpy())
        acf1 = par_mois.autocorr(lag=1) if len(par_mois) > 3 else float("nan")
        ok = (pA < seuil) and (pB < seuil)
        verdict = "OUI" if ok else ("n<5" if np.isnan(pA) or np.isnan(pB) else "non")
        out("%-22s %7d | %8d %10.4f %8.2f %9.2g | %7d %10.4f %8.2f %9.2g %7.2f | %8s" %
            (u, len(sub), len(par_evt), par_evt["CAR"].mean(), tA, pA,
             len(par_mois), par_mois.mean(), tB, pB, acf1, verdict))

    out("-" * 110)
    out("Lecture : PORTE A ferme la pseudo-replication (une regle projetee sur 5 tickers")
    out("          ne vote qu'une fois : son CAR = la moyenne du panier). PORTE B ferme")
    out("          la dependance temporelle (les evenements du meme mois partagent le")
    out("          choc de marche : ils fondent en un vote). verdict OUI = p_A ET p_B <")
    out("          seuil Bonferroni. ACF1 = autocorrelation des moyennes mensuelles :")
    out("          proche de 0 => l'independance entre mois (condition du test B) tient.")
    out("Rappel  : Congres date a la DIVULGATION (seule date visible du marche).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
