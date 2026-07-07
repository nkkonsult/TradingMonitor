# Les méthodes du Bloc 1 — manuel pédagogique

> **À qui s'adresse ce document ?** À une personne **qui ne connaît rien aux statistiques** : étudiant·e d'autre filière, lecteur curieux, jury non-spécialiste. Chaque méthode est expliquée comme dans un cours : l'idée, les calculs, les hypothèses, **pourquoi** ça marche, **où** tu l'as déjà rencontrée, et ce qu'on en a tiré ici.
>
> **Convention de lecture.** Pour chaque méthode :
> 1. **L'idée en une phrase** (ce qu'on cherche)
> 2. **Le calcul détaillé** (les formules, pas à pas)
> 3. **Hypothèses et précautions** (ce qu'il faut respecter pour que le test soit valide)
> 4. **Pourquoi ça marche** (l'intuition statistique)
> 5. **Où c'est déjà utilisé** (autres domaines)
> 6. **Application ici** (résultat exact dans notre Bloc 1)

---

## Tableau de bord des méthodes du Bloc 1

| Page Python | Méthode | Question posée | Famille statistique |
|---|---|---|---|
| `etape1_tests.py` | Shapiro-Wilk + Student (1 éch.) + Bonferroni | Chaque stratégie bat-elle le hasard ? | Tests d'hypothèse à 1 échantillon |
| `etape2_anova.py` | ANOVA à 1 & 2 facteurs + Tukey HSD (+ Bartlett/Levene) | Les stratégies diffèrent-elles entre elles ? | Tests d'hypothèse à plusieurs groupes |
| `etape3_chi2.py` | Khi-deux d'indépendance | Gagner dépend-il du contexte ? | Tests sur données qualitatives |
| `etape4_acp.py` | ACP (Analyse en Composantes Principales) | Le contexte d'entrée sépare-t-il gagnants et perdants ? | Analyse multivariée quantitative |
| `etape5_afc.py` | AFC (Analyse Factorielle des Correspondances) | Quelles stratégies vont avec quelles tranches de résultat ? | Analyse multivariée qualitative (2 var.) |
| `etape6_acm.py` | ACM (Analyse des Correspondances Multiples) | Quelles combinaisons de modalités vont avec « gagnant » ? | Analyse multivariée qualitative (n var.) |

> **Toutes les méthodes revendiquées ci-dessus sont vues en cours.** Les étapes 1 à 3 (Shapiro-Wilk, Student/Welch, ANOVA 1 & 2 facteurs avec interaction, Tukey HSD, Bonferroni, χ² d'indépendance) sont **explicitement enseignées** dans les cours **« Statistique avec SAS »** et **« Statistique avec Python »** du M1 — avec les mêmes librairies que celles du projet (`scipy.stats`, `statsmodels`). Les étapes 4 à 6 (ACP, AFC, ACM) viennent du cours **« Analyses des données »** (Périnel).
>
> **Méthodes complémentaires du Bloc 1, également vues en cours,** que l'on peut mobiliser sur les mêmes étapes :
> - **Tests d'homoscédasticité** : **Bartlett** (SAS `HOVTEST=bartlett`) et **Levene** (Python) — condition d'application de l'ANOVA, étape 2.
> - **Post-hoc de Dunnett** (comparaison de chaque groupe à un groupe de référence) — alternative à Tukey, étape 2, vue en cours au même titre que Bonferroni/Tukey.
> - **Tests de normalité complémentaires** sortis par `PROC UNIVARIATE NORMAL` : **Kolmogorov-Smirnov**, **Anderson-Darling**, **Cramér-von Mises** — robustesse de l'étape 1.
> - **Sur tableau de contingence** (étape 3, `PROC FREQ / CHISQ`) : **correction de Yates** (tableaux 2×2), **test exact de Fisher**, **G-test** (rapport de vraisemblance).
>
> ⚠️ **Non revendiqué comme méthode centrale.** Le code calcule aussi, à titre de vérification annexe, le test de **Wilcoxon** (rangs signés) et le **V de Cramér** ; ces deux-là **ne figurent pas dans les cours SAS/Python** (Wilcoxon n'est vu qu'en R ; le V de Cramér dans aucun des trois cours logiciels). Ils sont donc **écartés des méthodes présentées dans le rapport** et conservés uniquement comme contrôle interne.

---

# Étape 1 — Chaque stratégie bat-elle le hasard ?

**Page Python :** `etape1_tests.py` **Résultat :** `03_resultats/etape1_tests.txt`

## 1.1 Shapiro-Wilk — un test de normalité

### L'idée en une phrase
On veut savoir si une série de chiffres ressemble à une **courbe en cloche** (la fameuse **loi normale**), parce que beaucoup de tests statistiques supposent que c'est le cas.

### Le calcul détaillé
On dispose d'un échantillon de `n` valeurs `x₁, x₂, ..., xₙ` (ici : les `edge` des trades d'une stratégie).

**Étape 1.** On les classe par ordre croissant : `x₍₁₎ ≤ x₍₂₎ ≤ ... ≤ x₍ₙ₎`.

**Étape 2.** On calcule deux quantités qui résument l'échantillon :

- La **somme des carrés des écarts à la moyenne** (mesure totale de dispersion) :
  ```
  SCE = Σᵢ (xᵢ − x̄)²
  ```
  où `x̄` = moyenne des valeurs.

- Une combinaison spéciale `b` qui compare les valeurs **classées** aux valeurs qu'on aurait en théorie sous une loi normale parfaite :
  ```
  b = Σᵢ aᵢ · x₍ᵢ₎
  ```
  Les coefficients `aᵢ` sont calculés à partir des **espérances** des quantiles d'une loi normale standard (on les lit dans une table de Shapiro-Wilk).

**Étape 3.** La statistique du test :
```
W = b² / SCE
```
- `W` est compris entre **0 et 1**.
- `W ≈ 1` ⇔ l'échantillon ressemble vraiment à une normale.
- `W` éloigné de 1 ⇔ l'échantillon s'éloigne de la normale.

**Étape 4.** On compare `W` à un seuil critique (lu dans une table en fonction de `n` et du niveau α = 5 %). Si `W < seuil` ⇒ on **rejette la normalité** (p-value < 0.05).

### Hypothèses et précautions
- Le test n'est conçu que pour des échantillons **modérés** : il devient hypersensible pour `n > 5000`. À grand n, **tout écart minuscule** à la normale fait rejeter — alors que pour la pratique ça n'a pas d'importance.
- Notre solution : on **sous-échantillonne à n = 5000** quand la stratégie a plus de trades.

### Pourquoi ça marche
L'idée géniale de Shapiro et Wilk (1965) est de comparer **deux estimations de la variance** :
- une estimation **directe** (la SCE classique),
- une estimation **basée sur les statistiques d'ordre** (le `b²`), qui n'est correcte que si les données viennent vraiment d'une loi normale.

Si les deux estimations coïncident → c'est la normale. Si elles divergent → ce n'est pas la normale.

### Où c'est déjà utilisé
- **Dans tes cours** : Shapiro-Wilk est au **cœur de tes cours "Statistique avec SAS" et "Statistique avec Python"** — c'est LE test de normalité enseigné dans les deux (module *normalité*), avant tout test paramétrique. Il est aussi cité dans le cours "Statistique avec R" (Chevallier). C'est donc un acquis solide et **triplement couvert**.
- **Sur SAS** : `PROC UNIVARIATE DATA=... NORMAL;` donne directement `W` — **et l'option `NORMAL` sort aussi 3 autres tests** : Kolmogorov-Smirnov, Anderson-Darling et Cramér-von Mises. En ANOVA, on l'applique sur les **résidus** (`OUTPUT OUT=... R=residus;` puis `PROC UNIVARIATE ... NORMAL`).
- **Sur Python** (langage du projet) : `scipy.stats.shapiro(x.dropna())` — exactement l'appel vu en cours.
- **Sur R** : `shapiro.test()` (vu en cours stat avec R).
- **Lien avec tes acquis** : dans tes cours SAS/Python, Shapiro **précède systématiquement** le test de Student (`PROC TTEST` / `stats.ttest_ind`) : c'est la **vérification d'hypothèse** (normalité) avant d'utiliser un test paramétrique. C'est exactement le rôle qu'il joue ici.

### Application ici
Pour chaque stratégie, on a testé la normalité de l'`edge`. **Toutes les p-values sont < 10⁻¹⁵** → la normalité est rejetée partout. C'est **attendu** :
- les rendements financiers ont des **queues épaisses** (les krachs et envolées sont plus fréquents que dans une normale),
- à grand `n`, Shapiro rejette presque tout.

**Conséquence pratique :** on **documente** ce résultat, mais on s'appuie sur le **Théorème Central Limite** (voir 1.2) pour justifier le Student.

---

## 1.2 Test de Student à 1 échantillon — la stratégie a-t-elle un edge moyen positif ?

### L'idée en une phrase
On veut savoir si la **moyenne** de l'edge d'une stratégie est significativement supérieure à 0, ou si l'écart observé pourrait n'être qu'un coup de chance d'échantillon.

### ⚠️ Précision indispensable avant le calcul : que teste-t-on exactement ?

**Attention à un piège fréquent.** Quand on écrit `H₀ : edge moyen = 0`, ce **n'est pas** « le rendement de la stratégie vaut 0 ». C'est « la stratégie ne fait pas mieux que le hasard à exposition égale ».

Imagine une action qui monte de **+1 % par jour en moyenne** (très haussière).
- Un trade de la stratégie : achat j=100 → vente j=130 → `return_net ≈ +35 %`.
- Le même schéma fait au hasard sur la même action (200 dates de départ aléatoires, même durée, même sens) : `rand_return ≈ +30 %`.
- Donc `edge = +35 % − +30 % = +5 %`.

Le +5 % est le **vrai talent de timing** de la stratégie, après avoir retiré la dérive haussière de l'action. Si la stratégie n'avait fait que profiter de la hausse générale, son `edge` serait **proche de 0**, **même si son rendement est +35 %**.

**Donc** :
- `H₀ : edge moyen = 0` ⇔ la stratégie ne bat pas un tirage aléatoire de mêmes caractéristiques.
- C'est **plus fort** que « rendement nul » : ça neutralise le biais haussier du S&P 500 (97 % des titres montent sur la période → le rendement brut serait toujours positif et ne prouverait rien).

C'est pour ça que la variable testée est `edge`, pas `return_net` : on cherche le **talent**, pas la chance d'avoir acheté un marché haussier.

### Le calcul détaillé
**Données :** `n` trades, chacun a une valeur d'edge `eᵢ`.

**Hypothèses du test :**
- `H₀` (hypothèse nulle) : l'edge moyen vrai = 0 (la stratégie ne fait pas mieux que le hasard).
- `H₁` (hypothèse alternative) : l'edge moyen vrai > 0 (test **unilatéral à droite**).

**Étape 1 — Statistique de test :**
```
ē = (1/n) Σᵢ eᵢ          ← moyenne d'échantillon
s² = (1/(n−1)) Σᵢ (eᵢ − ē)²  ← variance non biaisée
t = ē / (s / √n)         ← la statistique de Student
```

**Étape 2 — Loi sous H₀ : pourquoi t suit-il une loi de Student ?**

C'est le point théorique clé. Il y a deux résultats mathématiques enchaînés.

**(a) Si les `eᵢ` suivaient une loi normale `N(μ, σ²)` parfaite,** alors par construction la moyenne d'échantillon `ē` suit `N(μ, σ²/n)` (propriété : la somme de gaussiennes est gaussienne, et on divise par n).
Donc :
```
(ē − μ) / (σ / √n)   suit   N(0, 1)
```
Sous H₀ (μ = 0), cette quantité suit donc une **loi normale standard**.

**(b) Mais on ne connaît pas `σ`** (l'écart-type vrai de la population). On n'a que `s`, son **estimation** sur notre échantillon. Quand on remplace `σ` par `s`, on injecte une **incertitude supplémentaire** dans la statistique. **William Sealy Gosset** (publication signée « Student » en 1908) a démontré que la nouvelle statistique :
```
t = (ē − μ) / (s / √n)
```
**ne suit plus** `N(0,1)` mais une autre loi, plus dispersée, avec des queues plus épaisses, qu'on appelle aujourd'hui **loi de Student à (n−1) degrés de liberté**, notée `t_{n−1}`.

Plus `n` grandit, plus `s` devient un bon estimateur de `σ`, et plus `t_{n−1}` se rapproche de `N(0,1)`. Pour `n > 30` environ, les deux lois sont quasi confondues.

**(c) Et si les `eᵢ` ne sont pas normaux ?** C'est précisément notre cas (Shapiro rejette). Mais **le Théorème Central Limite** garantit que **la moyenne** `ē` reste quasi-normale même quand les données individuelles ne le sont pas, dès que `n` est grand. Ici on a entre 970 et 8 400 trades par stratégie → on est très largement dans la zone de validité.

**Conclusion :** sous H₀, la statistique `t = ē / (s/√n)` suit `t_{n−1}` (avec une excellente approximation grâce au TCL).

**Étape 3 — p-value :** on calcule
```
p = P(T > t_observé)   où T ~ t_{n−1}
```
Si `p < α` → on rejette H₀.

### ⚠️ Le seuil α n'est PAS 0.05 ici — voir 1.4

Le seuil de rejet n'est pas 0.05 mais **0.005**. Ce n'est pas un caprice : c'est la **correction de Bonferroni** parce qu'on teste 10 stratégies en parallèle. Détail complet en section 1.4 ci-dessous.

### Hypothèses et précautions
Le Student suppose en théorie que les données sont **normales**. On a vu que ce n'était pas le cas (Shapiro rejette). **Mais** :
- ce qui compte vraiment, c'est que la **moyenne** soit quasi-normale,
- or le **Théorème Central Limite** garantit que pour `n` grand (≥ 30 environ, et chez nous on a entre 970 et 8400 trades par stratégie), la moyenne d'un échantillon est quasi-normale **quelle que soit** la distribution d'origine.

**Conclusion :** le test de Student reste **valide à grand n** même sans normalité.

### Pourquoi ça marche
Sous H₀ vraie, l'expression `(ē − 0) / (s/√n)` mesure **combien d'écart-types de la moyenne d'échantillon** sépare ce qu'on observe de zéro. Si cet écart est grand (en valeur absolue), il devient peu probable qu'il vienne du hasard pur.

**Intuition :** un écart de 3 écarts-types de la moyenne est extrêmement rare sous H₀ — environ 0.1 %. Si on observe `t = 3`, il est plus vraisemblable que H₀ soit fausse.

### Où c'est déjà utilisé
- **Dans tes cours de tests statistiques (SAS et Python)** : tu as étudié le **test t de Student** en détail — comparaison de 2 moyennes, **version de Welch** (`equal_var=False`) pour variances inégales, et version **appariée** (avant/après). Tu connais déjà la logique : statistique t, p-value, comparaison à α. La nuance ici = **version à 1 échantillon** (la moyenne contre une référence fixe, ici 0) : c'est le **cas particulier** où l'un des deux "groupes" est remplacé par la valeur théorique 0. La construction de la statistique est identique.
- **Sur SAS** : **`PROC TTEST`** (avec `CLASS` pour 2 groupes, `PAIRED` pour l'apparié) — sort en prime le **test de Fisher d'égalité des variances**. Le t à 1 échantillon en est la variante `VAR` seule contre une référence.
- **Sur Python** (langage du projet) : `scipy.stats.ttest_1samp` (notre cas à 1 échantillon) ; le cours montre `scipy.stats.ttest_ind(a, b, nan_policy='omit')` (2 éch., + `equal_var=False` pour Welch) et `scipy.stats.ttest_rel` (apparié).
- **Mise en perspective** : le t-test que tu connais (2 échantillons) compare `(ē₁ − ē₂) / SE`. Le t-test à 1 échantillon compare `(ē − μ₀) / SE` avec μ₀ = 0 ici. C'est la **même famille**, juste un cas particulier où l'un des "groupes" est remplacé par une valeur théorique.

### Application ici
Pour chaque stratégie, p-value du Student et verdict (avec correction de Bonferroni — voir 1.4).

Résultats clés :
| Stratégie | n | edge moyen | p-value Student | Verdict |
|---|---|---|---|---|
| `rsi_classic` | 7083 | **+1.27 %** | 3.9 × 10⁻⁹ | ✅ bat le hasard |
| `rsi_strict` | 973 | **+13.08 %** | 8 × 10⁻¹⁰ | ✅ bat le hasard |
| `rsi_trend` | 2777 | +0.27 % | 0.19 | ❌ non significatif |
| `db_bottom` | 8469 | −0.29 % | 0.99 | ❌ |
| `ma_crossover` | 5411 | −2.41 % | 1 | ❌ |
| toutes les figures (H&S, S/R) | — | négatif | > 0.45 | ❌ |

**Conclusion :** seules `rsi_classic` et `rsi_strict` battent le hasard.

---

## 1.3 Test de Wilcoxon (rangs signés) — confirmation non-paramétrique

### L'idée en une phrase
On veut vérifier la conclusion du Student **sans** supposer la moindre distribution sous-jacente, en regardant simplement les **rangs** des valeurs.

### Le calcul détaillé
**Étape 1.** Pour chaque trade, on calcule la valeur absolue de l'edge `|eᵢ|`.

**Étape 2.** On **classe ces valeurs absolues** de la plus petite à la plus grande, et on attribue un **rang** `rᵢ` (de 1 à n).

**Étape 3.** On calcule deux sommes :
```
W⁺ = somme des rangs des trades où eᵢ > 0
W⁻ = somme des rangs des trades où eᵢ < 0
```

**Étape 4.** La statistique de test est `W = min(W⁺, W⁻)` (ou `W⁺` selon la convention).

**Étape 5 — Loi sous H₀ :** sous H₀ (la médiane de e vaut 0), `W` suit une loi connue (loi de Wilcoxon, tabulée). Pour `n` grand, on l'approxime par une normale.

**Étape 6 — p-value :** comparer `W` observé à la loi théorique.

### Hypothèses et précautions
- Ne suppose **pas la normalité** (c'est son intérêt par rapport au Student).
- Suppose que la distribution est **symétrique** autour de la médiane (peu restrictif).
- Teste si la **médiane** vaut 0 (pas la moyenne — nuance importante quand la distribution est très asymétrique).

### Pourquoi ça marche
Sous H₀, les valeurs positives et négatives sont mélangées au hasard parmi tous les rangs. Donc `W⁺` et `W⁻` doivent être à peu près égaux, à `n(n+1)/4` chacun.

Si on observe un très gros `W⁺` (les positifs sont en haut du classement), c'est très improbable sous H₀ → on rejette.

### Où c'est déjà utilisé
- **Dans tes cours** : Wilcoxon est **explicitement mentionné dans le cours "Statistique avec R" (Chevallier)** comme un des tests sur la position, via `wilcox.test()`. C'est donc un test à ta disposition immédiate, présenté comme l'**équivalent non-paramétrique du Student** que tu connais. Si on retient un seul point à dire au jury : **Wilcoxon = même question que le Student, mais sans l'hypothèse de normalité** (parce qu'il travaille sur les rangs, pas les valeurs brutes).
- ⚠️ **Nuance honnête** : le test des rangs signés de Wilcoxon n'est **pas** couvert dans tes cours "Statistique avec SAS" ni "Statistique avec Python" (ils citent seulement **Mann-Whitney** comme alternative non-paramétrique, sans le coder). Il reste **vu en cours via R** — à présenter comme un complément non-paramétrique légitime.
- **Sur R** : `wilcox.test()` (vu en cours stat avec R).
- **Sur SAS** : `PROC NPAR1WAY` avec l'option `WILCOXON` (procédure existante, mais **hors du périmètre de ton cours SAS**).
- **Sur Python** (langage du projet) : `scipy.stats.wilcoxon` (fonction standard, mais **non montrée dans ton cours Python**).
- **Lien avec tes acquis** : tu as travaillé sur la **comparaison de modèles par précision** en classification. Wilcoxon joue un rôle similaire : il **compare** un échantillon à une référence (ici, 0) en termes de **rang**, ce qui est plus robuste que les valeurs absolues. C'est aussi un test classique pour comparer **deux classifieurs** sur les mêmes données (test de Wilcoxon des rangs signés sur les écarts de précision).
- **Pourquoi on l'a quand même utilisé ici** : pour avoir un **deuxième témoin** à côté du Student. Si les deux disent la même chose, le verdict est plus solide ; si les deux divergent (comme pour `rsi_trend`), on apprend quelque chose d'utile sur la distribution.

### Application ici
Wilcoxon **confirme** le Student pour `rsi_classic` (p = 5.8 × 10⁻⁶⁸) et `rsi_strict` (p = 4.8 × 10⁻²⁴) → résultat **robuste**.

Cas intéressant : `rsi_trend` a un Wilcoxon très significatif (p = 1.7 × 10⁻¹⁵) **alors que le Student dit non** (p = 0.19). Pourquoi ?
- Le Student teste la **moyenne** (sensible aux valeurs extrêmes),
- Wilcoxon teste la **médiane** (insensible aux extrêmes),
- Pour `rsi_trend`, la médiane est positive (beaucoup de petits gains), mais **quelques très grosses pertes** tirent la moyenne vers 0.

**Décision méthodologique du Bloc 1 :** on tranche **prudemment NON** pour `rsi_trend` — pour le trader, ce qui compte c'est la moyenne (le P&L cumulé), pas la médiane.

---

## 1.4 Correction de Bonferroni — le problème des comparaisons multiples

### L'idée en une phrase
On fait bien **un test séparé par stratégie** — c'est juste que quand on **multiplie le nombre de tests**, on **multiplie mécaniquement les occasions** de tomber sur un faux positif. Bonferroni durcit chaque test pour que le risque **global** (au moins un faux positif parmi tous les tests) reste maîtrisé.

### Le piège à comprendre absolument

> *« Mais je fais 10 tests séparés, un par stratégie. Pourquoi devrais-je changer le seuil ? »*

C'est l'intuition naturelle, et c'est le piège.

**Tu fais bien 10 tests indépendants, mécaniquement.** Mais quand tu interprètes l'ensemble, tu changes implicitement de question :
- Sur **un seul test** : *« quelle est la probabilité de me tromper sur cette stratégie ? »* → 5 %.
- Sur **10 tests** : *« quelle est la probabilité d'avoir AU MOINS UN FAUX POSITIF parmi mes 10 stratégies ? »* → **beaucoup plus que 5 %**.

### Analogie du dé à 6 faces

- Tu jettes **1 dé** : probabilité de tomber sur 6 = **1/6 ≈ 17 %**. Rare.
- Tu jettes **10 dés** : probabilité d'**au moins un 6** = **84 %**. Presque certain.

Tu n'as pas changé la règle du jeu. Chaque jet est toujours indépendant et a toujours 1/6 de chance. Mais en **multipliant les tentatives**, tu **multiplies les occasions** de tomber sur un 6.

### Le calcul exact pour ton cas

Sous H₀ (aucune des 10 stratégies ne marche), chaque test à α = 5 % a :
- P(faux positif sur ce test) = 0.05
- P(pas de faux positif) = 0.95

Sur **10 tests indépendants** :
```
P(zéro faux positif sur 10) = 0.95¹⁰ ≈ 0.599
P(au moins un faux positif sur 10) = 1 − 0.599 ≈ 0.401
```

**40 % de risque d'avoir au moins une stratégie déclarée gagnante par pur hasard**, alors qu'aucune ne marche réellement. Inacceptable.

### La solution Bonferroni : durcir chaque test individuel

On ne change rien à la **mécanique** des tests (toujours 10 tests séparés, toujours le même Student). On change juste la **barre à franchir** :
```
α_corrigé = α_global / m = 0.05 / 10 = 0.005
```

Garantie : le **risque global** (P(au moins un faux positif)) reste ≤ 5 %.

### Hypothèses et précautions
- Bonferroni est **conservateur** : il contrôle bien le risque global, mais peut **rater des effets réels** (perte de puissance, parce qu'on devient très exigeant).
- Pour beaucoup de tests (m > 20, comme en génomique avec des milliers de tests), on lui préfère parfois **Benjamini-Hochberg** qui contrôle le **FDR** (taux de faux découvertes) au lieu du **FWER** (probabilité d'au moins un faux positif), plus permissif mais toujours valide.
- Ici **m = 10** → Bonferroni reste adapté.

### Pourquoi ça marche (la démonstration)
**Inégalité de Boole :** la probabilité de l'union d'événements ≤ somme des probabilités individuelles.

Donc si chaque test individuel a un risque de faux positif ≤ α/m, alors :
```
P(au moins un faux positif) ≤ Σᵢ P(faux positif sur test i) ≤ m × (α/m) = α
```

CQFD : le risque global reste sous α.

### Illusion à éviter dans le rapport

Sans Bonferroni, tu pourrais publier : *« sur les 10 stratégies testées, le RSI trend a une p-value de 0.03 → il marche ! »*. C'est probablement un **artefact** du fait que tu as testé 10 fois.

Avec Bonferroni, la barre à 0.005 élimine ce candidat fragile. Tu ne déclares gagnantes que les stratégies qui restent significatives **malgré** la barre durcie. C'est exactement ce qu'on attend d'une démarche scientifique rigoureuse — et c'est ce qui distinguera ton mémoire d'un mémoire "naïf".

### Où c'est déjà utilisé
- **Dans tes cours** : Bonferroni **a bien été étudié explicitement**, comme **correction post-hoc pour comparaisons multiples**, dans tes cours "Statistique avec SAS" et "Statistique avec Python" (au même titre que Tukey et Dunnett). En Python, il s'obtient via `statsmodels` (`MultiComparison(...).allpairtest(stats.ttest_ind, method="bonf")`) ; en SAS il est présenté conceptuellement pour les comparaisons multiples (jugé « le plus conservateur »). Tu as donc déjà **la mécanique et le nom**.
- **Comparaison Tukey vs Bonferroni** : Tukey est **adapté à l'ANOVA** (compare toutes les paires de moyennes après ANOVA, méthode unifiée), Bonferroni est **général** (on l'applique sur n'importe quels tests, ici 10 tests de Student indépendants). Tes cours présentent les deux côte à côte : Bonferroni « sans groupe de référence », Dunnett « avec groupe de référence ».
- **Sur SAS** : Bonferroni est cité pour les comparaisons multiples ; Tukey s'obtient via `MEANS var / TUKEY` (1 facteur) ou `LSMEANS ... / ADJUST=TUKEY` (2 facteurs). (`PROC MULTTEST` existe pour Sidak/Holm/FDR mais **hors périmètre du cours**.)
- **Sur Python** : `MultiComparison(...).allpairtest(stats.ttest_ind, method="bonf")` (exactement l'appel vu en cours).
- **Lien avec tes acquis** : maintenant que tu as compris Bonferroni, **tu comprends mieux pourquoi Tukey existe** : c'est exactement le même problème (k comparaisons multiplient les faux positifs) mais avec une correction plus puissante adaptée à l'ANOVA.

### Application ici
On teste 10 stratégies → seuil corrigé à **0.005**.

- `rsi_classic` : p = 3.9 × 10⁻⁹ → **< 0.005** ✅ vraiment significatif
- `rsi_strict` : p = 8.0 × 10⁻¹⁰ → **< 0.005** ✅ vraiment significatif
- `rsi_trend` : p = 0.19 → **> 0.005** ❌ rejeté
- toutes les autres : p > 0.45 → ❌ rejeté

**Verdict :** seules **2 stratégies** (les deux RSI hors filtre tendance) survivent à la correction Bonferroni. Le verdict est solide même après contrôle du risque global.

---

# Étape 2 — Les stratégies diffèrent-elles entre elles ?

**Page Python :** `etape2_anova.py` **Résultat :** `03_resultats/etape2_anova.txt`

## 2.1 ANOVA à 1 facteur — comparer plusieurs groupes en un seul test

### L'idée en une phrase
Au lieu de comparer les stratégies **2 par 2** (ce qui ferait 45 tests à corriger), on demande **une seule chose** : « est-ce qu'au moins une stratégie a un edge moyen différent des autres ? ».

### Le calcul détaillé
On a `k = 10` groupes (stratégies), chacun avec `nⱼ` trades et un edge moyen `ēⱼ`.

**Étape 1 — Décomposer la variance totale en deux parties :**

- **SCE inter-groupes** (variabilité **entre** stratégies) :
  ```
  SCE_inter = Σⱼ nⱼ (ēⱼ − ē)²
  ```
  où `ē` est la grande moyenne (toutes stratégies confondues).
- **SCE intra-groupes** (variabilité **à l'intérieur** de chaque stratégie) :
  ```
  SCE_intra = Σⱼ Σᵢ (eⱼᵢ − ēⱼ)²
  ```

**Étape 2 — Statistique F :**
```
F = (SCE_inter / (k−1)) / (SCE_intra / (n−k))
```
Le numérateur = variance moyenne **entre** groupes. Le dénominateur = variance moyenne **dans** les groupes (le "bruit").

**Étape 3 — Loi sous H₀ :** si toutes les stratégies ont la même moyenne, `F` suit une loi de **Fisher F(k−1, n−k)**.

**Étape 4 — p-value :** si `F` observé est grand → p-value petite → on rejette H₀.

### Hypothèses et précautions
1. **Indépendance** des observations entre groupes (✓ chez nous : trades différents).
2. **Normalité** dans chaque groupe (rejetée mais peu importe à grand n grâce au TCL).
3. **Homoscédasticité** (variances égales entre groupes). On teste avec **Levene**. Si rejeté → ANOVA reste valide mais on peut basculer sur **Welch ANOVA** (corrige les variances inégales).

### Pourquoi ça marche
Si toutes les moyennes sont égales, l'écart **entre** groupes ne devrait pas être plus grand que l'écart **dans** les groupes (qui mesure le bruit naturel).

Si `F` est très supérieur à 1, c'est qu'il y a **trop d'écart entre groupes** pour que le hasard explique ça.

### Où c'est déjà utilisé
- **Dans tes cours** : tu as **explicitement étudié l'ANOVA à un facteur avec test post-hoc de Tukey**, à la fois **en SAS et en Python**. Donc ici, tu retrouves **exactement** la même mécanique : statistique F, décomposition de la variance (inter/intra), p-value sous loi de Fisher `F(k−1, N−k)`. Tes cours insistent aussi sur les **conditions** : normalité des résidus (Shapiro sur `model.resid`) et **homoscédasticité** (Bartlett — et Levene côté Python).
- **Sur SAS** : `PROC ANOVA` (effectifs équilibrés) ou `PROC GLM` (déséquilibrés). Syntaxe vue en cours :
  ```
  PROC GLM;
    CLASS strategy;
    MODEL edge = strategy;
    MEANS strategy / HOVTEST=bartlett;   /* homoscédasticité */
    MEANS strategy / TUKEY;              /* post-hoc */
  RUN;
  ```
- **Sur Python** (langage du projet) : ⚠️ **la forme vue en cours** est le **modèle linéaire** `statsmodels`, pas `f_oneway` :
  ```python
  from statsmodels.formula.api import ols
  import statsmodels.api as sm
  model = ols('edge ~ C(strategy)', data=df).fit()
  aov = sm.stats.anova_lm(model, typ=2)   # tableau d'ANOVA type II
  ```
  (`scipy.stats.f_oneway` donne le même F plus rapidement, mais **n'est pas la forme enseignée** dans ton cours Python.)
- **Spécificité ici** : on applique l'ANOVA dans un contexte **financier** (comparer le rendement de stratégies de trading) — domaine inédit, **mais la méthode est strictement la même** que ce que tu connais. C'est tout l'intérêt de la stat : un outil unique, des applications partout.

### Application ici
**F = 47, p ≈ 10⁻⁸⁵** → on rejette massivement H₀. Les stratégies **diffèrent** très significativement.

Mais l'ANOVA ne dit **pas lesquelles** diffèrent ⇒ on enchaîne avec Tukey.

---

## 2.2 Tukey HSD — quelles paires diffèrent vraiment ?

### L'idée en une phrase
Après une ANOVA significative, on veut savoir **quelles stratégies sont différentes** des autres, **deux par deux**, sans faire exploser le risque de faux positif.

### Le calcul détaillé
**Étape 1 — Pour chaque paire (i, j) :** calculer l'écart de moyennes
```
Δᵢⱼ = ēᵢ − ēⱼ
```

**Étape 2 — Statistique q (Studentized Range) :**
```
q = Δᵢⱼ / √(MS_intra / n_moyen)
```
où `MS_intra = SCE_intra / (n−k)`.

**Étape 3 — Loi sous H₀ :** sous H₀ (moyennes égales), `q` suit la **loi du range studentisé** `q(k, n−k)`, tabulée. Cette loi tient compte du fait qu'on regarde la **plus grande différence** parmi `k(k−1)/2` paires.

**Étape 4 :** on compare `|q|` au seuil critique. Si dépassé → la paire diffère significativement.

### Hypothèses et précautions
- Mêmes hypothèses que l'ANOVA.
- Tukey suppose des **tailles d'échantillon égales** entre groupes. Sinon, on prend **Tukey-Kramer** (légère adaptation).
- **Corrige automatiquement** le risque de faux positif global (pas besoin de Bonferroni en plus).

### Pourquoi ça marche
La loi du range studentisé tient compte du fait que parmi k groupes, on prendra **forcément** la paire la plus écartée. Donc le seuil est plus exigeant que celui d'un Student simple.

### Où c'est déjà utilisé
- **Dans tes cours** : tu as étudié Tukey **directement comme test post-hoc de l'ANOVA**, en SAS et en Python. C'est exactement le même usage qu'ici.
- **Sur SAS** : `PROC ANOVA`/`PROC GLM ... MEANS variable / TUKEY;` (1 facteur) ou `LSMEANS ... / ADJUST=TUKEY;` (2 facteurs) — produit automatiquement le tableau des comparaisons de paires avec p-values ajustées.
- **Sur Python** (langage du projet) : la forme vue en cours passe par **`MultiComparison`** :
  ```python
  import statsmodels.stats.multicomp as mc
  comp = mc.MultiComparison(df['edge'], df['strategy'])
  res = comp.tukeyhsd()          # tableau des paires + p-values ajustées
  ```
  (`pairwise_tukeyhsd(...)` existe aussi et donne le même résultat, mais le cours utilise `MultiComparison(...).tukeyhsd()`.)
- **Lien avec Bonferroni vu à la 1.4** : Tukey et Bonferroni résolvent le même problème (comparaisons multiples → faux positifs cumulés), mais avec deux philosophies :
  - **Bonferroni** = correction "à la main", générique, conservatrice, applicable à n'importe quels tests.
  - **Tukey** = correction "automatique" intégrée au modèle ANOVA, plus puissante (moins conservatrice) car elle exploite le fait que tous les groupes ont la même variance résiduelle.
  Maintenant que tu as vu les deux, tu sais que **ce sont des outils du même grenier**.

### Application ici
**18 paires sur 45** sont significativement différentes. Le `rsi_strict` se détache du reste (paires significatives contre presque toutes les autres stratégies).

---

## 2.3 ANOVA à 2 facteurs avec interaction — le classement dépend-il du régime ?

### L'idée en une phrase
On ajoute un deuxième facteur (le **régime de marché** : haussier/baissier) et on teste si l'effet d'une stratégie **change selon le régime**.

### Le calcul détaillé
Modèle linéaire :
```
edge = μ + αᵢ (effet stratégie) + βⱼ (effet régime) + γᵢⱼ (interaction) + ε
```

**Décomposition de la variance totale en 4 parties :**
- `SCE_stratégie` (effet propre stratégie)
- `SCE_régime` (effet propre régime)
- `SCE_interaction` (effet du couple stratégie × régime)
- `SCE_résidu` (bruit restant)

Pour chaque effet, on calcule un `F` propre :
```
F_stratégie = (SCE_stratégie / df_stratégie) / (SCE_résidu / df_résidu)
F_régime = ...
F_interaction = ...
```

**L'interaction est le test le plus important** : si elle est significative → l'effet de la stratégie **dépend** du régime.

### Hypothèses et précautions
- Mêmes que l'ANOVA simple.
- Idéalement design **équilibré** (mêmes effectifs par cellule), sinon ANOVA de type III.

### Pourquoi ça marche
Mathématiquement, on découpe la variance comme un puzzle : chaque effet "explique" une part. Si l'interaction explique une **grande** part, c'est qu'on ne peut pas dire « le RSI marche » dans l'absolu — il faut préciser « le RSI marche en marché baissier mais pas en haussier » (ou inversement).

### Où c'est déjà utilisé
- **Dans tes cours** : bonne nouvelle — l'**ANOVA à deux facteurs avec interaction est explicitement enseignée dans ton cours "Statistique avec SAS"** (le terme d'interaction s'écrit `facteur1*facteur2` dans le `MODEL`, avec `LSMEANS ... / ADJUST=TUKEY`). Tu n'introduis donc rien de nouveau : la décomposition de la variance s'enrichit (4 termes au lieu de 2), et on ajoute le **test d'interaction** (le plus important ici), exactement comme vu en cours.
- **Sur SAS** (extension directe de ton `PROC GLM`) :
  ```
  PROC GLM;
    CLASS strategy regime;
    MODEL edge = strategy regime strategy*regime;
  RUN;
  ```
  Le terme `strategy*regime` teste l'interaction. C'est juste **un terme de plus** dans le `MODEL`.
- **Sur Python** : `statsmodels.formula.api.ols('edge ~ C(strategy) * C(regime)', data=df).fit()` — le `*` génère automatiquement les effets principaux + interaction.
- **Pourquoi c'est crucial dans notre contexte** : tu sais déjà tester si A et B sont **indépendants** (χ²) ou comparer plusieurs groupes (ANOVA). Ici, on teste **un troisième niveau** : « est-ce que l'effet de A change selon B ? ». Cette question d'interaction est fondamentale dans toutes les sciences expérimentales (médecine, agronomie, économie), et c'est ce qui justifie le passage de "le RSI est bon" à "le RSI est bon **selon le régime**".

### Application ici
**F_interaction ≈ ?, p ≈ 5 × 10⁻⁶⁹** → interaction **massivement significative**.

**Interprétation :** une stratégie n'est pas bonne **dans l'absolu**, sa valeur **dépend du régime de marché**. C'est l'un des résultats forts du Bloc 1.

---

# Étape 3 — Gagner dépend-il du contexte ?

**Page Python :** `etape3_chi2.py` **Résultat :** `03_resultats/etape3_chi2.txt`

## 3.1 Test du khi-deux d'indépendance — relation entre deux variables qualitatives

### L'idée en une phrase
On veut savoir si deux **variables qualitatives** (catégories) sont **liées** ou **indépendantes** entre elles.

### Le calcul détaillé
On a un **tableau de contingence** qui croise deux variables. Exemple : `win × regime` :

|         | Gagnant | Perdant | Total |
|---------|---------|---------|-------|
| Haussier|  N₁₁    |  N₁₂    | N₁.   |
| Baissier|  N₂₁    |  N₂₂    | N₂.   |
| Total   |  N.₁    |  N.₂    |  N    |

**Étape 1 — Calculer les effectifs attendus sous H₀ (indépendance) :**
```
Eᵢⱼ = (Nᵢ. × N.ⱼ) / N
```
*Interprétation : si gagner était indépendant du régime, on aurait à peu près cet effectif dans chaque case.*

**Étape 2 — Statistique du khi-deux :**
```
χ² = Σᵢⱼ (Nᵢⱼ − Eᵢⱼ)² / Eᵢⱼ
```
Plus les effectifs observés s'éloignent des effectifs attendus, plus χ² est grand.

**Étape 3 — Loi sous H₀ :** si indépendance vraie, χ² suit une loi du **khi-deux à (r−1)(c−1) degrés de liberté**, où r = nb lignes et c = nb colonnes.

**Étape 4 — p-value :** si χ² observé > seuil critique → on rejette l'indépendance.

### Hypothèses et précautions
- Toutes les cases du tableau doivent avoir un **effectif attendu ≥ 5** (sinon on regroupe des modalités).
- Le χ² **détecte un lien** mais ne dit **pas sa force**. D'où le **V de Cramer** :
  ```
  V = √( χ² / (N × min(r−1, c−1)) )
  ```
  V ∈ [0, 1] :
  - V < 0.1 : lien **négligeable**,
  - 0.1 ≤ V < 0.3 : lien **faible**,
  - 0.3 ≤ V < 0.5 : lien **modéré**,
  - V ≥ 0.5 : lien **fort**.

### Pourquoi ça marche
Sous H₀ (indépendance), chaque écart `(Nᵢⱼ − Eᵢⱼ)` est dû au hasard d'échantillonnage. Normalisé par `√Eᵢⱼ`, il suit approximativement une loi normale. La somme des carrés de variables normales suit un χ² — d'où le nom.

### Où c'est déjà utilisé
- **Dans tes cours** : tu as **explicitement étudié le test du χ² d'indépendance**, en SAS et en Python. C'est exactement la même mécanique : tableau de contingence, effectifs attendus `t_ij = (n_i. × n_.j)/n`, statistique χ², degrés de liberté (r−1)(c−1), p-value. Tes cours couvrent aussi la **règle de Cochran** (≥ 80 % des effectifs théoriques ≥ 5).
- **Sur SAS** : `PROC FREQ` avec l'option `CHISQ`. Syntaxe vue en cours :
  ```
  PROC FREQ;
    TABLES win * regime / CHISQ EXPECTED;   /* EXPECTED = affiche les effectifs théoriques */
  RUN;
  ```
  L'option `CHISQ` sort aussi automatiquement la **correction de Yates** (tableaux 2×2), le **G-test** (Likelihood Ratio), et — avec `EXACT Fisher;` — le **test exact de Fisher**. ⚠️ **En revanche, le V de Cramér n'est PAS traité dans ton cours χ² SAS** (SAS réel peut le sortir, mais ton cours ne le couvre pas).
- **Sur Python** (langage du projet) : `scipy.stats.chi2_contingency(obs, correction=False)` renvoie `chi2, p, dof, thq` (χ², p-value, ddl, effectifs attendus) en un seul appel. L'argument `correction=` active la **correction de Yates**. Tableau de contingence via `pandas.crosstab(v1, v2)`.
- ⚠️ **Nouveauté à assumer : le V de Cramér**. Tu as appris le χ² (qui dit **s'il y a un lien**), mais **le V de Cramér n'est couvert dans aucun de tes 3 cours logiciels** (ni SAS, ni Python, ni R) — c'est donc une **méthode à introduire** dans le rapport, avec sa formule : `V = √(χ² / (N × min(r−1, c−1)))`, valeur entre 0 et 1, indépendante de la taille d'échantillon. Il faut la présenter comme une **extension du χ²** (que tu maîtrises), pas comme un acquis de cours. C'est particulièrement utile chez nous : à grand n, **tout χ² devient significatif** même pour des liens minuscules — le V de Cramér protège de cette illusion.
- **Lien avec ton projet de BDD** : un tableau de contingence, c'est techniquement le résultat d'un `GROUP BY var1, var2 COUNT(*)`. Si tu as fait des **requêtes SQL avec agrégations**, tu sais déjà construire la matière première du χ² — il ne manque que la couche statistique par-dessus.

### Application ici
Trois croisements menés :
| Croisement | χ² | p-value | V de Cramer | Verdict |
|---|---|---|---|---|
| win × régime | significatif | < 0.05 | **0.05** | lien réel mais **faible** |
| win × secteur | non | 0.08 | ≈ 0 | **indépendant** |
| win × stratégie | très significatif | < 10⁻³⁰⁰ | **0.41** | lien **fort** |

**Lecture :**
- Le **secteur** ne change pas le taux de gain (cohérent avec un marché efficient sur le secteur).
- La **stratégie** change énormément le taux de gain (le RSI gagne beaucoup plus souvent que les figures).
- Le **régime** a un effet réel mais marginal.

---

# Étape 4 — Le contexte d'entrée sépare-t-il gagnants et perdants ?

**Page Python :** `etape4_acp.py` **Résultat :** `03_resultats/etape4_acp.txt` + `etape4_acp.png`

## 4.1 ACP — Analyse en Composantes Principales

### L'idée en une phrase
On a plusieurs variables quantitatives (volatilité, RSI, distance à la MM200, durée…) et on veut les **résumer en 2 axes** pour pouvoir les **visualiser** sur un graphique, sans perdre trop d'information.

### Notations (cours Périnel, M1 Strasbourg)
Pour respecter les notations exactes du cours d'analyse des données :
- `X` = matrice des données, de dimension `(n, p)` (n individus / lignes, p variables / colonnes)
- `xᵢⱼ` = valeur de l'individu i sur la variable j
- `mᵢ` = **masse** de l'individu i (généralement `1/n`)
- `G = (x̄₁, ..., x̄_p)` = centre de gravité du nuage
- `λ_k` = **valeur propre** de rang k = **inertie** captée par l'axe k
- `c_ik` = **coordonnée** de l'individu i sur l'axe k
- `d_jk` = coordonnée de la variable j sur l'axe k (en ACP normée, c'est la **corrélation** entre Xⱼ et l'axe k)
- `I_total` = **inertie totale** du nuage = somme des variances des variables

### Le calcul détaillé
**Étape 1 — Centrage systématique :** pour chaque variable Xⱼ, on remplace `xᵢⱼ` par `xᵢⱼ − x̄ⱼ`. Géométriquement, on translate le nuage de sorte que `G` se confonde avec l'origine `O`. **Indispensable** pour que la matrice à diagonaliser soit la matrice de variance-covariance.

**Étape 2 — Réduction (= ACP normée).** On divise chaque variable centrée par son écart-type :
```
zᵢⱼ = (xᵢⱼ − x̄ⱼ) / s_j
```
**Obligatoire** si les variables ont des unités différentes (ici : volatilité en %, durée en jours, RSI en points). Sans ça, la variable à plus grande variance écrase les autres.

⚠️ **Vocabulaire du cours Périnel :** on parle d'**ACP normée** quand on réduit, **ACP simple (ou non normée)** quand on ne fait que centrer.

**Étape 3 — Matrice à diagonaliser.** En ACP normée, on diagonalise la **matrice de corrélation** :
```
R = (1/n) × Zᵀ × Z   (matrice p × p)
```
En ACP simple, on diagonalise la matrice de **variance-covariance**.

**Étape 4 — Diagonalisation.** On cherche les vecteurs propres `u₁, u₂, ..., u_p` et valeurs propres `λ₁ ≥ λ₂ ≥ ... ≥ λ_p` de R. Démonstration clé du cours (Cours 1bis Périnel) :
```
(1/n) × XᵀX × u₁ = λ₁ × u₁
```
C'est-à-dire : le premier axe factoriel est le **vecteur propre associé à la plus grande valeur propre** de la matrice de variance-covariance (ou de corrélation en ACP normée).

**Étape 5 — Composantes principales.** La k-ème composante principale `CP_k` est la projection des individus sur l'axe `u_k` :
```
c_ik = z_i · u_k   (coordonnée de l'individu i sur l'axe k)
```
Vecteur `CP_k = X × u_k`.

**Étape 6 — Formules de transition individu → variable (cours Périnel).** En ACP normée, on relie les coordonnées des variables `d_jk` à celles des individus :
```
v_k = (1 / √λ_k) × X × u_k
```
`d_jk` est alors le **coefficient de corrélation** entre la variable Xⱼ et l'axe k — propriété fondamentale du **cercle des corrélations**.

**Étape 7 — Inertie expliquée.** L'inertie totale vaut `I_total = Σⱼ V(X_j) = trace(R) = p` (en ACP normée). La part captée par l'axe k vaut `λ_k / I_total`.

### Critères de sélection du nombre d'axes (cours Périnel §11) ⭐

Trois critères vus dans le cours, à mentionner explicitement dans le rapport :

1. **Critère de Kaiser** (1960). En ACP normée, on retient les axes tels que `λ_k > 1` (l'axe doit "porter" plus d'information qu'une variable moyenne).
2. **Scree-test de Cattell** (1966). On trace l'**éboulis des valeurs propres** (λ_k vs k) et on cherche le **coude** (point de cassure) — on retient les axes avant le coude.
3. **Modèle du bâton brisé** (Frontier 1976). Une référence aléatoire : on compare λ_k à la valeur attendue sous H₀ "axes aléatoires". Si `λ_k > bk_k` où `bk_k = Σ_{j=k}^p (1/j)`, on garde l'axe.

⚠️ **Bonne pratique du rapport** : justifier le nombre d'axes retenus par **au moins l'un de ces 3 critères**, pas par "j'ai pris 2 parce que c'est visualisable".

### Diagnostics par individu / variable (cours Périnel §10) ⭐

Le cours insiste sur deux indicateurs **systématiquement** calculés pour chaque axe :

#### Qualité de représentation `cos²(i, k)`
```
cos²(i, k) = c_ik² / Σ_j c_ij²
```
Mesure à quel point l'individu i est **bien représenté** sur l'axe k. Proche de 1 = bien projeté, proche de 0 = mal projeté (ne pas interpréter).

#### Contribution `CTR(i, k)`
```
CTR(i, k) = m_i × c_ik² / λ_k
```
Mesure l'**effet levier** : à quel point l'individu i a contribué à construire l'axe k. Σ_i CTR(i, k) = 1.

⚠️ Un individu à **fort CTR sur PC1** est un individu **structurant** — c'est lui qui tire l'axe.

### Variables illustratives (= supplémentaires) — concept clé Périnel §12 ⭐

> **Très utile dans notre cas et pas encore exploité !**

**Idée :** projeter des variables ou modalités qui **n'ont pas servi** à construire les axes, mais qu'on veut **interpréter** par rapport à eux. Par exemple : projeter `régime`, `secteur`, `win` (qualitatives) en illustratives sur les axes construits avec les variables quantitatives.

**Pour une variable qualitative illustrative**, on calcule pour chaque modalité m :
- `c̄_mk` = coordonnée moyenne des individus de la modalité m sur l'axe k
- **V.Test** (valeur-test) :
```
V.Test(m, k) = c̄_mk × √(n_m / V_k)
```
où `n_m` = effectif de la modalité, `V_k` = variance des individus sur l'axe k.

**Règle de lecture** : `|V.Test| > 1.96` ⇔ la modalité est **significativement** liée à l'axe (au sens classique p-value < 5 %).

**Et le rapport de corrélation η²** :
```
η²(qualitative, axe_k) = V_inter / V_totale
```
Mesure la force de liaison entre une variable qualitative illustrative et un axe. η² ∈ [0, 1].

### Biplot (Périnel — représentation simultanée)
Représenter **sur le même graphique** les individus (par leurs coordonnées) et les variables (par leurs corrélations aux axes). Très élégant pour le rapport.

### Hypothèses et précautions
- **Variables quantitatives** (continues ou ordinales) — sinon utiliser l'AFC.
- **Standardisation obligatoire** si les variables ont des échelles différentes.
- L'ACP capture des relations **linéaires** uniquement. Pour les non-linéaires : **UMAP** (méthode plus récente, à comparer ; tu l'as vu en M1).

### Pourquoi ça marche
Géométriquement, l'ACP cherche la **direction de l'espace dans laquelle les données sont les plus étalées**. C'est `PC1` (axe portant le plus d'inertie). Puis la direction **orthogonale** la plus étalée → `PC2`. Etc.

Mathématiquement, on démontre (Cours 1bis Périnel) que cette direction est le **vecteur propre associé à la plus grande valeur propre** de la matrice de variance-covariance (ou de corrélation en ACP normée).

### Où c'est déjà utilisé
- **Dans tes cours d'analyse multivariée (Périnel)** : tu as **explicitement étudié l'ACP** (143 pages). Donc ici, **tu retrouves la méthode telle quelle** : centrage, réduction (ACP normée), matrice de corrélation, vecteurs propres, valeurs propres, inertie, cos², CTR, critère de Kaiser, scree-test de Cattell, bâton brisé, variables illustratives, V.Test, η², biplot.
- **Sur SAS** : `PROC PRINCOMP` fait l'ACP. **Sur R** : `FactoMineR::PCA()` (la référence, vue en cours).
- **Sur Python** : `sklearn.decomposition.PCA` (très utilisé) ou code numpy direct (c'est notre choix ici pour rester transparent).
- **Lien avec ton cours d'apprentissage statistique** : tu as étudié la **réduction de dimension** avec **UMAP, décomposition de Fourier, B-spline**. L'ACP est la **plus ancienne et la plus interprétable** de ces méthodes :
  - **ACP** : réduction **linéaire**, axes interprétables (loadings, corrélations, cos², CTR), idéale pour visualiser et **expliquer**.
  - **UMAP** : réduction **non-linéaire** via graphe des k plus proches voisins, meilleure pour **visualiser des clusters** mais axes non interprétables. ⚠️ Ne préserve **NI** les distances **NI** les densités → ne **pas** conclure sur des clusters UMAP sans validation indépendante.
  - **Fourier / B-spline** : décomposition spécifique aux **signaux** (séries temporelles, courbes).
  Quand tu as voulu réduire la dimension, tu avais le choix entre ces outils — ici on prend ACP parce qu'on veut comprendre **quelles variables** discriminent les gagnants des perdants (besoin d'interprétabilité, pas juste de visualisation).
- **Bibliographie cours Périnel à citer** : Saporta (2006), Lebart-Morineau-Piron (2006), Escofier-Pagès (2008), Husson-Lê-Pagès (2009).
- **Spécificité ici** : on l'applique à des **trades** au lieu de pixels, gènes ou patients — mais la mécanique est identique.

### Application ici
**4 variables de contexte d'entrée :** `vol_entry`, `rsi_entry`, `dist_ma200`, `holding_days`.

**Résultats :**
- PC1 explique ≈ 35 % de l'inertie totale, PC2 ≈ 25 %.
- On projette les trades **gagnants** (verts) et **perdants** (rouges) sur le plan (PC1, PC2).
- Le **d de Cohen** entre les deux nuages = **−0.12** → effet **négligeable**.

**À enrichir (à faire) :**
- Vérifier le **critère de Kaiser** (combien de λ_k > 1 ?) pour justifier le nombre d'axes.
- Projeter `regime`, `secteur`, `win` en **variables illustratives** + calculer leurs V.Test sur PC1 et PC2.
- Si une modalité a |V.Test| > 1.96 sur PC1, c'est un indicateur de séparation que le d de Cohen ne capte pas.

**Conclusion :** le contexte d'entrée seul **ne sépare pas** gagnants et perdants. Une stratégie ne peut pas être validée juste sur le profil du jour d'entrée — il faudra des signaux **externes** (Blocs 2 et 3).

---

# Étape 5 — Quelles stratégies vont avec quels résultats ?

**Page Python :** `etape5_afc.py` **Résultat :** `03_resultats/etape5_afc.txt` + `etape5_afc.png`

## 5.1 AFC — Analyse Factorielle des Correspondances

### L'idée en une phrase
L'AFC est l'**ACP des variables qualitatives** : elle prend un tableau croisant deux variables catégorielles (comme un χ²) et le **dessine** sur un graphique 2D pour voir quelles modalités vont ensemble.

### Notations (cours Périnel, M1 Strasbourg)
- `n_ij` = effectif observé dans la cellule (i, j) du tableau de contingence
- `n` = effectif total
- `f_ij = n_ij / n` = fréquence relative
- `f_i. = Σ_j f_ij` et `f.j = Σ_i f_ij` = **fréquences marginales** ligne / colonne
- `t_ij = n × f_i. × f_j.` = **effectif théorique** sous indépendance
- **Différence majeure avec l'ACP** : les masses sont **différentes** d'une ligne à l'autre (= `f_i.`). Cela change la métrique utilisée.

### Le calcul détaillé
**Étape 1 — Tableau de contingence.** Ici : `stratégie × tranche de rendement` (`perte`, `gain_modéré`, `gain_fort`). Une cellule = effectif observé.

**Étape 2 — Profils lignes et profils colonnes (cours Périnel).** L'AFC ne travaille pas directement sur les effectifs, mais sur les **profils** :
```
profil ligne i : (f_i1/f_i., f_i2/f_i., ..., f_iJ/f_i.)
profil colonne j : (f_1j/f.j, ..., f_Ij/f.j)
```
**Idée centrale :** deux lignes ont le même profil ⇔ elles "se répartissent" de la même façon sur les colonnes.

**Étape 3 — Distance du χ² (cours Périnel) ⭐.** Au lieu de la distance euclidienne classique, l'AFC utilise la **distance du χ²** entre profils :
```
d²_χ²(i, l) = Σ_j (1/f.j) × (f_ij/f_i. − f_lj/f_l.)²
```
**Pourquoi cette métrique ?** Pour respecter le **principe d'équivalence distributionnelle** (Benzécri) : fusionner deux colonnes de même profil ne doit pas changer la distance entre lignes. La pondération `1/f.j` donne plus de poids aux modalités rares.

**Étape 4 — Inertie totale.**
```
I_total = D² / n = χ²/n
```
où `D²` est la statistique du χ² du tableau. **Magnifique propriété** : l'inertie totale d'une AFC est directement reliée au χ² du tableau, donc à la statistique de test d'indépendance.

**Étape 5 — Décomposition spectrale.** On diagonalise la matrice des résidus standardisés. Les valeurs propres `λ_k` (souvent appelées **inerties principales** en AFC) vérifient :
```
0 ≤ λ_k ≤ 1
Σ_k λ_k = I_total
```

**Étape 6 — Coordonnées et formules de transition (cours Périnel).**
Coordonnées des lignes sur l'axe k : `c_ik = (1/√λ_k) × Σ_j (f_ij/f_i.) × d_jk` (formule **quasi-barycentrique**).
Coordonnées des colonnes : `d_jk = (1/√λ_k) × Σ_i (f_ij/f.j) × c_ik`.

⇒ Les lignes et les colonnes sont **représentables sur le même plan**.

**Étape 7 — Résidus de Haberman (cours Périnel, lien avec χ²) ⭐.**
```
r_ij = (n_ij − t_ij) / √(t_ij × (1 − f_i.) × (1 − f.j))
```
Sous H₀ (indépendance), `r_ij ~ N(0, 1)`. Donc `|r_ij| > 1.96` ⇔ p-value < 5 %. **Utilisable comme test cellule par cellule.**

### Hypothèses et précautions
- L'AFC est **descriptive**, pas inférentielle (pas de p-value directement — mais voir résidus Haberman).
- C'est l'**outil de visualisation** qui complète le test du χ².
- Bien lire : **les distances ligne-colonne ne sont pas directement interprétables** ; on lit les proximités entre lignes ou entre colonnes, et les **directions communes** (cadran haut-droite, etc.).
- ⚠️ **Effet Guttman (cours Périnel)** : si une variable cache un ordre sous-jacent (par exemple : satisfaction de "très insatisfait" à "très satisfait"), l'AFC produit une **parabole** caractéristique sur les axes 1-2. C'est un piège classique — bien identifier avant d'interpréter.

### Pourquoi ça marche
Sous **indépendance**, tous les résidus seraient nuls et l'AFC ne produirait aucun axe (toutes les λ_k = 0). Plus les résidus sont grands, plus les axes ont d'inertie. Les modalités qui contribuent fortement à un axe sont **fortement associées** dans la direction de cet axe.

### Où c'est déjà utilisé
- **Dans tes cours d'analyse multivariée (Périnel)** : tu as **explicitement étudié l'AFC** (62 pages). Tu retrouves ici la même mécanique : profils, distance du χ², principe d'équivalence distributionnelle, formules de transition (relations quasi-barycentriques), résidus de Haberman, effet Guttman.
- **Sur SAS** : `PROC CORRESP` fait l'AFC directement.
- **Sur R** : `FactoMineR::CA()` (vu en cours, le standard).
- **Sur Python** : pas de lib standard parfaite (contrairement à l'ACP). Souvent codé en numpy direct ou via la lib `prince`. Ici, on l'a codé en numpy pur pour rester transparent.
- **Lien avec le χ² et l'ACP que tu connais** : c'est exactement la **synthèse** de ce que tu as déjà appris.
  - Le **χ²** te dit : *« il y a un lien entre les variables. »*
  - L'**AFC** te dit : *« voici la carte de ce lien — telle modalité va avec telle autre. »*
  - Et la mécanique de l'AFC, mathématiquement, est l'**ACP avec la métrique du χ² au lieu de la distance euclidienne**, appliquée au tableau des fréquences. Quand tu as compris l'ACP **et** le χ², l'AFC est l'enfant naturel des deux : I_total = χ²/n.
- **Bibliographie cours Périnel à citer** : Saporta (2006), Lebart-Morineau-Piron (2006), Escofier-Pagès (2008), Husson-Lê-Pagès (2009).

### Application ici
**Résultat clé :**
- L'axe 1 explique **76 % de l'inertie** : il sépare clairement **gains** (gauche) et **pertes** (droite).
- Les stratégies **RSI** sont du côté gains (en particulier `rsi_strict` pointe vers `gain_fort`).
- Les figures (`sr_breakout`, `sr_breakdown`, `hs_classic`, `ma_crossover`) sont du côté pertes.

**À enrichir (à faire) :** calculer les **résidus de Haberman** sur le tableau pour avoir un test cellule par cellule (|r_ij| > 1.96 ⇔ liaison significative à 5 %).

**La carte confirme visuellement** les résultats des tests d'hypothèse — c'est cohérent et rassurant.

---

# Étape 6 — Quelles combinaisons de modalités vont avec « gagnant » ?

**Page Python :** `etape6_acm.py` **Résultat :** `03_resultats/etape6_acm.txt` + `etape6_acm.png`

## 6.1 ACM — Analyse des Correspondances Multiples

### L'idée en une phrase
L'ACM **généralise l'AFC** à **plus de deux variables qualitatives** en même temps. On peut croiser `stratégie + régime + secteur + win`.

### Notations (cours Périnel, M1 Strasbourg)
- `I` = nombre d'individus
- `J` = nombre de variables qualitatives
- `k_j` = nombre de modalités de la variable j
- `K = Σ_j k_j` = nombre **total** de modalités
- `I_k` = effectif de la modalité k (combien d'individus la prennent)
- `m_k = I_k / (I × J)` = **masse** de la modalité k
- `xᵢₖ` = 0 ou 1 dans le tableau disjonctif complet (TDC)

### Le calcul détaillé
**Étape 1 — Tableau disjonctif complet (TDC).** Chaque variable qualitative est explosée en plusieurs colonnes 0/1 (une par modalité). Exemple :
- `strategy` (10 modalités) → 10 colonnes 0/1
- `regime` (3 modalités) → 3 colonnes 0/1
- `sector` (11 modalités) → 11 colonnes 0/1
- `win` (2 modalités) → 2 colonnes 0/1

Chaque trade est un vecteur ligne de 0 et 1, où **exactement une colonne par variable vaut 1**. Total : K colonnes, somme par ligne = J.

**Étape 2 — Distance entre individus (cours Périnel) ⭐.**
```
d²_χ²(i, l) = (1/J) × Σ_k (I/I_k) × (xᵢₖ − xₗₖ)²
```
**Idée :** deux individus sont proches s'ils partagent un maximum de modalités, surtout **rares** (terme `I/I_k` qui amplifie les modalités peu fréquentes).

**Étape 3 — Inertie totale (cours Périnel).** Propriété remarquable :
```
I_total = K/J − 1
```
**L'inertie totale ne dépend que du nombre de modalités et de variables**, pas des effectifs ! Conséquence directe : les pourcentages d'inertie sont **mécaniquement faibles** (la "totale" est gonflée artificiellement).

**Étape 4 — Nombre d'axes maximal.**
```
nombre d'axes = K − J
```

**Étape 5 — Application AFC.** On applique une AFC simple au TDC (ou alternativement à la **matrice de Burt** = matrice de tous les croisements 2 à 2 entre modalités). Coordonnées des modalités sur les axes par formules quasi-barycentriques (mêmes que l'AFC, généralisées).

**Étape 6 — Correction de Benzecri (cours Périnel) ⭐.** Les valeurs propres brutes de l'ACM sont **toujours faibles** (souvent < 0.3). Benzecri propose une correction :
```
λ*_k = ((J / (J − 1))² × (λ_k − 1/J))²   (si λ_k > 1/J, sinon 0)
```
Après correction, les pourcentages d'inertie deviennent **comparables** à ceux d'une ACP "raisonnable".

⚠️ **À mentionner dans le rapport** : utiliser **soit** les inerties brutes (et expliquer pourquoi elles sont basses), **soit** les inerties corrigées de Benzecri (et le préciser).

**Étape 7 — Rapport de corrélation η² (cours Périnel).** Pour une variable qualitative `j` et un axe `C_s` :
```
η²(j, C_s) = V_inter / V_totale
```
Mesure la **liaison** entre la variable j et l'axe s. Plus η² est proche de 1, plus la variable est associée à l'axe. **Outil de lecture principal** en ACM (on ne lit pas seulement la carte mais aussi les tableaux η²).

### Hypothèses et précautions
- Toutes les variables doivent être qualitatives (sinon il faut **discrétiser** les quantitatives en classes — par exemple `vol_entry` en 3 quantiles).
- **Pourcentages d'inertie mécaniquement faibles** (souvent < 10 % par axe) : c'est une propriété connue de l'ACM. On utilise la **correction de Benzecri** pour des % plus comparables.
- On lit les **proximités** entre modalités, pas les distances absolues.
- ⚠️ **Effet Guttman** (cours Périnel) : même piège qu'en AFC — si une variable cache un ordre, la carte produit une parabole.
- ⚠️ L'ACM est particulièrement adaptée pour **détecter des liaisons non linéaires** entre variables qualitatives.

### Pourquoi ça marche
Les modalités qui apparaissent **souvent ensemble** (mêmes trades) se retrouvent **proches** sur la carte. Celles qui ne co-occurrent jamais sont **opposées**.

### Où c'est déjà utilisé
- **Dans tes cours d'analyse multivariée (Périnel)** : l'ACM est **explicitement couverte** dans le cours de Périnel (3ème partie, 59 pages). Donc tu retrouves ici la méthode telle quelle : TDC, distance du χ² adaptée, inertie K/J−1, correction de Benzecri, rapport de corrélation η².
- **La différence ACM vs AFC en une phrase** :
  - **AFC** : croise **2 variables qualitatives** (par exemple stratégie × tranche de rendement).
  - **ACM** : croise **N variables qualitatives** simultanément (stratégie + régime + secteur + win = 4 variables).
- **Sur SAS** : `PROC CORRESP` avec option `MCA`.
- **Sur R** : `FactoMineR::MCA()` (le standard, vu en cours).
- **Sur Python** : `prince` (lib externe) ou code numpy direct.
- **Astuce méthodologique** : techniquement, l'ACM se fait en construisant un **tableau disjonctif complet** (chaque modalité devient une colonne 0/1), puis en appliquant un AFC dessus. Donc **mathématiquement, l'ACM = AFC sur TDC**. Pas de nouvelle théorie à apprendre — juste une recette pour étendre l'AFC.
- **Piège à connaître pour le rapport** : les pourcentages d'inertie de l'ACM sont **mécaniquement bas** car l'inertie totale K/J−1 est gonflée. La **correction de Benzecri** rend les % comparables à ceux d'une ACP.
- **Bibliographie cours Périnel à citer** : Saporta (2006), Lebart-Morineau-Piron (2006), Escofier-Pagès (2008), Husson-Lê-Pagès (2009), et spécifiquement **Benzecri** pour la correction.

### Application ici
Variables croisées : `strategy + regime_entry + sector + win`.

**Résultat clé (visuel) :**
- **« gagnant »** voisine `rsi_classic`, `rsi_trend`, `db_bottom`, secteur `Information Technology`.
- **« perdant »** voisine `ma_crossover`, `sr_breakout`, `hs_inverse`.
- **Les secteurs restent groupés au centre** → le secteur ne discrimine pas le gain (cohérent avec le χ² de l'étape 3).

**À enrichir (à faire) :**
- Appliquer la **correction de Benzecri** sur les valeurs propres → pourcentages d'inertie comparables à ceux d'une ACP.
- Calculer les **rapports de corrélation η²** entre chaque variable et les 2 premiers axes pour quantifier quelle variable structure le plus chaque axe.

---

# Récapitulatif et fil conducteur

Les 6 étapes répondent toutes à la même question (« les stratégies techniques ont-elles une valeur ? ») mais par **6 chemins différents** :

| Étape | Outil | Type de réponse | Verdict |
|---|---|---|---|
| 1 | Tests d'hypothèse | quantitatif (p-value par stratégie) | Seuls les RSI battent le hasard |
| 2 | ANOVA + Tukey | comparaison globale | Les stratégies diffèrent, et **l'effet dépend du régime** |
| 3 | χ² + V Cramer | force du lien qualitatif | La stratégie compte beaucoup, le secteur non |
| 4 | ACP | géométrie quantitative | Le contexte d'entrée ne sépare pas gagnants/perdants |
| 5 | AFC | géométrie qualitative (2 var.) | Les RSI vont avec les gains |
| 6 | ACM | géométrie qualitative (n var.) | « Gagnant » co-occurre avec RSI, pas avec les figures |

**Convergence :** quand 6 méthodes indépendantes pointent toutes vers la même conclusion (« seul le RSI bat le hasard »), c'est un **gage de solidité**. C'est exactement la stratégie scientifique pour donner du poids à un résultat.

---

## À venir (hors de ce bloc)
- **Géométrie des figures** (prominence/symétrie/pente du cou) comme variables supplémentaires.
- **Régression** : **PAS dans ce bloc** — c'est le BLOC FINAL (voir `../ARCHITECTURE.md`), une fois tous les blocs validés.

---

## Bibliographie consolidée (à reprendre dans le rapport)

> Toutes les méthodes utilisées dans ce Bloc 1 sont ancrées dans des références académiques précises — citer ces ouvrages dans le rapport leur donne tout leur poids.

### Analyse multivariée (étapes 4, 5, 6 — ACP, AFC, ACM)
*Notations et concepts directement issus du cours d'analyse des données de **E. Périnel**, M1 Strasbourg.*
- **Saporta G.** (2006). *Probabilités, analyses des données et statistiques*, 2e éd., Technip. — La référence française pour ACP/AFC/ACM avec démonstrations rigoureuses.
- **Lebart L., Morineau A., Piron M.** (2006). *Statistique exploratoire multidimensionnelle*, Dunod. — Standard du domaine.
- **Escofier B., Pagès J.** (2008). *Analyses factorielles simples et multiples*, 4e éd., Dunod. — Référence sur l'AFC et l'ACM avec le concept de masses différentes.
- **Husson F., Lê S., Pagès J.** (2009). *Analyse de données avec R*, Presses Universitaires de Rennes. — Compagnon idéal du package `FactoMineR` (créé par les auteurs).
- **Bouroche J.M., Saporta G.** (1980). *L'analyse des données*, PUF, Collection Que sais-je ? — Introduction historique.
- **Benzecri J.-P.** (1973). *L'Analyse des Données*. — Père fondateur de l'école française d'analyse des données. À citer pour la correction de Benzecri en ACM et le principe d'équivalence distributionnelle.

### Tests d'hypothèse (étapes 1, 2, 3)
- **Gosset W.S. ("Student")** (1908). « The probable error of a mean ». *Biometrika*. — Article fondateur de la loi de Student.
- **Welch B.L.** (1947). « The generalization of "Student's" problem when several different population variances are involved ». *Biometrika*. — Variante Welch du test t.
- **Shapiro S.S., Wilk M.B.** (1965). « An analysis of variance test for normality (complete samples) ». *Biometrika*.
- **Wilcoxon F.** (1945). « Individual comparisons by ranking methods ». *Biometrics*. — Origine du test des rangs signés.
- **Tukey J.W.** (1949). « Comparing individual means in the analysis of variance ». *Biometrics*. — Test post-hoc HSD.
- **Bonferroni C.E.** (1936). *Teoria statistica delle classi e calcolo delle probabilità*. — Origine de la correction.
- **Cohen J.** (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed., Routledge. — Référence pour le d de Cohen et les tailles d'effet.

### Fondement théorique (étapes 1, 2)
- **Théorème Central Limite** (Lindeberg, Lévy) — démontre la quasi-normalité des moyennes d'échantillon à grand n, justifiant le Student même sans normalité des données originales.

### Outils logiciels mentionnés
- **R / FactoMineR** : Husson, Josse, Lê (2008). « FactoMineR: An R Package for Multivariate Analysis ». *Journal of Statistical Software*. — Package R standard pour ACP/AFC/ACM en cours.
- **Python / scipy.stats, statsmodels** : librairies vues dans le cours **« Statistique avec Python »** (N. Poulin, M1) — `scipy.stats` (shapiro, ttest_ind, chi2_contingency, bartlett/levene, chisquare) et `statsmodels` (ols + anova_lm, MultiComparison pour Tukey/Bonferroni). Ce sont **exactement** les outils utilisés dans les scripts du Bloc 1. scikit-learn = standard du projet pour l'ACP.
- **SAS** : cours **« Statistique avec SAS »** (N. Poulin / L. Gardes, M1) — `PROC UNIVARIATE NORMAL` (Shapiro + K-S + Anderson-Darling + Cramér-von Mises), `PROC TTEST`, `PROC ANOVA`/`PROC GLM` (Tukey, Bartlett, interaction), `PROC FREQ` (χ², Yates, Fisher, G-test), `PROC REG` (VIF, sélection), `PROC GENMOD` (GLM logistique/Poisson). Chaque test du Bloc 1 a son équivalent SAS documenté.

---

## Cohérence des notations avec les cours M1

Pour information du jury, voici la table de correspondance entre les notations utilisées dans ce document et celles des cours suivis :

| Concept | Cours Périnel (M1) | Ce document |
|---|---|---|
| Matrice de données | `X` de dimension `(n, p)` | idem |
| Centre de gravité | `G` | idem (peut s'écrire `O` après centrage) |
| Masse | `m_i` | idem |
| Inertie totale | `I_total` | idem |
| Valeur propre k | `λ_k` | idem (ou « variance de l'axe k ») |
| Coordonnée individu i / axe k | `c_ik` | idem |
| Composante principale | `CP_k` | idem |
| Qualité de représentation | `cos²` | idem |
| Contribution | `CTR` | idem |
| Valeur-test | `V.Test` | idem |
| Rapport de corrélation | `η²` | idem |
| Distance du χ² (AFC, ACM) | `d²_χ²` | idem |
| Tableau disjonctif complet | `TDC` | idem |
| Statistique de Student | `t` | idem |
| Statistique de Fisher | `F` | idem |
| Statistique du χ² | `χ²` (ou `D²` dans certains cours) | `χ²` |
| Statistique de Wilcoxon | `W` | idem |
