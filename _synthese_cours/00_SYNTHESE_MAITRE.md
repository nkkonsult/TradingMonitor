# Synthèse maître des cours de l'utilisateur

> **But du fichier.** Tout ce qui est important à retenir de chaque cours, de façon à ne plus avoir à rouvrir les PDF. Lue à chaque session Claude Code pour calibrer les explications avec **les notations exactes** du cours et identifier les **méthodes connues / non connues**.
>
> **Tenu à jour par Claude au fil des lectures.** Voir aussi `01_acp.md`, `02_afc.md`, etc. pour le détail par cours.
>
> 🎯 **VOIR AUSSI** : [99_SYNTHESE_FINALE.md](99_SYNTHESE_FINALE.md) — bilan final de toutes les méthodes utilisables dans le projet et celles à introduire.

---

## 🎓 Contexte académique global

- **Master 1 Statistique / DUAS**, Université de Strasbourg
- **Année 2024-25**
- Approche : statistique appliquée, équilibre théorie / pratique R

---

## 📚 Cours étudiés (et leur état de lecture par Claude)

| # | Cours | Enseignant | Lu | Synthèse |
|---|---|---|---|---|
| 1 | Analyses des données — ACP | Emmanuel Périnel | ✅ fait (143 pages) | [01_acp.md](01_acp.md) |
| 1bis | Analyses des données — AFC | Emmanuel Périnel | ✅ fait (62 pages) | [02_afc.md](02_afc.md) |
| 1ter | Analyses des données — ACM | Emmanuel Périnel | ✅ fait (59 pages) | [03_acm.md](03_acm.md) |
| 2 | Apprentissage stat — Linéaire pénalisé (Ridge/Lasso/Elastic-Net/Group-Lasso) | M1 Strasbourg | ✅ fait (23 pages) | [04_apprentissage_lineaire_penalise.md](04_apprentissage_lineaire_penalise.md) |
| 2a | Apprentissage stat — Introduction (sur-apprentissage, CV, ROC, métriques) | Chevallier & Birmelé | ✅ fait (35 pages) | [05_apprentissage_introduction.md](05_apprentissage_introduction.md) |
| 2c | Apprentissage stat — kNN et SVM | M1 Strasbourg | ✅ fait (13 pages) | [06_knn_svm.md](06_knn_svm.md) |
| 2d | Apprentissage stat — Arbres / Random Forest / Gradient Boosting | Chevallier & Birmelé | ✅ fait (19 pages) | [07_arbres_foret_boosting.md](07_arbres_foret_boosting.md) |
| 2e | Apprentissage stat — UMAP (réduction non linéaire) | Chevallier & Birmelé | ✅ fait (18 pages) | [08_umap.md](08_umap.md) |
| 2f | Apprentissage stat — Mesures d'importance (Permutation, Sobol, Shapley) | Birmelé | ✅ fait (6 pages) | [09_importance_variables.md](09_importance_variables.md) |
| 3 | Séries temporelles S2 | Davide Giraudo | ✅ fait (30 pages) | [10_series_temporelles.md](10_series_temporelles.md) |
| 4 | Stat avec R (lm, tests, clustering) | Augustin Chevallier | ✅ fait (20 slides) | [11_statistique_avec_R.md](11_statistique_avec_R.md) |
| 4a | R for Data Science (intro / transform / visualize / tidy / relational) | Hadley Wickham | ⏳ à lire (~5 PDFs) | _à venir si pertinent_ |
| 5 | Bases de données (Merise / MCD / MLD / SQL / DF / Normalisation) | E. Claeys | ✅ fait (5 PDFs principaux lus) | [12_bases_de_donnees.md](12_bases_de_donnees.md) |
| 6 | Théorie des sondages (Horvitz-Thompson, SAS, stratifié) | S. Maistre | ✅ fait partiel (~40 pages) — peu pertinent projet | [13_theorie_sondages.md](13_theorie_sondages.md) |

---

## 🛠️ Plateformes et outils utilisés en cours

