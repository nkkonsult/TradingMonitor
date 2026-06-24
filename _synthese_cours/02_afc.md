# Synthèse — Cours AFC (Périnel, Strasbourg M1 2024-25)

> Cours complet de 62 pages lu et résumé.

---

## 1. Cadrage général

**Enseignant** : Emmanuel Périnel
**Niveau** : Master 1 Statistique / DUAS, Strasbourg
**Famille** : analyses factorielles (à côté de l'ACP et l'ACM)
**Logiciel** : R + package **FactoMineR** (fonction `CA`) + factoextra

### Différence avec l'ACP
| ACP | AFC |
|---|---|
| individus × variables QUANTITATIVES | tableau de **contingence** (2 variables QUALITATIVES) |
| moyennes, écarts-types, corrélations | profils, masses, distance du χ² |
| nuage des individus (R^p) + variables (R^n) | 2 nuages de **profils** (lignes et colonnes) |
| centrage + réduction | **profils** (pourcentages par ligne ou colonne) |
| matrice X^t X | tableau de **résidus standardisés** |

---

## 2. Notations

| Symbole | Signification |
|---|---|
| `n_ij` | effectif observé de l'individu vérifiant modalités `i` (ligne) et `j` (colonne) |
| `n_i•` | total de la ligne `i` |
| `n_•j` | total de la colonne `j` |
| `n` | effectif total du tableau |
| `t_ij = (n_i• × n_•j) / n` | **effectif théorique** sous indépendance |
| `m_i = n_i• / n` | **masse** de la ligne i |
| `m_j = n_•j / n` | **masse** de la colonne j |
| `n_ij / n_i•` | terme du **profil ligne** i |
| `n_ij / n_•j` | terme du **profil colonne** j |
| `D²` | statistique du χ² (= n × inertie totale) |
| `r_ij` | résidu ajusté de Haberman |
| `λ_k` | k-ème valeur propre = inertie de l'axe k |
| `c_ik` ou `F_k(i)` | coordonnée du profil ligne i sur l'axe k |
| `G_k(j)` | coordonnée du profil colonne j sur l'axe k |

---

## 3. Le tableau analysé

**Tableau de contingence** : croisement de deux variables qualitatives.
- Lignes (I modalités) : ex. départements
- Colonnes (J modalités) : ex. candidats
- Case `(i,j)` : `n_ij` = effectif des individus possédant simultanément la modalité i et la modalité j.

### Exemples de tableaux de contingence
- PCS × arrondissement → nombre d'habitants de chaque profession dans chaque arrondissement
- Couleur des yeux × couleur des cheveux
- Cause de décès × classe d'âge
- Discours candidats × mots cités

