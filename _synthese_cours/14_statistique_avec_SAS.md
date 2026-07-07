---
name: 14-statistique-avec-SAS
description: Synthèse cours "Statistique avec SAS" (N. Poulin / L. Gardes, CeStatS Strasbourg, 6 PDF ~240 p.) — DATA step, PROC UNIVARIATE (4 tests de normalité), PROC TTEST, PROC ANOVA/GLM (Tukey/Dunnett/Bartlett), PROC REG (VIF, sélection), PROC GENMOD (GLM généralisé Poisson/logistique), PROC FREQ (χ² Pearson/Yates/Fisher/G-test)
metadata:
  type: reference
---

# Statistique avec SAS (N. Poulin & L. Gardes, CeStatS / IRMA Strasbourg)

> Cours **pratique orienté logiciel** — 6 PDF (~240 pages), environnement **SAS University Edition**.
> Fil conducteur : le jeu de données **`mais`** (Hauteur, Masse, Couleur, Parcelle, Verse_Traitement, Hauteur_J7).
> Sources exemples GLM : Zuur et al. (2009), *Mixed Effects Models and Extensions in Ecology with R*.
>
> ⭐ **Intérêt majeur pour le projet** : ce cours **confirme comme "vues en cours"** plusieurs méthodes du Bloc 1 qu'on croyait "nouvelles" (Shapiro-Wilk, Bonferroni, Tukey, ANOVA, χ²) et fournit la **syntaxe SAS exacte** pour chacune. Voir aussi le pendant Python [[15-statistique-avec-python]].

## 0. Bases SAS (session1.pdf, 46 slides)

### Structure d'un programme
- **2 types de blocs** : étape **DATA** (import/gestion/création de variables) et **PROCédures** (`PROC ... RUN;`).
- Chaque instruction finit par **`;`**. SAS **non sensible à la casse**.
- Commentaires : `* ... ;` ou `/* ... */`.

### Import / export / exploration
```sas
PROC IMPORT OUT=lib.mais DATAFILE="chemin/mais.xlsx" DBMS=xlsx;
    GETNAMES=YES;
RUN;
PROC CONTENTS DATA=lib.mais; RUN;   /* descripteur : nb obs/var, type Char/Num, length */
PROC PRINT DATA=lib.mais; VAR Hauteur Masse; RUN;   /* options : NOOBS, TITLE, LABEL/SPLIT, BY, PAGEBY */
PROC SORT DATA=lib.mais OUT=lib.maistri; BY var1 DESCENDING var2; RUN;
PROC EXPORT DATA=lib.mais OUTFILE="chemin/out.xlsx" DBMS=xlsx REPLACE; RUN;
```
Création manuelle : `DATA t; INPUT nom $ age; DATALINES;` (ou `CARDS;`) — le **`$`** suit les variables **caractère**.

### Notations / règles de données
- Types : **caractère** (≤ 32 767 octets) et **numérique** (flottant 8 octets).
- Dates = nb de jours depuis le **1er janvier 1960**.
- Manquants : **numérique `.`**, **caractère espace**. (Un "NA" numérique force le passage en caractère.)
- Bibliothèques : `LIBNAME libref "chemin";` (4 par défaut : SASHELP, SASUSER, WORK, WEBWORK).

## 1. Normalité et test de Student (normalitefinal1.pdf)

### Cadre des tests d'hypothèse
H0 vs H1 ; test uni/bilatéral ; erreur type I (α) / type II (β) ; puissance 1−β ; décision par **p-value** (`p < α ⟹ H1`).

### 4 tests de normalité — `PROC UNIVARIATE ... NORMAL`
L'option **`NORMAL`** déclenche **4 tests d'ajustement à la loi normale** :
- **Shapiro-Wilk** (le plus adapté à la normalité)
- **Kolmogorov-Smirnov**
- **Anderson-Darling**
- **Cramér-von Mises**

```sas
PROC UNIVARIATE DATA=mais1 NORMAL;    /* + CLASS Verse_Traitement; pour tester par groupe */
    VAR Hauteur;
    QQPLOT Hauteur / NORMAL(MU=EST SIGMA=EST);   /* Q-Q plot */
RUN;
```

### Test de Student — `PROC TTEST`
```sas
PROC TTEST DATA=mais1;
    VAR Hauteur; CLASS Verse_Traitement;   /* 2 groupes */
RUN;
PROC TTEST DATA=mais1; PAIRED Hauteur*Hauteur_J7; RUN;   /* apparié avant/après */
```
`PROC TTEST` produit **automatiquement** le **test de Fisher d'égalité des variances** + les QQ-plots des 2 groupes (**mais pas** Shapiro — à faire à part). Welch-Satterthwaite et Mann-Whitney sont **cités** comme alternatives.

