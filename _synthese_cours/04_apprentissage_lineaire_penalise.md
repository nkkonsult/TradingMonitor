# Synthèse — Cours Modèles linéaires pénalisés (Apprentissage statistique, Strasbourg M1)

> Cours complet de 23 pages lu et résumé. **Cours critique pour ton Bloc final** (Décision n°2 = option B+ avec Lasso).

---

## 1. Cadrage : pourquoi pénaliser ?

### Régression des moindres carrés classique
**Problème** : trouver `β` qui minimise
```
β^R = argmin ‖Y − Xβ‖²₂
```
Équivalent à l'EMV pour un modèle linéaire gaussien.

### Écueils des moindres carrés
1. **Variables explicatives corrélées** :
   - Interprétation difficile des coefficients
   - Une variable peut "attirer" l'influence d'une autre fortement corrélée
   - **Double effet** : variables "cachées" + **instabilité** des coefficients
2. **Absence de sélection** : tous les coefficients de β sont non-nuls → risque de **sur-apprentissage**
3. EMV `β̂ = (X'X)⁻¹ X'Y` **non défini** si plus de variables que d'observations (`p > n`)
4. La **sélection des variables** peut être le but de l'étude

### Exemple du cours
Jeu **House-prices** (Kaggle) : Y = prix immobilier, X = 80 variables descriptives du bien.

---

## 2. Régression Ridge (L2)

### Principe
Force le vecteur `β` à être **borné en norme L2** : une variable ne peut "attirer" les coefficients des variables corrélées que dans une **certaine mesure**.

### Écriture sous contrainte (pour c > 0 fixé)
```
β^Ridge = argmin ‖Y − Xβ‖²₂   sous contrainte ‖β‖²₂ ≤ c
```

### Écriture lagrangienne (équivalente, pour λ > 0)
```
β^Ridge(λ) = argmin (‖Y − Xβ‖²₂ + λ‖β‖²₂)
```
- `λ → 0` : on retrouve la régression classique
- `λ → +∞` : la solution est `β = 0`
- En faisant varier `λ` : famille de modèles de plus en plus pénalisés

### Solution analytique (forme close !)
```
β^Ridge = (X'X + λI_p)⁻¹ X'Y
```

### Remarques importantes
1. La pénalité rend le problème **strictement convexe** → résoluble par descente de gradient quelle que soit la dimension
2. **Biaisé** (en petite dimension) mais **moindre variance** que MCO
3. **En cas de variables corrélées** : la **répartition entre variables est meilleure**. MCO risque de mettre tout le poids sur une variable, Ridge répartit.

### Choix de λ
- **Outils de visualisation** (chemin de régularisation)
- **Validation croisée** (choix automatique) — voir `sklearn.RidgeCV`

### Inconvénient
- **Pas de sélection** : tous les coefficients restent non-nuls (juste rapetissés)
- Difficulté d'interprétation en grande dimension

---

## 3. Régression Lasso (L1)

### Principe
Favorise les solutions ayant un **grand nombre de coordonnées nulles** → **régression parcimonieuse**. Utile pour la **sélection de variables**.

Considère la **norme L1** plutôt que L2 → met de nombreux coefficients **exactement à 0**.

### Écriture sous contrainte
```
β^Lasso = argmin ‖Y − Xβ‖²₂   sous contrainte ‖β‖₁ ≤ c
```

### Écriture lagrangienne
```
β^Lasso(λ) = argmin (‖Y − Xβ‖²₂ + λ‖β‖₁)
```

### Pas de forme close !
Contrairement à Ridge, **plus de formule analytique**. Mais la fonction `f(β) = ‖Y − Xβ‖²₂ + λ‖β‖₁` est **convexe** → minimum unique trouvable algorithmiquement (descente de coordonnées).

### Illustration géométrique (clé pour comprendre)
- **Boule L2** (Ridge) : **cercle** dans le plan (β₁, β₂)
- **Boule L1** (Lasso) : **losange** (avec sommets sur les axes)
- L'estimateur est le point de tangence entre la boule de contrainte et les ellipses de vraisemblance
- Avec L1 (losange), la tangence se produit souvent **sur un sommet** → un coefficient devient exactement 0
- Avec L2 (cercle), la tangence est sur le bord → tous les coefs sont non-nuls

### Choix de λ — 2 approches

**1. Validation croisée** (la plus simple)
```python
from sklearn.linear_model import LassoCV
alphas = [1, 10, 100, 1000, 10000]
lasso_cv = LassoCV(alphas=alphas, cv=5)
lasso_cv.fit(X_train_processed, y_train)
print("Meilleur alpha :", lasso_cv.alpha_)
```

