---
name: 15-statistique-avec-python
description: Synthèse cours "Statistique avec Python" (N. Poulin, CeStatS Strasbourg, 6 PDF ~270 p. + code) — Python de base, pandas/numpy descriptif, scipy.stats (shapiro, ttest_ind/rel, bartlett/levene, chisquare, chi2_contingency), statsmodels (ols + anova_lm typ=2, MultiComparison tukeyhsd/bonf)
metadata:
  type: reference
---

# Statistique avec Python (N. Poulin, CeStatS Strasbourg)

> Pendant Python du cours SAS [[14-statistique-avec-SAS]] — **mêmes méthodes, mêmes exemples** (jeu `mais.csv`), traduits en Python. 6 PDF (~270 pages) + un script `session3.py`.
> Conventions d'import du cours : `import pandas as pds` (⚠️ **`pds`**, pas `pd`), `import numpy as np`, `from scipy import stats`, `import statsmodels.api as sm`.
>
> ⭐ **Intérêt pour le projet** : donne les **appels Python exacts** utilisés dans le Bloc 1 (`etape1_tests.py` … `etape3_chi2.py`) et permet de **corriger** quelques appels supposés à tort dans `bloc1/02_methodes/explication.md`.

## 0. Python de base (session1.pdf, session2.pdf) — aucune statistique

- **session1** : opérateurs (`+ - * ** / //`), types (`int/float/complex`, `bool`, `None`), séquences (chaînes, listes, tuples), méthodes de listes (`.append()`, `.pop()`, `.sort()`, `.reverse()`, `.remove()`), slicing `L[i:j:k]` (`L[::-1]`), dictionnaires `{clé: valeur}`, ensembles `set()` (`&`, `|`, `in`).
- **session2** : indentation (4 espaces), `if/elif/else`, boucles `while`/`for ... in range()`, `break`/`continue`, f-strings `f'...{var}...'`, fonctions `def f(a, b=défaut): return`, modules `import ... as`, `import math`.

## 1. Données & descriptif (session3.pdf + session3.py)

```python
import os; os.chdir(r"chemin")            # raw string
import pandas as pds
mais = pds.read_csv("mais.csv", delimiter=";")   # CSV français ; séparateur ';'
mais.info(); list(mais.columns)
mais["Hauteur"]; mais[["Hauteur","Masse"]]        # sélection colonnes
mais.loc[:10, "Hauteur"]                          # loc : borne j INCLUSE
mais.iloc[2, 2]                                    # iloc : borne j EXCLUE
mais.select_dtypes(include=[np.number])            # tri quanti / quali
```
- **Descriptif numpy** : `np.mean`, `np.median(x.dropna())`, `np.percentile(x.dropna(), 25)`, `np.std`.
- **Résumé** : `stats.describe(x.dropna())`. **Qualitatif** : `x.value_counts()`, `pds.crosstab(mais.Couleur, "freq")`.
- ⚠️ **NaN partout** dans `mais.csv` → `.dropna()` systématique (scipy est sensible aux NaN).

## 2. Normalité & Student (normalitefinal1.pdf)

