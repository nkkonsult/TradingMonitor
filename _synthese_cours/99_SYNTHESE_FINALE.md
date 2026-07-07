---
name: 99-synthese-finale
description: Synthèse FINALE — bilan des 12 cours lus, méthodes utilisables dans le projet TradingMonitor, méthodes manquantes à introduire, recommandations pour le rapport
metadata:
  type: project
---

# 🎯 Synthèse FINALE — toutes les armes du projet TradingMonitor

> Document final consolidant les 12 cours lus (M1 Statistique & DUAS, Strasbourg).
> Date : 2026-06-24.

## 📚 Couverture des cours

| # | Cours | Pages | Synthèse |
|---|---|---|---|
| 1 | ACP (Périnel) | 143 | [01_acp.md](01_acp.md) |
| 2 | AFC (Périnel) | 62 | [02_afc.md](02_afc.md) |
| 3 | ACM (Périnel) | 59 | [03_acm.md](03_acm.md) |
| 4 | Apprentissage — Linéaire pénalisé | 23 | [04_apprentissage_lineaire_penalise.md](04_apprentissage_lineaire_penalise.md) |
| 5 | Apprentissage — Introduction | 35 | [05_apprentissage_introduction.md](05_apprentissage_introduction.md) |
| 6 | Apprentissage — kNN & SVM | 13 | [06_knn_svm.md](06_knn_svm.md) |
| 7 | Apprentissage — Arbres / RF / GB | 19 | [07_arbres_foret_boosting.md](07_arbres_foret_boosting.md) |
| 8 | Apprentissage — UMAP | 18 | [08_umap.md](08_umap.md) |
| 9 | Apprentissage — Importance des variables | 6 | [09_importance_variables.md](09_importance_variables.md) |
| 10 | Séries temporelles (Giraudo) | 30 | [10_series_temporelles.md](10_series_temporelles.md) |
| 11 | Statistique avec R (Chevallier) | 20 slides | [11_statistique_avec_R.md](11_statistique_avec_R.md) |
| 12 | Bases de données (Claeys) | 5 PDFs | [12_bases_de_donnees.md](12_bases_de_donnees.md) |
| 13 | Théorie des sondages (Maistre) | ~40 / 150 | [13_theorie_sondages.md](13_theorie_sondages.md) |
| 14 | **Statistique avec SAS** (Poulin/Gardes) | 6 PDF ~240 | [14_statistique_avec_SAS.md](14_statistique_avec_SAS.md) |
| 15 | **Statistique avec Python** (Poulin) | 6 PDF ~270 + code | [15_statistique_avec_python.md](15_statistique_avec_python.md) |

**Total** : **~1170 pages** lues et synthétisées (15 cours).

> 🆕 **Ajout SAS + Python (2026-07-01)** : ces 2 cours **confirment comme "vues en cours"** la quasi-totalité des méthodes du Bloc 1 (Shapiro, Student/Welch, ANOVA 1 & 2 facteurs + interaction, Tukey, Bonferroni, χ²) — elles ne sont donc plus "à introduire". Nouveauté exploitable : **GLM généralisé / régression logistique** (`PROC GENMOD`) pour le Bloc final.

---

## ✅ Méthodes utilisables dans le projet — par bloc

### Bloc 1 — Stratégies techniques (test sur 38 035 trades S&P 500)

#### Étape 1 : Tests de significativité par stratégie
| Méthode | Statut cours | Notes |
|---|---|---|
| Test t Welch (1 et 2 échantillons) | ✅ **triple** | `PROC TTEST` (SAS) / `ttest_ind` (Python) / `t.test()` (R) |
| **Test de Wilcoxon** (rang signé) | ✅ R uniquement | `wilcox.test()` — **non vu** en SAS/Python |
| **Shapiro-Wilk** (normalité) | ✅ **confirmé SAS+Python+R** | `PROC UNIVARIATE NORMAL` / `stats.shapiro` / `shapiro.test()` — **cœur des cours normalité** |
| **Bonferroni** | ✅ **confirmé** | enseigné comme post-hoc (SAS + Python `method="bonf"`) |
| **Edge = return − rand_return** | ⭐ analogie estimateur de régression ([[13-theorie-sondages]]) | Neutralise biais marché haussier |

> ⭐ **3 tests de normalité bonus vus en SAS** (`PROC UNIVARIATE NORMAL`) : Kolmogorov-Smirnov, Anderson-Darling, Cramér-von Mises — à citer si besoin de robustesse.

