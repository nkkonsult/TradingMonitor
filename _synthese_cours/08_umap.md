---
name: 08-umap
description: Synthèse cours "Réduction de la dimension non linéaire - UMAP" (Chevallier & Birmelé, 18 pages) — réduction de dimension non linéaire via graphe de plus proches voisins
metadata:
  type: reference
---

# UMAP — Réduction de dimension non linéaire (18 pages)

## 1. Problématique

- Données Xᵢ dans ℝᵈ (grande dimension)
- On cherche une **surface 𝓜** (variété) de dimension plus petite telle que les données soient « sur » 𝓜
- **ACP** ([[01-acp]]) suppose que 𝓜 est un **hyperplan** (linéaire)
- ❌ Si les données ne sont **PAS sur un plan** (= relations non linéaires), l'ACP échoue
- **Objectif** : trouver 𝓜 même non linéaire, puis projeter les Xᵢ dans ℝ^d_small

## 2. Algorithmes non linéaires
- Laplacian EigenMap
- t-SNE
- **UMAP** (Uniform Manifold Approximation and Projection) ← **étudié dans ce cours**

Tous ces algorithmes ont un fonctionnement **similaire** :
- Hypothèse 1 : les données sont sur une variété 𝓜
- Hypothèse 2 : les données sont échantillonnées **uniformément** sur 𝓜

## 3. Vue d'ensemble de l'algorithme

3 étapes :
1. Construire le **graphe des k plus proches voisins**
2. **Symétriser** le graphe
3. Trouver une représentation de ce graphe dans un espace de **dimension plus petite**, en conservant sa structure

**Idée centrale** : le graphe des voisins décrit correctement la structure de 𝓜.

## 4. Hypothèse de densité uniforme — astuce métrique

L'hypothèse de densité uniforme paraît restrictive. Mais on peut trouver une **nouvelle métrique** sur 𝓜 telle que la densité devienne uniforme :
- Changer de métrique = compresser certaines zones et en dilater d'autres
- Le graphe des k plus proches voisins **construit implicitement** cette métrique

**Concrètement** : si on note rᵢ la distance au k-ème voisin le plus éloigné,
- rᵢ petit → points concentrés → distances **agrandies**
- rᵢ grand → points dispersés → distances **réduites**

## 5. Construction du graphe des voisins

### 5.1 Graphe initial
- On connecte chaque Xᵢ à ses k plus proches voisins
- ⚠️ Le graphe n'est **pas symétrique** (Xⱼ peut être voisin de Xᵢ sans l'inverse)

### 5.2 Poids des arêtes (smooth k-NN)
Pour un point Xᵢ :
- On note ρᵢ la distance au **voisin le plus proche**
- σᵢ choisi pour que :
$$ \sum_{j=1}^k \exp\left(\frac{-\max(0, d(X_i, X_{i_j}) - \rho_i)}{\sigma_i}\right) = \log_2(k) $$

Poids des arêtes :
$$ w(X_i, X_{i_j}) = \exp\left(\frac{-\max(0, d(X_i, X_{i_j}) - \rho_i)}{\sigma_i}\right) $$

Propriétés :
- Poids du voisin le plus proche = 1
- Somme des poids = log₂(k)

### 5.3 Justification du choix des poids
- Idée naïve : prendre les distances comme poids
- **Mais** en grande dimension, les distances entre 2 points deviennent toutes similaires → **fléau de la dimension** (curse of dimensionality)
- Stratégie naïve = poids quasi-identiques pour tous → inutile
- ⇒ Choix relatif à la distance du voisin le plus proche

### 5.4 Symétrisation
Pour rendre le graphe symétrique, UMAP combine les poids :
$$ p_{ij} = w(X_i, X_j) + w(X_j, X_i) - w(X_i, X_j) \cdot w(X_j, X_i) $$

Interprétation : probabilité que Xᵢ soit connecté à Xⱼ **ET** Xⱼ soit connecté à Xᵢ.

## 6. Réduction de dimension

### 6.1 Espace d'arrivée
Chaque Xᵢ → un point Yᵢ dans ℝᵖ (typiquement p = 2 ou 3 pour visualisation).

Proximité dans l'espace d'arrivée :
$$ q_{i,j} = \frac{1}{1 + a \|Y_i - Y_j\|_2^{2b-1}} $$

(a et b sont des paramètres internes UMAP)

### 6.2 Fonction de coût (à minimiser)
$$ C = \sum_{i,j} p_{ij} \log\frac{p_{ij}}{q_{ij}} + (1 - p_{ij}) \log\frac{1 - p_{ij}}{1 - q_{ij}} $$

= entropie croisée binaire entre la structure originelle p et la structure projetée q.

### 6.3 Graph Layout (algorithme d'optimisation)
- Forces **attractives** : voisins proches
- Forces **répulsives** : points éloignés
- Descente de gradient itérative
- À chaque itération : 2 points sélectionnés, forces appliquées
- On itère jusqu'à stabilisation du graphe

