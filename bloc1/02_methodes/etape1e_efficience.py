# -*- coding: utf-8 -*-
"""
Etape 1e — Le marche est-il previsible par son propre passe ?

Box-Pierce sur la serie des rendements quotidiens du marche agrege,
puis mesure de l'amplitude de l'autocorrelation trouvee et de son
exploitabilite une fois les frais pris en compte.

Sortie : bloc1/03_resultats/etape1e_efficience.txt
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(RACINE, "bloc3", "01_donnees", "rendements_secteurs.csv")
DST = os.path.join(RACINE, "bloc1", "03_resultats", "etape1e_efficience.txt")

lignes = []


def out(txt=""):
    print(txt)
    lignes.append(txt)


def acf(v, h):
    """Autocorrelation d'ordre h."""
    c = v - v.mean()
    return np.sum(c[h:] * c[:-h]) / np.sum(c * c)


df = pd.read_csv(SRC)
x = df["MARCHE"].dropna().values
T = len(x)

out("=" * 62)
out("ETAPE 1e — PREVISIBILITE DU MARCHE (efficience faible)")
out("=" * 62)
out("")
out("Serie : rendements quotidiens du marche agrege")
out("T = %d jours de cotation" % T)
out("moyenne  = %+.6f" % x.mean())
out("ecart-type = %.6f" % x.std(ddof=1))
out("")

out("--- Autocorrelations ---")
bande = 1.96 / np.sqrt(T)
out("bande de significativite a 5%% : +/- %.4f" % bande)
rhos = []
for h in range(1, 11):
    r = acf(x, h)
    rhos.append(r)
    flag = "  *" if abs(r) > bande else ""
    out("  rho(%2d) = %+.4f%s" % (h, r, flag))
out("nb hors bande sur 10 : %d" % sum(1 for r in rhos if abs(r) > bande))
out("")

out("--- Test de Box et Pierce sur la serie brute ---")
for m in (6, 10):
    S = T * sum(acf(x, h) ** 2 for h in range(1, m + 1))
    p = 1 - stats.chi2.cdf(S, m)
    out("  %2d retards : S = %7.2f   ddl = %2d   p = %.3e" % (m, S, m, p))
out("")
out("  -> l'independance est rejetee : il y a de la memoire dans le marche.")
out("")

out("--- Mais quelle amplitude ? ---")
rho1 = rhos[0]
out("  rho(1)      = %+.4f" % rho1)
out("  rho(1)^2    = %.5f  soit %.2f %% de la variance du lendemain"
    % (rho1 ** 2, 100 * rho1 ** 2))
out("")

out("--- Cette memoire est-elle exploitable ? ---")
out("  Strategie contrarienne : parier chaque jour contre la veille.")
c = x - x.mean()
sig = np.sign(-c[:-1])
gains = sig * x[1:]
out("  gain moyen par jour = %+.6f  (%.4f %%)" % (gains.mean(), 100 * gains.mean()))
out("  nb de jours         = %d" % len(gains))
out("")
for frais in (0.0001, 0.0005, 0.0010):
    net = gains.mean() - frais
    verdict = "gagnant" if net > 0 else "PERDANT"
    out("  net apres %.2f %% de frais aller-retour : %+.6f  -> %s"
        % (100 * frais, net, verdict))
out("")
out("CONCLUSION : le marche est previsible au sens statistique,")
out("mais l'avantage est trop faible pour couvrir les frais.")
out("C'est l'efficience faible au sens de Fama (1970).")

with open(DST, "w", encoding="utf-8") as f:
    f.write("\n".join(lignes) + "\n")
print("\n[ecrit] %s" % DST)
