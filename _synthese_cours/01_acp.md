# Synthèse — Cours ACP (Périnel, Strasbourg M1 2024-25)

> Cours complet de 143 pages lu et résumé. Tous les concepts essentiels sont ci-dessous.
> **Ne pas rouvrir le PDF** — tout est ici.

---

## 1. Cadrage général

**Enseignant** : Emmanuel Périnel
**Niveau** : Master 1 Statistique / DUAS, Strasbourg
**Approche** : statistique exploratoire, **géométrique** (algèbre matricielle), peu d'hypothèses sur les données
**Famille** : analyses factorielles, à côté de l'AFC et l'ACM
**Logiciel** : R + package **FactoMineR** + factoextra (visualisations)

### Place de l'ACP dans le panorama

```
Analyses factorielles
├── ACP    → individus × variables QUANTITATIVES
├── AFC    → tableau de contingence (2 variables qualitatives)
└── ACM    → individus × variables QUALITATIVES

Méthodes de classification (complémentaires)
├── CAH   → arbre hiérarchique (dendrogramme)
└── k-means → partitionnement direct (k connu a priori)
```

---

## 2. Notations (à respecter dans le rapport)

| Symbole | Signification |
|---|---|
| `X` | matrice de données `(n, p)` |
| `n` | nombre d'individus |
| `p` | nombre de variables |
| `x_ij` | valeur de l'individu `i` sur la variable `j` |
| `x_i` | vecteur ligne (un individu) |
| `X_j` | vecteur colonne (une variable) |
| `G = (x̄_1, ..., x̄_p)` | centre de gravité (barycentre) |
| `m_i` | masse de l'individu `i` (généralement `1/n`) |
| `m_j` | masse de la variable `j` (généralement `1`) |
| `d²(i, l) = Σ_j (x_ij − x_lj)²` | distance euclidienne (carrée) |
| `I = Σ_i m_i d²(G, i) = Σ_j V(X_j)` | **inertie totale** (= variance multidim) |
| `λ_k` | valeur propre = inertie de l'axe `k` |
| `v_k` | vecteur propre de l'axe `k` |
| `c_ik` | coordonnée de l'individu `i` sur l'axe `k` |
| `d_jk` | coordonnée de la variable `j` sur l'axe `k` (= `r(X_j, v_k)` en ACP normée) |
| `H_i` | projection orthogonale de `i` sur le plan factoriel |
| `CP_k` | composante principale de rang `k` (variable synthétique) |

---

## 3. Objectifs de l'ACP

