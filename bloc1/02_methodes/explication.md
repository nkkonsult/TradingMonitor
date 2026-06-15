# Les méthodes — ce que fait chaque page Python (+ résultats attendus)

> Pendant du `dictionnaire.md` du dossier `01_donnees/`. Ici on documente **la machine** :
> une page Python = une méthode statistique. Chaque page **lit** `01_donnees/trades.csv`
> et **écrit** son verdict dans `03_resultats/`. Le code est en annexe du rapport ;
> ce fichier sert à savoir, sans lire le code, **ce que chaque méthode fait et conclut**.

| Page Python | Méthode (cours) | Question posée | Sort dans `03_resultats/` |
|---|---|---|---|
| `etape1_tests.py` | Shapiro + Student + Wilcoxon (+ Bonferroni) | Chaque stratégie bat-elle le hasard ? | `etape1_tests.txt` |
| `etape2_anova.py` | ANOVA 1 & 2 facteurs + Tukey HSD | Les stratégies diffèrent-elles ? selon le régime ? | `etape2_anova.txt` |
| `etape3_chi2.py` | Khi-deux d'indépendance (+ V de Cramer) | Gagner dépend-il du contexte ? | `etape3_chi2.txt` |
| `etape4_acp.py` | ACP (composantes principales) | Le contexte d'entrée sépare-t-il gagnants/perdants ? | `etape4_acp.txt` (+ `.png`) |
| `etape5_afc.py` | AFC (correspondances) | Quelle stratégie va avec quel type de rendement ? | `etape5_afc.txt` (+ `.png`) |
| `etape6_acm.py` | ACM (correspondances multiples) | Quelles modalités vont avec « gagnant » ? | `etape6_acm.txt` (+ `.png`) |

---

## `etape1_tests.py` — chaque stratégie bat-elle le hasard ?
**Ce que ça fait.** Pour chaque stratégie, prend ses trades et teste si l'`edge` moyen
(avantage vs hasard) est **significativement positif**.
1. **Shapiro-Wilk** : teste la normalité de l'edge (documenté — rejette quasi partout à
   grand n, c'est attendu).
2. **Student à 1 échantillon** (H₀ : edge moyen = 0, unilatéral H₁ : > 0). Justifié par le
   **Théorème Central Limite** : à grand n, la moyenne est quasi-normale, donc Student reste
   valide même si l'edge brut ne l'est pas.
3. **Wilcoxon** reporté en plus (contrôle non-paramétrique) : s'il dit la même chose, le
   résultat est **robuste**.
4. **Bonferroni** : on teste 10 stratégies, donc on durcit le seuil à 0,05/10 = **0,005**
   (sinon trop de faux positifs).

**Résultat obtenu.** Seules **`rsi_classic` (+1,3 %)** et **`rsi_strict` (+13 %)** battent le
hasard après Bonferroni. Toutes les figures (épaule-tête-épaule, doubles, support/résistance)
et le croisement de moyennes : **non significatives ou négatives**. `rsi_trend` est limite
(Student non, Wilcoxon oui → on tranche prudemment : non).

---

## `etape2_anova.py` — les stratégies diffèrent-elles entre elles ?
**Ce que ça fait.** Au lieu de comparer 2 à 2 (trop de tests), compare les 10 d'un coup.
1. **ANOVA à 1 facteur** (`edge ~ stratégie`) : au moins une stratégie a-t-elle un edge
   moyen différent ?
2. **Tukey HSD** : si oui, **quelles paires** diffèrent vraiment (corrige les comparaisons
   multiples).
3. **ANOVA à 2 facteurs** (`edge ~ stratégie × régime`) : le terme d'**interaction** teste le
   résultat phare — *le classement des stratégies s'inverse-t-il selon que le marché monte
   ou descend ?*

**Résultat obtenu.** ANOVA très significative (**F = 47, p ≈ 1e-85**) → les stratégies
diffèrent nettement. Tukey : **18 paires sur 45** diffèrent (le RSI strict se détache de
presque tout). Interaction stratégie × régime **p ≈ 5e-69** → **le classement DÉPEND du
régime** : c'est l'argument fort du rapport (une stratégie n'est pas bonne « dans l'absolu »).

---

## `etape3_chi2.py` — gagner dépend-il du contexte ?
**Ce que ça fait.** Construit des **tableaux de contingence** (gagnant/perdant croisé avec le
contexte) et applique le **test du khi-deux d'indépendance**. H₀ : « gagner » est indépendant
du contexte. Le **V de Cramer** donne la **force** du lien (0 = nul, 1 = total).
Trois croisements : gain × régime, gain × secteur, gain × stratégie.