## 7. Code Python (librairie `umap-learn`)

### Initialisation
```python
import umap
reducer = umap.UMAP(n_neighbors=30, min_dist=0.1,
                    n_components=2, random_state=42)
```

### Hyperparamètres
| Paramètre | Rôle |
|---|---|
| `n_neighbors` | k du graphe de voisins (15-50 typique). **Petit** = structure locale, **grand** = structure globale |
| `min_dist` | distance minimale dans la représentation finale (0.0-1.0). **Petit** = clusters serrés, **grand** = points étalés |
| `n_components` | dimension de l'espace final (2 ou 3 pour visu, plus pour features) |

### Réduction d'un dataset
```python
X_umap = reducer.fit_transform(X)
plt.scatter(X_umap[:, 0], X_umap[:, 1], c=y, cmap='Spectral')
```

### Pour transformer de nouvelles données (pipeline ML)
```python
trans = reducer.fit(X_train)
X_train_umap = trans.transform(X_train)
X_test_umap  = trans.transform(X_test)  # ⚠️ jamais fit sur le test
```

UMAP suit la nomenclature sklearn (`fit` + `transform` séparés).

## 8. UMAP + classification

UMAP comme **réducteur de features avant classifieur** :
```python
X_train_umap = umap.UMAP(...).fit_transform(X_train)
clf = LogisticRegression().fit(X_train_umap, y_train)
```

⇒ Peut améliorer un classifieur sur données très haute dimension.

## 9. ⚠️ Limites — Clustering

> **POINT IMPORTANT** : UMAP **NE préserve PAS** :
> - les distances
> - les densités
> - parfaitement les plus proches voisins

➡️ Il est **difficile de savoir** si un cluster visible sur la projection UMAP correspond réellement à quelque chose dans les données.

> « Mais il semble que cela fonctionne tout de même raisonnablement dans certains cas. »

---

## 🎯 Applications au projet TradingMonitor

### Quand utiliser UMAP plutôt que l'ACP ([[01-acp]]) ?

| Critère | ACP | UMAP |
|---|---|---|
| Type de relations capturées | **Linéaires** uniquement | Non linéaires |
| Interprétabilité des axes | ✅ axes = combinaisons des variables | ❌ axes sans signification |
| Préservation des distances | ✅ globale | ❌ locale seulement |
| Cours universitaire | ✅ vu en cours ([[01-acp]]) | ✅ vu en cours (ce cours) |
| Pour rapport | "méthode statistique vue en M1" | "comparaison méthodes linéaire/non-linéaire" |

### Cas d'usage projet

1. **Bloc 1 — Trades multidimensionnels**
   - 38 035 trades × N variables (durée, taille, secteur, momentum, vol…)
   - ACP donne une projection linéaire
   - **UMAP** pourrait révéler des **clusters de profils de trades** non visibles en ACP
   - 📊 Cas d'usage typique : "j'ai comparé l'ACP linéaire et UMAP non-linéaire pour valider que les axes ACP capturent bien la structure des trades"

2. **Bloc 3 — Régimes de marché**
   - Si on prend les rendements quotidiens × N actions, l'UMAP pourrait isoler les **régimes** (bull / bear / sideways) non linéairement
   - À combiner avec un clustering (HDBSCAN typiquement)

3. **⚠️ Attention au piège du clustering visuel** :
   - Si UMAP montre 3 clusters distincts, ça ne veut PAS dire qu'il y a 3 vrais régimes
   - Les distances et densités ne sont pas préservées
   - Toujours **valider** avec une autre méthode (k-means sur données originales, CAH…)

### Comparaison ACP vs UMAP dans le rapport (idée de pattern)

| Méthode | Variance expliquée | Visualisation | Validation statistique |
|---|---|---|---|
| ACP normée | 73% sur 2 axes (PC1 = facteur marché) | OK mais étalée | ✅ cos², CTR, V.Test |
| UMAP | (pas applicable) | Clusters visibles | ❌ pas de métrique standard |

➡️ **Conclusion méthodologique pour le rapport** : UMAP utile pour **explorer** mais pas pour **conclure**.

---

## ✅ Méthodes acquises dans ce cours
- UMAP (algorithme complet : graphe k-NN, smooth k-NN, symétrisation, optimisation)
- Graphe des k plus proches voisins (asymétrique → symétrique)
- Notion de **variété** et de **changement de métrique**
- Curse of dimensionality (fléau de la dimension)
- Mention de **t-SNE** et **Laplacian EigenMap** (cousins de UMAP)

## 🆕 À étudier (PAS dans ce cours)
- **t-SNE** en détail (algorithme similaire, antérieur, beaucoup utilisé)
- **PaCMAP**, **TriMap** (versions plus récentes, mieux préservent la structure globale)
- **HDBSCAN** (clustering hiérarchique sur projection UMAP)
- **Trustworthiness / Continuity** (métriques pour évaluer une projection non linéaire)
