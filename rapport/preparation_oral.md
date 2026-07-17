# Préparation de l'oral — anticipation des questions du jury

> **Hors rapport.** Ce fichier ne fait PAS partie du mémoire LaTeX. Il sert
> à préparer les 10 minutes de questions (soutenance : 20 min exposé + 10 min
> questions, en français, à huis clos). Les consignes valorisent
> *l'autonomie* et *la pertinence des réponses aux questions*.
>
> Format : pour chaque méthode, la **question probable**, la **réponse
> courte** à donner, et le **piège à éviter**.

---

## Bloc 1 — Étape 1 (Student, Shapiro, TCL, Bonferroni)

> ⭐ **Questions issues de la rédaction** (soulevées en écrivant le rapport —
> ce sont des points sur lesquels je me suis effectivement interrogé, donc
> le jury le peut aussi).

**Q : Pourquoi tester µ_edge alors que la moyenne ē est connue ? On teste un truc qu'on connaît ?**
- R : On ne teste pas ē (la moyenne observée, connue). On teste **µ_edge**, l'edge moyen *théorique* de la stratégie « en général » (inconnu). ē n'est que l'**estimateur** qui sert à trancher sur µ_edge. C'est le principe de l'inférence : remonter de l'échantillon (connu, limité) à la population (inconnue).
- Piège : ne jamais dire « on teste la moyenne » sans préciser « théorique ».

**Q : Pourquoi dire « edge moyen » et pas simplement « edge » ?**
- R : Trois niveaux à distinguer. (1) l'edge d'UN trade e_i ; (2) l'edge moyen *observé* ē (moyenne des e_i sur l'échantillon) ; (3) l'edge moyen *théorique* µ_edge = E[e_i] (espérance, inconnue). Le test juge la stratégie **dans son ensemble** (sa tendance centrale), donc sur la moyenne — d'où « edge moyen ».

**Q : Que représente exactement la statistique t ?**
- R : Le **nombre d'erreurs-types** séparant l'edge moyen observé de zéro. t = ē / (s/√n). Petit t → banal (dans le bruit) ; grand t → suspect, écart difficile à attribuer au hasard. Le √n récompense la quantité de données : même edge = plus convaincant sur 7000 trades que sur 20.
- Piège : ne pas confondre **erreur-type** (incertitude sur la moyenne, s/√n) et **écart-type** (dispersion des données, s).

