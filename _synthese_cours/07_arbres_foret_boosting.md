---
name: 07-arbres-foret-boosting
description: Synthèse cours "Arbres de décision" (Chevallier & Birmelé, 19 pages) — arbres CART (Gini, élagage), forêts aléatoires (bagging, OOB), importance des variables, Gradient Boosting
metadata:
  type: reference
---

# Arbres de décision, Forêts aléatoires, Gradient Boosting (Chevallier & Birmelé, 19 pages)

> Cours **central pour le projet** : couvre 3 méthodes différentes (arbre seul, forêt, boosting) + l'importance des variables qui peut compléter le Lasso pour le Bloc final.

## 1. Arbre de décision

### Principe
- Découpage récursif de l'espace par des seuils du type `x_j ≤ c`
- À chaque feuille terminale : une décision (classe majoritaire ou valeur moyenne)
- Lecture intuitive : suite de **if/else** dans un arbre

### Classification vs régression
| Type | y | Feuilles |
|---|---|---|
| Classification | qualitative | une classe |
| Régression | quantitative | une valeur |

### Code sklearn
```python
from sklearn.tree import DecisionTreeClassifier
decision_tree = DecisionTreeClassifier().fit(X, y)
tree.plot_tree(decision_tree, filled=True)
```

## 2. Algorithme CART

### Étapes
1. **Découpage** : chercher la variable X_j et le seuil c qui divisent en deux groupes les plus "purs"
2. **Division** : créer deux branches
3. **Récursivité** : répéter sur chaque branche jusqu'à la condition d'arrêt
4. **Affectation des feuilles** : classe majoritaire (classif) / moyenne (régression)

### 2.1 Pureté (classification) — Indice de Gini
$$ E(S) = \sum_{i=1}^L p_i(1-p_i) = 1 - \sum_{i=1}^L p_i^2 $$
- E(S) = 0 ⇔ tous dans la même classe (population pure)
- E(S) petit ⇔ population presque pure

### 2.2 Découpage classification
Minimiser :
$$ \text{card}(S_{t_g}) \cdot E(S_{t_g}) + \text{card}(S_{t_d}) \cdot E(S_{t_d}) $$
⇒ découpage qui maximise la pureté pondérée des deux sous-populations.

### 2.3 Découpage régression — variance intra-groupe
$$ \text{card}(S_{t_g}) \cdot V(S_{t_g}) + \text{card}(S_{t_d}) \cdot V(S_{t_d}) $$
⇒ maximise l'homogénéité des sous-groupes.

### 2.4 Conditions d'arrêt
- Nœud suffisamment **pur** (seuil sur Gini)
- Population **trop petite** (seuil sur card)

### 2.5 Élagage (Pruning)
Un arbre **trop profond** = sur-apprentissage. On minimise :
$$ R_\alpha(\text{arbre}) = R(\text{arbre}) + \alpha \cdot \frac{\text{Nb feuilles}}{n} $$
- R = taux de mauvaises classifications (ou MSE en régression)
- **α = paramètre de régularisation** (plus α grand → arbres plus simples privilégiés)