#### Étape 2 : ANOVA + Tukey
- ✅ ANOVA 1 facteur — **confirmé SAS (`PROC ANOVA`/`GLM`) + Python (`ols`+`anova_lm(typ=2)`)**
- ✅ Tukey HSD — `means / TUKEY` (SAS), `MultiComparison().tukeyhsd()` (Python)
- ✅ **ANOVA 2 facteurs avec interaction — CONFIRMÉE vue en cours** (`model Y=A B A*B` en SAS) — n'est plus une "extension à introduire"
- ✅ Conditions : homoscédasticité Bartlett (SAS+Python) / Levene (Python) ; normalité des résidus (`model.resid` / `output r=residus`)

#### Étape 3 : χ² + V de Cramer
- ✅ χ² d'indépendance — **confirmé SAS (`PROC FREQ / CHISQ`) + Python (`chi2_contingency`)**
- 🆕 V de Cramer — **reste "à introduire" : NON couvert en SAS, Python NI R** (bien vérifié dans les 3 cours logiciels)
- ✅ bonus vus : correction de Yates, test exact de Fisher, G-test (SAS)

#### Étape 4 : ACP des trades
- ✅ ACP normée ([[01-acp]])
- ✅ Critère de Kaiser, Scree-test Cattell
- ✅ cos², CTR
- ✅ **Variables illustratives** (régime/secteur/win) — à exploiter !
- ✅ V.Test pour modalités illustratives
- ✅ Biplot

#### Étape 5 : AFC sur tableau de contingence
- ✅ AFC complète ([[02-afc]])
- ✅ Résidus de Haberman

#### Étape 6 : ACM
- ✅ ACM avec correction de Benzecri ([[03-acm]])
- ✅ η² rapport de corrélation

### Bloc 2 — Signaux d'information (n8n agents)
- 🆕 **Modélisation MCD/MLD** ([[12-bases-de-donnees]]) ⭐ — angle fort pour le rapport (entités GOUVERNEMENT, CONTRAT, NAICS, POLITICIEN, TRADE_INSIDER)
- 🆕 **Normalisation 3NF** pour éviter redondances
- ✅ **SQL** : SELECT, JOIN, GROUP BY pour agréger les signaux

### Bloc 3 — Relations inter-actions (sectorielles)
- ✅ ACP sectorielle (PC1 = 73% marché)
- ✅ ARIMA via pipeline 7 étapes ([[10-series-temporelles]]) : KPSS/DF → ACF/PACF → AIC → estimation → Box-Pierce
- ✅ Tests KPSS, Dickey-Fuller (stationnarité)
- ✅ Box-Pierce (validation résidus)
- 🆕 Causalité de Granger — **non explicitement dans le cours séries temp** !
- 🆕 SARIMA (extension saisonnalité)
- 🆕 GARCH (volatilité) — pas dans le cours

### Bloc final — Régression sur signaux validés

#### Architecture proposée — quadruple validation ⭐
1. **Lasso CV** ([[04-apprentissage-lineaire-penalise]]) → sélection (β = 0 ou non)
2. **Random Forest + OOB** ([[07-arbres-foret-boosting]]) → check non-linéaire, importance Gini
3. **Permutation importance** → robustesse
4. **Valeurs de Shapley** ([[09-importance-variables]]) ⭐ → arbitrage définitif (gère les variables corrélées)

#### Méthode décidée : **option B+**
- Porte B (filtre soft Spearman + FDR Benjamini-Hochberg p<0.20)
- Lasso CV + ~5-10 interactions ciblées
- Validation par **TimeSeriesSplit** (cf [[05-apprentissage-introduction]])

#### Choix de la méthode de régression
| Critère | Lasso | RF | SVM-RBF | Gradient Boosting | **GLM logistique** |
|---|---|---|---|---|---|
| Interprétable | ✅✅ | ✅ (importance) | ❌ | ⚠️ | ✅✅ (odds-ratios) |
| Non-linéaire | ❌ (sauf interactions) | ✅ | ✅✅ | ✅✅ | ❌ |
| Sur-apprentissage maîtrisé | ✅ (λ) | ✅ (bagging) | ⚠️ (C, γ) | ⚠️ (T, ν) | ✅ (VIF, sélection) |
| Recommandation projet | ⭐ Bloc final principal | Alternative non-linéaire (rapport) | Mention | Mention (XGBoost industrie) | **⭐ si cible = `win` 0/1** |

> 🆕 **Nouvelle carte (cours SAS `PROC GENMOD`)** : la **régression logistique** ([[14-statistique-avec-SAS]]) est directement pertinente si le Bloc final modélise **`win` (gagnant/perdant, binaire)** plutôt que `edge` (continu). Méthode paramétrique **interprétable** (coefficients = log-odds), avec sélection par **VIF + AIC/LRT** vue en cours. La **régression de Poisson** couvre le comptage d'événements (Bloc 2).

---

## 🆕 Méthodes MANQUANTES à introduire dans le rapport