(À mettre en avant dans le rapport pour montrer que ce qu'on fait dans TradingMonitor mobilise les outils vus en formation.)

| Outil | Cours | Usage |
|---|---|---|
| **R** | tous (sauf BDD) | Langage de stats principal |
| **FactoMineR** | Analyses des données | ACP, AFC, ACM |
| **ggplot2, ggtext** | Analyses des données | Visualisations |
| **SQL** | Bases de données | Requêtes, jointures, sous-requêtes |
| _(à compléter au fil des lectures)_ | | |

---

## 🗂️ Index des méthodes — statut de chacune

(✅ = vue en cours / 🆕 = nouvelle à introduire dans le rapport / 🔍 = vue partiellement)

### Tests d'hypothèse
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| Test de Student 1 échantillon | 🆕 (mais lien fort avec Welch) | _à confirmer dans cours tests_ | Bloc 1 étape 1 |
| Test de Student 2 échantillons (Welch) | ✅ | (mentionné par l'utilisateur) | — |
| Test de Wilcoxon (rangs signés) | 🆕 | — | Bloc 1 étape 1 |
| Shapiro-Wilk | 🆕 | — | Bloc 1 étape 1 |
| Correction de Bonferroni | 🆕 (mais lien avec Tukey) | — | Bloc 1 étape 1 |
| Test du χ² d'indépendance | ✅ | _à confirmer_ | Bloc 1 étape 3 |
| V de Cramer | 🆕 (extension du χ²) | — | Bloc 1 étape 3 |

### ANOVA
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| ANOVA 1 facteur | ✅ | _à confirmer_ | Bloc 1 étape 2 |
| Tukey HSD | ✅ | _à confirmer_ | Bloc 1 étape 2 |
| ANOVA 2 facteurs + interaction | 🆕 (extension naturelle) | — | Bloc 1 étape 2 |

### Analyse multivariée
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| **ACP** | ✅ | Périnel — Cours 1 | Bloc 1 étape 4 |
| **AFC** | ✅ | Périnel — Cours 2 | Bloc 1 étape 5 |
| **ACM** | ✅ | Périnel — Cours 3 | Bloc 1 étape 6 |
| **CAH** (classification ascendante hiérarchique) | ✅ | Périnel — mentionné | non utilisé pour l'instant 🔍 |
| **k-means** | ✅ | Périnel — mentionné | non utilisé pour l'instant 🔍 |
| **Critère de Kaiser** (sélection axes ACP) | ✅ | Périnel ACP §11 | non utilisé encore 🔍 |
| **Scree-test de Cattell** | ✅ | Périnel ACP §11 | non utilisé encore 🔍 |
| **Modèle du bâton brisé** | ✅ | Périnel ACP §11 | non utilisé encore 🔍 |
| **cos²** (qualité de représentation) | ✅ | Périnel ACP §10 | utilisable Bloc 1 étape 4 |
| **Contribution (CTR)** | ✅ | Périnel ACP §10 | utilisable Bloc 1 étape 4 |
| **Variables illustratives** | ✅ | Périnel ACP §12 | **utilisable Bloc 1 étape 4** (régime/secteur en illustratifs) |
| **V.Test** | ✅ | Périnel ACP §12 | utilisable pour ACP/AFC/ACM |
| **η² (rapport corrélation)** | ✅ | Périnel ACP §12 | utilisable pour quali×axe |
| **Biplot** | ✅ | Périnel ACP | utilisable visualisation |

### Machine learning / classification
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| Random Forest | ✅ | Apprentissage stat | non |
| SVM | ✅ | Apprentissage stat | non |
| kNN | ✅ | Apprentissage stat | non |
| UMAP | ✅ | Apprentissage stat | non |
| Décomposition de Fourier, B-spline | ✅ | Apprentissage stat | non |
| **Régression linéaire pénalisée (Lasso, Ridge)** | ✅ | Apprentissage stat — `LineairePenalise.pdf` | **prévue Bloc final (option B+)** |

### Séries temporelles
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| ACF / PACF | ✅ | Séries temporelles | Bloc 3 étape 4 (ARIMA) |
| Tests de stationnarité (ADF) | ✅ | Séries temporelles | Bloc 3 étape 4 |
| Différenciation simple et saisonnière | ✅ | Séries temporelles | _potentiel pour Bloc 3 robustesse_ |
| SARIMA | ✅ | Séries temporelles | _ARIMA simple utilisé, SARIMA pas encore_ |
| Causalité de Granger | _à confirmer_ | _peut-être dans séries temp_ | Bloc 3 étape 2 |
| Simulation Monte Carlo + IC | ✅ | Séries temporelles | non encore |

### Bases de données
| Méthode | Statut | Cours référence | Utilisée dans projet |
|---|---|---|---|
| Modélisation MCD / MLD | ✅ | BDD | _potentiel pour Bloc 2 (architecture events)_ |
| SQL : jointures, sous-requêtes, agrégations | ✅ | BDD | SQLite déjà utilisé (results.db, snapshots.db) |
| Clés primaires / étrangères | ✅ | BDD | utilisé dans schéma SQLite |
| Sélection (SELECT) | ✅ | BDD | partout |
| Dépendances fonctionnelles, formes normales | ✅ | BDD — `Cours DP FN v3.pdf` | non utilisé encore |

### Théorie des sondages
(à compléter)

---

## 💡 Méthodes que l'utilisateur a vues en cours et qu'on POURRAIT mobiliser dans le projet

(À chaque méthode, je note : où elle pourrait servir + intérêt méthodologique pour le rapport)

| Méthode | Où la mobiliser | Intérêt pour le rapport |
|---|---|---|
| **Classification CAH / k-means** | Sur les trades (Bloc 1) ou sur les actions (Bloc 3) | "j'ai utilisé la classification vue en cours pour grouper les trades par profil" |
| **Variables illustratives en ACP** | Bloc 1 étape 4 (ACP des trades) | Projeter `regime`, `secteur`, `win` en illustratifs — montre une compétence avancée du cours non encore exploitée |
| **V.Test sur modalités illustratives** | Bloc 1 étapes 4-6 | Quantifier proprement la liaison qualitatif × axe (au lieu du χ² seul) |
| **Critère de Kaiser + Scree-test** | Toute ACP du projet | Justifier rigoureusement le nombre d'axes retenus (au lieu de prendre 2 par défaut) |
| **Biplot** | Bloc 1 étape 4 | Représentation simultanée individus + variables, plus élégante |
| **Random Forest** | Bloc final, comme alternative non-linéaire à la régression Lasso | Comparaison méthodes paramétriques vs non-paramétriques |
| **SARIMA** | Bloc 3 (extension de l'ARIMA déjà fait) | Plus rigoureux : prendre en compte la saisonnalité |
| **Simulation Monte Carlo** | Bloc 3 ou Bloc final (intervalles de confiance sur les prévisions) | "j'ai utilisé MC vu en séries temp pour quantifier l'incertitude" |
| **Modélisation MCD/MLD** | Bloc 2 (architecture base events normalisée) | Démontrer compétence BDD au-delà du code |
| **UMAP** | Bloc 1 (alternative non-linéaire à l'ACP) | "j'ai comparé ACP linéaire et UMAP non-linéaire" |
| **B-spline** | Bloc 3 (lissage des séries de prix) | Méthode élégante pour visualiser les tendances |

---

## ❌ Méthodes que je voudrais utiliser dans le projet et qui ne sont PAS vues en cours

(À surveiller : il faudra peut-être les introduire avec plus de pédagogie dans le rapport, ou trouver une alternative vue en cours.)

| Méthode | Où je voudrais l'utiliser | Alternative possible vue en cours |
|---|---|---|
| Test de Wilcoxon | Bloc 1 étape 1 (déjà fait) | _pas d'équivalent direct_ |
| Shapiro-Wilk | Bloc 1 étape 1 (déjà fait) | _pas d'équivalent direct_ |
| Correction de Bonferroni | Bloc 1 étape 1 (déjà fait) | Tukey HSD (autre philo mais même problème) |
| ANOVA 2 facteurs avec interaction | Bloc 1 étape 2 (déjà fait) | _extension naturelle de l'ANOVA 1 facteur_ |
| V de Cramer | Bloc 1 étape 3 (déjà fait) | _extension naturelle du χ²_ |
| Test de Diebold-Mariano | Bloc 3 robustesse (prévu) | _à voir si vu en séries temp_ |
| Bootstrap | Bloc 1 robustesse (prévu) | _peut-être lien avec MC vu en séries temp_ |
| Walk-forward validation | Bloc 1 robustesse (prévu) | _à voir si vu en apprentissage stat_ |
| Newey-West standard errors | Bloc final | _à voir_ |
| Lasso (régression L1) | Bloc final | ✅ vu dans `LineairePenalise.pdf` |

---

## 📐 NOTATIONS — convention par méthode (à utiliser dans le rapport)

(Toutes ces notations viennent directement des cours de l'utilisateur — à respecter dans le rapport pour cohérence.)

### ACP (cours Périnel — voir 01_acp.md pour détail complet)
- `X` : matrice de données `(n, p)`
- `n` : nombre d'individus, `p` : nombre de variables
- `x_ij` : valeur de l'individu `i` sur la variable `j`
- `x_i` : vecteur d'un individu
- `X_j` : vecteur d'une variable
- `G = (x̄_1, ..., x̄_p)` : centre de gravité
- `m_i` : masse de l'individu i (généralement 1/n)
- `d²(i, l) = Σ_{j=1}^p (x_ij − x_lj)²` : distance euclidienne
- `I = Σ_i m_i · d²(G, i) = Σ_j V(X_j)` : **inertie totale** (= variance multidim)
- `λ_k` = valeur propre = inertie de l'axe k
- `c_ik` = coordonnée de l'individu `i` sur l'axe `k`
- `d_jk` = coordonnée de la variable `j` sur l'axe `k` (= r(X_j, axe k) en ACP normée)
- `H_i` = projection orthogonale de l'individu sur le plan factoriel
- `CP_k` = composante principale de rang k
- **Centrage systématique** : `x_ij → x_ij − x̄_j` (G → O)
- **Réduction** (= ACP normée) : `x_ij → (x_ij − x̄_j) / s_j` — obligatoire si unités différentes

**Concepts importants vus en cours et utilisables dans le rapport** :
- ACP normée vs non normée
- Critère de Kaiser (λ_k > 1) pour sélectionner les axes
- Scree-test de Cattell (coude dans éboulis)
- Modèle du bâton brisé (Frontier 1976)
- cos² = qualité de représentation
- CTR = contribution (effet levier sur l'éloignement²)
- Variables illustratives (= supplémentaires) quanti/quali
- V.Test (|V.Test| > 1.96 ⇔ p-value < 5%) pour modalités illustratives
- η² = rapport de corrélation pour la force de liaison qualitative×axe
- Biplot (représentation simultanée individus + variables)

### AFC (à compléter)
### ACM (à compléter)
### Tests d'hypothèse (à compléter)
### ANOVA (à compléter)
### Régression linéaire pénalisée (à compléter avec Lasso/Ridge)
### Séries temporelles (à compléter avec SARIMA)

---

## 📖 Références bibliographiques citées dans les cours

(À reprendre dans la bibliographie du rapport pour ancrer les méthodes dans la littérature académique vue en cours.)

### Analyses des données (Périnel)
- Bouroche J.M. et Saporta G. (1980). *L'analyse des données*, PUF, Collection Que sais-je ?
- Cornillon P.A. et al. (2008). *Statistiques avec R*, Presses Universitaires de Rennes
- Escofier B. et Pagès J. (2008). *Analyses factorielles simples et multiples*, 4e éd., Dunod
- Husson F., Lê S. et Pagès J. (2009). *Analyse de données avec R*, Presses Universitaires de Rennes
- Lebart L., Morineau A. et Piron M. (2006). *Statistique exploratoire multidimensionnelle*, Dunod
- Saporta G. (2006). *Probabilités, analyses des données et statistiques*, 2e éd., Technip

### (autres cours à compléter au fil de la lecture)
