"""ETAPE 6 (Bloc 2) — CONTAGION DECALEE (lead-lag) : A PRECEDE-T-IL B ?

QUESTION : l'etape 5 a montre que les actifs lies a A bougent AUTOUR du signal. Mais
           bougent-ils EN MEME TEMPS (simultane, deja price-in, non exploitable) ou APRES
           (decale) ? Si le mouvement de B arrive APRES le signal sur A, alors le signal
           sur A ANNONCE le mouvement de B -> signal potentiellement exploitable.

DEMARCHE (croise etude d'evenement + logique de Granger) :
  1) DECOMPOSITION du rendement anormal de la cible B en deux sous-fenetres autour de J0 :
        - IMMEDIAT  : AR de B cumule sur J0..J+1 (reaction du jour meme)
        - DECALE    : AR de B cumule sur J+2..J+5 (reaction retardee)
     Un DECALE significativement != 0 => B reagit encore plusieurs jours apres le signal
     capte sur A : la contagion se propage dans le temps.
  2) TEST DE PREDICTIBILITE (esprit Granger) : sur toutes les paires (A signal, B cible),
     le rendement anormal de A au jour du signal predit-il le rendement anormal de B le
     LENDEMAIN ? Regression AR_B(J+1) ~ AR_A(J0) ; pente significative => A precede B.

Entree :  bloc2/01_donnees/evenements.csv (+ prix, + liens_thematiques.py)
Sortie :  bloc2/03_resultats/etape6_leadlag.txt
Lance  :  python bloc2/02_methodes/etape6_leadlag.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

from _moteur import (charger_evenements, marche, _rendements,
                     EST_DEB, EST_FIN, MIN_EST)

ICI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ICI / "01_donnees"))
import liens_thematiques as LT  # noqa: E402
from etape5_contagion import top_pairs_correles  # reutilise la selection des pairs

OUT = ICI / "03_resultats" / "etape6_leadlag.txt"
ALPHA = 0.05
K_PAIRS = 3


def ar_journalier(ticker: str, date: pd.Timestamp, rmkt: pd.Series):
    """Renvoie les AR de B par jour relatif {-1:.., 0:.., 1:.., ...5:..} ou None.

    Meme modele de marche que le moteur, mais on GARDE le detail jour par jour pour
    separer reaction immediate (J0..J1) et decalee (J2..J5).
    """
    r = _rendements(ticker)
    if r is None:
        return None
    df = pd.DataFrame({"r": r, "m": rmkt}).dropna()
    if date not in df.index:
        futurs = df.index[df.index >= date]
        if len(futurs) == 0:
            return None
        date = futurs[0]
    pos = df.index.get_loc(date)
    if isinstance(pos, slice):
        pos = pos.start
    e0, e1 = pos + EST_DEB, pos + EST_FIN
    if e0 < 0 or e1 <= e0:
        return None
    est = df.iloc[e0:e1]
    if len(est) < MIN_EST:
        return None
    beta, alpha = np.polyfit(est["m"].to_numpy(), est["r"].to_numpy(), 1)
    jours = {}
    for j in range(-1, 6):
        k = pos + j
        if 0 <= k < len(df):
            row = df.iloc[k]
            jours[j] = float(row["r"] - (alpha + beta * row["m"]))
    return jours


def _test(x: np.ndarray, seuil: float):
    if len(x) < 5:
        return float("nan"), "n<5"
    p = st.ttest_1samp(x, 0.0).pvalue
    return p, ("OUI" if p < seuil else "non")


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = charger_evenements()
    rmkt = marche()
    univers = sorted(ev["ticker"].unique())
    sources = (ev.groupby("ticker").size().sort_values(ascending=False)
               .head(12).index.tolist())

    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 92)
    out("ETAPE 6 (Bloc 2) - CONTAGION DECALEE (lead-lag) : le signal sur A ANNONCE-t-il B ?")
    out("Immediat = AR cible cumule J0..J1 | Decale = AR cible cumule J2..J5")
    out("=" * 92)

    # accumulateurs par type de cible
    acc = {"pairs": {"imm": [], "dec": [], "ar_a": [], "ar_b1": []},
           "themes": {"imm": [], "dec": [], "ar_a": [], "ar_b1": []}}

    for a in sources:
        dates = sorted(ev[ev["ticker"] == a]["date"].unique())
        cibles = {"pairs": [p for p, _ in top_pairs_correles(a, univers, K_PAIRS)],
                  "themes": LT.themes_de(a)}
        for d in dates:
            ar_a = ar_journalier(a, d, rmkt)              # rendement anormal de la SOURCE
            a0 = ar_a.get(0) if ar_a else None
            for typ, liste in cibles.items():
                for b in liste:
                    arb = ar_journalier(b, d, rmkt)
                    if arb is None:
                        continue
                    imm = sum(arb.get(j, 0.0) for j in (0, 1))
                    dec = sum(arb.get(j, 0.0) for j in (2, 3, 4, 5))
                    acc[typ]["imm"].append(imm)
                    acc[typ]["dec"].append(dec)
                    if a0 is not None and 1 in arb:
                        acc[typ]["ar_a"].append(a0)
                        acc[typ]["ar_b1"].append(arb[1])

    seuil = ALPHA / 2
    out("\n%-16s %8s %10s %10s %11s %11s" %
        ("type de cible", "n", "AR_imm", "AR_decale", "p_immediat", "p_decale"))
    out("-" * 92)
    for typ, nom in (("pairs", "pairs correles"), ("themes", "themes/mat.1res")):
        imm = np.array(acc[typ]["imm"])
        dec = np.array(acc[typ]["dec"])
        p_imm, v_imm = _test(imm, seuil)
        p_dec, v_dec = _test(dec, seuil)
        out("%-16s %8d %10.4f %10.4f %11.2g %11.2g"
            % (nom, len(imm), imm.mean() if len(imm) else float('nan'),
               dec.mean() if len(dec) else float('nan'), p_imm, p_dec))
        out("%-16s %8s %10s %10s   -> immediat=%s  decale=%s"
            % ("", "", "", "", v_imm, v_dec))

    # --- test de predictibilite (esprit Granger) : AR_A(J0) -> AR_B(J+1) ---
    out("\n" + "=" * 92)
    out("PREDICTIBILITE (esprit Granger) : le choc sur A en J0 predit-il B le lendemain ?")
    out("Regression  AR_B(J+1) = a + b * AR_A(J0)   ; pente b>0 & p<0.05 => A precede B")
    out("-" * 92)
    out("%-16s %8s %10s %11s %8s" % ("type de cible", "n", "pente_b", "p_pente", "verdict"))
    for typ, nom in (("pairs", "pairs correles"), ("themes", "themes/mat.1res")):
        xa = np.array(acc[typ]["ar_a"])
        yb = np.array(acc[typ]["ar_b1"])
        if len(xa) < 10:
            out("%-16s %8d  (trop peu)" % (nom, len(xa)))
            continue
        reg = st.linregress(xa, yb)
        verdict = "A PRECEDE B" if (reg.pvalue < ALPHA and reg.slope > 0) else "non"
        out("%-16s %8d %10.3f %11.2g %8s"
            % (nom, len(xa), reg.slope, reg.pvalue, verdict))

    out("\n" + "-" * 92)
    out("Lecture : AR_decale significatif => la cible bouge ENCORE J2..J5 apres le signal")
    out("          sur A (contagion qui se propage dans le temps). Pente Granger>0 &")
    out("          significative => le choc sur A ANNONCE le mouvement de B le lendemain :")
    out("          c'est le cas potentiellement EXPLOITABLE (A precede B). Un effet")
    out("          uniquement IMMEDIAT (J0..J1) est deja price-in, donc non exploitable.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
