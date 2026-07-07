# Préparation de l'oral — anticipation des questions du jury

> **Hors rapport.** Ce fichier ne fait PAS partie du mémoire LaTeX. Il sert
> à préparer les 10 minutes de questions (soutenance : 20 min exposé + 10 min
> questions, en français, à huis clos). Les consignes valorisent
> *l'autonomie* et *la pertinence des réponses aux questions*.
>
> Format : pour chaque méthode, la **question probable**, la **réponse
> courte** à donner, et le **piège à éviter**.

---

## Bloc 1 — Étape 1 (Shapiro, Student, Bonferroni)

**Q : Shapiro rejette la normalité partout. Comment justifiez-vous alors un test de Student ?**
- R : Le Student ne suppose pas la normalité des données brutes mais celle de *la moyenne*. Le **théorème central limite** garantit la quasi-normalité de la moyenne pour n grand (ici 973 à 8 469 trades). La condition qui compte est donc satisfaite.
- Piège : ne pas prétendre que « les données sont normales ». Assumer le rejet et s'appuyer explicitement sur le TCL.

**Q : Pourquoi tester `edge` et pas `return_net` ?**
- R : Sur la période, ~97 % des titres montent → un rendement positif ne prouve rien. `edge = return_net − rand_return` neutralise la dérive haussière : on teste un *talent de timing*, pas la chance d'un marché porteur.

**Q : Pourquoi Bonferroni, puisque vous faites 10 tests séparés ?**
- R : Mécaniquement 10 tests indépendants, mais l'interprétation d'ensemble change la question : « au moins un faux positif parmi 10 » vaut ~40 % à α=5 %. Bonferroni ramène le risque global sous 5 % en durcissant le seuil individuel à 0,005 (inégalité de Boole).
- Piège : savoir citer l'analogie des 10 dés (P(au moins un 6) = 84 %).

**Q : Pourquoi ne pas avoir gardé le test de Wilcoxon / le V de Cramér ?**
- R : Choix d'ancrage aux méthodes explicitement vues dans les cours SAS/Python du M1. Wilcoxon n'y figure pas (vu seulement en R), le V de Cramér dans aucun des trois cours logiciels. Ils ont servi de **vérification interne** mais ne sont pas revendiqués comme méthodes du rapport.
- Piège : rester cohérent — ne pas les présenter comme centraux.

---

## Bloc 1 — Étape 2 (ANOVA + Tukey + interaction)

**Q : Quelles conditions d'application de l'ANOVA avez-vous vérifiées ?**
- R : Indépendance ; normalité des résidus (TCL) ; **homoscédasticité** via Bartlett et Levene. En cas de variances inégales, ANOVA de Welch.

**Q : Que signifie une interaction stratégie × régime significative ?**
- R : L'effet d'une stratégie **dépend du régime de marché** : on ne peut pas dire « le RSI est bon » dans l'absolu, seulement « bon dans tel régime ». C'est un des résultats forts du bloc.

**Q : Pourquoi Tukey plutôt que des Student deux à deux ?**
- R : Tukey (range studentisé) corrige automatiquement le risque des k(k−1)/2 comparaisons ; il est adapté au cadre ANOVA (variance résiduelle commune), là où Bonferroni est générique.

---

## Bloc 1 — Étape 3 (khi-deux)

**Q : Vos χ² sont énormes. N'est-ce pas trop beau ?**
- R : À grand n, le χ² devient significatif même pour un lien négligeable. La significativité ne mesure pas la force : c'est précisément la limite que je souligne (d'où l'intérêt, hors périmètre cours, d'une mesure d'effet).

**Q : Conditions d'application du χ² ?**
- R : Effectifs théoriques ≥ 5 (règle de Cochran), vérifiés ici. Sur 2×2 / faibles effectifs : Yates, Fisher exact ou G-test.

---

## Bloc 1 — Étapes 4-6 (ACP / AFC / ACM)

**Q : Comment avez-vous choisi le nombre d'axes en ACP ?**
- R : Critères de **Kaiser** (valeurs propres > 1 en ACP normée) et **scree-test de Cattell** (coude de l'éboulis), pas un choix arbitraire de 2 axes.

**Q : Pourquoi projeter `win`/`régime`/`secteur` en illustratifs ?**
- R : Ces variables n'ont pas servi à construire les axes ; les projeter *a posteriori* (valeur-test) permet de les interpréter sans qu'elles influencent la structure. Bonne pratique du cours Périnel.

---

## Bloc 3 — Granger / ACP / ARIMA

**Q : 48 paires de Granger significatives : signal exploitable ?**
- R : Non nécessairement. Avec ~4 132 jours, la puissance est telle que « significatif » ≠ « exploitable » (retards courts, gains faibles). Et « Granger-cause » = prédictif, pas causal.

**Q : Pourquoi ARIMA sur le rendement et pas sur le prix ?**
- R : Le prix est non stationnaire (marche aléatoire, ADF p≈1) ; ARIMA exige la stationnarité, obtenue par passage aux rendements (ADF p≈10⁻²⁶).

---

## Questions transverses / méthodologie

**Q : Quelle est votre principale limite ?**
- R : Résultats *in-sample*. Une validation *walk-forward* (hors échantillon, respectant l'ordre temporel) est nécessaire avant tout usage. Les k-fold classiques fuiteraient l'information du futur.

**Q : Autonomie — qu'avez-vous fait seul ?**
- R : [à personnaliser] conception de l'architecture en blocs, construction des bases, choix et implémentation des méthodes, interprétation.
