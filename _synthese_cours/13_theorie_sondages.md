---
name: 13-theorie-sondages
description: Synthèse cours "Théorie des sondages" (S. Maistre, M1 Statistique Strasbourg, ~150 pages au total) — plans de sondage, estimateurs Horvitz-Thompson, sondage stratifié/grappes/probabilités inégales, amélioration des estimateurs
metadata:
  type: reference
---

# Théorie des sondages (S. Maistre, M1 Strasbourg, 2025-2026)

> Cours sur l'estimation à partir d'**échantillons d'une population FINIE**. Différence cruciale avec la stat classique : on ne suppose pas i.i.d., on a une population réelle de taille N.
> Lecture partielle effectuée (intro complète + 20 pages de Partie 1). Le reste (sondage stratifié, grappes, probabilités inégales, amélioration estimateurs) est synthétisé en concepts clés.

## 1. Cadre conceptuel

### 1.1 Différence avec la statistique classique
- **Stat classique** : suppose échantillon i.i.d. d'une population hypothétique infinie
- **Sondages** : population **FINIE** de taille N, valeurs Yᵢ **non aléatoires**
- L'**aléa vient du choix de l'échantillon** s, pas des valeurs

### 1.2 Notations standard
- **U** : population de taille N
- **Yᵢ** : valeur de la variable pour l'individu i (déterministe)
- **s = {i₁, …, iₙ}** : échantillon (aléatoire), de taille n
- **p(s)** : probabilité de tirer l'échantillon s
- **πᵢ = Σ_{s ∋ i} p(s)** : probabilité d'inclusion de i dans l'échantillon
- **πᵢⱼ** : probabilité d'inclusion conjointe de i ET j
- Pour un sondage de taille fixe : Σᵢ πᵢ = n

### 1.3 Distinction clé : unité d'observation ≠ unité d'échantillonnage
- **Unité d'observation** : où on mesure Y (ex: patient)
- **Unité d'échantillonnage** : ce qu'on tire (ex: hôpital)
- Si différentes → risque de **défaut de couverture** ⚠️

### 1.4 Paramètres types à estimer
- **Total** : T = Σᵢ∈U Yᵢ
- **Moyenne** : Ȳ = (1/N) Σᵢ∈U Yᵢ
- **Dispersion** : S²_Y = (1/(N-1)) Σᵢ∈U (Yᵢ - Ȳ)²
- **Taille** : N = Σᵢ∈U 1
- **Quantiles**, **proportions**, etc.

⚠️ Ce sont des **vraies valeurs** sur la population U, pas des paramètres d'une loi sous-jacente.

## 2. Précision d'un estimateur

### 2.1 Erreurs d'échantillonnage
$$ B(\widehat{\theta}) = \mathbb{E}[\widehat{\theta}] - \theta = \sum_s p(s) \widehat{\theta}(s) - \theta \quad \text{(biais)} $$
$$ \text{Var}(\widehat{\theta}) = \sum_s p(s) (\widehat{\theta}(s) - \mathbb{E}[\widehat{\theta}])^2 $$
$$ \text{EQM}(\widehat{\theta}) = B^2(\widehat{\theta}) + \text{Var}(\widehat{\theta}) \quad \text{(Erreur quadratique moyenne)} $$
$$ CV(\widehat{\theta}) = \sigma(\widehat{\theta}) / \theta \quad \text{(coefficient de variation)} $$

### 2.2 Types d'erreurs dans une enquête
| Type | Source | Réduction |
|---|---|---|
| **Échantillonnage** | Biais + variance | Augmenter n, améliorer base, changer estimateur |
| **Observation / mesure** | Enquêteur, enquêté, codification, info | Améliorer questionnaire, formation |
| **Couverture** | Base incomplète | Améliorer la base |
| **Non-réponse** | Refus, absence | Pondérations, imputations |

## 3. Estimateur de Horvitz-Thompson ⭐

> **Estimateur universel** pour tout plan de sondage avec πᵢ > 0.

