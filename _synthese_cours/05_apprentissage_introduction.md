---
name: 05-apprentissage-introduction
description: Synthèse cours "Apprentissage - Introduction" (Chevallier & Birmelé, 35 pages) — concepts fondamentaux du machine learning supervisé / non supervisé, sur-apprentissage, validation croisée, métriques de classification binaire et courbe ROC
metadata:
  type: reference
---

# Apprentissage – Introduction (Chevallier & Birmelé, 35 pages)

> Cours **Apprentissage statistique** M1 Strasbourg — fondations.

## 1. Apprentissage vs Statistiques

| Statistiques | Apprentissage (ML) |
|---|---|
| Estimation et interprétation des paramètres | Qualité des prédictions |
| Quantification incertitude (IC, bayesien) | Quantification incertitude plus délicate |

➡️ **La frontière est floue.** Mais la régression pénalisée Lasso/Ridge ([[04-apprentissage-lineaire-penalise]]) est typiquement un cas hybride : modèle interprétable + objectif prédictif.

## 2. Trois grandes classes de méthodes

1. **Apprentissage supervisé** — données annotées (X, Y), on cherche f : X → Y
   - Y quantitatif → **régression**
   - Y qualitatif → **classification**
2. **Apprentissage non supervisé** — données non annotées X seul, on cherche la structure
   - Clustering, réduction de dimension (ex. ACP → [[01-acp]])
3. **Apprentissage par renforcement** — pas de données, agent + feedback (AlphaGo) — **non abordé**

## 3. Fonction de perte et risque empirique

- Vecteur (X, Y), ensemble de fonctions de prédiction **𝓕**
- **Fonction de perte L** : distance entre prédiction et vérité
- **Risque empirique** :
$$ R_{emp}(f) = \sum_i L(f(X_i), Y_i) $$
- **Règle apprise** :
$$ g = \arg\min_{f \in \mathcal{F}} \sum_i L(f(X_i), Y_i) $$

### Exemple modèle linéaire
- 𝓕 = fonctions linéaires/affines
- L(y₁, y₂) = ‖y₁ − y₂‖² (perte quadratique)
- Argmin calculable **exactement** (= MCO, lien avec [[04-apprentissage-lineaire-penalise]])

### sklearn — fonction `m.score`
- Régression : R²
- Classification : % prédictions correctes
- ⚠️ `m.score` ≠ fonction de perte L

## 4. Sur-apprentissage et généralisation 🔑

> **Concept central pour le projet trading.**

- **Généralisation** : capacité à prédire sur de **nouvelles données**
- **Sur-apprentissage** : augmenter les paramètres fait toujours baisser R_emp, mais dégrade la généralisation
- Illustration 3 cas :
  - **Under-fit** : modèle trop simple
  - **Good fit** : modèle équilibré
  - **Over-fit** : modèle qui capture le bruit

### 🚨 Règle d'or (capitalisée dans le cours)
> **NE JAMAIS ÉVALUER LA QUALITÉ D'UNE RÈGLE SUR LES DONNÉES QUI ONT SERVI À APPRENDRE LA RÈGLE EN QUESTION**

## 5. Découpage des données

### Ensemble de test
- N'est PAS utilisé lors du `fit`
- Sert à évaluer le **risque empirique sur données nouvelles**
- = mesure honnête de la généralisation