(= je voulais les utiliser mais elles ne sont pas dans les cours suivis. Il faudra justifier leur usage en bibliographie.)

### Tests d'hypothèse (Bloc 1)
| Méthode | Pourquoi | Référence à citer |
|---|---|---|
| **Bootstrap** (Efron 1979) | Construire IC sans hypothèse paramétrique | Robustesse Bloc 1 |
| **Test de Diebold-Mariano** | Comparer performance prédictive de 2 stratégies | Bloc 3 robustesse |

### Séries temporelles (Bloc 3)
| Méthode | Pourquoi |
|---|---|
| **Causalité de Granger** | Tester si une série en prédit une autre |
| **VAR** (Vector AR) | Multi-séries (plusieurs indices à la fois) |
| **GARCH/ARCH** | Volatilité variable (très utile en finance) |
| **Cointégration** | Relations long-terme entre séries non stationnaires |
| **SARIMA** | Saisonnalité explicite |
| **Test de Ljung-Box** | Amélioration de Box-Pierce vu en cours |

### Apprentissage (Bloc final)
| Méthode | Pourquoi |
|---|---|
| **TimeSeriesSplit** sklearn | Validation croisée respectant l'ordre temporel |
| **Walk-forward analysis** | Standard du backtesting financier |
| **XGBoost / LightGBM / CatBoost** | Boosting industriel — vu cours = théorique seulement |
| **SHAP** (Lundberg & Lee 2017) | Implémentation efficace des Shapley values |
| **PaCMAP / TriMap** | Versions plus récentes de UMAP |
| **HDBSCAN** | Clustering hiérarchique sur projection UMAP |
| **Conformal prediction** | IC autour des prédictions RF |

### Métriques trading
| Méthode | Pourquoi |
|---|---|
| **Sharpe / Sortino / Calmar ratios** | Standards risk-adjusted performance |
| **Max drawdown** | Risque maximal |
| **Profit factor**, **Win rate** | Diagnostic stratégie |

---

## 🎯 Stratégies/méthodes à mobiliser EN PRIORITÉ dans le rapport

### TOP 5 atouts méthodologiques inattendus

1. **Valeurs de Shapley pour variables corrélées** ([[09-importance-variables]]) ⭐⭐
   > Cours rare, théorie des jeux, mathématiquement le bon choix quand les Xᵢ sont corrélées (cas du projet). **Différenciateur fort.**

2. **Group-Lasso pour architecture en blocs** ([[04-apprentissage-lineaire-penalise]]) ⭐
   > Au lieu de Lasso classique sur 30+ variables des 3 blocs, utiliser Group-Lasso pour **sélectionner par blocs entiers** ("le Bloc 2 entier participe ou pas"). Cohérent avec l'architecture.

3. **Pipeline ARIMA 7 étapes** ([[10-series-temporelles]])
   > Protocole rigoureux KPSS/DF → ACF/PACF → AIC → estimation innovations → validation Box-Pierce. **Légitimité méthodologique**.

4. **Variables illustratives en ACP** ([[01-acp]])
   > Projeter `regime`, `secteur`, `win` en illustratifs sur l'ACP des trades. Compétence avancée du cours non triviale.

5. **MCD/MLD du Bloc 2** ([[12-bases-de-donnees]])
   > Au lieu de "j'ai stocké en CSV", schéma Merise propre avec entités/cardinalités/clés étrangères. **Compétence BDD démontrée.**

### Quick wins faciles à ajouter
- `pam` (k-medoids robuste) au lieu de k-means ([[11-statistique-avec-R]]) — finance avec krachs
- Critère de Kaiser explicite ([[01-acp]]) — au lieu de prendre 2 axes par défaut
- Test de Box-Pierce sur résidus ARIMA ([[10-series-temporelles]]) — validation propre

---

## ⚠️ Pièges méthodologiques à éviter

### Erreur 1 : Validation croisée k-fold classique en séries temporelles ❌
- En séries temporelles, NE PAS utiliser `cv=5` standard ⇒ information du futur fuite
- ✅ Utiliser `TimeSeriesSplit` sklearn

### Erreur 2 : Prix bruts dans ARIMA ❌
- Les prix d'actions sont NON stationnaires
- ✅ Toujours travailler sur **rendements logarithmiques**

### Erreur 3 : Permutation importance avec variables corrélées ❌
- Sous-estime systématiquement quand X₁ et X₂ corrélés
- ✅ Utiliser **valeurs de Shapley** (cf cours [[09-importance-variables]])

### Erreur 4 : OOB error en séries temporelles ❌
- OOB suppose observations indépendantes
- Pas valide en finance (autocorrélation)
- ✅ Utiliser TimeSeriesSplit

### Erreur 5 : Clustering visuel UMAP comme conclusion ❌
- UMAP ne préserve ni distances ni densités
- ✅ Toujours valider avec k-means/CAH sur données originales