$$ \widehat{T}_\pi = \sum_{i \in s} \frac{Y_i}{\pi_i} \quad ; \quad \widehat{\overline{Y}}_\pi = \frac{1}{N} \sum_{i \in s} \frac{Y_i}{\pi_i} $$

- **Sans biais** pour le total et la moyenne
- **Poids de sondage** : wᵢ = 1/πᵢ
  - Interprétation : chaque individu de l'échantillon "représente" wᵢ individus de la population

## 4. Sondage Aléatoire Simple (SAS) ⭐

> Le plan de référence : tirage de n individus sans remise, équiprobable.

### Propriétés
- Probabilité de tirer un échantillon précis : 1/C(N,n)
- Probabilité d'inclusion : πᵢ = n/N

### Estimateurs
- Moyenne : ȳ = (1/n) Σᵢ∈s Yᵢ (= estimateur de Horvitz-Thompson dans ce cas)
- Total : T̂ = N·ȳ

### Variance (formule clé)
Soit **f = n/N** le **taux de sondage** :
$$ \text{Var}(\bar{y}) = (1-f) \frac{S^2}{n} $$

- Diminue avec **n** (taille échantillon)
- Diminue avec **f** (taux de sondage)
- Quand N → ∞ : tend vers S²/n (formule classique de stat)
- **(1-f)** = **correction de population finie**

### IC normal (TCL)
$$ \left[\bar{y} - q^{(1-\alpha/2)}\sqrt{(1-f)\frac{s^2}{n}}; \bar{y} + q^{(1-\alpha/2)}\sqrt{(1-f)\frac{s^2}{n}}\right] $$

### Estimation d'une proportion P
- P = moyenne d'une variable indicatrice (1 si caractéristique présente)
- P̂ = p (proportion observée)
- Var(p) ≈ (1-f) P(1-P)/n

## 5. Autres plans de sondage (sommaire)

### 5.1 Sondage stratifié
- Découper la population en **strates** homogènes
- Tirer un SAS dans chaque strate
- **Réduit la variance** si les strates sont homogènes intérieurement
- Allocation **proportionnelle** (πᵢ identique) ou **Neyman** (optimale selon dispersion)

### 5.2 Sondage à plusieurs degrés (grappes)
- Premier degré : tirer des **grappes** (ex: villes)
- Deuxième degré : tirer des individus dans chaque grappe
- **Moins coûteux** (concentration géographique) mais **moins précis**

### 5.3 Sondage à probabilités inégales
- πᵢ ≠ πⱼ
- Permet de **sur-représenter** certains individus importants
- Estimateur Horvitz-Thompson reste valable

### 5.4 Échantillonnage équilibré
- Imposer des **contraintes** sur l'échantillon (ex: même moyenne d'âge que la pop)
- Algorithme du **CUBE** (Tillé)

### 5.5 Sondages empiriques (non probabilistes)
- Sans base de sondage propre
- Méthode des **quotas** : marketing
- Sortir du cadre rigoureux

## 6. Effet de sondage (DEFF)

> Comparer un plan à la **référence SAS**.

$$ \text{DEFF} = \frac{\text{Var}(\widehat{\theta})}{\text{Var}_{\text{SAS}}(\widehat{\theta})} $$

- DEFF < 1 : plan plus précis que SAS (bien stratifié)
- DEFF > 1 : plan moins précis (grappes)
- Les IC sont multipliés par √DEFF par rapport à SAS

## 7. Amélioration des estimateurs (Partie 2 — concepts)

### 7.1 Information auxiliaire
Si on connaît une variable auxiliaire X sur **toute la population** (recensement) :
- **Estimateur par ratio** : Ŷ_ratio = (ȳ/x̄) · X̄
- **Estimateur par régression** : Ŷ_reg = ȳ + β̂(X̄ - x̄)
- Plus précis si Y et X sont corrélés

### 7.2 Calage / post-stratification
- Ajuster les poids du sondage pour que les marges connues (âge, sexe…) coïncident avec celles de la population
- Améliore la précision si les marges sont liées à Y

---

