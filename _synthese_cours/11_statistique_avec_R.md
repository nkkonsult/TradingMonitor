---
name: 11-statistique-avec-R
description: Synthèse cours "Statistique avec R" (Augustin Chevallier, 20 slides) — régression lm(), tests statistiques usuels, classification (CAH, k-means, PAM, Fuzzy)
metadata:
  type: reference
---

# Statistique avec R (Augustin Chevallier, 20 slides Beamer)

> Cours **pratique et bref** (slides) — recensement des fonctions R essentielles pour : régression, tests, clustering.

## 1. Régression — `lm()`

### Syntaxe
```r
m1 <- lm(formula, data, ...)
```

### Formules R
| Syntaxe | Sens |
|---|---|
| `y ~ x1 + x2` | y expliqué par x1 et x2 (avec constante) |
| `y ~ x1 + x2 - 1` ou `+0` | sans constante |
| `y ~ x1:x2` | **interaction** seule (x1·x2) |
| `y ~ x1*x2` | équivaut à `x1 + x2 + x1:x2` ⭐ |

### Fonctions associées
- `summary(m1)` — résumé (coefs, p-valeurs, R²)
- `predict(m1, newdata=...)` — prédiction sur nouvelles données

### Modèles apparentés (même syntaxe)
- `glm()` — modèles linéaires généralisés (logistique, Poisson…)
- `gam()` — modèles additifs généralisés

## 2. Tests statistiques

### Convention
Tous les tests usuels en R suivent la convention `nomTest.test()`. La plupart sont dans le package `stats` (chargé par défaut).

### Tests usuels recensés
| Catégorie | Fonctions R |
|---|---|
| **Position** | `t.test()`, `pairwise.t.test()`, `prop.test()`, `wilcox.test()`, `kruskal.test()`, `mcnemar.test()` |
| **Variabilité** | `var.test()`, `bartlett.test()` |
| **Distribution** | `ks.test()` (Kolmogorov-Smirnov), `shapiro.test()` (normalité) |
| **Indépendance** | `chisq.test()` (χ²), `fisher.test()`, `cor.test()` (corrélation) |

➡️ **À cocher pour le projet** : la plupart des tests évoqués dans `bloc1/02_methodes/explication.md` sont **déjà disponibles directement en R** :
- Test de Student : `t.test()`
- Wilcoxon : `wilcox.test()`
- Shapiro-Wilk : `shapiro.test()`
- χ² : `chisq.test()`
- Corrélation : `cor.test()`

## 3. Classification (Clustering)

### 3.1 Objectif
- Observations {Xᵢ, 1 ≤ i ≤ n} dans (E, d)
- Constituer **K groupes homogènes** (K souvent inconnu)
- Hétérogénéité = somme des distances dans chaque groupe (deux à deux ou au centre)

### 3.2 Trois familles d'approches

#### A. **Classification ascendante hiérarchique (CAH)** — agglomérative

**Algorithme** :
1. Choix d'une distance (euclidienne, Manhattan, …)
2. Calcul de la matrice de dissimilarités
3. Tant que tous regroupés :
   - Fusionner les 2 individus/clusters les plus similaires
   - Recalculer les dissimilarités
4. Choix du nombre de classes (coupe du dendrogramme)

**R** :
- `stats::hclust()` — fonction de base
- `cluster::agnes()` — plus de possibilités
- Affichage : `plot()` du résultat → **dendrogramme**
- `cutree(hc, k=4)` → couper à K classes

#### B. **Classification divisive** (descendante)
- Inverse de la CAH : on part d'un seul groupe et on divise itérativement
- R : `cluster::diana()` — Divisive ANAlysis

#### C. **Classification centroïde — k-means**

**Algorithme** :
1. Choix d'une distance + nombre de classes K
2. Initialisation aléatoire des K centres
3. Tant que non stable :
   - Affecter chaque individu au centre le plus proche
   - Recalculer les centres (moyenne des individus du cluster)

**R** :
- `stats::kmeans()` — k-means standard
- `cluster::pam()` — **Partitioning Around Medoids** : centroïdes pris **dans les observations** (= médianes), avec **distance de Manhattan**. Plus **robuste aux outliers** que k-means.
- `cluster::clara()` — **CLustering LARge Applications** : version k-means pour gros datasets

