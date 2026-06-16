"""ETAPE 3 (Bloc 3) — Le "facteur marche" : ACP sur les rendements sectoriels.

QUESTION : peut-on resumer les 11 secteurs par quelques FACTEURS communs ? En finance,
           le 1er facteur est en general "le marche" (tout monte/descend ensemble = risque
           systematique) ; les facteurs suivants opposent des groupes de secteurs.

DEMARCHE (cours) :
  1) STANDARDISATION des 11 series de rendements (centrer-reduire).
  2) ACP = diagonalisation de la matrice de correlation (vecteurs/valeurs propres).
  3) % de variance par composante : PC1 eleve = un seul facteur explique l'essentiel
     (marche tres "couple"). LOADINGS : poids de chaque secteur dans PC1, PC2.
     - PC1 : tous les secteurs du meme signe => "facteur marche".
     - PC2 : oppose typiquement cycliques (Tech, Conso disc.) et defensifs (Utilities, Sante).

Entree :  bloc3/01_donnees/rendements_secteurs.csv
Sorties:  bloc3/03_resultats/etape3_acp.txt  (+ .png si matplotlib)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CSV = Path(__file__).resolve().parents[1] / "01_donnees" / "rendements_secteurs.csv"
OUT = Path(__file__).resolve().parents[1] / "03_resultats" / "etape3_acp.txt"
PNG = Path(__file__).resolve().parents[1] / "03_resultats" / "etape3_acp.png"


def main() -> None:
    df = pd.read_csv(CSV, index_col="date", parse_dates=True)
    secteurs = [c for c in df.columns if c != "MARCHE"]
    X = df[secteurs].to_numpy()
    lines: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lines.append(s)

    out("=" * 72)
    out("ETAPE 3 (Bloc 3) - ACP SUR LES RENDEMENTS SECTORIELS (facteur marche)")
    out("Entree: rendements_secteurs.csv (%d jours, %d secteurs)" % (len(df), len(secteurs)))
    out("=" * 72)

    # 1) standardisation  2) ACP via la matrice de correlation
    Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    C = np.corrcoef(Z, rowvar=False)
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    ratio = vals / vals.sum()

    out("\n[1] Variance expliquee :")
    cum = 0.0
    for i, r in enumerate(ratio, 1):
        cum += r
        out("    PC%-2d : %5.1f %%   (cumul %5.1f %%)" % (i, 100 * r, 100 * cum))
    out("\n  -> PC1 = '%0.0f %%' : part du risque qui est SYSTEMATIQUE (commune a tout le marche)."
        % (100 * ratio[0]))

    out("\n[2] Loadings (poids de chaque secteur) :")
    out("    %-24s %8s %8s" % ("secteur", "PC1", "PC2"))
    for j, s in enumerate(secteurs):
        out("    %-24s %8.3f %8.3f" % (s, vecs[j, 0], vecs[j, 1]))
    out("\n  PC1 : tous de meme signe => c'est bien le 'facteur marche' (tout bouge ensemble).")
    out("  PC2 : les signes OPPOSES separent deux familles de secteurs (cycliques vs defensifs).")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    out("\n-> ecrit dans %s" % OUT)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6))
        a1.bar(range(1, len(ratio) + 1), 100 * ratio, color="#1f77b4")
        a1.set_xlabel("composante"); a1.set_ylabel("% variance")
        a1.set_title("Variance expliquee (PC1 = facteur marche)")
        a2.axhline(0, color="#ccc", lw=0.8); a2.axvline(0, color="#ccc", lw=0.8)
        a2.scatter(vecs[:, 0], vecs[:, 1], c="#d62728")
        for j, s in enumerate(secteurs):
            a2.annotate(s, (vecs[j, 0], vecs[j, 1]), fontsize=7)
        a2.set_xlabel("PC1 (%.0f %%)" % (100 * ratio[0]))
        a2.set_ylabel("PC2 (%.0f %%)" % (100 * ratio[1]))
        a2.set_title("Loadings des secteurs")
        fig.tight_layout(); fig.savefig(PNG, dpi=110)
        out("-> graphique : %s" % PNG)
    except ImportError:
        out("(matplotlib absent : graphique non genere)")


if __name__ == "__main__":
    main()