**Q : La condition de Student, c'est la normalité des données ou de la moyenne ?**
- R : Formellement le test suppose la normalité des **observations** (l'edge). Mais ce qui rend réellement t valide, c'est la normalité de la **moyenne** ē — garantie par le TCL à grand n même si les observations ne sont pas normales. Raisonnement en 3 temps : condition posée sur l'edge → Shapiro la teste, échec → TCL la sauve via la moyenne.

**Q : Shapiro rejette la normalité partout. Comment justifiez-vous alors un test de Student ?**
- R : Le Student ne suppose pas la normalité des données brutes mais celle de *la moyenne*. Le **théorème central limite** garantit la quasi-normalité de la moyenne pour n grand (ici 973 à 8 469 trades). La condition qui compte est donc satisfaite.
- Piège : ne pas prétendre que « les données sont normales ». Assumer le rejet et s'appuyer explicitement sur le TCL.

**Q : Concrètement, comment le test de Shapiro « voit »-il la normalité ? Et pourquoi W ≈ 1 = normal ?**
- R : W = b²/SCE compare deux mesures de dispersion : SCE (écarts à la moyenne, classique) et b² (dispersion *attendue si les valeurs triées suivaient une loi normale*, via les espérances des statistiques d'ordre). Elles ne coïncident que sous normalité → W ≈ 1. C'est la **version chiffrée de la droite de Henry (QQ-plot)** : W proche de 1 = les points triés s'alignent sur la droite gaussienne.
- Piège : W est **toujours ≤ 1** ; ne pas écrire « H1 : W < 1 » (toujours vrai). La bonne opposition est W ≃ 1 (H0) vs W ≪ 1 (H1).

**Q : Comment décide-t-on que W est « assez proche » de 1 ?**
- R : Pas de seuil arbitraire sur W. On calcule la **p-value** (proba d'un W aussi bas si les données étaient normales, pour ce n). À grand n, la distribution de W sous H0 se resserre vers 1 → le moindre écart devient significatif → rejet quasi systématique. C'est pourquoi Shapiro est un mauvais juge de normalité sur des milliers de trades.
- Chiffre à dégainer : dans nos données, W va de 0,49 (ma_crossover) à 0,96 (dt_top) — mais les DEUX sont rejetés. Même une distribution « presque normale » (W=0,96) échoue au test à cause du grand n. Preuve concrète que le test sur-rejette. (détail : tableau en annexe)

**Q : Attention au sens de H0 pour Shapiro ?**
- R : Oui, INVERSE de Student. Pour Shapiro, H0 = « c'est normal » (la propriété recherchée). Donc p-value faible → on REJETTE la normalité.

**Q : Le TCL n'est-il pas un ajout artificiel pour contourner le rejet de Shapiro ?**
- R : Non, c'est même le contraire : le TCL *justifie la forme même* de la statistique t. La quantité (ē−µ)/(σ/√n) qui converge vers N(0,1) dans le TCL est exactement t (sous H0, µ=0, avec s à la place de σ). Le test de Student n'est donc rien d'autre que l'application du TCL. Le rejet de Shapiro sur les données individuelles ne l'affecte pas, puisque t ne dépend que de la moyenne.
- Piège : bien dire « le TCL rend la MOYENNE normale, pas les données ».

**Q : Pourquoi une moyenne devient-elle normale alors que les données ne le sont pas ? (intuition du TCL)**
- R : Effet de compensation : en moyennant des milliers d'edges, les valeurs extrêmes (grosses pertes/gains) s'annulent mutuellement ; ce qui survit est une fluctuation régulière et symétrique autour de µ = la cloche. Image des dés : un dé seul = loi plate (uniforme), mais la moyenne de 10 dés = cloche. Moyenner fait émerger la normale, quelle que soit la loi de départ.

**Q : Pourquoi tester `edge` et pas `return_net` ?**
- R : Sur la période, ~97 % des titres montent → un rendement positif ne prouve rien. `edge = return_net − rand_return` neutralise la dérive haussière : on teste un *talent de timing*, pas la chance d'un marché porteur.

**Q : Pourquoi Bonferroni, puisque vous faites 10 tests séparés ?**
- R : Mécaniquement 10 tests indépendants, mais l'interprétation d'ensemble change la question : « au moins un faux positif parmi 10 » vaut ~40 % à α=5 %. Bonferroni ramène le risque global sous 5 % en durcissant le seuil individuel à 0,005 (inégalité de Boole).
- Piège : savoir citer l'analogie des 10 dés (P(au moins un 6) = 84 %).

**Q : D'où vient le 0,40 ? (attention : PAS 0,05×10 = 0,50)**
- R : Calcul par le complémentaire : P(au moins un FP) = 1 − P(aucun FP) = 1 − 0,95¹⁰ ≈ 0,40. On multiplie 0,95 par lui-même (puissance), pas par 10 (l'addition donnerait 0,50, voire >1 avec plus de tests → absurde).
- Le 0,50 = borne de Boole (m×α), c'est un MAJORANT, pas la valeur exacte. Boole ne sert pas à calculer le 0,40 ; il sert à *garantir* le seuil corrigé.

**Q : Le 0,95, il vaut ça sous quelle condition ?**
- R : SOUS H0 vraie. α = P(rejeter H0 | H0 vraie) est conditionnel *par définition*. Le calcul du 0,40 se place donc dans le pire cas : « si aucune stratégie n'a d'edge (H0 vraie partout), quel risque d'en déclarer une gagnante à tort ? ». Si H0 est fausse, il n'y a pas de faux positif possible.
- Piège : ne pas dire « P(faux positif) = 5 % » sans le « sous H0 ».

**Q : Vérification que Bonferroni marche ?**
- R : Avec α'=0,005 : risque global = 1 − 0,995¹⁰ ≈ 0,049 < 0,05. Objectif atteint. Bonferroni est même légèrement conservateur (4,9 % < 5 %), au prix de possibles faux négatifs.

**Q : Faut-il corriger Shapiro et le TCL par Bonferroni ?**
- R : Non. Le TCL n'est pas un test (aucune p-value à corriger). Shapiro est un test de *diagnostic* (condition), pas de *décision finale* — hors de la famille de décisions dont on contrôle le risque global. On ne corrige QUE les 10 tests de Student (le verdict). Corriger Shapiro reviendrait d'ailleurs à faciliter la conclusion « c'est normal », ce qu'on ne veut pas.

**Q : Pourquoi ne pas avoir gardé le test de Wilcoxon / le V de Cramér ?**
- R : Choix d'ancrage aux méthodes explicitement vues dans les cours SAS/Python du M1. Wilcoxon n'y figure pas (vu seulement en R), le V de Cramér dans aucun des trois cours logiciels. Ils ont servi de **vérification interne** mais ne sont pas revendiqués comme méthodes du rapport.
- Piège : rester cohérent — ne pas les présenter comme centraux.

---

## Bloc 1 — Étape 1 bis (dépendance : ICC, DEFF, deux portes, série mensuelle)

**Q : Pourquoi la correction DEFF laisse-t-elle passer `rsi_classic` alors que l'agrégation le rejette ?**
- R : Le DEFF corrige la **variance** mais garde la **pondération** du test naïf (un titre à 200 trades pèse 200 fois plus qu'un titre à 1 trade). Comme ρ intra-titre ≈ 0 pour `rsi_classic`, DEFF ≈ 1 et rien ne change. L'agrégation change la *question* : chaque titre vote une fois, à poids égal. Si l'avantage est concentré sur quelques titres très tradés, le test pondéré dit « oui », le test équipondéré dit « non » → l'avantage ne se généralise pas.
- Piège : ne pas dire que le DEFF était « faux » — il répond à une autre question (variance sous la pondération existante).

**Q : ρ intra-titre ≈ 0, donc les trades étaient indépendants ? Où était le problème ?**
- R : L'ICC par ticker ne voit que la porte ACTION. `rsi_classic` tombe surtout par la porte PÉRIODE (p_B = 0,039 ≫ 0,005) et par l'équipondération. La dépendance a deux portes ; en fermer une ne suffit pas.

**Q : Votre Student sur les moyennes mensuelles suppose les mois indépendants. Le sont-ils ?**
- R : Non — c'est exactement l'objet de l'étape 1d. Des trades durent plus d'un mois → mois voisins corrélés (ρ(1) jusqu'à 0,56 pour `ma_crossover`). Correction par variance de long terme d'un AR(p) : DEFF temporel jusqu'à 6,4. Aucun verdict ne bascule.

**Q : Pourquoi DEUX tests de stationnarité (DF et KPSS) ?**
- R : Leurs H0 sont **opposées** : Dickey–Fuller pose H0 « racine unité » (p petit = stationnaire), KPSS pose H0 « stationnaire » (p grand = stationnaire). Quand les deux concordent, la conclusion ne dépend pas du choix de l'hypothèse nulle — beaucoup plus robuste qu'un test seul.
- Piège : ne pas lire les deux p-values dans le même sens.

**Q : D'où sort la variance « de long terme » σ²η/(1−ΣΦ)² ?**
- R : La variance de la moyenne d'une série autocorrélée fait intervenir TOUTES les autocovariances : Var(x̄) ≈ (1/T)·Σₕ γ(h) (somme sur tous les retards). Pour un AR(p), cette somme vaut exactement σ²η/(1−ΣΦᵢ)². Le s²/T classique n'en est que le cas particulier « tout γ(h≠0) = 0 », c'est-à-dire l'indépendance. Plus ΣΦ approche 1 (persistance forte), plus la correction explose.

**Q : Pourquoi Box–Pierce sur les résidus, et pourquoi χ²(H − p) ?**
- R : Il valide la condition de la correction : si les résidus de l'AR sont un bruit blanc, le modèle a capturé toute l'autocorrélation, donc la variance de long terme est le bon dénominateur. On retire p degrés de liberté car p paramètres Φ ont été estimés sur les mêmes données.

**Q : Pourquoi ne pas pondérer les moyennes de titres par leur nombre de trades ?**
- R : Ce serait réintroduire le test naïf (les gros titres redomineraient). L'équipondération est le choix le plus prudent : « une unité réelle, un vote ». Pour un outil de VALIDATION, on préfère perdre de la puissance que laisser passer un faux positif.

**Q : Pourquoi le bootstrap par grappes préserve-t-il la dépendance ?**
- R : On tire des tickers ENTIERS avec remise : l'intérieur de chaque grappe (et sa dépendance) voyage intact dans chaque réplique. On ne simule jamais l'indépendance entre trades — seule reste l'hypothèse d'indépendance entre titres.

**Q : `rsi_strict` passe la porte titre avec p = 4×10⁻⁴, ce n'est pas suffisant ?**
- R : Non : le protocole exige les DEUX portes. Son edge est partagé par beaucoup de titres (porte action OK) mais concentré sur quelques mois (p_B = 0,26, présent 138 mois sur 195) : avantage **épisodique**, sans régularité temporelle démontrable — inexploitable tel quel.

**Q : Mois sans trade traités comme consécutifs — ça ne fausse pas l'ACF ?**
- R : Limite assumée, signalée dans le rapport. Couverture > 88 % partout sauf `rsi_strict` (71 %) ; l'approximation raccourcit certains écarts temporels et tendrait plutôt à SURestimer l'autocorrélation, donc la correction — sens conservateur pour notre usage (validation).

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

**Q : Vous passez le Bloc 1 à éliminer la dépendance et le Bloc 3 à la chercher. N'est-ce pas contradictoire ?**
- R : Non — la dépendance joue deux rôles opposés selon la question posée. Pour **juger** (Bloc 1), elle est une nuisance : chaque trade doit être un témoin indépendant, sinon pseudo-réplication et faux positifs ; l'indépendance y est une *condition d'application* qu'on vérifie et répare. Pour **prédire** (Bloc 3, lead-lag), elle est la ressource : un marché où tout est indépendant = marché efficient = rien à trader ; l'indépendance y est *l'hypothèse nulle* qu'on cherche à rejeter (Granger).
- Le raffinement : distinguer par **retard**. La dépendance *simultanée* (chocs communs, facteur marché à 73 % de l'ACP) est intradable ET toxique pour l'inférence — c'est la porte « période » du Bloc 1. La dépendance *retardée* (lead-lag) est le seul gisement exploitable, car le délai laisse le temps de passer l'ordre.
- Boucle à citer : le facteur marché mesuré par l'ACP du Bloc 3 EST la cause commune que le Bloc 1 a dû neutraliser. Et toute dépendance retardée transformée en stratégie devra repasser par l'outil de validation du Bloc 1. Les deux blocs sont les deux faces du même objet.



**Q : Quelle est votre principale limite ?**
- R : Résultats *in-sample*. Une validation *walk-forward* (hors échantillon, respectant l'ordre temporel) est nécessaire avant tout usage. Les k-fold classiques fuiteraient l'information du futur.

**Q : Autonomie — qu'avez-vous fait seul ?**
- R : [à personnaliser] conception de l'architecture en blocs, construction des bases, choix et implémentation des méthodes, interprétation.