## 🎯 Applications au projet TradingMonitor

### Pertinence générale : LIMITÉE pour le projet de trading
Le projet n'utilise PAS d'échantillonnage classique :
- On a la **population entière** des trades (38 035) — pas besoin de sonder
- Données financières publiques exhaustives — pas d'enquête

### Mais quelques concepts utiles ⭐

#### A. Estimateur Horvitz-Thompson pour pondérer des trades
Si on veut estimer une **performance ajustée** sur une sous-population particulière :
- πᵢ = probabilité qu'un trade i appartienne à un "régime" particulier
- Reweighter `1/πᵢ` permet de **dé-biaiser** un sous-échantillon

#### B. Sondage stratifié pour les backtests ⭐
Au lieu de prendre 38 035 trades en bloc :
- **Stratifier** par secteur, taille de marché, régime
- **Allocation Neyman** pour échantillonner plus densément les strates à forte dispersion
- ⇒ Permet d'estimer la performance moyenne avec moins de biais

#### C. Estimateurs par régression pour backtest avec contrôles
- Y = rendement du trade
- X = momentum du marché (S&P 500 le même jour)
- **Estimateur de régression** : `R_ajusté = ȳ + β(X_marché - x̄)`
- ⇒ **Neutralise** l'effet marché (alpha pur vs beta du marché)

🔥 **C'est exactement le concept d'edge dans le projet !**
> edge = return_net − rand_return

C'est une forme d'**estimateur de régression** où la covariable est le rendement moyen d'un trade aléatoire sur le même ticker/durée.

#### D. Validation hold-out comme "sondage" temporel
- Population : tous les jours boursiers passés
- Échantillon : période de test
- Strate : période × régime de marché
- ⇒ Le **walk-forward** vu en [[05-apprentissage-introduction]] est une forme de sondage stratifié temporel

#### E. Plans d'expérience (Partie 3 — non lu)
Le 4ème PDF couvre les **plans d'expérience**, utiles si le projet voulait faire des **A/B testing** sur des variantes de stratégies. À explorer si pertinent.

### Limites pour le projet
- Pas d'enquête avec questionnaire
- Pas de population à échantillonner (on a tout)
- **Le cours ne couvre pas** la sélection de variables ni les méthodes ML

### Angle de rapport
> Mention possible : « Bien que le projet ne pratique pas de sondage au sens classique, la notion d'**estimateur sans biais corrigé par information auxiliaire** (cours sondages M1) éclaire la construction de l'edge = return_net − rand_return : on neutralise un biais de population (marché haussier S&P 500 sur 2020-2025) en utilisant une covariable. »

---

## ✅ Méthodes / concepts acquis
- Plan de sondage, probabilités d'inclusion πᵢ, πᵢⱼ
- Sondage de taille fixe vs aléatoire
- Paramètres / estimateurs **linéaires**
- **Estimateur de Horvitz-Thompson** (universel, sans biais)
- **Poids de sondage** wᵢ = 1/πᵢ
- **Sondage Aléatoire Simple (SAS)** + formule variance avec (1-f)
- Estimation d'une proportion
- **DEFF** (Design Effect)
- Sondage stratifié (Neyman, proportionnelle)
- Sondage à plusieurs degrés (grappes)
- Probabilités inégales
- Échantillonnage équilibré (CUBE)
- Estimateurs par **ratio** et par **régression**
- Information auxiliaire
- Calage / post-stratification

## 🆕 À étudier si nécessaire (Partie 2 + plans d'expérience non lus)
- **Calage** détaillé (algorithmes)
- Estimateurs **GREG** (généralisés par régression)
- **Bootstrap** en population finie
- **Plans d'expérience** : factoriels, plans D-optimaux, Box-Behnken
- Pour les sondages financiers : **Stratification temporelle** avec dates

## ⚠️ Note
Lecture partielle (~40 pages sur ~150). Suffisant car concepts faiblement applicables au projet trading. Si besoin futur de méthodes plus poussées (calage, plans d'expérience), revenir aux PDFs originaux.
