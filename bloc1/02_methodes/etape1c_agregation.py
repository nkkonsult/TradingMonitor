"""ETAPE 1c — Fermer les portes de la dépendance : AGRÉGATION par action et par période.

RAISONNEMENT (cf. rapport) : deux trades ne peuvent être liés que par une cause
commune, et il n'en existe que deux possibles :
  - la porte ACTION  : deux trades sur le même titre partagent la vie de ce titre ;
  - la porte PÉRIODE : deux trades simultanés partagent les mêmes journées de bourse
    (le "déclenchement collectif" des signaux se ramène à cette porte).

SOLUTION PAR AGRÉGATION (une grappe = un seul vote) :
  Test A (porte action)  : moyenne des edges par (stratégie, ticker)
                           -> 1 observation par titre -> Student sur ~500 moyennes.
  Test B (porte période) : moyenne des edges par (stratégie, mois d'entrée)
                           -> 1 observation par mois  -> Student sur ~190 moyennes.
                           (nécessite entry_date : base régénérée après 2026-07)

Chaque test : H0 mu = 0 vs H1 mu > 0, seuil de Bonferroni 0.05/10.
Verdict final "OUI" seulement si les DEUX portes fermées confirment.

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape1c_agregation.txt
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats as st

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1c_agregation.txt"
ALPHA = 0.05


def test_unilateral(means) -> tuple[int, float, float, float]:
    """Student a 1 echantillon sur les moyennes de grappes, H1 : mu > 0.

    Renvoie (k grappes, moyenne des moyennes, t, p unilaterale).
    """
    k = len(means)
    if k < 3:
        return k, float("nan"), float("nan"), float("nan")
    t, p_two = st.ttest_1samp(means, 0.0)
    p = p_two / 2 if t > 0 else 1 - p_two / 2
    return k, float(means.mean()), float(t), float(p)


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    has_dates = "entry_date" in df.columns
    strategies = sorted(df["strategy"].unique())
    seuil = ALPHA / len(strategies)
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 118)
    out("ETAPE 1c - TEST PAR AGREGATION : une action = un vote / un mois = un vote")
    out("Entree: trades.csv (%d trades)   Seuil Bonferroni: %.4f   Dates disponibles: %s" %
        (len(df), seuil, "OUI" if has_dates else "NON (porte periode non testable)"))
    out("=" * 118)
    out("%-14s %6s | %8s %10s %8s %10s | %7s %10s %8s %10s | %7s" %
        ("strategie", "n", "k_actions", "edge_moy_A", "t_A", "p_A",
         "k_mois", "edge_moy_B", "t_B", "p_B", "verdict"))
    out("-" * 118)

    if has_dates:
        df["mois"] = pd.to_datetime(df["entry_date"]).dt.to_period("M")

    for kname in strategies:
        sub = df[df["strategy"] == kname]

        # --- Test A : porte ACTION (1 titre = 1 vote) ----------------------
        means_a = sub.groupby("ticker")["edge"].mean()
        ka, ma, ta, pa = test_unilateral(means_a)

        # --- Test B : porte PERIODE (1 mois d'entree = 1 vote) -------------
        if has_dates:
            means_b = sub.groupby("mois")["edge"].mean()
            kb, mb, tb, pb = test_unilateral(means_b)
            ok = (pa < seuil) and (pb < seuil)
            out("%-14s %6d | %8d %10.4f %8.2f %10.2g | %7d %10.4f %8.2f %10.2g | %7s" %
                (kname, len(sub), ka, ma, ta, pa, kb, mb, tb, pb,
                 "OUI" if ok else "non"))
        else:
            ok = pa < seuil
            out("%-14s %6d | %8d %10.4f %8.2f %10.2g | %7s %10s %8s %10s | %7s" %
                (kname, len(sub), ka, ma, ta, pa, "-", "-", "-", "-",
                 "OUI*" if ok else "non"))

    out("-" * 118)
    out("Lecture : Test A = Student sur les moyennes PAR TITRE (ferme la porte 'action' :")
    out("          la dependance entre trades d'un meme titre ne peut plus rien changer,")
    out("          chaque titre ne vote qu'une fois).")
    out("          Test B = Student sur les moyennes PAR MOIS D'ENTREE (ferme la porte")
    out("          'periode' : les trades simultanes sont fondus en un seul vote).")
    out("          verdict OUI = p_A ET p_B < seuil Bonferroni." )
    if not has_dates:
        out("          (*) dates absentes du CSV : verdict provisoire sur la seule porte action.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("")
    out("-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