L'ACP vise à :
1. **(Lignes)** Bilan des **ressemblances entre individus**
2. **(Colonnes)** Bilan des **corrélations entre variables**
3. **Mise en liaison** des deux études (quelles variables caractérisent un groupe d'individus ?)
4. **Construction de variables synthétiques** : les **composantes principales** (CP)

---

## 4. Transformations préalables des données

### Centrage (SYSTÉMATIQUE en ACP)
```
x_ij → x_ij − x̄_j
```
- Translate le nuage sur l'origine (G = O)
- Toutes les variables ont moyenne 0

### Réduction (PAS systématique — sous conditions)
```
x_ij → (x_ij − x̄_j) / s_j
```
- Divise par l'écart-type
- Toutes les variables ont écart-type 1 (longueur 1 dans l'espace)

#### Quand faut-il réduire ?
- **Obligatoire** si les variables ont des **unités différentes** (sinon la variable la plus dispersée écrase tout)
- **Discutable** si même unité (à juger au cas par cas)

#### Vocabulaire
- **ACP normée** = ACP sur données centrées-**réduites**
- **ACP non normée** = ACP sur données centrées **non** réduites
- Conséquence : en ACP normée, toutes les variables ont la **même importance** dans la construction des axes

---

## 5. Le nuage des individus

### Concepts clés
- Chaque individu = un point dans un espace à **p dimensions**
- **Centre de gravité G** = barycentre du nuage
- **Distance euclidienne** entre individus : `d²(i, l) = Σ (x_ij − x_lj)²`

### Inertie : la variance multidimensionnelle
```
I = Σ_i m_i × d²(G, i) = Σ_j V(X_j)
```
- Mécanique : résistance à la rotation
- Statistique : dispersion totale
- Liée à la **forme** du nuage (allongement)

### Ajustement = projection sur un plan
- Espace à p dimensions inaccessible → on cherche une **projection** sur 2 dimensions
- **Critère** : maximiser l'**inertie projetée** (= projection la plus « vaste », la moins déformante)
- **Projection orthogonale** sur les axes factoriels

### Décomposition de l'inertie projetée
```
I_proj = I_1 + I_2  (axes 1 et 2)
I_k = Σ_i m_i × d²(G, H_ik)  ← inertie de l'axe k = variance des coordonnées
```

### Axes factoriels (= axes principaux d'inertie)
- **Axe 1** = direction d'**allongement maximal** du nuage
- **Axe 2** = deuxième direction d'allongement, **orthogonale** à l'axe 1
- etc.

### Critères équivalents pour le meilleur plan
1. **Inertie projetée maximale**
2. Distances entre individus les moins déformées (= les plus grandes possible — la projection réduit toujours)
3. Le plan passe **au plus près** de tous les individus (somme des carrés des distances minimale)

⚠️ **Attention aux proximités trompeuses** : deux individus peuvent paraître proches en projection alors qu'ils sont éloignés dans l'espace réel. D'où l'importance du **cos²** (voir section 10).

---

## 6. Le nuage des variables

### Concepts clés
- Espace à **n dimensions** (une dimension par individu)
- Chaque variable = un vecteur depuis l'origine
- **Longueur d'une variable** = son écart-type
- Si données centrées-réduites → toutes les variables sur une **hypersphère de rayon 1**

### Cosinus = corrélation linéaire
**Résultat fondamental :**
```
r(X_1, X_2) = cos(angle entre X_1 et X_2)
```
- Angle aigu (cos proche de +1) → variables très corrélées positivement
- Angle plat (cos proche de -1) → corrélation négative
- Angle droit (cos = 0) → variables non corrélées
- Angle 45° → r = √2/2 ≈ 0.71

**Conséquence :** l'ACP étudie des **liaisons linéaires** entre variables.

### Le cercle des corrélations
- Projection des variables sur le plan factoriel
- Chaque variable projetée a longueur ≤ 1
- Plus la variable est **proche du cercle**, mieux elle est représentée

---

## 7. Composantes principales (CP)

### Définition
Chaque axe factoriel définit une **nouvelle variable synthétique** appelée **composante principale (CP)**.

```
CP_1 = (1/√λ_1) × (poids_1 · X_1 + poids_2 · X_2 + ... + poids_p · X_p)
```

Le poids d'une variable dans CP_k est **proportionnel à sa corrélation** avec l'axe k (donc à `d_jk`).

### Propriétés des CP
- **Combinaisons linéaires** des variables initiales
- **Non corrélées entre elles** (les axes sont orthogonaux)
- **Inertie maximale** (CP_1 résume au mieux, puis CP_2, etc.)

### Nouvelle vision de l'ACP
> L'ACP **remplace** un ensemble de variables initiales corrélées par un ensemble de **CP non corrélées** entre elles et de variance maximale.

---

## 8. Point de vue mathématique

### Procédure de calcul
1. Construire la **matrice d'inertie V** :
   - `V = (1/n) X^t X`
   - `V = matrice de variance-covariance` si données centrées
   - `V = matrice des corrélations` si données centrées-réduites (ACP normée)
2. **Diagonaliser V** :
   - Vecteurs propres `u_1, u_2, ...` = axes factoriels
   - Valeurs propres `λ_1 ≥ λ_2 ≥ ...` = inerties des axes
3. **Trier** les valeurs propres par ordre décroissant
4. **Projeter** les individus sur les axes

### Nombre d'axes
- `Nombre d'axes = min(n, p)`
- En pratique, n > p donc on a `p` axes
- En ACP normée : `Inertie totale = trace(V) = p`

### Démonstration matricielle (Cours 1bis Périnel)

**Problème de maximisation** : trouver `u_1` unitaire qui maximise l'inertie projetée :
```
max  I_1 = (1/n) u_1^t (X^t X) u_1     sous contrainte  u_1^t u_1 = 1
```

**Méthode du lagrangien** :
```
L = (1/n) u_1^t (X^t X) u_1 − λ_1 (u_1^t u_1 − 1)
```

En dérivant par rapport à `u_1` et en annulant :
```
(1/n) (X^t X) u_1 = λ_1 u_1
```

Donc :
- `u_1` = **vecteur propre** de `V = (1/n) X^t X` associé à `λ_1`
- `λ_1` = **valeur propre** = **inertie projetée sur l'axe** `u_1`

En multipliant à gauche par `u_1^t` (avec `u_1^t u_1 = 1`) :
```
I_1 = (1/n) u_1^t (X^t X) u_1 = λ_1
```

**Second axe `u_2`** : même raisonnement avec contraintes supplémentaires `u_2^t u_2 = 1` et `u_1 ⊥ u_2` → `u_2` = 2e vecteur propre associé à `λ_2`.

### Théorème d'emboîtement des solutions
> Le meilleur espace de projection de dimension `k` est engendré par les `k` vecteurs propres associés aux `k` plus grandes valeurs propres de `V`.
>
> Si `F_k` est le meilleur espace de dimension k, alors `F_{k+1} = F_k ⊕ (sous-espace 1D d'inertie max, orthogonal à F_k)`.

**Conséquence pratique** : on construit successivement (axe 1, puis axe 2 dans le complément orthogonal, etc.) — pas besoin de chercher directement le « meilleur plan ».

### Lien nuage individus / nuage variables (formules de transition)

Le nuage des variables (dans R^n) conduit à diagonaliser `X X^t` (dimension n×n) avec valeurs propres `μ_k`.

**Résultat fondamental** : `λ_k = μ_k` (les valeurs propres sont identiques).

**Formules de transition** :
```
v_k = (1/√λ_k) × X u_k        ← coord des variables à partir des coord des individus
u_k = (1/√λ_k) × X^t v_k      ← inverse
```

**Astuce calculatoire** : on ne diagonalise que la **plus petite** des deux matrices (X^t X de dim p×p, ou X X^t de dim n×n), et on déduit l'autre par les formules de transition.

### Propriétés des composantes principales (CP)
- `C_k = X u_k` : vecteur des coordonnées des n individus sur l'axe k
- `Var(C_k) = λ_k`
- Les CP sont **orthogonales 2 à 2** (donc non corrélées)
- L'ACP **transforme** les variables initiales corrélées en CP non corrélées et de variance maximale

---

## 9. Interprétation conjointe individus / variables

### Formules de transition
Lien entre coordonnées des individus et coordonnées des variables sur le même axe :

```
c_ik = (1/√I_k) Σ_j ((x_ij − x̄_j)/s_j) × d_jk

d_jk = (1/√I_k) × (1/n) Σ_i ((x_ij − x̄_j)/s_j) × c_ik
```

### Règle de lecture directionnelle
Un individu `(i)` situé du côté **+** de l'axe :
- Prend des **valeurs élevées** pour les variables placées **dans sa direction** et **fortement liées** à l'axe
- Prend des **valeurs faibles** pour les variables placées en **direction opposée** et fortement liées

---

## 10. Aides à l'interprétation : cos² et contribution

### 10.1 Coordonnées des individus
Tableau direct des `c_ik` pour chaque individu et chaque axe.

### 10.2 Qualité de représentation d'un individu : cos²
**Question** : la position de l'individu sur le plan est-elle fidèle à sa position réelle ?

```
QLT_(1,2)(i) = cos²(θ_i) = (OH_i / Oi)²

QLT_(1,2)(i) = cos²(θ_i1) + cos²(θ_i2)
```

**Propriété fondamentale** : `Σ_k QLT_k(i) = 1` (somme sur tous les axes)

**Lecture** :
- cos² **proche de 1** → individu **bien représenté** sur le plan (proximités fiables)
- cos² **faible** → individu mal représenté (attention aux proximités trompeuses !)

### 10.3 Contribution d'un individu à un axe : CTR
**Question** : quels individus ont le plus contribué à construire l'axe ?

```
CTR_k(i) = m_i × c_ik² / I_k    (en % de l'inertie de l'axe)
```

**Propriétés** :
- `Σ_i CTR_k(i) = 1`
- **Effet levier** : la CTR dépend de l'**éloignement au carré** → les individus aux extrémités contribuent énormément

**Utilité** :
- Identifier les individus **importants** pour interpréter l'axe
- Repérer les individus à **trop forte contribution** (à retirer éventuellement)

### Contribution au plan (1,2)
```
CTR_(1,2)(i) = m_i × (c_i1² + c_i2²) / (I_1 + I_2)
```

### 10.4 Coordonnées et qualité des variables
En ACP normée :
```
d_jk = r(X_j, axe k)        ← coordonnée = corrélation
QLT_(1,2)(j) = (OH_j)²       ← proximité au bord du cercle
```

### 10.5 Contribution d'une variable à un axe
```
CTR_k(X_j) = m_j × c_jk² = c_jk²   (si m_j = 1)
CTR_(1,2)(X_j) = c_j1² + c_j2²
```

⚠️ **Astuce** : la position d'une variable sur le cercle des corrélations donne **à la fois** sa contribution et sa qualité.

---

## 11. Combien d'axes interpréter ?

Trois critères courants :

### 11.1 Critère de Kaiser
```
On retient les axes d'inertie > inertie moyenne
En ACP normée : inertie moyenne = 1 → retenir λ_k > 1
```

### 11.2 Scree-test de Cattell (« coude »)
- Regarder l'éboulis des valeurs propres
- Repérer une **rupture de pente** (coude)
- Garder les axes **avant le coude**

Version numérique : différences premières, puis secondes ; on retient `λ_1, ..., λ_{k+1}` où `δ_k < 0`.

### 11.3 Modèle du « bâton brisé » (broken stick, Frontier 1976)
On retient les axes dont le % d'inertie est **supérieur** à celui prédit par un tirage aléatoire (le bâton brisé en p morceaux).

```
b_k = (1/p) × Σ_{i=k}^{p} (1/i)
```

### 11.4 Quantiles de Husson (95%)
Table donnant le **quantile à 95%** du % d'inertie des 2 premières dimensions pour 10000 ACP de variables indépendantes. On retient si on dépasse le quantile.

---

## 12. Variables illustratives (supplémentaires)

### Variables actives vs illustratives
- **Variables actives** : participent à la **construction des axes**
- **Variables illustratives** (= supplémentaires) : **projetées a posteriori** pour aider à l'interprétation, mais ne participent pas à la construction

### Pourquoi c'est utile
1. Faciliter l'interprétation des axes (ex: projeter `Latitude`, `Couleur politique` sur une ACP sur les températures)
2. Mettre en relation deux ensembles de variables
3. **PEUVENT ÊTRE QUALITATIVES OU QUANTITATIVES** (en ACP, les actives doivent être quantitatives)

### Variables quantitatives illustratives
- Projetées sur le cercle des corrélations
- Aides : `$coord`, `$cor`, `$cos2`

### Variables qualitatives illustratives
- Chaque modalité projetée comme le **barycentre** des individus qui la portent
- **V.Test** pour évaluer si la modalité est significativement liée à l'axe

#### V.Test (très important pour le rapport)
Sous H₀ : "les n_k individus ont été tirés au hasard", la coordonnée moyenne suit :
```
N(0, s_ck²)   où s_ck² = ((n − n_k)/(n − 1)) × s²/n_k
```

D'où :
```
V.Test = c_k / s_ck ≈ N(0, 1)
```

**Règle d'interprétation** :
```
|V.Test| > 1.96  ⇔  p-value < 5%
```
La modalité est **statistiquement liée à l'axe**.

#### η² (rapport de corrélation)
Mesure l'**intensité** de la liaison entre une variable qualitative et un axe.

---

## 13. Mise en œuvre R (cours)

### Package FactoMineR
```r
acp.temp <- PCA(temp[, 1:12],
                scale.unit = TRUE,    # TRUE = ACP normée
                ncp = 5,              # nombre d'axes à conserver
                ind.sup = NULL,       # individus supplémentaires
                quanti.sup = NULL,    # variables quantitatives illustratives
                quali.sup = NULL,     # variables qualitatives illustratives
                graph = TRUE,         # affichage automatique
                axes = c(1, 2))
```

### Organisation des résultats (`res$`)
```
res$eig                 → inerties des axes (eigenvalues, % variance, cumul)
res$ind$coord           → coordonnées des individus
res$ind$contrib         → contributions des individus
res$ind$cos2            → qualités de représentation
res$ind$dist            → distance au point moyen
res$var$coord           → coordonnées des variables
res$var$contrib         → contributions des variables
res$var$cos2            → qualités de représentation
res$var$cor             → corrélations avec les axes
res$quanti.sup$...      → résultats variables quantitatives illustratives
res$quali.sup$coord     → coordonnées (barycentres) des modalités
res$quali.sup$v.test    → V.Test
res$quali.sup$eta2      → rapport de corrélation η²
```

### Package factoextra (visualisations)
```r
fviz_eig(acp.temp, addlabels = TRUE)              # éboulis des inerties
fviz_pca_ind(acp.temp, repel = TRUE)              # plan des individus
fviz_pca_var(acp.temp)                            # cercle des corrélations
fviz_pca_biplot(acp.temp)                         # biplot (les deux ensemble)
fviz_cos2(acp.temp, choice = "ind", axes = 1:2)   # cos² des individus
fviz_contrib(acp.temp, choice = "var", axes = 1)  # contributions des variables
```

### Autres packages utiles
- **corrplot** : visualiser les matrices de corrélation
- **Rcmdr + RcmdrPlugin.FactoMineR** : interface graphique (menu FactoMineR)

---

## 14. Synthèse d'usage pour le projet TradingMonitor

### Notations à reprendre dans le rapport (cohérence avec ce cours)
- Utiliser `c_ik` pour coordonnées individus, `d_jk` pour coordonnées variables
- Parler d'**inertie** (= variance multidim) plutôt que de "variance des composantes principales"
- Utiliser **% d'inertie** (= `λ_k / Σ λ_k`)
- Mentionner explicitement « **ACP normée** » si données centrées-réduites
- Pour la qualité : **cos²** (et non « qualité de représentation » seul)
- Pour la sélection des axes : critère de **Kaiser** et/ou **Cattell** (scree-test)

### Méthodes du cours pas encore exploitées dans le projet
- ✅ **Variables illustratives** : on pourrait projeter `regime_entry` (qualitatif) en illustratif sur une ACP des trades — actuellement on n'a pas fait cette distinction active/illustrative
- ✅ **V.Test** sur modalités qualitatives → quantifier la liaison régime × axe
- ✅ **η²** comme mesure de force de liaison
- ✅ **Biplot** (`fviz_pca_biplot`) → représentation simultanée
- ⚠️ Le projet utilise `numpy` pur, pas FactoMineR. Pour montrer la cohérence avec le cours dans le rapport : **citer les fonctions équivalentes** et expliquer pourquoi on a refait en numpy (transparence pédagogique).

### Pour le rapport — phrases à utiliser
> *« Conformément à la méthodologie vue en cours (Périnel, M1 Stat Strasbourg), on a réalisé une ACP normée (données centrées-réduites). »*

> *« La qualité de représentation des individus sur le plan (cos²) est >= X, ce qui garantit que les proximités observées ne sont pas trompeuses. »*

> *« On retient deux axes au critère de Kaiser (inertie > 1 en ACP normée), qui restituent ensemble 99 % de l'inertie. »*

> *« Pour évaluer la liaison entre le régime et les axes, on calcule le V.Test (cours, p. 142). |V.Test| > 1.96 indique une liaison significative à 5 %. »*

---

## 15. Bibliographie citée dans le cours

- Bouroche J.M. et Saporta G. (1980). *L'analyse des données*, PUF, Que sais-je ?
- Cornillon P.A. et al. (2008). *Statistiques avec R*, Presses Univ. Rennes
- Escofier B. et Pagès J. (2008). *Analyses factorielles simples et multiples*, 4e éd., Dunod
- Husson F., Lê S. et Pagès J. (2009). *Analyse de données avec R*, Presses Univ. Rennes
- Lebart L., Morineau A. et Piron M. (2006). *Statistique exploratoire multidimensionnelle*, Dunod
- Saporta G. (2006). *Probabilités, analyses des données et statistiques*, 2e éd., Technip
- Frontier S. (1976). Modèle du bâton brisé.
