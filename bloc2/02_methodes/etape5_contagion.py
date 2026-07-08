"""ETAPE 5 (Bloc 2) — CONTAGION SIMULTANEE : le signal sur A fait-il bouger B ?

QUESTION (recadrage) : on ne cherche PAS si le signal est tradable sur le titre A
           lui-meme, mais s'il a un IMPACT sur d'autres actifs B lies a A. Quand un
           signal tombe sur A (ex. un contrat pour Lockheed, une transaction sur Tesla),
           les actifs LIES a A (pairs correles, matieres premieres, ETF de theme)
           realisent-ils un rendement anormal AUTOUR de la meme date (impact simultane) ?

DEMARCHE :
  - Pour chaque titre-source A qui recoit des signaux, on determine deux familles de CIBLES :
      (1) PAIRS CORRELES : les k titres du S&P 500 les plus correles a A (data-driven,
          correlation des rendements quotidiens) -> "qui bouge avec A".
      (2) THEMES / MATIERES PREMIERES : proxies ETF declares (liens_thematiques.py)
          -> "quel sous-jacent economique A entraine".
  - Pour chaque cible B et chaque date de signal sur A, on calcule le CAR de B
    (meme moteur d'etude d'evenement que les etapes precedentes, fenetre J-1..J+5).
  - On teste, par type de cible, si le CAR moyen de B est significativement != 0
    (Student + Wilcoxon, Bonferroni) -> B REAGIT-il au signal capte sur A ?

Entree :  bloc2/01_donnees/evenements.csv (+ prix, + liens_thematiques.py)
Sortie :  bloc2/03_resultats/etape5_contagion.txt
Lance  :  python bloc2/02_methodes/etape5_contagion.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

from _moteur import (EVT_DEB, EVT_FIN, car_evenement, charger_evenements,
                     marche, _rendements)

ICI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ICI / "01_donnees"))
import liens_thematiques as LT  # noqa: E402

OUT = ICI / "03_resultats" / "etape5_contagion.txt"
ALPHA = 0.05
K_PAIRS = 3                     # nb de pairs correles retenus par titre-source
CORR_MIN_JOURS = 500           # historique commun mini pour une correlation fiable


def top_pairs_correles(source: str, univers: list[str], k: int) -> list[tuple[str, float]]:
    """Les k titres les plus correles (en rendement quotidien) au titre source."""
    rs = _rendements(source)
    if rs is None:
        return []
    cors = []
    for b in univers:
        if b == source:
            continue
        rb = _rendements(b)
        if rb is None:
            continue
        df = pd.DataFrame({"a": rs, "b": rb}).dropna()
        if len(df) < CORR_MIN_JOURS:
            continue
        c = df["a"].corr(df["b"])
        if pd.notna(c):
            cors.append((b, float(c)))
    cors.sort(key=lambda x: -x[1])
    return cors[:k]


def cars_cibles(dates: list[pd.Timestamp], cibles: list[str], rmkt) -> np.ndarray:
    """CAR de chaque (cible, date) : tableau plat des CAR exploitables."""
    out = []
    for b in cibles:
        for d in dates:
            res = car_evenement(b, d, rmkt)
            if res is not None:
                out.append(res[0])
    return np.array(out)


def _test(car: np.ndarray, seuil: float) -> tuple[float, float, str]:
    if len(car) < 5:
        return float("nan"), float("nan"), "n<5"
    t, p = st.ttest_1samp(car, 0.0)
    try:
        pw = st.wilcoxon(car).pvalue
    except ValueError:
        pw = float("nan")
    return p, pw, ("OUI" if p < seuil else "non")


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    univers = sorted(ev["ticker"].unique())      # on cherche les pairs parmi les titres suivis

    # titres-source = ceux qui recoivent le plus de signaux (impact le plus mesurable)
    sources = (ev.groupby("ticker").size().sort_values(ascending=False)
               .head(12).index.tolist())

    lignes_pairs, lignes_themes = [], []
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 90)
    out("ETAPE 5 (Bloc 2) - CONTAGION SIMULTANEE : le signal sur A fait-il reagir les")
    out("actifs LIES a A (pairs correles + matieres premieres/themes) autour de J0 ?")
    out("Fenetre d'impact J%d..J%d | %d titres-source | k=%d pairs correles"
        % (EVT_DEB, EVT_FIN, len(sources), K_PAIRS))
    out("=" * 90)

    # accumulateurs globaux (tous signaux confondus) pour un test d'ensemble par type
    car_pairs_all, car_themes_all = [], []

    out("\n%-6s %-28s %-22s %8s %10s %9s" %
        ("source", "pairs correles (corr)", "themes lies", "n_sig", "", ""))
    out("-" * 90)
    for a in sources:
        dates = sorted(ev[ev["ticker"] == a]["date"].unique())
        pairs = top_pairs_correles(a, univers, K_PAIRS)
        themes = LT.themes_de(a)
        plabel = ", ".join("%s(%.2f)" % (p, c) for p, c in pairs) or "-"
        tlabel = ", ".join(themes) or "-"
        out("%-6s %-28s %-22s %8d" % (a, plabel[:28], tlabel[:22], len(dates)))

        car_p = cars_cibles(dates, [p for p, _ in pairs], rmkt)
        car_t = cars_cibles(dates, themes, rmkt)
        car_pairs_all.append(car_p)
        car_themes_all.append(car_t)

    # --- tests d'ensemble : les cibles reagissent-elles, en moyenne ? ---
    car_pairs = np.concatenate([c for c in car_pairs_all if len(c)]) if car_pairs_all else np.array([])
    car_themes = np.concatenate([c for c in car_themes_all if len(c)]) if car_themes_all else np.array([])
    seuil = ALPHA / 2      # 2 types de cible testes

    out("\n" + "=" * 90)
    out("TEST D'ENSEMBLE - le CAR moyen des cibles est-il != 0 autour du signal sur A ?")
    out("Bonferroni (2 types de cible) : %.4f" % seuil)
    out("-" * 90)
    out("%-22s %8s %11s %11s %11s %8s" %
        ("type de cible", "n", "CAR_moy", "p_student", "p_wilcox", "verdict"))
    for nom, car in (("pairs correles", car_pairs), ("themes/matieres 1res", car_themes)):
        p, pw, v = _test(car, seuil)
        if len(car) < 5:
            out("%-22s %8d  (trop peu d'observations)" % (nom, len(car)))
            continue
        out("%-22s %8d %11.4f %11.2g %11.2g %8s"
            % (nom, len(car), car.mean(), p, pw, v))

    out("\n" + "-" * 90)
    out("Lecture : verdict=OUI => en moyenne, quand A recoit un signal, ce type de cible")
    out("          realise un rendement anormal significatif AUTOUR de la meme date")
    out("          (impact simultane / contagion). Le SIGNE de CAR_moy dit le sens (les")
    out("          cibles montent ou baissent avec A). L'etape 6 teste l'impact DECALE.")
    out("Rappel  : correlation n'est pas causalite ; effet de taille (CAR_moy) a regarder.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
