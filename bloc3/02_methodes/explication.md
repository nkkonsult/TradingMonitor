# Les méthodes du Bloc 3 — ce que fait chaque page Python (+ résultats)

> Pendant du dictionnaire : ici on documente **la machine**. Une page = une méthode, qui lit
> `01_donnees/rendements_secteurs.csv` et écrit dans `03_resultats/`.

| Page Python | Méthode (cours) | Question | Sort dans `03_resultats/` |
|---|---|---|---|
| `etape1_correlations.py` | Corrélation de Pearson | Quels secteurs bougent ensemble ? | `etape1_correlations.txt` (+ `.png`) |
| `etape2_granger.py` | Causalité de Granger | Un secteur en précède-t-il un autre ? | `etape2_granger.txt` |
| `etape3_acp_rendements.py` | ACP | Quel est le « facteur marché » ? | `etape3_acp.txt` (+ `.png`) |
| `etape4_arima.py` | ADF, ACF/PACF, ARIMA | Peut-on prévoir le marché avec son passé ? | `etape4_arima.txt` (+ `.png`) |

---

## `etape1_correlations.py` — quels secteurs bougent ensemble ?
**Ce que ça fait.** Calcule la **matrice de corrélation** (Pearson) entre les 11 secteurs,
la **corrélation moyenne** hors-diagonale (degré de « couplage » du marché), les paires les
plus/moins corrélées, et la corrélation de chaque secteur avec le `MARCHE` (exposition au
risque systématique). Carte de chaleur en sortie.

**Résultat obtenu.** Corrélation moyenne **0,70** → le marché bouge largement « d'un bloc ».
Les plus couplés au marché : **Industrials (0,96), Financials (0,94)** (cycliques) ; les
moins : **Utilities (0,66), Energy (0,71)** (défensifs/spécifiques). Paire la plus
diversifiante : **Energy ↔ Utilities (0,43)**.

---

## `etape2_granger.py` — un secteur en précède-t-il un autre ?
**Ce que ça fait.** Pour chaque paire **ordonnée** (A→B), le **test de causalité de Granger**
demande si le passé récent de A améliore la prévision de B (relation de *lead-lag*). Retards
1–3 jours, correction de **Bonferroni** sur les 110 paires.

**Résultat obtenu.** **48 paires sur 110** significatives. Secteur **meneur principal :
Financials** (précède 10 secteurs), puis **Consumer Staples** (8). ⚠️ **Nuance essentielle :**
l'échantillon est énorme (4132 jours) → le test a une **très grande puissance**, donc
« significatif » **n'est pas** « exploitable » : retards courts, gains de prévision faibles.
À confirmer en **effet de taille** et **hors-échantillon** avant d'en faire un signal. *(Et
« Granger-cause » = prédictif au sens statistique, pas causalité réelle.)*

---

## `etape3_acp_rendements.py` — le « facteur marché »
**Ce que ça fait.** ACP sur les 11 séries de rendements (standardisées). En finance, le 1er
axe est en général **le marché** (tout monte/descend ensemble). Donne le **% de variance** par
composante et les **loadings** (poids de chaque secteur).

**Résultat obtenu.** **PC1 = 73 %** de la variance, tous les secteurs du **même signe** → c'est
le **facteur marché** : 73 % du risque est **systématique** (commun), seulement ~27 % est
spécifique aux secteurs. **PC2 (8 %)** oppose **défensifs** (Utilities, Staples, Real Estate)
et **cycliques** (Tech, Energy, Consommation disc.) — l'axe « risk-on / risk-off ».

---

## `etape4_arima.py` — peut-on prévoir le marché avec son passé ?
**Ce que ça fait.** Sur la série `MARCHE` : **test ADF** de stationnarité (sur le prix et sur
le rendement), **ACF/PACF** (autocorrélations), puis un **ARIMA(1,0,1)** sur le rendement.

**Résultat obtenu.** Le **prix est non stationnaire** (ADF p ≈ 1 → marche aléatoire), le
**rendement est stationnaire** (p ≈ 10⁻²⁶). Les **autocorrélations sont quasi nulles**
(|ACF| ≤ 0,09). Dans l'ARIMA, les termes AR et MA sont significatifs mais **se compensent
presque** (−0,77 / +0,70) → série proche d'un **bruit blanc**. **Conclusion : efficience
faible** — le passé du marché ne permet guère de prévoir le lendemain. Il faut des **signaux
externes** (Blocs 1 et 2), pas la série seule.

---

## Synthèse du bloc
Le marché est **fortement couplé** (corr. 0,70 ; facteur marché 73 %) et **peu prévisible par
lui-même** (ARIMA ≈ bruit blanc). Il existe des **liens de lead-lag** (Financials mène), mais
statistiquement gonflés par la taille d'échantillon → à valider avant exploitation. Voir
`SYNTHESE.md`.