**2. Stability selection** ⭐ (très intéressant pour ton projet)
> On effectue un grand nombre d'apprentissages sur des sous-échantillonnages (80% des données) ou des bootstraps. On garde les variables apparaissant dans **plus de la moitié (ou du tiers)** des échantillons. On peut ensuite réaliser un apprentissage non pénalisé sur les variables sélectionnées.

### Attention au Lasso
> En cas de variables **corrélées**, une variable va être **privilégiée arbitrairement** par rapport aux autres (contrairement à Ridge qui répartit).

**Exemple concret** : sur House-prices, Lasso a mis à 0 beaucoup de variables (BsmtUnfSF, 1stFlrSF, EnclosedPorch, MSZoning_FV, MSZoning_RH, etc.) alors que Ridge gardait tout.

---

## 4. Comparaison Ridge vs Lasso

| Critère | Ridge (L2) | Lasso (L1) |
|---|---|---|
| Pénalité | `‖β‖²₂` | `‖β‖₁` |
| Solution analytique | ✅ `(X'X + λI)⁻¹ X'Y` | ❌ algorithmique |
| Coefficients nuls | Non, juste rapetissés | **Oui** (sélection) |
| Variables corrélées | Bien réparti | Une variable privilégiée arbitrairement |
| Interprétabilité | Difficile (tout non-nul) | Bonne (modèle parcimonieux) |
| Géométrie | Boule L2 (cercle) | Boule L1 (losange) |
| Cas n < p | OK (pénalisation = régularisation) | OK + sélection |

---

## 5. Elastic-Net : le meilleur des deux mondes

### Principe
Mélange une pénalité Ridge et une pénalité Lasso pour profiter des avantages des deux.

### Formulation
```
β^E-Net = argmin (‖Y − Xβ‖²₂ + λ(α‖β‖₁ + (1−α)‖β‖²₂))
```
- `α = 1` → Lasso pur
- `α = 0` → Ridge pur
- `α ∈ (0, 1)` → mélange

### Pourquoi c'est intéressant pour ton projet
- **Sélection de variables** comme Lasso
- **Gestion des variables corrélées** comme Ridge (pas de choix arbitraire)
- Particulièrement utile quand tu as **beaucoup de variables corrélées** (cas typique en finance : RSI(14) et RSI(21) corrélés, MM20 et MM50 corrélées, etc.)

### Inconvénient
- **2 hyperparamètres** à régler (`α` et `λ`) → grille de validation croisée plus lourde

---

## 6. Group-Lasso

### Principe
Quand on connaît **à l'avance** une partition des variables en groupes corrélés `G₁, ..., G_q`.

### Formulation
```
β^GL = argmin (‖Y − Xβ‖²₂ + λ Σ_{i=1}^q ‖β_q‖₂)
```
où `β_q` est le sous-vecteur de β correspondant aux variables du groupe q.

### Interprétation
- **Ridge à l'intérieur des groupes** (limite les effets de corrélations internes)
- **Lasso entre les groupes** (sélectionne des groupes entiers)

### Pour ton projet TradingMonitor
🎯 **Très pertinent** : tu pourrais grouper tes variables par bloc :
- Groupe "Bloc 1 technique" : RSI, MM, Donchian, H&S...
- Groupe "Bloc 2 événementiel" : contrats gouv, Congress trades, insider...
- Groupe "Bloc 3 relations" : facteur marché, lead-lag sectoriels...

Le Group-Lasso te permettrait de **sélectionner des familles entières** de signaux au lieu de variables individuelles. C'est cohérent avec ton architecture en blocs !

---

## 7. Pénalités pour la classification

### Adaptation aux modèles linéaires généralisés (GLM)
On remplace l'objectif `‖Y − Xβ‖²₂` par **l'opposé de la log-vraisemblance** :
```
β^E-Net = argmin (−log L(X) + λ(α‖β‖₁ + (1−α)‖β‖²₂))
```

### Cas de la régression logistique pénalisée
Pour classifier (ex: BUY/HOLD/SELL) :
```
β = argmin (−Σ log(e^{βX_i} / (1 + e^{βX_i})) + λ(α‖β‖₁ + (1−α)‖β‖²₂))
```

### Application à ton projet
Si tu veux à terme **classifier** des trades (gagnants vs perdants), tu peux faire une **régression logistique Lasso** et obtenir les **variables qui prédisent le gain**.

---

## 8. Code Python clé (à reprendre dans le projet)