⇒ équilibre précision / complexité (cf [[05-apprentissage-introduction]] règle d'or).

## 3. Forêts aléatoires (Random Forest)

### Limitations des arbres seuls
- ❌ **Sensibilité au bruit** : petite variation des données → arbre très différent
- ❌ **Sur-apprentissage** : arbres profonds capturent le bruit

### Principe du bagging
1. **Rééchantillonnage bootstrap** : chaque arbre construit sur un échantillon **avec remise**
2. **Sélection aléatoire de variables** : à chaque nœud, k variables tirées parmi les p

### Décisions finales
- **Régression** : moyenne des prédictions de tous les arbres
- **Classification** : vote majoritaire

### Hyperparamètres clés
| Param | Conseil |
|---|---|
| `n_estimators` (nombre d'arbres) | Aussi grand que possible (100, 500, 1000) |
| `max_features` | √p en classif, p/3 en régression — à tuner |

### Variance du modèle
La variance mesure la **sensibilité aux variations des données d'entraînement**. RF réduit la variance grâce au moyennage.

### Code
```python
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
classifier = RandomForestClassifier(n_estimators=100)
regressor = RandomForestRegressor(n_estimators=100)
```

## 4. Erreur Out-Of-Bag (OOB) ⭐

> **Avantage majeur de RF** : pas besoin d'ensemble de validation séparé !

### Principe
- Chaque arbre est construit sur un sous-échantillon bootstrap
- Donc certaines observations n'ont **pas** servi à entraîner certains arbres
- Pour une observation, on utilise UNIQUEMENT les arbres qui ne l'ont pas vue
- L'erreur calculée = **Out-Of-Bag error** ≈ validation croisée intégrée

### Usage
```python
clf = RandomForestClassifier(oob_score=True, warm_start=True)
clf.fit(X, y)
oob_error = 1 - clf.oob_score_
```

⇒ permet de tuner `n_estimators` en traçant erreur OOB vs nombre d'arbres.

## 5. Importance des variables ⭐⭐

> **EXTRÊMEMENT utile pour le projet** : permet d'identifier quelles variables Xᵢ comptent réellement, en complément du Lasso.

### 5.1 Via réduction d'impureté (Gini)
- Chaque split d'arbre est basé sur une variable
- Importance = somme de la **réduction d'impureté** générée par cette variable lors des splits
- Pour RF : moyenne sur tous les arbres

```python
rf.feature_importances_  # tableau d'importances
```

### 5.2 Importance par permutation 🔑
Méthode **plus robuste** :
1. Calculer performance initiale du modèle
2. **Permuter** les valeurs d'une variable → détruit la relation X_i ↔ y
3. Recalculer la performance
4. Si forte chute → variable **importante**

**Avantages** :
- ✅ Indépendant du modèle (utilisable sur Lasso, SVM, etc.)
- ✅ Mesure directe de l'impact réel

**Limite** ⚠️ :
- ❌ Si X_i est **corrélée** à d'autres X_j, ces dernières compensent → **sous-estimation** de l'importance de X_i

```python
from sklearn.inspection import permutation_importance
result = permutation_importance(rf, X, y, n_repeats=10)
```

### Utilités
- **Interprétabilité** : modèle plus transparent
- **Compréhension** : identifier les variables clés
- **Réduction de dimension** : supprimer les variables peu importantes

## 6. Gradient Boosting (cours bonus)

### Principe général du Boosting
Construire **séquentiellement** un modèle fort F(x) comme combinaison linéaire de modèles faibles h_t(x) :
$$ F(x) = \sum_{t=1}^T \alpha_t h_t(x) $$
- Les modèles faibles = arbres peu profonds (stumps)
- Minimisation de L(y, F(x)) par **descente de gradient**

### Algorithme Gradient Boosting
1. Initialiser F_0(x) = arg min Σ L(y_i, γ)
2. Pour t = 1 à T :
   - Calculer les **résidus** (gradient négatif) : r_{i,t} = −[∂L/∂F](x_i)
   - Entraîner un arbre h_t(x) pour prédire r_{i,t}
   - Trouver le multiplicateur optimal γ_t
   - Mise à jour : F_t(x) = F_{t-1}(x) + γ_t · h_t(x)

### Exemple régression (MSE)
- L(y, F) = Σ (y_i − F(x_i))²
- Résidus = y_i − F_{t-1}(x_i)

### Régularisation
- **Shrinkage** : F_t = F_{t-1} + **ν** · γ_t · h_t (ν = learning rate)
- **Subsampling** : chaque arbre sur sous-échantillon aléatoire
- **Early stopping** : arrêter si perte validation n'améliore plus

### Avantages
- ✅ Modélise relations non linéaires **complexes**
- ✅ Minimise directement la perte
- ✅ Robuste aux outliers
- ✅ Chaque arbre corrige les erreurs du précédent

### Limites
- ❌ Sensible aux hyperparamètres (T, ν, profondeur)
- ❌ **Entrainement séquentiel** (non parallèle, lent)
- ❌ Sur-apprentissage si T trop grand ou ν trop élevé

---

## 🎯 Applications au projet TradingMonitor

### Random Forest pour le Bloc final — alternative naturelle au Lasso ⭐
**Tableau de comparaison** :

| Critère | Lasso ([[04-apprentissage-lineaire-penalise]]) | Random Forest |
|---|---|---|
| Interprétabilité | ✅ coefficients explicites | 🔄 importance des variables |
| Non-linéarités | ❌ (sauf interactions explicites) | ✅ naturelles |
| Sélection variables | ✅ coefs à 0 | 🔄 importance |
| Sur-apprentissage | ✅ contrôlé par λ | ✅ contrôlé par bagging |
| Données corrélées | ⚠️ instable | ✅ robuste |
| Validation | CV nécessaire | **OOB intégrée** |

➡️ Pour le rapport : **RF est l'alternative non-linéaire incontournable du Lasso**.

### Importance des variables comme **complément du Lasso** 🔑
- Lasso → quelles variables sont **gardées dans la régression** ?
- RF importance → quelles variables ont **l'impact prédictif réel** ?
- **Comparer les deux** = très solide méthodologiquement pour le rapport
- ⚠️ Si Lasso garde X mais RF dit que X est peu importante → la variable est peut-être **redondante** avec une autre (problème de colinéarité)

### Gradient Boosting (XGBoost / LightGBM)
- Standard de l'industrie en finance prédictive
- Plus performant que RF en général mais plus dur à régler
- **Hors cours mais à mentionner** dans le rapport

### Arbres simples = règles trading interprétables
Un arbre seul donne des règles du type :
- Si RSI < 30 ET volatilité > 2% → BUY
- Sinon si MA(20) > MA(50) → HOLD
- Sinon → SELL

⇒ Très intéressant pour **expliquer une stratégie** à un humain, même si l'arbre seul est moins performant qu'une forêt.

### OOB pour le backtesting ⚠️
Attention : OOB suppose que les observations sont **indépendantes**. En séries temporelles, ce n'est **pas le cas** (autocorrélation des prix). Donc :
- ❌ OOB classique n'est pas une vraie validation pour des données temporelles
- ✅ Utiliser **TimeSeriesSplit** sklearn à la place (cf [[05-apprentissage-introduction]])

---

## ✅ Méthodes acquises dans ce cours
- Arbre de décision (CART)
- Indice de Gini, découpage classification
- Découpage régression (variance intra)
- Élagage avec α
- Random Forest (bagging + sous-échantillonnage variables)
- OOB error
- Importance via réduction Gini
- Importance par permutation
- Gradient Boosting (algorithme général)
- Shrinkage, subsampling, early stopping

## 🆕 À étudier (PAS dans ce cours)
- **XGBoost / LightGBM / CatBoost** — implémentations optimisées du GB
- **SHAP values** (alternative moderne à la feature importance, plus précise)
- **TimeSeriesSplit** pour validation temporelle
- **Conformal prediction** (intervalle de confiance autour des prédictions RF)