### Ensemble de validation
- Les modèles ont des **hyperparamètres** (nombre de variables, profondeur d'arbre, λ Ridge/Lasso...)
- Le choix de l'hyperparamètre fait partie de l'apprentissage → **NE PEUT PAS** être fait sur le jeu test
- → on resépare l'apprentissage en (apprentissage + validation)
- **Validation** : choisir l'hyperparamètre
- **Test** : évaluer le modèle final retenu
- ⚠️ **On ne compare PAS les valeurs d'hyperparamètres sur les données de test !**

### Répartition classique
- 60% apprentissage / 20% validation / 20% test
- ⚠️ « on perd beaucoup de données » → on recourt à la **validation croisée**

## 6. Validation croisée (CV) ⭐

### Processus k-fold
1. Diviser apprentissage en **k folds** (typiquement k=5 ou k=10)
2. Utiliser k-1 folds pour entraîner
3. Utiliser le fold restant pour valider
4. Répéter k fois en changeant le fold de validation

### Avantages
- Généralisation testée **une fois sur chaque point**
- Plus besoin d'ensemble de validation séparé

### Variantes
- **k-fold** : k=5 ou k=10 standard
- **LOOCV** (Leave-One-Out) : k=n, coûteux
- **Stratified k-fold** : préserve la distribution des classes dans chaque fold (important si déséquilibre)

### Code sklearn
```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_train, y_train, cv=5)
print("Score moyen:", scores.mean())
```

## 7. Classification binaire — matrice de confusion

|   | Prédit Positif | Prédit Négatif |
|---|---|---|
| **Réel Positif** | TP (Vrai Positif) | FN (Faux Négatif) |
| **Réel Négatif** | FP (Faux Positif) | TN (Vrai Négatif) |

- **FP = erreur de type I** (faux positif)
- **FN = erreur de type II** (faux négatif)

## 8. Métriques de classification binaire

| Métrique | Formule | Mesure |
|---|---|---|
| **Accuracy** | (TP+TN) / total | proportion de prédictions correctes |
| **Precision** | TP / (TP+FP) | parmi prédits positifs, % réellement positifs |
| **Recall** (sensibilité) | TP / (TP+FN) | parmi vrais positifs, % détectés |
| **Specificity** | TN / (TN+FP) | parmi vrais négatifs, % détectés |
| **F1-score** | 2 × (Pr × Re) / (Pr + Re) | moyenne harmonique précision/rappel |

➡️ **F1-score** très utile en cas de **déséquilibre de classes** (cas trading : peu de signaux positifs vs beaucoup de HOLD).

### ROC AUC
- Aire sous la courbe ROC
- AUC proche de 1 = meilleur modèle
- AUC = 0.5 = modèle aléatoire

## 9. Courbe ROC — choix du seuil

### Modèles probabilistes
- Régression logistique, réseaux neurones → sortie = **probabilité**
- **Seuil** convertit probabilité en classe : « prédit 1 si proba > seuil »

### Effet du seuil
- **Seuil par défaut = 0.5**
- **Seuil bas** (0.3) : Plus de TP, mais plus de FP
- **Seuil haut** (0.8) : Moins de FP, mais moins de TP

### Courbe ROC
- Trace **TPR vs FPR** pour différents seuils
$$ TPR = \frac{TP}{TP+FN} \quad ; \quad FPR = \frac{FP}{FP+TN} $$
- **Point bas-gauche** : seuil élevé, presque tout classé négatif
- **Point haut-droite** : seuil bas, presque tout classé positif
- Courbe se rapprochant du coin haut-gauche = meilleur modèle

### Comparaison de modèles
- Si une courbe ROC domine l'autre partout → modèle dominé
- Sinon arbitrage selon le coût des erreurs (FP vs FN)

---

## 🎯 Applications au projet TradingMonitor

### Sur-apprentissage en backtesting — risque MAJEUR
> Le sur-apprentissage est **LE** risque numéro 1 en trading quantitatif.

Si une stratégie est optimisée sur 2020-2023 et évaluée sur 2020-2023, elle paraîtra parfaite mais **ne généralisera pas** sur 2024+.

➡️ **Règle d'or à appliquer absolument** : tout backtest doit comporter un **walk-forward** (entrainement glissant, validation sur données futures non vues).

### Découpage temporel (PAS k-fold standard !) ⚠️
- En séries temporelles, on **NE peut PAS** mélanger les dates (info du futur fuiterait dans le train)
- Utiliser **TimeSeriesSplit** sklearn : train < validation < test dans le temps
- Exemple Bloc 1 : train 2020-2022 / validation 2023 / test 2024-2025

### Bloc final (régression Lasso) → cross-validation **temporelle**
- `LassoCV(cv=TimeSeriesSplit(n_splits=5))` au lieu de `LassoCV(cv=5)`
- L'hyperparamètre λ est choisi sur la validation, le R² final mesuré sur test

### Métriques pour classification BUY/SELL/HOLD
Si l'agent doit prédire 3 classes (achat / vente / rien) :
- **Precision** : si on dit BUY, à quel point a-t-on raison ? (= éviter les faux signaux qui font perdre de l'argent en frais)
- **Recall** : combien de vrais signaux BUY a-t-on détectés ? (= ne pas rater d'opportunités)
- **F1-score** : équilibre des deux
- ⚠️ Le **trading n'aime pas les faux positifs** (chaque trade = coût) → maximiser la **précision** plutôt que le rappel

### Lien avec les autres méthodes
- ACP ([[01-acp]]) = exemple d'apprentissage **non supervisé** (pas de Y, on cherche la structure de X)
- AFC ([[02-afc]]) = idem, non supervisé sur tableau de contingence
- Ridge/Lasso ([[04-apprentissage-lineaire-penalise]]) = supervisé avec validation croisée pour choisir λ

---

## ✅ Méthodes acquises dans ce cours
- Sur-apprentissage et règle d'or
- Train / validation / test
- Validation croisée k-fold, stratified, LOOCV
- Matrice de confusion
- Accuracy / Precision / Recall / Specificity / F1
- Courbe ROC, AUC, seuil

## 🆕 À étudier (PAS dans ce cours)
- **TimeSeriesSplit** (validation croisée temporelle) — sklearn
- **Walk-forward analysis** (méthodologie standard en backtesting)
- **Métriques trading spécifiques** : Sharpe, Sortino, max drawdown, profit factor, win rate (pas couvert ici, voir si dans Séries temporelles)
