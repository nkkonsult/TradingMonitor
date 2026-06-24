---
name: 09-importance-variables
description: Synthèse cours "Mesures d'importance de variable" (Birmelé, 6 pages) — permutation, indices de Sobol, valeurs de Shapley
metadata:
  type: reference
---

# Mesures d'importance de variable (Birmelé, 6 pages)

> ⭐ Cours **clé pour le Bloc final** : présente 3 méthodes mathématiquement rigoureuses pour mesurer l'importance des Xᵢ dans Y = Q(X₁, …, Xₙ), valables pour **TOUT modèle** Q (linéaire, RF, NN…).

## 1. Problématique

- Modèle générique : Y = Q(X₁, …, Xₙ)
- Q peut être : modèle linéaire, forêt aléatoire, réseau de neurones, n'importe quoi
- **Question** : quelle est l'importance de chacune des variables Xᵢ dans la prédiction de Y ?

## 2. Importance par permutation (rappel)

### Principe (déjà vu dans [[07-arbres-foret-boosting]])
- Permuter aléatoirement les valeurs de Xᵢ → on obtient X'ᵢ indépendante de Y par construction
- Réentraîner le modèle avec X'ᵢ → mesurer la **baisse de performance**
- **Importance = baisse de performance**

### Inconvénient ⚠️ — variables corrélées
> **POINT CRITIQUE** : si X₁ et X₂ sont **fortement corrélés** et tous deux importants pour Y :
> - Quand on permute X₁, **X₂ porte encore l'information** → baisse modérée
> - Idem dans l'autre sens
> - ⇒ On risque de déclarer **ni X₁ ni X₂ importantes** alors que leur couple est informatif

➡️ **Pertinent pour le projet** : les variables Bloc 3 (indices sectoriels) sont **très corrélés entre eux** (PC1 = 73%). La permutation va sous-estimer leur importance individuelle.

## 3. Indices de Sobol — Décomposition de la variance

### 3.1 Idée
> Xᵢ est d'autant plus importante que **fixer sa valeur réduit les variations de Y**.

### 3.2 Décomposition de la variance
$$ \text{Var}(Y) = \mathbb{E}[\text{Var}(Y|X_i)] + \text{Var}(\mathbb{E}[Y|X_i]) $$

### 3.3 Indice de Sobol d'ordre 1
$$ S_i = \frac{\text{Var}(\mathbb{E}[Y|X_i])}{\text{Var}(Y)} = 1 - \frac{\mathbb{E}[\text{Var}(Y|X_i)]}{\text{Var}(Y)} $$

Propriétés :
- ✅ Indice **normalisé** entre 0 et 1
- ✅ Insensible au changement d'échelle
- = part de variance de Y expliquée par Xᵢ seule

### 3.4 Décomposition de Hoeffding (variables indépendantes)
Si Xᵢ indépendants et Q de carré intégrable :
$$ Q(\mathbf{X}) = Q_0 + \sum_i Q_i(X_i) + \sum_{i<j} Q_{i,j}(X_i, X_j) + \ldots + Q_{1,\ldots,p}(X_1, \ldots, X_p) $$

avec contraintes :
- Q₀ constante
- 𝔼[Q_I(X_I) | X_J] = 0 pour tout J ⊊ I

Cette décomposition implique :
$$ \text{Var}(Y) = \sum_{I \subset \{1, \ldots, p\}} \text{Var}(Q_I(X_I)) $$

### 3.5 Indice de Sobol d'ordre supérieur
Pour tout ensemble I ⊂ {1, …, p} :
$$ S_I = \frac{\text{Var}(Q_I(X_I))}{\text{Var}(Y)} $$

Propriété : indices **normalisés** ⇒ Σ_I S_I = 1.

### 3.6 Indice de Sobol TOTAL d'une variable
$$ S_i^{\text{tot}} = \sum_{I \subset \{1, \ldots, p\}, i \in I} S_I $$

⇒ prend en compte l'influence de Xᵢ **seule** + via toutes ses **interactions**.

| Indice | Interprétation |
|---|---|
| Sᵢ (ordre 1) | importance individuelle pure de Xᵢ |
| Sᵢ^tot | importance totale (seule + interactions) |
| Sᵢ^tot − Sᵢ | part dûe aux interactions |

### 3.7 Calcul des indices
- **Théorique** : possible dans certains cas (modèle linéaire)
- **Pratique** : estimation par **Monte-Carlo** sur copies indépendantes des entrées :
$$ S_i = \frac{\text{Cov}(Y, Y^i)}{\text{Var}(Y)} \quad ; \quad S_i^{\text{tot}} = \frac{\mathbb{E}[(Y - Y^{-i})^2]}{2\text{Var}(Y)} $$

### 3.8 Limitation — Métamodèles
- Sobol nécessite des **lois d'entrée** pour simuler des X indépendants
- Solution : **métamodèle** = modélisation de Y en fonction de X via :
  - modèle linéaire
  - processus gaussien
  - **polynômes du chaos**
- Dans le cas linéaire ou polynômes du chaos → coefficients de Sobol calculables **directement**

### ⚠️ Hypothèse forte
Décomposition de Hoeffding valable **uniquement pour entrées indépendantes**. ⇒ problème en finance où **toutes les variables sont corrélées**.

## 4. Valeurs de Shapley — Théorie des jeux

> **Solution au problème des variables corrélées** : les indices de Shapley n'exigent **pas l'indépendance** des entrées.