**Notations** : `T = (X̄₁−X̄₂) / √(S²₁/n₁ + S²₂/n₂)`, loi de Student à `n₁+n₂−2` ddl. Fisher : `F = S²₁/S²₂`, loi de Fisher à `(n₁−1, n₂−1)` ddl.

## 2. ANOVA — `PROC ANOVA` / `PROC GLM` (anovafinal.pdf)

### Modèle et notations
- Modèle : `X_j = μ_j + ε`, `ε ~ N(0, σ)`. H0 : `μ₁ = … = μ_k`.
- Statistique **F**, sous H0 **loi de Fisher à (k−1, N−k) ddl** (k groupes, N effectif total).
- ⚠️ Le cours reste **conceptuel** sur la décomposition de variance : **pas de formules SCE/SCT/SCR détaillées**, et **pas de sommes de carrés Type I/II/III**.

### Conditions et leurs tests
- **Normalité** (Shapiro-Wilk sur les résidus) ; **homoscédasticité** : **test de Bartlett** via `HOVTEST=bartlett` (H0 : variances égales, `B ~ χ²(k−1)`).
- ⚠️ **Levene N'EST PAS enseigné côté SAS** (seul Bartlett). L'ANOVA est dite robuste à la non-normalité, **pas** à l'hétéroscédasticité.

### Syntaxe (1 facteur)
```sas
PROC ANOVA DATA=mais1;              /* ou PROC GLM (effectifs déséquilibrés OK) */
    class Parcelle;
    model Hauteur = Parcelle;
    means Parcelle / HOVTEST=bartlett;   /* homoscédasticité */
    means Parcelle / TUKEY;              /* post-hoc toutes paires */
    means Parcelle / DUNNETT('Nord');    /* post-hoc vs groupe de référence */
run;
```
Extraction des résidus (avec GLM) pour tester leur normalité :
```sas
PROC GLM DATA=mais1;
    class Parcelle; model Hauteur = Parcelle;
    output out=mais2 r=residus;
run;
PROC UNIVARIATE DATA=mais2 normal; var residus; run;
```

### Post-hoc (comparaisons multiples)
Distinction **sans référence** (k(k−1)/2 paires : **Bonferroni**, **Tukey**) vs **avec référence** (k−1 : **Bonferroni**, **Dunnett**).
- Réellement montrés en SAS : **Tukey** et **Dunnett**. Bonferroni **cité** (jugé « trop conservateur ») mais sans option SAS dédiée. **Scheffé / Duncan absents.**

### ANOVA 2 facteurs (+ interaction) — `PROC GLM` uniquement
```sas
PROC GLM DATA=mais1;
    class Parcelle Verse_Traitement;
    model Hauteur = Parcelle Verse_Traitement Parcelle*Verse_Traitement;  /* interaction = A*B */
    lsmeans Parcelle Verse_Traitement Parcelle*Verse_Traitement / ADJUST=TUKEY;
run;
```

## 3. Régression linéaire — `PROC REG` (linmodfinal.pdf)

- Simple : `Y = aX + b + ε` ; `â = Cov(X,Y)/σ²_X`, `b̂ = ȳ − â x̄` (le point moyen `(x̄, ȳ)` est sur la droite).
- **R²** : test H0 `R²=0`, statistique **F ~ Fisher-Snedecor(1, n−2)**.
- **Tests pente / ordonnée** : loi de **Student à n−2 ddl**.
- **Multicolinéarité — VIF** : `VIF_i = 1/(1−R²_i)`, seuils **> 10** (arbitraire) ou **> 3** (plus strict). Retrait itératif de la variable au plus grand VIF.
- **Sélection de modèle** : **AIC / BIC / LRT** ; règle **10 observations par paramètre**.

```sas
PROC REG DATA=mais1;
    model Hauteur = Masse / VIF;                    /* VIF */
    output out=mais2 r=residus;                     /* résidus → UNIVARIATE normal */
run;
PROC REG DATA=mais1 plots=diagnostics(unpack);      /* Q-Q, résidus, Cook */
    model Masse = Hauteur hauteur_j7 nb_grains / selection=backward SLSTAY=0.05;
run;
```
`selection=` : `backward`, `stepwise`, `Rsquare` (+ affichage `AIC BIC`). `PROC SGPLOT ... scatter y= x=;` pour le nuage (`PROC GPLOT` indisponible sous SAS University).