**Résultat obtenu.**
- gain × **régime** : lien significatif mais **faible** (V = 0,05) — on gagne un peu plus
  souvent en marché baissier (artefact à discuter).
- gain × **secteur** : **indépendant** (p = 0,08) — le secteur ne change pas le taux de gain.
- gain × **stratégie** : lien **fort** (V = 0,41) — sans surprise, le taux de gain dépend
  énormément de la stratégie choisie.

---

## `etape4_acp.py` — le contexte d'entrée sépare-t-il gagnants et perdants ?
**Ce que ça fait.** On décrit chaque trade par **4 variables de contexte** mesurées le jour
de l'entrée (`vol_entry`, `rsi_entry`, `dist_ma200`, `holding_days`). L'**ACP** résume ces 4
variables en 2 axes (PC1, PC2) pour pouvoir **visualiser**, puis on regarde si gagnants et
perdants occupent des zones différentes.
1. **Standardisation** (centrer-réduire) : chaque variable → moyenne 0, écart-type 1.
2. **ACP** = diagonalisation de la matrice de covariance (vecteurs propres = axes, valeurs
   propres = variance portée par chaque axe). Codée en **numpy pur** (pas de dépendance).
3. **% de variance expliquée** + **loadings** (poids de chaque variable dans chaque axe).
4. **Projection** des trades sur (PC1, PC2), comparaison gagnants/perdants (écart des moyennes
   = **d de Cohen**) + nuage de points coloré (`etape4_acp.png`).

> Important : l'ACP n'utilise **que le contexte d'entrée**, pas `win`/`edge` (la cible). On
> teste donc honnêtement si, *avant de connaître l'issue*, le contexte sépare déjà les trades.
> Un d de Cohen proche de 0 = le contexte d'entrée seul **ne prédit pas** l'issue (résultat
> instructif : ça motive l'apport d'autres signaux — c'est tout l'enjeu des blocs suivants).

---

## `etape5_afc.py` — quelle stratégie va avec quel résultat ? (variables qualitatives)
**Ce que ça fait.** L'**AFC** (analyse factorielle des correspondances) est la **carte** du
test du χ² : sur un tableau de contingence **stratégie × tranche de rendement** (perte /
gain modéré / gain fort), elle place lignes et colonnes sur un même plan. **Proximité =
association.** Codée en numpy (moteur d'analyse des correspondances : centrage par rapport à
l'indépendance, normalisation par les masses, SVD).

**Résultat obtenu.** L'axe 1 (**76 %** d'inertie) sépare clairement **gains** (à gauche) et
**pertes** (à droite). Les stratégies **RSI** sont du côté des gains (`rsi_strict` pointe vers
`gain_fort`) ; `sr_breakout`, `sr_breakdown`, `hs_classic` sont du côté de la **perte**. La
carte confirme visuellement le verdict des tests.

---

## `etape6_acm.py` — quelles modalités vont avec « gagnant » ? (plusieurs variables)
**Ce que ça fait.** L'**ACM** (analyse des correspondances multiples) généralise l'AFC à
**plusieurs** variables qualitatives : `strategy + regime + secteur + issue` (gagnant/perdant).
Construit le **tableau disjonctif complet** (une colonne 0/1 par modalité) puis lui applique
l'analyse des correspondances. Toutes les modalités sont placées sur une carte ; proximité =
co-occurrence.

**Résultat obtenu.** « **gagnant** » voisine `rsi_classic`, `rsi_trend`, `db_bottom` et le
secteur *Information Technology* ; « **perdant** » voisine `ma_crossover`, `sr_breakout`,
`hs_inverse`. Les **secteurs restent groupés au centre** (association faible — cohérent avec
l'indépendance gain×secteur trouvée au χ²). *Note : en ACM, les % d'inertie par axe sont
mécaniquement faibles (propriété connue de la méthode) ; on lit les proximités, pas les %.*

---

## À venir (hors de ce bloc)
- **Géométrie des figures** (prominence/symétrie/pente du cou) comme variables supplémentaires :
  raffinement possible, spécifique à chaque stratégie.
- **Régression** : **PAS dans ce bloc** — c'est le BLOC FINAL (voir `../ARCHITECTURE.md`),
  une fois tous les blocs validés.
