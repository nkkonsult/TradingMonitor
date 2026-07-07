"""ETAPE 1 (Bloc 2) — ETUDE D'EVENEMENT : le signal deplace-t-il le cours ?

QUESTION : quand un signal d'information tombe (un membre du Congres achete, un contrat
           est attribue, une regulation sort), le titre concerne realise-t-il un
           rendement ANORMAL (au-dela de ce que le marche explique) autour de la date ?

DEMARCHE (methode de cours : etude d'evenement / event study) :
  1) MODELE DE MARCHE. Sur une FENETRE D'ESTIMATION (J-250 -> J-11, hors evenement) on
     regresse le rendement du titre sur celui du marche :  R_i = alpha + beta*R_mkt.
     -> alpha, beta decrivent le comportement NORMAL du titre.
  2) RENDEMENT ANORMAL. Sur la FENETRE D'EVENEMENT (J-1 -> J+5) :
        AR_t = R_reel_t - (alpha + beta*R_mkt_t)        (ce que le titre fait EN PLUS)
  3) CAR = somme des AR sur la fenetre d'evenement (rendement anormal CUMULE).
  4) TEST. Sur l'ensemble des evenements d'un signal : le CAR moyen est-il != 0 ?
        - Student 1-echantillon (H0: CAR moyen = 0)   [TCL : n grand => valide]
        - Wilcoxon (controle non-parametrique)
        - Bonferroni sur le nombre de signaux testes.
  5) Courbe du CAR moyen jour par jour (J-1..J+5) exportee en PNG.

Le rendement du MARCHE = colonne 'MARCHE' du Bloc 3 (moyenne S&P 500) si dispo, sinon SPY.

Entree :  bloc2/01_donnees/evenements.csv  (+ prix via backend/charts/data.get_ohlcv)
Sortie :  bloc2/03_resultats/etape1_event_study.txt  + etape1_car.png
Lance  :  python bloc2/02_methodes/etape1_event_study.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ICI = Path(__file__).resolve().parents[1]        # .../bloc2
CSV = ICI / "01_donnees" / "evenements.csv"
OUT_TXT = ICI / "03_resultats" / "etape1_event_study.txt"
OUT_PNG = ICI / "03_resultats" / "etape1_car.png"

sys.path.insert(0, str(ICI.parents[0] / "backend"))
from charts import data  # noqa: E402

# --- Fenetres (en jours de bourse) ---
EST_DEB, EST_FIN = -250, -11     # fenetre d'estimation (comportement normal)
EVT_DEB, EVT_FIN = -1, 5         # fenetre d'evenement (autour du jour 0)
MIN_EST = 60                     # min de jours d'estimation pour un beta fiable
ALPHA = 0.05


def _marche() -> pd.Series:
    """Rendement quotidien du marche : colonne MARCHE du Bloc 3, sinon SPY via yfinance."""
    ref = ICI.parents[0] / "bloc3" / "01_donnees" / "rendements_secteurs.csv"
    if ref.exists():
        m = pd.read_csv(ref, index_col="date", parse_dates=True)["MARCHE"]
        m.index = m.index.tz_localize(None)
        return m
    spy = data.get_ohlcv("SPY")["Close"].pct_change()
    spy.index = pd.to_datetime(spy.index).tz_localize(None)
    return spy


_PRIX_CACHE: dict[str, pd.Series] = {}


def _rendements(ticker: str) -> pd.Series | None:
    if ticker not in _PRIX_CACHE:
        try:
            px = data.get_ohlcv(ticker)["Close"]
            r = px.pct_change()
            r.index = pd.to_datetime(r.index).tz_localize(None)
            _PRIX_CACHE[ticker] = r
        except Exception:  # noqa: BLE001
            _PRIX_CACHE[ticker] = None
    return _PRIX_CACHE[ticker]


def car_evenement(ticker: str, date: pd.Timestamp, rmkt: pd.Series):
    """Renvoie (CAR, serie AR par jour de la fenetre) pour un evenement, ou None."""
    r = _rendements(ticker)
    if r is None:
        return None
    df = pd.DataFrame({"r": r, "m": rmkt}).dropna()
    if date not in df.index:
        # aligne sur le 1er jour de bourse >= date
        futurs = df.index[df.index >= date]
        if len(futurs) == 0:
            return None
        date = futurs[0]
    pos = df.index.get_loc(date)
    if isinstance(pos, slice):
        pos = pos.start
    # fenetre d'estimation
    e0, e1 = pos + EST_DEB, pos + EST_FIN
    if e0 < 0 or e1 <= e0:
        return None
    est = df.iloc[e0:e1]
    if len(est) < MIN_EST:
        return None
    # modele de marche : R_i = alpha + beta*R_mkt
    beta, alpha = np.polyfit(est["m"].to_numpy(), est["r"].to_numpy(), 1)
    # fenetre d'evenement
    v0, v1 = pos + EVT_DEB, pos + EVT_FIN + 1
    if v0 < 0 or v1 > len(df):
        return None
    evt = df.iloc[v0:v1]
    ar = evt["r"].to_numpy() - (alpha + beta * evt["m"].to_numpy())
    if len(ar) != (EVT_FIN - EVT_DEB + 1):
        return None
    return float(ar.sum()), ar


def main() -> None:
    warnings.filterwarnings("ignore")
    ev = pd.read_csv(CSV, parse_dates=["date"])
    rmkt = _marche()
    signaux = sorted(ev["signal"].unique())
    seuil_bonf = ALPHA / len(signaux)
    lines: list[str] = []
    jours = list(range(EVT_DEB, EVT_FIN + 1))
    courbes: dict[str, np.ndarray] = {}

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 88)
    out("ETAPE 1 (Bloc 2) - ETUDE D'EVENEMENT : rendement anormal cumule (CAR) par signal")
    out("Fenetre estimation J%d..J%d | Fenetre evenement J%d..J%d | Bonferroni=%.4f"
        % (EST_DEB, EST_FIN, EVT_DEB, EVT_FIN, seuil_bonf))
    out("=" * 88)
    out("%-12s %7s %10s %10s %11s %11s %8s" %
        ("signal", "n", "CAR_moy", "CAR_med", "p_student", "p_wilcox", "verdict"))
    out("-" * 88)

    for sig in signaux:
        sub = ev[ev["signal"] == sig]
        cars, ars = [], []
        for _, row in sub.iterrows():
            res = car_evenement(str(row["ticker"]), row["date"], rmkt)
            if res is None:
                continue
            cars.append(res[0])
            ars.append(res[1])
        if len(cars) < 5:
            out("%-12s %7d  (trop peu d'evenements exploitables)" % (sig, len(cars)))
            continue
        cars = np.array(cars)
        courbes[sig] = np.mean(np.vstack(ars), axis=0).cumsum()
        t, p_two = st.ttest_1samp(cars, 0.0)
        p_student = p_two          # bilateral : on teste != 0 (hausse OU baisse)
        try:
            p_wilcox = st.wilcoxon(cars).pvalue
        except ValueError:
            p_wilcox = float("nan")
        verdict = "OUI" if p_student < seuil_bonf else "non"
        out("%-12s %7d %10.4f %10.4f %11.2g %11.2g %8s" %
            (sig, len(cars), cars.mean(), np.median(cars), p_student, p_wilcox, verdict))

    out("-" * 88)
    out("Lecture : CAR_moy = rendement anormal moyen cumule sur la fenetre d'evenement.")
    out("          verdict=OUI => le signal deplace le cours de facon significative (!=0)")
    out("          APRES correction de Bonferroni. Signe de CAR_moy = sens de l'effet.")
    out("Note    : test bilateral (un signal peut faire MONTER ou BAISSER le cours).")
    out("          'significatif' n'est pas 'exploitable' : voir l'effet de taille (CAR_moy).")

    # --- Courbe CAR moyen jour par jour ---
    if courbes:
        plt.figure(figsize=(8, 5))
        for sig, c in courbes.items():
            plt.plot(jours, c * 100, marker="o", label=sig)
        plt.axhline(0, color="grey", lw=0.8)
        plt.axvline(0, color="red", lw=0.8, ls="--", label="jour de l'evenement")
        plt.xlabel("jour relatif a l'evenement")
        plt.ylabel("CAR moyen (%)")
        plt.title("Rendement anormal cumule moyen autour de l'evenement (Bloc 2)")
        plt.legend()
        plt.tight_layout()
        OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(OUT_PNG, dpi=110)
        out("\n-> courbe CAR : %s" % OUT_PNG)

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    out("-> ecrit dans %s" % OUT_TXT)


if __name__ == "__main__":
    main()