### 4.1 Idée
Inspirée de la théorie des jeux coopératifs (Shapley 1953) : comment répartir équitablement un gain entre les joueurs d'une coalition ?

➡️ Ici : les "joueurs" sont les variables Xᵢ, le "gain" est l'amélioration de la prédiction.

### 4.2 Définition formelle
Pour tout ensemble I ⊂ {1, …, p}, on définit le **gain de I** :
$$ c(I) = \frac{\text{Var}(\mathbb{E}[Y|X_I])}{\text{Var}(Y)} $$

La **valeur de Shapley** de la variable j est la **moyenne du gain supplémentaire** apporté par j lorsqu'elle intègre un ensemble I :
$$ \eta_j = \frac{1}{p} \sum_{I, j \notin I} \binom{p-1}{|I|}^{-1} (c(I \cup j) - c(I)) $$

### 4.3 Cas d'entrées indépendantes
$$ \eta_j = \sum_{j \in I} \frac{S_I}{|I|} $$

Propriété :
$$ S_j \leq \eta_j \leq S_j^{\text{tot}} $$

⇒ Shapley est entre Sobol partiel et Sobol total. **Limite** : ne permet pas de différencier la part dûe à Xⱼ seule de la part des interactions.

### 4.4 Cas d'entrées CORRÉLÉES ⭐
> **AVANTAGE MAJEUR** : « le grand avantage des indices de Shapley par rapport à ceux de Sobol est qu'ils sont définis SANS HYPOTHÈSE D'INDÉPENDANCE entre entrées. »

⚠️ Limite : variables **très fortement corrélées** seront **indiscernables** par Shapley (chacune se voit attribuer la même part).

### 4.5 Calcul
- Calcul exact = **2^p calculs** → infaisable au-delà de p = 20 variables
- Forme alternative :
$$ \eta_j = \frac{1}{p!} \sum_{\sigma} (c([\sigma]_j \cup j) - c([\sigma]_j)) $$
où [σ]_j = indices précédant j dans la permutation σ.
- **Approximation par Monte-Carlo** sur échantillon de permutations

---

## 🎯 Applications au projet TradingMonitor

### Tableau récapitulatif des 3 méthodes

| Critère | Permutation | Sobol | Shapley |
|---|---|---|---|
| Indépendant du modèle | ✅ | ✅ (via métamodèle) | ✅ (via métamodèle) |
| Variables corrélées | ❌ sous-estime | ❌ exige indépendance | ✅ pas d'hypothèse |
| Sépare effet seul / interactions | ❌ | ✅ (Sᵢ vs Sᵢᵗᵒᵗ) | ❌ (mélange) |
| Coût calcul | Faible | Moyen (MC) | **2^p ou MC** |
| Maturité dans le rapport | classique RF | référence théorique | état de l'art |

### Pour le Bloc final — méthodologie idéale

Les variables du projet sont **massivement corrélées** :
- Bloc 1 : stratégies techniques sur mêmes actions (forte corrélation entre signaux MA20, MA50, RSI…)
- Bloc 3 : indices sectoriels (PC1 = 73% du marché → tout corrélé)
- Bloc 2 : signaux d'achat insiders se chevauchent

➡️ La **permutation va sous-estimer** systématiquement → mauvais choix
➡️ **Sobol nécessite l'indépendance** → pas applicable directement
➡️ **Shapley est LE choix méthodologique** correct, même si plus coûteux

### Combinaison gagnante pour le rapport ⭐

| Méthode | Sortie | Rôle |
|---|---|---|
| **Lasso CV** ([[04-apprentissage-lineaire-penalise]]) | coefficients (β = 0 ou non) | sélection de variables (sparse) |
| **Random Forest** ([[07-arbres-foret-boosting]]) | feature_importance_ Gini | check rapide non-linéaire |
| **Permutation importance** | baisse de performance | check robustesse |
| **Shapley values** (via SHAP library) | contribution par observation | ✅ **importance définitive** pour les variables corrélées |

➡️ **Pattern de rapport** : « Le Lasso a sélectionné les variables X₂, X₅, X₇. Une analyse par valeurs de Shapley confirme que X₂ et X₅ sont les contributeurs principaux à Y (η = 0.34 et 0.28), tandis que X₇ est masquée par sa corrélation avec X₂. »

### Note pratique : la librairie **SHAP** (hors cours)
- `shap.TreeExplainer` pour Random Forest / XGBoost → calcul exact en O(arbres × profondeur)
- `shap.LinearExplainer` pour Lasso / régression
- `shap.KernelExplainer` (générique, lent, par Monte-Carlo)
- ⚠️ Pas dans le cours, mais c'est l'implémentation standard de l'industrie

---

## ✅ Méthodes acquises dans ce cours
- Importance par permutation (et ses limites en cas de corrélation)
- Indices de Sobol d'ordre 1
- Indices de Sobol total et par sous-ensemble
- Décomposition de Hoeffding
- Estimation par Monte-Carlo
- **Valeurs de Shapley** (théorie des jeux appliquée aux variables)
- Métamodèles (polynômes du chaos, processus gaussien)

## 🆕 À étudier (PAS dans ce cours)
- **Librairie SHAP** Python (Lundberg & Lee 2017) — implémentation efficace des Shapley values
- **Polynômes du chaos** en détail
- **Processus gaussien** comme métamodèle
- **PFI** (Permutation Feature Importance) avec n_repeats pour stabilité
- **Conditional permutation importance** (variante qui gère mieux les corrélations)