### Pourquoi pas une ACP du tableau de contingence ?
**Mauvaise idée** : sur l'exemple présidentielles 2012, l'ACP donne un **effet taille** prédominant (88% de l'inertie) où l'axe 1 ordonne les départements du plus petit au plus grand. La structure géopolitique du vote (l'info intéressante) s'efface.

**Conclusion** : il faut travailler sur des **profils** (pourcentages) et non sur les effectifs bruts → c'est l'AFC.

---

## 4. Les profils

### Profils lignes
On divise chaque case par le total de la ligne :
```
profil ligne i = (n_i1/n_i•, n_i2/n_i•, ..., n_iJ/n_i•)
```
Chaque profil ligne **somme à 1** (= 100%). C'est la **distribution conditionnelle** des colonnes sachant la ligne.

### Profils colonnes
Idem mais on divise par le total de la colonne :
```
profil colonne j = (n_1j/n_•j, n_2j/n_•j, ..., n_Ij/n_•j)
```

### Lecture des profils sur l'exemple
- Profil ligne Bas-Rhin : (2.76% EvaJoly, 21.21% LePen, 33.62% Sarkozy, ...) → c'est le score *en %* des candidats dans ce département.
- Profil colonne Sarkozy : répartition de ses voix par département.

### Masses des modalités (différence importante avec l'ACP)
**En ACP** : tous les individus ont la même masse `1/n`.
**En AFC** : les masses sont **différentes**, proportionnelles à l'effectif marginal.
```
m_i = n_i• / n     (masse de la ligne i)
m_j = n_•j / n     (masse de la colonne j)
```
Une modalité avec **beaucoup d'observations** pèse plus.

---

## 5. L'AFC comme analyse d'un lien de dépendance

### Question fondamentale
Existe-t-il un lien de dépendance entre les deux variables qualitatives ?

### Cas de l'indépendance parfaite
- H₀ : `P(A | B) = P(A)` ⇔ `P(A ∩ B) = P(A) × P(B)`
- En tableau : **égalité des profils lignes** (tous identiques) **et** égalité des profils colonnes.

### Cas du lien fort
- Profils lignes très différents entre eux
- Profils colonnes très différents entre eux

### Test du χ² (rappel)
**Statistique** :
```
D² = Σ_i Σ_j (n_ij − t_ij)² / t_ij     où t_ij = (n_i• × n_•j) / n
```
Sous H₀ (indépendance), `D² ~ χ²((I−1)(J−1))`.

### Contributions au χ²
**Contribution de la case (i,j)** :
```
CTR(i,j) = (n_ij − t_ij)² / t_ij        (brute)
CTR(i,j) / D²                            (en %)
```

### Attirance / répulsion
- **Attirance** : `n_ij > t_ij` ⇔ effectif observé **supérieur** à l'attendu en indépendance → modalités attirées
- **Répulsion** : `n_ij < t_ij` ⇔ effectif observé **inférieur** → modalités repoussées

### Résidus ajustés de Haberman
**Pour tester la significativité d'une attirance/répulsion** :
```
r_ij = (n_ij − t_ij) / √(t_ij × (1 − f_i) × (1 − f_j))
```
où `f_i = n_i•/n` et `f_j = n_•j/n` sont les fréquences marginales.

**Sous H₀**, `r_ij` suit asymptotiquement une loi `N(0,1)`.

**Règle d'interprétation** :
```
|r_ij| > 1.96  ⇔  association significative à 5%
r_ij > 0       → ATTIRANCE
r_ij < 0       → RÉPULSION
```

### Lien entre le test du χ² et l'AFC
> L'AFC est un **outil graphique** qui montre **comment se structure le lien de dépendance** détecté par le χ² :
> - quelles modalités lignes ressemblent ?
> - quelles modalités colonnes ressemblent ?
> - quelles attirances/répulsions ?

---

## 6. La distance du χ² (au cœur de l'AFC)

### Définition
La distance utilisée pour comparer deux profils lignes (par exemple) :
```
d²_χ²(i, l) = Σ_j (1/m_j) × (n_ij/n_i• − n_lj/n_l•)²
```
**Le facteur `1/m_j`** est crucial : il **revalorise** les colonnes de faible effectif.

### Propriété fondamentale : l'équivalence distributionnelle
> Si deux lignes (resp. colonnes) ont des **profils identiques**, alors leur **agrégation** ne modifie pas les distances entre profils colonnes (resp. profils lignes).

**Conséquence pratique** : robustesse vis-à-vis du **découpage en modalités** d'une variable nominale. On peut regrouper des modalités similaires sans perdre d'information.

---

## 7. Ajustement des deux nuages de profils

### Démarche
- Les **I profils lignes** forment un nuage dans R^J (espace à J dimensions).
- Les **J profils colonnes** forment un nuage dans R^I.
- On cherche le **meilleur plan de projection** dans chaque cas.

### Critère
Maximiser **l'inertie projetée** :
```
I = Σ_i m_i × d²_χ²(H_i, G)
```
où `G` est le centre de gravité et `H_i` la projection de `i`.

### Centres de gravité = profils moyens
- **Barycentre des profils lignes** `G_I` = profil de la ligne « total » :
  ```
  G_I = (n_•1/n, n_•2/n, ..., n_•J/n)
  ```
- **Barycentre des profils colonnes** `G_J` :
  ```
  G_J = (n_1•/n, n_2•/n, ..., n_I•/n)
  ```

**Interprétation** : plus une modalité se rapproche (ou s'écarte) du centre de gravité, plus son profil est proche (ou différent) du profil moyen.

### Lien fondamental entre les deux ajustements
> Les valeurs propres `λ_k` sont **identiques** pour les deux nuages.
>
> Les coordonnées sur les axes sont liées par les **relations quasi-barycentriques (formules de transition)** :
> ```
> F_k(i) = (1/√λ_k) × Σ_j (n_ij/n_i•) × G_k(j)
> G_k(j) = (1/√λ_k) × Σ_i (n_ij/n_•j) × F_k(i)
> ```

**Interprétation** : une modalité ligne `i` est au "quasi-barycentre" de l'ensemble des modalités colonnes, **pondérées par le profil ligne**. Et réciproquement.

### Conséquence : la représentation superposée
Comme les deux ajustements partagent les mêmes axes, on peut **superposer** les deux nuages sur le même graphique. C'est ce qu'on appelle le **plan factoriel AFC**.

⚠️ **Attention** : on ne lit pas directement les distances ligne-colonne. On lit :
- les **proximités entre lignes** (départements similaires)
- les **proximités entre colonnes** (candidats similaires)
- les **directions** : une ligne et une colonne dans la même direction → attirance
- les **directions opposées** → répulsion

---

## 8. Interprétation des résultats

### 8.1 Inertie totale
```
I(N_I) = I(N_J) = D² / n
```
- Plus l'inertie est élevée, plus les **profils sont différents** et plus le **lien de dépendance est fort**.
- L'inertie totale est égale à `D²/n` (lien direct avec le test du χ²).

### 8.2 Nombre d'axes
```
Nombre d'axes AFC = min(I − 1, J − 1)
```
(différent de l'ACP qui donne `min(I, J)`).

### 8.3 Inertie maximale par axe
**Propriété importante** : `λ_k ≤ 1` (toutes les valeurs propres sont entre 0 et 1).

Cas extrême `λ_k = 1` : les modalités lignes et colonnes sont parfaitement **partitionnées en deux sous-ensembles qui s'opposent** le long de l'axe.

### 8.4 Critères pour le choix du nombre d'axes
- **Critère de Kaiser** : retenir les axes dont `λ_k > inertie moyenne`
- **Scree-test de Cattell** : chercher le **coude**
- **Critère incontournable** : la possibilité d'**interpréter** les dimensions !

### 8.5 Contributions
**Contribution d'une modalité (ligne ou colonne) i à l'axe k** :
```
CTR_k(i) = (m_i × c_ik²) / λ_k
```
⚠️ **Attention** : l'individu le **plus éloigné** sur un axe n'a **pas nécessairement** la plus forte contribution → il faut tenir compte de la **masse** !

### 8.6 Qualité de représentation (cos²)
Même définition qu'en ACP. Mesure la **proximité au plan**.

### 8.7 Attirance / répulsion en lecture graphique
- Une modalité ligne est principalement « **attirée** » par les modalités colonnes situées dans **sa direction** (loin du centre).
- Elle est « **repoussée** » par celles en direction opposée.

---

## 9. L'effet Guttman (piège à connaître)

### Situation
Quand le tableau de contingence a une **structure diagonale** (« scalogramme ») : les valeurs élevées sont sur une bande diagonale, et 0 ailleurs. Cela arrive quand les variables ont un **ordre naturel**.

### Symptôme
Sur le plan (1, 2), on observe un **effet « parabole »** (en U). Le facteur de rang `s` est mathématiquement un **polynôme de degré s** du premier facteur.

### Conséquence pour le rapport
Si on voit une parabole nette sur le plan (1, 2), c'est probablement un effet Guttman :
- Le tableau a une structure d'ordre
- L'axe 2 n'apporte **aucune information supplémentaire** par rapport à l'axe 1
- On peut interpréter uniquement l'axe 1

### Quand ça apparaît
- Variables dont les modalités présentent un ordre naturel
- Variables quantitatives découpées en classes (catégories d'âge, tranches de revenu...)

---

## 10. Mise en œuvre R (cours)

### Package FactoMineR
```r
# Importer les données
president12 <- read.table(...)
row.names(president12) <- as.character(president12$Departement)

# Sélectionner les lignes et colonnes actives
president12.CA <- president12[1:96, 2:11]

# Lancer l'AFC
res <- CA(president12.CA, ncp = 5,
          row.sup = NULL, col.sup = NULL,
          graph = FALSE)

# Représentation superposée
plot.CA(res, axes = c(1, 2), col.row = "red", col.col = "blue")
```

### Résultats accessibles via `res$`
- `res$eig` → valeurs propres et inertie par axe
- `res$row$coord` → coordonnées des lignes
- `res$row$contrib` → contributions des lignes
- `res$row$cos2` → qualités de représentation
- `res$col$coord`, `res$col$contrib`, `res$col$cos2` → idem pour colonnes
- `res$row.sup`, `res$col.sup` → modalités supplémentaires

### Visualisations factoextra
```r
fviz_eig(res, addlabels = TRUE)         # éboulis
fviz_ca_biplot(res, pointsize = "cos2") # biplot avec cos²
fviz_contrib(res, choice = "row", axe = 1)
fviz_contrib(res, choice = "col", axe = 1)
```

### Diagnostic du χ²
```r
res.chi <- chisq.test(tableau)
res.chi$expected   # effectifs théoriques t_ij
res.chi$residuals  # résidus standardisés
res.chi$stdres     # résidus ajustés de Haberman
```

---

## 11. Synthèse d'usage pour le projet TradingMonitor

### Notations à reprendre dans le rapport
- Utiliser `t_ij` pour les effectifs théoriques (au lieu de `E_ij`)
- Utiliser `r_ij` pour les résidus ajustés de Haberman (au lieu de "résidus standardisés")
- Citer la **distance du χ²** explicitement (pas la distance euclidienne)
- Parler de **profils lignes / profils colonnes** (pas de "fréquences relatives")

### Méthodes du cours pas encore exploitées dans le projet
- ✅ **Résidus ajustés de Haberman** : pour quantifier finement les attirances/répulsions entre stratégies × régimes ou stratégies × secteurs (au lieu du seul χ²)
- ✅ **Principe d'équivalence distributionnelle** : justifie le regroupement de modalités similaires
- ✅ **Diagnostic effet Guttman** : si on observe une parabole, il faut le signaler
- ✅ **Mention du critère « possibilité d'interpréter »** pour le choix du nombre d'axes

### Pour le rapport — phrases à utiliser
> *« L'AFC est ici l'outil graphique qui visualise la structure du lien détecté par le χ² (cours Périnel, M1 Stat Strasbourg). »*

> *« La distance du χ² utilisée en AFC revalorise les colonnes de faible effectif (propriété d'équivalence distributionnelle). »*

> *« Le résidu ajusté de Haberman r_ij = (n_ij − t_ij) / √(t_ij × (1 − f_i)(1 − f_j)) permet de tester localement la significativité de chaque attirance/répulsion à 5 % (|r_ij| > 1.96). »*

> *« Les relations quasi-barycentriques (formules de transition) permettent l'interprétation simultanée des deux nuages superposés sur le même plan factoriel. »*