### Normalité
```python
stats.shapiro(mais["Hauteur"].dropna())      # Shapiro-Wilk (H0 : normal)
import statsmodels.api as sm
sm.qqplot(mais["Hauteur"], loc=np.mean(...), scale=np.std(...), line='45')   # Q-Q plot
```
- Kolmogorov-Smirnov, Anderson-Darling, Cramér-von Mises **cités mais non codés**.
- ⚠️ **Non vus** : `normaltest` (D'Agostino), Jarque-Bera, `kstest`, `anderson`.

### Test de Student (2 moyennes)
```python
HautNon = mais["Hauteur"][mais["Verse.Traitement"]=="Non"]
HautOui = mais["Hauteur"][mais["Verse.Traitement"]=="Oui"]
stats.ttest_ind(HautNon, HautOui, nan_policy='omit')                    # variances égales
stats.ttest_ind(HautNon, HautOui, nan_policy='omit', equal_var=False)   # WELCH
stats.ttest_rel(mais["Hauteur"], mais["Hauteur.J7"], nan_policy='omit') # APPARIÉ
```
- **Fisher-Snedecor (égalité des variances)** : **pas de fonction scipy dédiée** → recodée à la main avec `stats.f.cdf(f, dfn, dfd)`.
- Mann-Whitney **cité** (non codé). Notation : `T`, loi de Student à `n₁+n₂−2` ddl.

## 3. ANOVA 1 facteur (anovafinal.pdf)

### ⚠️ Via `ols` + `anova_lm`, PAS `f_oneway`
```python
from statsmodels.formula.api import ols
import statsmodels.api as sm
model = ols('Hauteur ~ Parcelle', data=mais).fit()
aov_table = sm.stats.anova_lm(model, typ=2)      # table d'ANOVA type II
stats.shapiro(model.resid)                        # normalité des RÉSIDUS
```
Le cours **n'utilise pas** `scipy.stats.f_oneway` — c'est l'approche **modèle linéaire** `ols`/`anova_lm(typ=2)`.

### Conditions
```python
stats.bartlett(HautE, HautN, HautO, HautS)   # homoscédasticité (privilégié)
stats.levene(HautE, HautN, HautO, HautS)     # Levene (robuste non-normalité) ← vu côté Python (≠ SAS)
```

### Post-hoc — `statsmodels.stats.multicomp`
```python
import statsmodels.stats.multicomp as mc
comp = mc.MultiComparison(test['Hauteur'], test['Parcelle'])
comp.allpairtest(stats.ttest_ind, method="bonf")   # BONFERRONI
res = comp.tukeyhsd()                               # TUKEY (via MultiComparison, pas pairwise_tukeyhsd)
res.plot_simultaneous(...)
```
- ⚠️ C'est `MultiComparison(...).tukeyhsd()`, **pas** `pairwise_tukeyhsd` directement.
- Dunnett : « pas de méthode simple en Python » (renvoi à R).

## 4. Tests du χ² (chisquarefinal1.pdf)

### χ² d'ajustement
```python
stats.chisquare(n_obs, n_thq)     # n_obs, n_thq = effectifs observés / théoriques
```

### χ² d'indépendance
```python
obs = numpy.array([[25,9,3,7],[13,17,10,7],[7,13,8,5]])
chi2, p, dof, thq = stats.chi2_contingency(obs, correction=False)   # correction= = Yates (2×2)
# tableau depuis les données :
pds.crosstab(mais['Couleur'], mais['Parcelle'], margins=False)
```
- **Correction de Yates** = argument `correction=` (le cours utilise `correction=False`).
- **Règle de Cochran** vérifiée par double boucle sur `thq` (≥ 80 % des `t_ij ≥ 5`).
- ⚠️ **V de Cramér NON abordé** (comme côté SAS).

---

## 🎯 Applications au projet TradingMonitor

### Corrections à apporter à `bloc1/02_methodes/explication.md`
Le fichier a été rédigé **de mémoire** ; confronté au cours réel :
| Affirmation actuelle | Réalité du cours Python | Action |
|---|---|---|
| ANOVA via `scipy.stats.f_oneway` | Le cours utilise `ols` + `anova_lm(typ=2)` | ajouter/privilégier la forme vue en cours |
| `scipy.stats.wilcoxon` | **Wilcoxon non vu** en Python (ni Mann-Whitney codé) | signaler que c'est hors cours Python |
| `pairwise_tukeyhsd` | Le cours utilise `MultiComparison(...).tukeyhsd()` | corriger l'appel |
| χ² : `chi2_contingency` renvoie « χ², p, ddl, attendus » | ✅ exact (`chi2, p, dof, thq`) | OK |
| Bonferroni « pas explicite en M1 » | ✅ **enseigné** (`method="bonf"`) | revaloriser |

### Méthodes du Bloc 1 confirmées « vues en cours » (Python)
- **Shapiro-Wilk** → `stats.shapiro` ✅
- **Student 1/2 éch. + Welch + apparié** → `ttest_1samp` / `ttest_ind` / `ttest_rel` ✅
- **ANOVA** → `ols` + `anova_lm` ✅ (+ Bartlett/Levene pour les conditions)
- **Tukey + Bonferroni** → `MultiComparison` ✅
- **χ² indépendance** → `chi2_contingency` ✅

### Boîte à outils Python (à citer dans le rapport)
| Méthode | Appel exact | Librairie |
|---|---|---|
| Normalité | `stats.shapiro(x.dropna())` | scipy.stats |
| Q-Q plot | `sm.qqplot(x, loc=, scale=, line='45')` | statsmodels |
| Student / Welch | `stats.ttest_ind(a, b, nan_policy='omit'[, equal_var=False])` | scipy.stats |
| Apparié | `stats.ttest_rel(a, b, nan_policy='omit')` | scipy.stats |
| Homoscédasticité | `stats.bartlett(...)` / `stats.levene(...)` | scipy.stats |
| ANOVA | `ols('Y ~ X', data=df).fit()` + `sm.stats.anova_lm(m, typ=2)` | statsmodels |
| Post-hoc | `mc.MultiComparison(y, x).tukeyhsd()` / `.allpairtest(..., method="bonf")` | statsmodels |
| χ² ajustement | `stats.chisquare(n_obs, n_thq)` | scipy.stats |
| χ² indépendance | `stats.chi2_contingency(obs, correction=False)` | scipy.stats |
| Contingence | `pds.crosstab(v1, v2)` | pandas |

---

## ✅ Méthodes acquises dans ce cours
- Python de base (types, contrôle, fonctions, modules)
- pandas : `read_csv`, `.loc`/`.iloc`, `select_dtypes`, `crosstab`, `value_counts`, `.dropna()`
- numpy descriptif : `mean`, `median`, `percentile`, `std`
- **scipy.stats** : `shapiro`, `ttest_ind` (+ Welch), `ttest_rel`, `bartlett`, `levene`, `chisquare`, `chi2_contingency`, `f.cdf`
- **statsmodels** : `ols` + `anova_lm(typ=2)`, `qqplot`, `MultiComparison` (`tukeyhsd`, `allpairtest` Bonferroni)

## 🆕 À noter (hors cours Python — ne PAS supposer présents)
- `scipy.stats.f_oneway` (le cours passe par `ols`/`anova_lm`)
- `pairwise_tukeyhsd` direct (le cours passe par `MultiComparison`)
- **Wilcoxon** (`stats.wilcoxon`), Mann-Whitney codé, `normaltest`/D'Agostino, Jarque-Bera, `kstest`, `anderson`
- **V de Cramér**
- seaborn, sklearn, matplotlib (usage explicite non montré)
- ttest_1samp (le cours montre `ttest_ind`/`rel` à 2 échantillons ; la version 1 échantillon du Bloc 1 en est le cas particulier)