### Erreur 6 : Régression sur Y sans considérer le biais marché ❌
- Le S&P 500 monte sur 2020-2025 → toute stratégie d'achat semble gagner
- ✅ Concept d'**edge = return_net − rand_return** (déjà dans le projet)
- Voir analogie estimateur de régression ([[13-theorie-sondages]])

---

## 📐 Notations à respecter dans le rapport

(Pour cohérence avec les cours suivis — éviter dérive des notations.)

| Concept | Notation cours |
|---|---|
| Données | X = matrice (n, p) |
| Individu i | xᵢ vecteur ligne |
| Variable j | X_j vecteur colonne |
| Masse | mᵢ (= 1/n par défaut) |
| Inertie totale | I_total = Σⱼ V(X_j) |
| Valeur propre k | λ_k |
| Coord individu i sur axe k | c_ik |
| Composante principale | CP_k |
| Fonction de perte | L(y₁, y₂) |
| Risque empirique | R_emp(f) |
| Régularisation L2 (Ridge) | λ‖β‖²₂ |
| Régularisation L1 (Lasso) | λ‖β‖₁ |
| Auto-covariance | γ(h) |
| Auto-corrélation | ρ(h) |
| **Auto-corrélation partielle** | **τ(h)** |
| Innovation | εₜ |
| Indice de Sobol | Sᵢ, Sᵢᵗᵒᵗ |
| Valeur de Shapley | ηⱼ |

---

## 📖 Bibliographie consolidée (à intégrer au rapport)

### Analyses des données (Périnel)
- Saporta G. (2006). *Probabilités, analyses des données et statistiques*, Technip.
- Lebart, Morineau, Piron (2006). *Statistique exploratoire multidimensionnelle*, Dunod.
- Escofier, Pagès (2008). *Analyses factorielles simples et multiples*, Dunod.
- Husson, Lê, Pagès (2009). *Analyse de données avec R*, PUR.

### Apprentissage
- Codd E.F. (1970). Relational model.
- Shapley L. (1953). Théorie des jeux.
- Lundberg & Lee (2017). SHAP values — NeurIPS.
- Tibshirani (1996). Lasso — JRSS.
- Hoerl & Kennard (1970). Ridge regression.

### Séries temporelles
- Box & Jenkins (1970). *Time Series Analysis*.
- Hamilton (1994). *Time Series Analysis*.

### Bases de données
- Codd E.F. (1970). *A relational model of data for large shared data banks*.
- Merise — Tardieu (années 1970-80).

---

## ✅ Action items immédiats pour le projet

1. **Préserver les synthèses** : ces 13 fichiers sont versionnés dans `_synthese_cours/` et poussés sur git ⇒ accessibles sur les 2 PCs de l'utilisateur.
2. **Charger MEMORY.md** à chaque session : pointe vers ce fichier de synthèse finale.
3. **Bloc final** : passer de la décision "B+" théorique à l'implémentation avec :
   - `LassoCV(cv=TimeSeriesSplit(n_splits=5))`
   - Comparaison avec RandomForestRegressor (importance)
   - Calcul des Shapley values via librairie SHAP
4. **Bloc 3** : implémenter le pipeline ARIMA 7 étapes complet (actuellement partiel).
5. **Bloc 2** : formaliser le MCD/MLD des events government contracts.
6. **Walk-forward backtest** : à mettre en place (méthode standard absente des cours).

---

## 🏁 Conclusion

Le projet TradingMonitor mobilise les compétences vues en **8 cours de M1 Statistique/DUAS** :
- Analyses factorielles (ACP, AFC, ACM) → exploration des trades
- Apprentissage statistique (Linéaire pénalisé, RF, importance) → Bloc final
- Séries temporelles (ARIMA) → Bloc 3
- Stat avec R (tests, lm, clustering) → analyses
- **Statistique avec SAS** (UNIVARIATE, TTEST, ANOVA/GLM, REG, GENMOD, FREQ) → **valide tout le Bloc 1** + GLM logistique Bloc final
- **Statistique avec Python** (scipy.stats, statsmodels) → **langage exact du projet**, tests du Bloc 1 reproduits à l'identique
- Bases de données (Merise, SQL) → architecture
- Sondages (Horvitz-Thompson, estimateurs) → légitime le concept d'edge

**Aucune méthode utilisée n'est en dehors du cadre des cours** — toutes ont un appui pédagogique. Les méthodes "manquantes" identifiées (SHAP, GARCH, XGBoost, TimeSeriesSplit, walk-forward) sont des **extensions naturelles** des concepts vus, à introduire avec leur bibliographie propre.

C'est un projet **méthodologiquement solide** et **académiquement défendable**. 🎯
