# Synthèse — Cours ACM (Périnel, Strasbourg M1 2024-25)

> Cours complet de 59 pages lu et résumé.

---

## 1. Cadrage général

**Enseignant** : Emmanuel Périnel
**Niveau** : Master 1 Statistique / DUAS, Strasbourg
**Famille** : analyses factorielles (généralisation de l'AFC à N variables qualitatives)
**Logiciel** : R + package **FactoMineR** (fonction `MCA`) + factoextra

### Différence avec l'ACP et l'AFC
| ACP | AFC | ACM |
|---|---|---|
| individus × variables QUANTITATIVES | tableau de contingence (2 variables QUALITATIVES) | individus × **plusieurs** variables QUALITATIVES |
| matrice X^t X | tableau résidus standardisés | **Tableau Disjonctif Complet (TDC)** |
| moyennes, écarts-types | profils, masses | profils + **modalités** au cœur |

### Idée fondatrice
> **L'ACM est une AFC appliquée au Tableau Disjonctif Complet (TDC).**

---

## 2. Notations

| Symbole | Signification |
|---|---|
| `I` | nombre d'individus |
| `J` | nombre de variables qualitatives actives |
| `K_j` | nombre de modalités de la variable j |
| `K = Σ K_j` | nombre total de modalités |
| `x_ik` | élément du TDC : 1 si l'individu i prend la modalité k, 0 sinon |
| `I_k` | nombre d'individus possédant la modalité k |
| `I_kh` | nombre d'individus possédant **les deux** modalités k et h |
| `m_i = 1/I` | masse de l'individu i (en général uniforme) |
| `m_k = I_k / (I × J)` | masse de la modalité k |
| `λ_s` | s-ème valeur propre = inertie de l'axe s |
| `F_s(i)` | coordonnée de l'individu i sur l'axe s |
| `G_s(k)` | coordonnée de la modalité k sur l'axe s |
| `η²(j, C_s)` | rapport de corrélation entre variable j et axe s |

---

## 3. Le tableau analysé : le TDC

### Tableau Disjonctif Complet
Le tableau de données initial avec **codage condensé** (1 colonne par variable) est transformé en **codage binaire 0/1** (1 colonne par modalité).

**Exemple** :
```
CODAGE CONDENSÉ              CODAGE BINAIRE (TDC)
Tactile  Focale.min          Tactile_oui Tactile_non  Foc<25  Foc>27
oui      >27           →     1           0            0       1
non      <25           →     0           1            1       0
```

**Propriété** : exactement **J cases à 1** par ligne (autant que de variables).
Chaque ligne somme à `J`. Chaque colonne k somme à `I_k`.

### Choix des variables et recodage préalable
- **Variables actives** : qualitatives (sinon recodage en classes)
- **Variables illustratives (supplémentaires)** : qualitatives ET/OU quantitatives
- **Modalités rares** (effectif < 2% du total) à recoder en amont :
  1. Regrouper avec modalités voisines (si possible)
  2. Remplacer par modalité au hasard
  3. Substituer par la valeur modale (la plus fréquente)
- **Tris à plat** avant ACM pour identifier les modalités à recoder

### Pourquoi recoder les modalités rares ?
> Une modalité rare joue souvent un **rôle prédominant** en ACM : elle attire les axes factoriels artificiellement. Certains axes risquent d'être engendrés uniquement par ces modalités.

---

## 4. Les deux nuages de profils

### Masses
- **Masse d'un individu** : `m_i = 1/I` (uniforme)
- **Masse d'une modalité** : `m_k = I_k / (I × J)` (proportionnelle à sa fréquence)

### Profils
- **Profil ligne i** : `(x_ik / J)_{k=1..K}` (somme à 1)
- **Profil colonne k** : `(x_ik / I_k)_{i=1..I}` (somme à 1)

---

## 5. Distances utilisées (du χ²)

### Distance entre deux individus
```
d²_χ²(i, l) = (1/J) × Σ_k (I / I_k) × (x_ik − x_lk)²
```

**Lecture** :
- Deux individus sont d'autant **plus proches** qu'ils possèdent **un grand nombre de modalités en commun**
- Une **modalité rare** (petit `I_k`) **éloigne** son possesseur de tous les autres (le facteur `I/I_k` est grand)

### Distance entre deux modalités
```
d²_χ²(k, h) = (I / (I_k × I_h)) × (I_k + I_h − 2·I_kh)
```

**Lecture** :
- Deux modalités sont d'autant **plus distantes** qu'elles ont été **choisies simultanément** par un **petit nombre** d'individus (faible `I_kh`)
- Deux modalités souvent choisies ensemble sont proches

---

## 6. Axes factoriels et inerties

### Nombre d'axes
```
Nombre d'axes ACM = K − J
```
où `K = Σ K_j` (total modalités) et `J` = nombre de variables.

### Inertie totale
```
I(N_K) = I(N_I) = K/J − 1
```
Égale pour les deux nuages (propriété d'AFC).

### Inertie d'une variable
```
I(j) = (1/J) × (K_j − 1)
```
**Conséquence** : une variable avec **beaucoup de modalités** apporte plus d'inertie → attention à ne pas créer artificiellement de l'inertie en sur-découpant.

### Inertie d'une modalité
```
I(k) = (1/J) × (I − I_k) / I
```
**Lecture** : une modalité **rare** (`I_k` petit) apporte beaucoup d'inertie → encore une raison de recoder les modalités rares.

### Inertie moyenne par axe
```
Inertie moyenne = 1/J
```

### Faibles taux d'inertie en ACM
> Contrairement à l'ACP/AFC, en ACM les % d'inertie sont **mécaniquement faibles** (souvent 10-30% pour le premier axe). C'est une propriété connue → on ne lit **pas** les % comme en ACP.

### Correction de Benzecri (et Greenacre)
Pour ajuster les % d'inertie et obtenir des valeurs plus interprétables :
```
λ* = (J / (J−1))² × (λ − 1/J)²
```
On ne retient que les axes dont `λ > 1/J` (= inertie moyenne).

**Exemple R** :
```r
a = 1
vp.benz = 0
K = length(res$eig[,1])
J = length(res$var$eta2[,1])
for (i in 1:K) {
  if (res$eig[i,1] > 1/J) {
    vp.benz[a] = ((J/(J-1)) * (res$eig[i,1] - 1/J))^2
    a = a + 1
  }
}
```

---

## 7. Interprétation des résultats

### 7.1 Éloignement / proximité au centre de gravité

**Centre de gravité des individus** `G_I` : barycentre du nuage des individus.
**Centre de gravité des modalités** `G_K` : barycentre du nuage des modalités.

**Lecture cruciale** :

| Position | Lecture (modalité) | Lecture (individu) |
|---|---|---|
| **Proche du centre** | Modalité **fréquente** (souvent choisie) | Individu prenant des modalités **fréquentes** |
| **Loin du centre** | Modalité **rare** (peu choisie) | Individu prenant des modalités **rares** |

**Formules** :
```
d²_χ²(k, G_K) = (I/I_k) − 1
d²_χ²(i, G_I) = (1/J) × Σ_k (x_ik/I_k) − 1
```

### 7.2 Relations quasi-barycentriques (formules de transition)

```
G_s(k) = (1/√λ_s) × Σ_i (x_ik / I_k) × F_s(i)
F_s(i) = (1/√λ_s) × Σ_k (x_ik / J) × G_s(k)
```

**Interprétation** :
- *« Une modalité est au quasi-barycentre des individus qui la possèdent »*
- *« Un individu est au quasi-barycentre des modalités qu'il possède »*

Le facteur `1/√λ_s` est un **facteur de dilatation** : sans lui ce serait un vrai barycentre, mais avec, les modalités sont éloignées du barycentre exact.

### 7.3 Représentation simultanée
Comme en AFC, on **superpose** les deux nuages (modalités + individus) sur le même plan factoriel. On lit :
- proximités modalité × modalité → modalités souvent choisies ensemble
- proximités individu × modalité → modalité caractéristique de cet individu
- ⚠️ Attention : ne pas lire les distances directes individu × modalité (mêmes précautions qu'en AFC)

### 7.4 Variables illustratives
- **Quantitatives** : projetées sur un cercle des corrélations (comme en ACP)
- **Qualitatives** : chaque modalité projetée comme barycentre des individus la possédant
- Aides : `$quanti.sup$coord`, `$quali.sup$coord`, `$quali.sup$cos2`

---

## 8. La représentation graphique des variables (importante)

### Coordonnée d'une variable sur un axe = intensité de la liaison
```
η²(j, C_s)
```
où `C_s` est la composante principale associée à l'axe s.

### Rapport de corrélation η²
- Mesure de liaison entre **variable qualitative** et **variable quantitative** (ici, la composante principale)
- `η² ∈ [0, 1]`
- Lien avec la décomposition de la variance (ANOVA à 1 facteur) :
  ```
  η² = V.Inter / V.Totale = V.Inter / (V.Inter + V.Intra)
  ```

### Interprétation visuelle
La liaison est d'autant plus intense que la variable forme des sous-populations :
- **homogènes** (faible V.Intra)
- **bien séparées** le long de l'axe (forte V.Inter)

### Propriétés
```
η²(j, C_s) = J × Σ_k I_s(k)
I_s (inertie axe s) = (1/J) × Σ_j η²(j, C_s)
```

**Conséquence** : une variable dont les **modalités apportent beaucoup d'inertie** à un axe est **fortement liée** à cet axe.

---

## 9. L'effet Guttman en ACM

### Symptôme
Apparition d'une **parabole** ou structure en U sur le plan (1, 2). Les deux facteurs sont alors liés mathématiquement :
- **Facteur 1** : facteur d'échelle (« effet taille »)
- **Facteur 2** : opposition extrêmes / moyens (polynôme degré 2 du facteur 1)

### Quand ça apparaît
- Modalités ayant un **ordre naturel** (échelles d'opinion type Likert)
- Variables quantitatives **mises en classes**

### Décision
Si on observe un effet Guttman :
- Le facteur 2 n'apporte **aucune information supplémentaire** → on interprète uniquement le facteur 1
- Le tableau a une structure d'ordre forte sur les lignes ET les colonnes

---

## 10. ACM et étude de liaisons non linéaires

### Cas d'usage très intéressant
> Quand deux variables **quantitatives** sont **non corrélées linéairement** (r ≈ 0) mais **non indépendantes**, l'ACP ne le voit pas. Mais en **découpant en classes** et en faisant une ACM, on révèle le lien.

### Exemple du cours
**Variables** : Sucre (quantité) et Hedo (note hédonique).
- ACP : corrélation linéaire ≈ 0 (les variables semblent indépendantes)
- ACM (après recodage en classes) : on voit clairement les associations (peu sucré + pas bon, moyennement sucré + bon, trop sucré + pas bon).

### Application pour ton projet TradingMonitor
**Très utile** : si tu détectes des **non-corrélations** linéaires entre indicateurs techniques, tu peux faire une ACM sur leurs classes pour révéler les liens non linéaires.

---

## 11. Mise en œuvre R (cours)

### Package FactoMineR
```r
# Recoder les variables quantitatives en classes
# (manuellement ou via fonction de discrétisation)

# Lancer l'ACM
res <- MCA(photo.MCA,
           ncp = 5,
           ind.sup = NULL,
           quanti.sup = 9:12,    # variables quanti illustratives
           quali.sup = 13:14,    # variables quali illustratives
           graph = FALSE)
```

### Résultats accessibles via `res$`
```
res$eig                    → valeurs propres et % inertie
res$ind$coord              → coordonnées individus
res$ind$contrib            → contributions individus
res$ind$cos2               → qualités représentation
res$var$coord              → coordonnées modalités
res$var$contrib            → contributions modalités
res$var$cos2               → qualités représentation modalités
res$var$eta2               → rapports de corrélation η² (variables × axes)
res$quanti.sup$coord       → coords variables quanti illust.
res$quali.sup$coord        → coords modalités quali illust.
```

### Visualisations
```r
plot.MCA(res, axes = c(1, 2), habillage = 14)  # avec coloration par groupe
plotellipses(res, keepvar = c("Type", "Tactile"), level = 0.95)
fviz_mca_ind(res, col.ind = "cos2", select.ind = list(cos2 = 0.5))
fviz_mca_var(res, col.var = "cos2", select.var = list(contrib = 10))
fviz_contrib(res, choice = "var", axes = 1)
```

---

## 12. Synthèse d'usage pour le projet TradingMonitor

### Notations à reprendre dans le rapport
- Utiliser `K`, `J`, `K_j`, `I_k`, `I_kh` pour les notations ACM
- Citer la **distance du χ²** spécifique à l'ACM (avec le facteur `I/I_k`)
- Parler du **TDC** explicitement (le concept clé)
- Mentionner `η²` (rapport de corrélation) au lieu de "corrélation" pour les liaisons qualitatif × axe
- Préciser **correction de Benzecri** si on commente les % d'inertie (cours p. 28)

### Méthodes du cours déjà utilisées dans le projet
- ✅ ACM dans l'étape 6 du Bloc 1 (sur `strategy + regime_entry + sector + win`)

### Méthodes du cours pas encore exploitées
- ✅ **Tris à plat préalables** : vérifier qu'il n'y a pas de modalités rares avant ACM
- ✅ **Recodage des modalités rares** (si trouvées, regrouper ou substituer)
- ✅ **Correction de Benzecri** sur les inerties (à mentionner dans le rapport pour justifier que les % bas sont normaux)
- ✅ **Rapport de corrélation η²** comme métrique principale au lieu des seules positions sur la carte
- ✅ **Variables illustratives** : `regime`, `secteur` pourraient être projetés en illustratifs au lieu d'être actifs (à discuter selon la question posée)
- ✅ **Ellipses de confiance** sur les modalités (`plotellipses`) — beaucoup plus visuel pour le rapport
- ✅ **ACM pour liaisons non linéaires** : si certaines paires d'indicateurs techniques semblent indépendantes (corrélation ≈ 0) en ACP, refaire une ACM sur leurs classes peut révéler des liens.

### Pour le rapport — phrases à utiliser
> *« L'ACM est une AFC appliquée au Tableau Disjonctif Complet (TDC), où chaque variable qualitative est explosée en autant de colonnes binaires que de modalités (cours Périnel, M1 Stat Strasbourg, p. 16-18). »*

> *« Les pourcentages d'inertie sont mécaniquement faibles en ACM (propriété connue, voir cours p. 27). On utilise la correction de Benzecri pour obtenir des taux ajustés interprétables. »*

> *« Le rapport de corrélation η²(j, C_s) ∈ [0, 1] mesure l'intensité de la liaison entre une variable qualitative et un axe factoriel. Il correspond à la part de variabilité INTER sous-populations dans la variabilité totale, comme en ANOVA à 1 facteur. »*

> *« Un effet Guttman (structure en U sur le plan factoriel) indique un ordre naturel sur les modalités — le facteur 2 n'apporte alors aucune information supplémentaire au-delà du facteur 1. »*
