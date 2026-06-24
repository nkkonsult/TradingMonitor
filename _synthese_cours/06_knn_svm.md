---
name: 06-knn-svm
description: Synthèse cours "Méthodes kNN et SVM" (13 pages) — k plus proches voisins (classification/régression) et Support Vector Machine (séparateur à marge maximale, vecteurs support, kernel trick)
metadata:
  type: reference
---

# Méthodes kNN et SVM (M1 Strasbourg, 13 pages)

## 1. k-Nearest Neighbors (kNN)

### Principe
Pour un point à classer, sélectionner les **k points les plus proches** dans le jeu d'apprentissage et :
- **Classification** : vote majoritaire
- **Régression** : moyenne des Y

### Variantes
- **Autre distance** que l'euclidienne (Mahalanobis, Manhattan, distance pondérée…)
- **Poids** sur les votes, décroissants avec la distance

### Avantages
- ✅ Simplicité du concept et de la mise en œuvre
- ✅ Peu de paramètres (k + choix de la distance)

### Inconvénients
- ❌ Nécessite de **garder toutes les données en mémoire** pour prédire
- ❌ **Fléau de la dimension** : quand p devient grand, la distance perd son sens (tous les points deviennent équidistants)

### Code
```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()  # OBLIGATOIRE avant kNN
X_scaled = scaler.fit_transform(X)

knn = KNeighborsClassifier(n_neighbors=9)
knn.fit(X_scaled, Y)
```

⚠️ **Standardisation obligatoire** : sinon les variables à grande échelle dominent la distance.

---

## 2. Support Vector Machine (SVM)

### Cadre
- Classification binaire avec yᵢ ∈ {−1, +1}
- On cherche une **surface de séparation** f : 𝒳 → ℝ
- Décision : y = +1 ⇔ f(x) > 0

### 2.1 Séparateurs linéaires
$$ f(x) = \sum_{j=1}^{d} w_j x_j + b = \langle w, x \rangle + b $$

L'hyperplan séparateur est défini par ⟨w, x⟩ + b = 0.

### 2.2 Données linéairement séparables
- Il existe une **infinité** d'hyperplans séparateurs possibles
- **Critère de choix : la marge**
$$ Marge(f) = \min_i d(x_i, H) $$
- Le meilleur hyperplan est celui dont la marge est **la plus grande**
- = celui qui passe au **milieu** entre les deux nuages

### 2.3 Vecteurs supports 🔑
> Les points les plus proches de H* (à distance = marge) sont appelés **vecteurs supports**.

3 propriétés clés :
1. **Seuls les vecteurs supports définissent f\*** : ajouter des points hors de la bande ne change rien
2. On peut imposer |⟨w, xₛ⟩ + b| = 1 → marge = **1/‖w‖**
3. ⇒ Maximiser la marge = **minimiser ‖w‖**

### 2.4 Problème d'optimisation (primal)
$$ \text{Trouver } w^* = \arg\min \tfrac{1}{2}\|w\|^2 \quad \text{sous} \quad y_i(\langle w, x_i\rangle + b) \geq 1 $$

### 2.5 Forme duale (avec multiplicateurs de Lagrange αᵢ)
$$ \text{Trouver } \alpha^* = \arg\max_\alpha \left( \sum_i \alpha_i - \tfrac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j \langle x_i, x_j\rangle \right) $$
sous αᵢ ≥ 0 et Σ αᵢyᵢ = 0.

**Propriétés** :
- αᵢ ≠ 0 ⇔ xᵢ est un vecteur support
- w* = Σᵢ αᵢ* yᵢ xᵢ
- Nouvelle donnée x : classée selon signe de ⟨w*, x⟩ + b*

### 2.6 Données NON linéairement séparables — soft margin
Introduction d'une **pénalité** ξᵢ par point :
$$ \xi_i = \max(0, 1 - y_i(\langle w, x_i\rangle + b)) $$
- ξᵢ = 0 pour points bien classés au-delà de la marge
- ξᵢ > 0 pour points dans la bande centrale ou mal classés

Problème :
$$ \min \|w\|^2 + C\sum_i \xi_i \quad \text{tel que} \quad y_i(\langle w, x_i\rangle+b) \geq 1 - \xi_i $$