### 3.3 Classification floue (Fuzzy)
- Chaque individu reçoit une **probabilité d'appartenance** à chaque groupe
- Les centres sont pondérés par ces probabilités
- Classification finale = groupe le plus probable
- R : `cluster::fanny()` — Fuzzy Analysis Clustering

### 3.4 Note importante : `scale()`
Avant clustering ⇒ **standardiser** avec `scale()` quand les variables ont des échelles différentes (sinon la variable à grande échelle domine la distance).

---

## 🎯 Applications au projet TradingMonitor

### Atout principal pour le rapport
> Toutes les méthodes statistiques utilisées dans le projet (test t, χ², ANOVA, ACP, régression, clustering) sont **directement disponibles dans R** en quelques lignes.

Si le rapport doit utiliser R (Master de stats à Strasbourg), ce cours est la **boîte à outils de référence** :
- `lm()` pour la régression du Bloc final (avec interactions via `x1*x2`)
- `t.test()`, `wilcox.test()`, `shapiro.test()` pour le Bloc 1 étape 1
- `chisq.test()` pour le Bloc 1 étape 3
- `cor.test()` pour le Bloc 3 (corrélations sectorielles)
- `hclust()` pour clusteriser les trades en profils
- `kmeans()` ou `pam()` pour clusteriser les régimes de marché

### Comparaison Python ↔ R pour le projet

| Méthode | Python (actuel projet) | R équivalent |
|---|---|---|
| Régression | `sklearn.LinearRegression`, `statsmodels.OLS` | `lm()` |
| Logistique | `sklearn.LogisticRegression` | `glm(..., family=binomial)` |
| Ridge/Lasso | `sklearn.RidgeCV`, `sklearn.LassoCV` | `glmnet::glmnet()` |
| ACP | `sklearn.PCA` | `FactoMineR::PCA()` ⭐ (vu en cours [[01-acp]]) |
| AFC | _custom numpy_ | `FactoMineR::CA()` (vu [[02-afc]]) |
| ACM | _custom numpy_ | `FactoMineR::MCA()` (vu [[03-acm]]) |
| CAH | `scipy.cluster.hierarchy.linkage` | `hclust()` ou `agnes()` |
| k-means | `sklearn.KMeans` | `kmeans()` ou `pam()` (robuste) |
| ARIMA | `statsmodels.tsa.arima` | `forecast::auto.arima()` (référence !) |

➡️ **PAM** (Partitioning Around Medoids) est **plus robuste** que k-means face aux outliers — en finance avec des journées de krachs, c'est très pertinent.

### Pour le rapport
- Tous les tests et modèles évoqués dans `bloc1/02_methodes/explication.md` ont une **implémentation R native one-liner**
- Cela **simplifie** énormément la communication méthodologique : `t.test(x, y)` est sans ambiguïté
- Mentionner les packages utilisés : `stats`, `cluster`, `FactoMineR`, `glmnet`, `forecast`

### Limites du cours pour le projet
- Cours **très bref** (1 slide par concept)
- Pas de détails sur les variantes (ex: types de liaisons pour CAH : Ward, single, complete, average)
- Pas de couverture sur :
  - `survival` (analyse de survie) — utile pour durée de holding d'un trade
  - `gam()` (modèles additifs) — utile pour relations non linéaires
  - Packages dplyr / ggplot2 (couvertures dans intro.pdf et autres)

---

## ✅ Méthodes acquises dans ce cours
- `lm()` + syntaxe formula R (incluant `*` et `:` pour interactions)
- `summary()`, `predict()`
- `glm()`, `gam()` (mentionnés)
- Convention `*.test()` pour les tests
- ≈ 15 tests statistiques nommés
- **CAH** via `hclust`, `agnes`
- **Classification divisive** via `diana`
- **k-means** via `kmeans`
- **PAM** (k-medoids robuste) via `pam`
- **CLARA** (k-means gros datasets) via `clara`
- **Fuzzy clustering** via `fanny`
- Importance de `scale()` avant clustering

## 🆕 À étudier (PAS dans ce cours)
- Méthodes de liaison CAH (Ward, single, complete, average) — important pour reproductibilité
- Méthodes pour **choisir K** (silhouette, gap statistic, elbow method)
- `survival` package (analyse de durée)
- `forecast::auto.arima()` pour automatisation du pipeline [[10-series-temporelles]]
- Packages **tidyverse** (dplyr, tidyr, ggplot2) — couverts dans les autres PDFs du dossier
