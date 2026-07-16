"""ETAPE 1b — Les trades sont-ils INDEPENDANTS ? (diagnostic + correction)

PROBLEME : le test de Student de l'etape 1 suppose les edges independants.
Or des trades d'un meme titre (ou de titres correles) peuvent se chevaucher
et subir les memes chocs de marche -> dependance -> l'erreur-type s/sqrt(n)
est SOUS-estimee -> p-values trop optimistes.

DEMARCHE (concepts de cours : ANOVA inter/intra + DEFF du cours de sondages) :
  1) DIAGNOSTIC : correlation intra-grappe rho des edges, grappe = ticker
     (estimateur ANOVA : rho = (MSB - MSW) / (MSB + (n0 - 1) MSW)).
  2) CORRECTION : effet de plan de Kish  DEFF = 1 + (m_bar - 1) * rho,
     taille effective n_eff = n / DEFF, erreur-type corrigee = s*sqrt(DEFF)/sqrt(n),
     puis test de Student corrige (H0: mu_edge = 0, H1: > 0), seuil Bonferroni.
  3) ROBUSTESSE : bootstrap PAR GRAPPES (on reechantillonne des tickers entiers,
     ce qui preserve la dependance intra-titre) -> p-value sans hypothese
     d'independance entre trades.

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape1b_dependance.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape1b_dependance.txt"
ALPHA = 0.05
B_BOOT = 4000  # nb de reechantillonnages bootstrap


def icc_anova(groups: list[np.ndarray]) -> tuple[float, float, float]:
    """Correlation intra-classe (ANOVA a 1 facteur, effectifs desequilibres).

    Renvoie (rho, MSB, MSW). rho est tronque a [0, 1] (negatif -> 0).
    """
    k = len(groups)
    sizes = np.array([len(g) for g in groups], dtype=float)
    n = sizes.sum()
    grand = np.concatenate(groups).mean()
    ssb = float(sum(m * (g.mean() - grand) ** 2 for m, g in zip(sizes, groups)))
    ssw = float(sum(((g - g.mean()) ** 2).sum() for g in groups))
    msb = ssb / (k - 1)
    msw = ssw / (n - k)
    n0 = (n - (sizes ** 2).sum() / n) / (k - 1)  # taille "moyenne" ajustee
    rho = (msb - msw) / (msb + (n0 - 1) * msw)
    return max(0.0, min(1.0, rho)), msb, msw


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    rng = np.random.default_rng(2026)
    strategies = sorted(df["strategy"].unique())
    seuil_bonf = ALPHA / len(strategies)
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 110)
    out("ETAPE 1b - DIAGNOSTIC DE DEPENDANCE + TEST DE STUDENT CORRIGE (grappe = ticker)")
    out("Entree: trades.csv (%d trades)   Seuil Bonferroni: %.4f   Bootstrap: %d tirages" %
        (len(df), seuil_bonf, B_BOOT))
    out("=" * 110)
    out("%-14s %6s %5s %6s %6s %6s %7s | %9s %9s | %9s %9s %9s %7s" %
        ("strategie", "n", "k", "m_bar", "rho", "DEFF", "n_eff",
         "t_naif", "t_corr", "p_naif", "p_corr", "p_boot", "verdict"))
    out("-" * 110)

    for kname in strategies:
        sub = df[df["strategy"] == kname]
        edge = sub["edge"].to_numpy()
        n = len(edge)

        # --- 1) diagnostic : ICC par ticker -------------------------------
        groups = [g.to_numpy() for _, g in sub.groupby("ticker")["edge"]]
        kclu = len(groups)
        m_bar = n / kclu
        rho, _, _ = icc_anova(groups)

        # --- 2) correction : DEFF de Kish -> Student corrige --------------
        deff = 1.0 + (m_bar - 1.0) * rho
        n_eff = n / deff
        s = edge.std(ddof=1)
        se_naif = s / np.sqrt(n)
        se_corr = se_naif * np.sqrt(deff)
        t_naif = edge.mean() / se_naif
        t_corr = edge.mean() / se_corr
        p_naif = float(st.t.sf(t_naif, df=n - 1))
        p_corr = float(st.t.sf(t_corr, df=max(2.0, n_eff - 1)))

        # --- 3) robustesse : bootstrap par grappes (tickers) --------------
        sums = np.array([g.sum() for g in groups])
        cnts = np.array([len(g) for g in groups], dtype=float)
        idx = rng.integers(0, kclu, size=(B_BOOT, kclu))
        boot_means = sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)
        # test bootstrap centre : distribution de (mean* - mean_obs) sous H0
        p_boot = float(np.mean(boot_means - edge.mean() >= edge.mean()))

        verdict = "OUI" if (p_corr < seuil_bonf and p_boot < seuil_bonf) else "non"
        out("%-14s %6d %5d %6.1f %6.3f %6.2f %7.0f | %9.2f %9.2f | %9.2g %9.2g %9.2g %7s" %
            (kname, n, kclu, m_bar, rho, deff, n_eff,
             t_naif, t_corr, p_naif, p_corr, p_boot, verdict))

    out("-" * 110)
    out("Lecture : rho = correlation intra-titre des edges (0 = trades independants).")
    out("          DEFF = effet de plan de Kish : la variance reelle de la moyenne est")
    out("          DEFF fois celle calculee sous independance -> n_eff = n/DEFF.")
    out("          p_corr = p-value Student avec erreur-type corrigee (df = n_eff - 1).")
    out("          p_boot = bootstrap par grappes (tickers reechantillonnes entiers),")
    out("          aucune hypothese d'independance entre trades d'un meme titre.")
    out("          verdict OUI = p_corr ET p_boot < seuil Bonferroni (0.005).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("")
    out("-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
