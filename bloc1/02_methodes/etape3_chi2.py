"""ETAPE 3 — Gagner depend-il du contexte ?  (test du KHI-DEUX d'independance)

QUESTION : la proportion de trades GAGNANTS (win=1) est-elle independante du contexte
           (regime de marche, secteur) ? Ou bien gagne-t-on plus souvent dans certaines
           conditions ?

DEMARCHE (methode de cours) :
  Tableau de CONTINGENCE (effectifs croises) puis test du KHI-DEUX d'independance.
  H0 : "gagner" est independant du contexte. p < 0.05 => il y a un LIEN.
  On regarde aussi le V de Cramer = force du lien (0 = nul, 1 = total).

Entree :  bloc1/01_donnees/trades.csv
Sortie :  bloc1/03_resultats/etape3_chi2.txt
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "trades.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape3_chi2.txt"
ALPHA = 0.05


def cramer_v(chi2: float, n: int, table_shape: tuple[int, int]) -> float:
    """Force du lien (0..1), derivee du khi-deux."""
    k = min(table_shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if k > 0 else float("nan")


def test_independance(df: pd.DataFrame, col: str, out) -> None:
    table = pd.crosstab(df["win"], df[col])
    chi2, p, ddl, _ = st.chi2_contingency(table)
    v = cramer_v(chi2, len(df), table.shape)
    out("\n[%s]  'gagner' depend-il de : %s ?" % (col, col))
    out("    tableau de contingence (lignes = win 0/1) :")
    out(table.to_string())
    out("    khi2 = %.1f   ddl = %d   p = %.3g   V de Cramer = %.3f" % (chi2, ddl, p, v))
    out("    -> %s (lien %s)" % (
        "LIEN significatif" if p < ALPHA else "independance (pas de lien)",
        "faible" if v < 0.1 else "modere" if v < 0.3 else "fort"))


def main() -> None:
    df = pd.read_csv(CSV).dropna(subset=["edge"])
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 78)
    out("ETAPE 3 - GAGNER DEPEND-IL DU CONTEXTE ?  (khi-deux d'independance)")
    out("Entree: trades.csv (%d trades)" % len(df))
    out("=" * 78)

    # tous trades confondus : le succes depend-il du regime ? du secteur ?
    test_independance(df, "regime_entry", out)
    test_independance(df, "sector", out)
    # et la strategie elle-meme influence-t-elle la proba de gagner ?
    test_independance(df, "strategy", out)

    out("\nLecture : un LIEN significatif ne dit pas que c'est rentable, seulement que")
    out("          la frequence de gain n'est pas la meme selon le contexte. Le V de")
    out("          Cramer dit si ce lien est faible (anecdotique) ou fort (important).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)


if __name__ == "__main__":
    main()