➡️ **C = paramètre de régularisation**
- C **petit** → tolère plus d'erreurs (marge large, moins de sur-apprentissage)
- C **grand** → impose la séparation (marge serrée, risque de sur-apprentissage)

### 2.7 SVM non linéaire — Kernel Trick ⭐

**Théorème de Mercer** : si K : 𝒳×𝒳 → ℝ symétrique et définie positive, alors ∃ ℋ (Hilbert) et φ : 𝒳 → ℋ tels que :
$$ K(x, y) = \langle \phi(x), \phi(y) \rangle $$

K est appelé **noyau défini positif**.

**Intérêt** : SVM dual n'utilise que des **produits scalaires** ⟨xᵢ, xⱼ⟩. En les remplaçant par K(xᵢ, xⱼ), on travaille implicitement dans ℋ (espace de plus grande dimension) **sans jamais calculer φ**.

#### Noyaux usuels
| Noyau | Formule | Usage |
|---|---|---|
| Linéaire | K(x, x') = ⟨x, x'⟩ | SVM linéaire classique |
| Exponentiel | K(x, x') = exp(−γ‖x − x'‖) | Non linéaire |
| **Gaussien (RBF)** | K(x, x') = exp(−γ‖x − x'‖²) | **Le plus utilisé**, frontières très flexibles |

**Interprétation** : K(x, x') est une **mesure de similarité** — plus x et x' se ressemblent, plus K est grand.

### 2.8 Optimisation avec noyau
$$ \alpha^* = \arg\max_\alpha \left( \sum_i \alpha_i - \tfrac{1}{2}\sum_{i,j} \alpha_i\alpha_j y_i y_j K(x_i, x_j) \right) $$
sous C ≥ αᵢ ≥ 0 et Σ αᵢyᵢ = 0.

Classification d'une nouvelle donnée :
$$ f(x) = \sum_i \alpha_i^* y_i K(x_i, x) + b^* $$

---

## 🎯 Applications au projet TradingMonitor

### Quand utiliser kNN ?
- **Non recommandé** en trading direct : fléau de la dimension dès qu'on a > 10 variables Xᵢ
- **Utile pour** : trouver des **régimes de marché similaires** par jour (lookup historique)
  - Ex: "le pattern des 5 derniers jours ressemble le plus à quels jours historiques ?"
  - Puis voir ce qui s'est passé après (mean reversion ?)

### Quand utiliser SVM ?
- **Classification BUY vs HOLD** sur signaux Bloc 1 + Bloc 2 + Bloc 3
- Avec noyau **RBF** : capture les **non-linéarités** que la régression Lasso ne voit pas
- ⚠️ Pas adapté à de très gros datasets (38 035 trades = limite haute)
- Hyperparamètre **C** à tuner par cross-validation (cf [[05-apprentissage-introduction]])

### Vecteurs supports = trades-clés
Concept intéressant : seuls quelques trades "frontière" déterminent la règle. ⇒ permet d'identifier les **trades critiques** dans l'historique (ceux qui ont le plus influencé la décision).

### Comparaison avec Lasso ([[04-apprentissage-lineaire-penalise]])
| Critère | Lasso | SVM noyau RBF |
|---|---|---|
| Interprétabilité | ✅ coefficients explicites | ❌ boîte noire |
| Non-linéarités | ❌ (sauf interactions explicites) | ✅ naturelles |
| Bloc final du projet | ✅ option B+ retenue | 🔄 alternative non-linéaire |

➡️ Pour le rapport : pourrait être présenté comme **comparaison méthodologique** (linéaire vs non linéaire).

---

## ✅ Méthodes acquises dans ce cours
- kNN classification/régression
- SVM linéaire (hard margin)
- SVM soft margin avec C
- Kernel trick (linéaire, exponentiel, gaussien RBF)
- Vecteurs supports
- Dualité Lagrange

## 🆕 À étudier (PAS dans ce cours)
- **Multi-classe SVM** (One-vs-One, One-vs-Rest) — utile pour BUY/SELL/HOLD à 3 classes
- **SVR** (Support Vector Regression) — version régression du SVM, pourrait remplacer le Lasso
- **Tuning de C et γ par grid search** — pratique standard avec sklearn