## 4. GLM **généralisé** — `PROC GENMOD` (glmfinal.pdf) 🆕

> ⚠️ **Attention nom** : ce PDF traite du **Modèle Linéaire GÉNÉRALISÉ** (Nelder & Wedderburn 1972 — Poisson, logistique, binomial), via **`PROC GENMOD`**. Ce **n'est PAS** la `PROC GLM` (modèle linéaire général) des cours 2-3. **Méthode entièrement nouvelle par rapport aux 13 cours précédents.**

### Structure d'un GLM (3 composantes)
1. **Distribution** de Y (famille exponentielle) : continues (normale, Gamma, inverse-gaussienne), discrètes (binomiale, Poisson).
2. **Prédicteur linéaire** `η_i` (peut contenir des interactions).
3. **Fonction de lien canonique** `g` : `g(E[Y_i]) = η_i`.
GLM normale + lien identité = régression linéaire classique.

| Données | Loi | Lien | E / Var | SAS |
|---|---|---|---|---|
| Comptage | **Poisson** | `log` | E=Var=λ | `dist=poisson link=log` |
| Binaire (0/1) | **Bernoulli** (logistique) | **logit** = `log(p/(1−p))` | E=π, Var=π(1−π) | `dist=binomial link=logit` |
| Proportions succès/total | **Binomiale** | logit | E=nπ | `dist=binomial link=logit` |

### Syntaxe
```sas
PROC GENMOD DATA=rk;
    model tot_N = D_park / dist=poisson link=log type3;   /* type3 = 1 test LRT / variable */
run;
PROC GENMOD DATA=boar;
    model Tb = LengthCT / dist=binomial link=logit;       /* logistique */
run;
PROC GENMOD DATA=TbDeer;
    model DeerPos/DeerSampled = OpenLand ScrubLand / dist=binomial link=logit;  /* proportions */
run;
```
- **Sur-dispersion** : `Φ = Deviance/(n−p)` ; si `Φ ≠ 1`, corriger avec **`pscale`** (Pearson χ²) ou **`dscale`** (déviance) → quasi-Poisson / quasi-Binomiale. Si `Φ > 15` → Negative Binomial / Zero-Inflated.
- **Sélection** : VIF via `PROC REG` d'abord (retirer VIF > 3), puis AIC ou LRT (`type3`, retirer la plus grande p-value > 5 %).
- **Offset** (taille de référence) : option `offset=logBZ` ; **interactions** `A*B` ; facteurs déclarés via `CLASS`.

---

## 🎯 Applications au projet TradingMonitor