### Préparation des données
```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Identification des colonnes
qualitative_cols = X.select_dtypes(include=['object', 'string']).columns
quantitative_cols = X.select_dtypes(include=['int64', 'float64']).columns

# Encodage variables qualitatives
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_qual_encoded = encoder.fit_transform(X[qualitative_cols])

# Standardisation variables quantitatives (IMPORTANT pour Ridge/Lasso !)
scaler = StandardScaler()
X_quant_scaled = scaler.fit_transform(X[quantitative_cols])

# Concaténation
X_processed = pd.concat([
    pd.DataFrame(X_quant_scaled, columns=quantitative_cols),
    pd.DataFrame(X_qual_encoded, columns=encoder.get_feature_names_out(qualitative_cols))
], axis=1)
```

### Ridge avec validation croisée
```python
from sklearn.linear_model import RidgeCV
alphas = [0.001, 0.01, 0.1, 1, 10, 100]
ridge_cv = RidgeCV(alphas=alphas, cv=5)
ridge_cv.fit(X_train_processed, y_train)
print("Meilleur alpha :", ridge_cv.alpha_)
```

### Lasso avec validation croisée
```python
from sklearn.linear_model import LassoCV
alphas = [1, 10, 100, 1000, 10000]
lasso_cv = LassoCV(alphas=alphas, cv=5)
lasso_cv.fit(X_train_processed, y_train)
print("Meilleur alpha :", lasso_cv.alpha_)

# Coefficients (avec beaucoup de 0.0000)
for feature, coef in zip(X_train_processed.columns, lasso_cv.coef_):
    print(f"{feature}: {coef:.4f}")
```

### Elastic-Net
```python
from sklearn.linear_model import ElasticNetCV
en_cv = ElasticNetCV(
    alphas=[0.001, 0.01, 0.1, 1, 10],
    l1_ratio=[0.1, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0],  # α dans la notation cours
    cv=5
)
en_cv.fit(X_train_processed, y_train)
print(f"alpha={en_cv.alpha_}, l1_ratio={en_cv.l1_ratio_}")
```

---

## 9. Synthèse d'usage pour le projet TradingMonitor

### Lien direct avec la décision méthodologique n°2 (option B+)
Dans la mémoire `project_dashboard_evolution.md`, on a tranché pour B+ : **filtre doux Porte B + Lasso CV + interactions ciblées**. Ce cours valide pleinement ce choix :
- ✅ Lasso = standard moderne pour la sélection (Tibshirani 1996)
- ✅ Le cours confirme : "**en cas de variables corrélées, une variable va être privilégiée**" → c'est exactement le piège qu'on veut éviter, d'où l'idée de combiner Lasso avec un filtre amont (Porte B).
- ✅ **Stability selection** mentionnée dans le cours = méthode complémentaire à utiliser pour rendre Lasso robuste.

### Méthodes du cours à exploiter dans le projet
- ✅ **Lasso CV** dans le Bloc final : pour la sélection automatique des variables prédictives
- ✅ **Stability selection** : faire 100 bootstraps, ne garder que les variables apparaissant dans > 50% des cas
- ✅ **Elastic-Net** : meilleur que Lasso pur quand variables fortement corrélées (cas typique en finance)
- ✅ **Group-Lasso** ⭐ : **idéal pour ton architecture en blocs** — sélectionner des familles entières de signaux (Bloc 1 / Bloc 2 / Bloc 3)
- ✅ **Standardisation préalable obligatoire** : `StandardScaler` avant tout Ridge/Lasso (sinon les coefficients ne sont pas comparables)
- ✅ **Régression logistique pénalisée** : pour la version "classification BUY/HOLD/SELL" si tu vas dans cette direction

### Pour le rapport — phrases à utiliser
> *« La régression Lasso (Tibshirani 1996) ajoute une pénalité L1 à la somme des carrés des résidus : `β^Lasso = argmin (‖Y − Xβ‖²₂ + λ‖β‖₁)`. Géométriquement, la boule L1 (losange) favorise des solutions sur ses sommets, mettant ainsi de nombreux coefficients exactement à 0 (cours Apprentissage Stat, M1 Strasbourg). »*

> *« Le paramètre λ est sélectionné par validation croisée (5-fold). La standardisation des variables explicatives est un pré-requis pour que la pénalité soit appliquée uniformément. »*

> *« Pour gérer les variables corrélées (RSI(14) et RSI(21), MM20 et MM50...), on privilégie une régression Elastic-Net qui combine pénalités L1 et L2, évitant la sélection arbitraire d'une variable parmi les corrélées. »*

> *« Compte tenu de l'architecture en blocs du projet (Bloc 1 technique, Bloc 2 événementiel, Bloc 3 relations), une approche Group-Lasso est envisagée pour sélectionner des familles entières de signaux plutôt que des variables isolées. »*

---

## 10. À retenir en une phrase

**Lasso = régression + sélection automatique de variables**. C'est la brique centrale de ton Bloc final, avec la nuance que **Elastic-Net** ou **Group-Lasso** sont des extensions naturelles à considérer selon la structure de tes données.