### Ce cours **revalorise** le Bloc 1 (méthodes crues "nouvelles" → en fait vues en cours)
| Méthode Bloc 1 | Statut avant | Statut réel (ce cours) | Syntaxe SAS |
|---|---|---|---|
| **Shapiro-Wilk** | 🆕 « pas explicite » | ✅ **cœur du cours normalité** | `PROC UNIVARIATE ... NORMAL` |
| **Student 1/2 éch. + Welch** | ✅ mentionné | ✅ confirmé | `PROC TTEST` |
| **ANOVA 1 facteur** | ✅ | ✅ confirmé | `PROC ANOVA` / `PROC GLM` |
| **Tukey HSD** | ✅ | ✅ confirmé | `means / TUKEY` |
| **Bonferroni** | 🆕 « pas explicite » | ✅ **enseigné** (post-hoc) | (cité, pas d'option) |
| **ANOVA 2 facteurs + interaction** | 🆕 extension | ✅ **enseignée** | `model Y = A B A*B; lsmeans` |
| **χ² d'indépendance** | ✅ | ✅ confirmé | `PROC FREQ ... CHISQ` |

### Nouveautés exploitables
- **GLM généralisé (`PROC GENMOD`)** ⭐ : la **régression logistique** (`dist=binomial link=logit`) est directement pertinente pour le **Bloc final** si on modélise `win` (0/1) au lieu de `edge` continu. Alternative paramétrique interprétable à Lasso/RF.
- **VIF** (`/ VIF`, seuil 3) : diagnostic de multicolinéarité pour la régression du Bloc final.
- **Sélection backward/stepwise + AIC/BIC** : protocole de sélection de variables vu en cours (à mentionner face au Lasso).
- **Régression de Poisson** : utilisable pour modéliser un **nombre d'événements** (ex. nb de trades/signaux par période — Bloc 2).

### Comparaison SAS ↔ R ↔ Python (à mettre dans le rapport)
| Besoin | SAS | R ([[11-statistique-avec-R]]) | Python ([[15-statistique-avec-python]]) |
|---|---|---|---|
| Normalité | `PROC UNIVARIATE NORMAL` | `shapiro.test()` | `stats.shapiro()` |
| t-test | `PROC TTEST` | `t.test()` | `stats.ttest_ind()` |
| ANOVA | `PROC ANOVA` / `GLM` | `aov()` / `lm()` | `ols()` + `anova_lm()` |
| Tukey | `means / TUKEY` | `TukeyHSD()` | `MultiComparison().tukeyhsd()` |
| χ² | `PROC FREQ / CHISQ` | `chisq.test()` | `stats.chi2_contingency()` |
| Régression | `PROC REG` | `lm()` | `sklearn` / `statsmodels.OLS` |
| GLM (logistique) | `PROC GENMOD` | `glm(family=binomial)` | `statsmodels ... Logit` |

---

## ✅ Méthodes acquises dans ce cours
- Programmation SAS : DATA step, PROC IMPORT/EXPORT/CONTENTS/PRINT/SORT
- **PROC UNIVARIATE NORMAL** → Shapiro-Wilk, Kolmogorov-Smirnov, Anderson-Darling, Cramér-von Mises + Q-Q plot
- **PROC TTEST** (1 éch., 2 éch., apparié) + test de Fisher des variances automatique
- **PROC ANOVA / PROC GLM** : ANOVA 1 et 2 facteurs + interaction (`A*B`)
- Post-hoc **Tukey** (`means / TUKEY`, `lsmeans / ADJUST=TUKEY`) et **Dunnett**
- Homoscédasticité **Bartlett** (`HOVTEST=bartlett`)
- **PROC REG** : régression simple/multiple, **VIF**, sélection `backward`/`stepwise`, AIC/BIC/LRT
- **PROC GENMOD** 🆕 : GLM généralisé (Poisson `log`, logistique `logit`, binomial), sur-dispersion (`pscale`/`dscale`), offset
- **PROC FREQ** : χ² Pearson (ajustement + indépendance), Yates, Fisher exact, G-test (voir détail chi-2 ci-dessous)

## 5. Tests du χ² — `PROC FREQ` (chisquarefinal1.pdf)

### Variantes couvertes
- **χ² de Pearson** — ajustement à une loi (`ν = k−1`) ET indépendance (`ν = (k−1)(c−1)`)
- **Correction de continuité de Yates** (tableaux 2×2) : `χ²_Yates = Σ (|n_ij − t_ij| − 0.5)² / t_ij`
- **Test exact de Fisher** (petits effectifs / Cochran non vérifié)
- **G-test / Likelihood Ratio Chi-Square** (Sokal & Rohlf 1981)
- ⚠️ **Le V de Cramér n'est PAS abordé dans ce cours.**
- Condition de **Cochran** : ≥ 80 % des effectifs théoriques ≥ 5.

```sas
/* ajustement (dé équilibré) */
PROC FREQ DATA=dice ORDER=DATA;
    TABLES face / CHISQ TESTF=(16.667 16.667 16.667 16.667 16.667 16.667) NOCUM;
    WEIGHT effectif;
RUN;
/* indépendance */
PROC FREQ DATA=couleur ORDER=DATA;
    TABLES YEUX*CHEVEUX / CHISQ EXPECTED;   /* croisement = var1*var2 ; EXPECTED = effectifs théoriques */
    WEIGHT effectif;                        /* WEIGHT seulement si données pré-agrégées */
    EXACT Fisher;                           /* test exact de Fisher */
RUN;
```
Options `TABLES` : `CHISQ`, `TESTP=(...)` (proportions), `TESTF=(...)` (effectifs), `EXPECTED`, `NOCUM`. Yates + Fisher sortent automatiquement pour un 2×2 avec `CHISQ`.

## 🆕 À noter (limites / hors cours)
- Sommes de carrés **Type I/II/III** non traitées (juste évoquées).
- **Levene** non enseigné côté SAS (seulement Bartlett).
- **V de Cramér** non couvert (⚠️ à corriger dans `bloc1/02_methodes/explication.md` qui laisse entendre le contraire).
- **Scheffé / Duncan** non couverts.
- Kruskal-Wallis / Mann-Whitney seulement cités (non détaillés en SAS).
