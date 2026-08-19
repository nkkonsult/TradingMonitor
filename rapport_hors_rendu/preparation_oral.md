# Préparation de l'oral — anticipation des questions du jury

> **Hors rapport.** Ce fichier ne fait PAS partie du mémoire LaTeX. Il sert
> à préparer les 10 minutes de questions (soutenance : 20 min exposé + 10 min
> questions, en français, à huis clos). Les consignes valorisent
> *l'autonomie* et *la pertinence des réponses aux questions*.
>
> Format : pour chaque méthode, la **question probable**, la **réponse
> courte** à donner, et le **piège à éviter**.

---

## Fiche « fonctionnement des stratégies » (au cas où le jury demande)

> ⚠️ Le rapport ne détaille PAS les mécaniques (c'est de l'analyse technique, hors
> sujet stat). Mais le jury PEUT demander « comment marche telle stratégie ? ».
> Savoir expliquer 2-3 familles en une phrase suffit. Règles réelles (code
> `backend/charts/strategy/`) :

- **RSI** (`rsi_classic` 30/70, `rsi_strict` 20/80, `rsi_trend` + filtre MM200) :
  l'indicateur RSI mesure si un titre est « survendu » (bas) ou « suracheté » (haut).
  Achat quand le RSI **ressort de la survente** (repasse au-dessus du seuil bas),
  vente quand il ressort du surachat. `rsi_trend` n'achète qu'au-dessus de la
  moyenne mobile 200 jours (filtre de tendance).
- **Croisement de moyennes mobiles** (`ma_crossover`) : achat quand la moyenne
  mobile courte passe au-dessus de la longue (*golden cross*), vente au croisement
  inverse (*death cross*).
- **Figures chartistes** (`db_bottom`/`dt_top` = double creux/sommet ;
  `hs_classic`/`hs_inverse` = épaule-tête-épaule) : détection de motifs graphiques
  de retournement (deux creux successifs = signal d'achat, etc.).
- **Cassures** (`sr_breakout`/`sr_breakdown`) : achat quand le cours franchit une
  résistance vers le haut, vente quand il casse un support vers le bas.
- **`oracle`** (témoin) : triche en regardant le cours des 30 jours à venir,
  n'entre que si ça monte d'au moins **5 %** (v2), avec ~1 an de repos entre deux
  entrées pour garder un volume comparable aux vraies stratégies. Sert à prouver
  que l'outil sait valider un vrai avantage (faux négatif impossible).
  (La v1 à +25 % a été abandonnée : voir la fiche méthodes, histoire des deux oracles.)

**LA réponse-parade si le jury insiste sur une mécanique** :
> « Le fonctionnement précis de chaque stratégie relève de l'analyse technique ;
> mon outil est **agnostique au signal** — il juge un edge, quelle qu'en soit la
> provenance. C'est une force du protocole, et l'oracle le prouve : il "fonctionne"
> par un mécanisme tout autre (la triche), et l'outil le juge sans difficulté. »
- Détail important : les 10 vraies stratégies n'utilisent QUE de l'information
  **passée** (pas de fuite du futur) ; seul l'oracle regarde l'avenir, volontairement.

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

**Q : Pourquoi diviser par l'écart-type ? Pourquoi ne pas garder ē seul ?**
- R : ē seul n'est pas interprétable : +0,012 est-il « loin » de 0 ? Ça dépend de la dispersion. Diviser par s/√n convertit ē en **nombre d'écarts-types au-dessus de 0** → une échelle universelle qui permet de calculer une p-value. Sans cette mise à l'échelle, aucune référence pour juger « loin ».

**Q : Pourquoi une loi de Student et pas une normale ?**
- R : Si on connaissait le vrai σ, (ē−µ)/(σ/√n) serait **normale** exacte. Mais σ est inconnu, remplacé par **s estimé sur le même échantillon** → on divise une variable (ē) par une autre variable (s) → la loi du rapport est **Student** (n−1 ddl), une cloche à queues un peu plus épaisses qui absorbe l'incertitude sur s. Student = normale corrigée du fait que s est estimé.
- Nuance à dégainer : à grand n, s ≈ σ → Student ≈ normale (indiscernables au-delà de n≈100). À nos n (978 à 8 513), aucune différence pratique — d'où l'emploi de « normale » via le TCL, rigoureusement une Student.
- Piège : le **TCL** parle de la normalité de **ē** ; le nom **Student** parle de la loi du **t** (car s estimé). Les deux ne se contredisent pas.

**Q : Comment estime-t-on l'écart-type s ?**
- R : Écart-type empirique : s = √[ (1/(n−1)) Σ(eᵢ−ē)² ]. On divise par **n−1** (correction de Bessel), pas n : les écarts sont calculés par rapport à ē elle-même estimée sur les données → sans correction, on sous-estimerait la vraie dispersion. C'est le **même n−1** que les degrés de liberté de la loi de Student (un degré « consommé » pour estimer ē).

**Q : La condition de Student, c'est la normalité des données ou de la moyenne ?**
- R : Formellement le test suppose la normalité des **observations** (l'edge). Mais ce qui rend réellement t valide, c'est la normalité de la **moyenne** ē — garantie par le TCL à grand n même si les observations ne sont pas normales. Raisonnement en 3 temps : condition posée sur l'edge → Shapiro la teste, échec → TCL la sauve via la moyenne.

**Q : Shapiro rejette la normalité partout. Comment justifiez-vous alors un test de Student ?**
- R : Le Student ne suppose pas la normalité des données brutes mais celle de *la moyenne*. Le **théorème central limite** garantit la quasi-normalité de la moyenne pour n grand (ici 978 à 8 513 trades). La condition qui compte est donc satisfaite.
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

## Bloc 1 — Valeurs aberrantes / extrêmes (question posée à d'autres candidats)

**Q : Vos données contiennent-elles des valeurs aberrantes ? Comment les avez-vous traitées ?**
- R : D'abord distinguer deux notions. Une valeur **aberrante** est une erreur (saisie, mesure) : à corriger ou supprimer. Une valeur **extrême** est une vraie réalisation d'une distribution à queues lourdes : de l'information. Mes données contiennent des valeurs extrêmes, pas d'aberrantes : les edges sont calculés à partir de cours réels, bornés par construction (un titre ne peut pas perdre plus de 100 %, les durées sont bornées) ; en revanche les distributions sont très asymétriques et à queues lourdes — c'est structurel en finance, et c'est visible dans le W de Shapiro (0,50 pour `ma_crossover`, 0,59 pour l'oracle).
- Je ne les ai **pas supprimées ni winsorisées**, et c'est un choix : un edge extrême est souvent LE moteur du gain d'une stratégie. L'écarter fausserait le jugement dans les deux sens. Le protocole est construit pour être **robuste aux extrêmes** plutôt que pour les nettoyer.
- Piège : ne jamais dire « il n'y en a pas » ni « je les ai enlevées ». Dire : « je les ai gardées, et voici les quatre protections du protocole ».

**Q : Quelles protections, concrètement ?**
- R : Quatre, par étage. (1) Le test porte sur la **moyenne** : un point extrême tire ē mais gonfle aussi s au dénominateur — effet plutôt conservateur sur t. (2) Le **bootstrap** ne suppose aucune forme : les extrêmes sont dans les répliques, la cloche les intègre d'elle-même. (3) L'**agrégation équipondérée** retire aux extrêmes leur poids : un méga-trade ne pèse que dans SA grappe (son titre, son mois), qui n'a qu'une voix. (4) Une stratégie dont l'avantage ne tient qu'à quelques points extrêmes est **exactement ce que les deux portes détectent** — c'est le cas vécu de `rsi_strict` : avantage réel mais concentré sur quelques mois, rejeté pour ça.

**Q : Un seul trade extrême peut-il faire basculer un verdict ?**
- R : Sur le test naïf, avec n de l'ordre de 7 000, un trade pèse 1/n dans la moyenne et gonfle s : très improbable. Et si un petit groupe d'extrêmes portait l'avantage, l'agrégation le neutralise — l'unité de vote devient le titre ou le mois, plus le trade.

**Q : Pourquoi ne pas tester la médiane, ou utiliser un test robuste ?**
- R : Parce que le paramètre économiquement pertinent est la **moyenne** : le gain total d'une stratégie = somme des edges = n × moyenne. Une stratégie peut avoir une médiane négative et être rentable grâce à quelques grands gains (asymétrie positive) — un test sur la médiane la déclarerait perdante à tort. La moyenne est le seul paramètre qui agrège correctement les extrêmes AVEC le reste. (Wilcoxon : vu seulement en R, utilisé en vérification interne, non revendiqué — cohérent avec le reste du discours.)

**Q : Les queues lourdes ne menacent-elles pas le TCL ?**
- R : Le TCL exige une **variance finie** — garantie ici car les rendements d'un trade sont bornés. Les queues lourdes ralentissent la convergence, elles ne l'empêchent pas : c'est exactement pourquoi il faut n grand, et pourquoi une des perspectives est un garde-fou d'effectif. Ici n va de 978 à 8 513.
- Bonus si on insiste : l'oracle est le cas le plus extrême (W = 0,59, distribution tronquée par construction — que des trades gagnants), et le protocole le juge sans difficulté.

**Q : Comment détecteriez-vous des valeurs aberrantes si vous deviez le faire ?**
- R : Boîte à moustaches / règle 1,5 × IQR, ou écart à la moyenne en unités d'écart-type. Mais en finance cette règle marquerait des centaines de points parfaitement légitimes : elle détecte les extrêmes, pas les erreurs. La vraie vérification d'aberrance, je l'ai faite en amont, au niveau des données sources : cours réels, edges bornés, aucune valeur impossible.

---

## Bloc 1 — Étape 1 bis (dépendance : ICC, DEFF, deux portes, série mensuelle)

**Q : Pourquoi la correction DEFF laisse-t-elle passer `rsi_classic` alors que l'agrégation le rejette ?**
- R : Le DEFF corrige la **variance** mais garde la **pondération** du test naïf (un titre à 200 trades pèse 200 fois plus qu'un titre à 1 trade). Comme ρ intra-titre ≈ 0 pour `rsi_classic`, DEFF ≈ 1 et rien ne change. L'agrégation change la *question* : chaque titre vote une fois, à poids égal. Si l'avantage est concentré sur quelques titres très tradés, le test pondéré dit « oui », le test équipondéré dit « non » → l'avantage ne se généralise pas.
- Piège : ne pas dire que le DEFF était « faux » — il répond à une autre question (variance sous la pondération existante).

**Q : ρ intra-titre ≈ 0, donc les trades étaient indépendants ? Où était le problème ?**
- R : L'ICC par ticker ne voit que la porte ACTION. `rsi_classic` tombe surtout par la porte PÉRIODE (p_B = 0,039 ≫ 0,005) et par l'équipondération. La dépendance a deux portes ; en fermer une ne suffit pas.

**Q : Dans la formule de l'ICC, c'est quoi n₀ exactement ? (formule NON mise dans le rapport)**
- R : n₀ = la taille MOYENNE AJUSTÉE des grappes (≈ nb de trades par titre), corrigée de l'inégalité des tailles de grappes. Formule :
  n₀ = (1/(k−1)) · ( N − (Σ nᵢ²)/N )
  où k = nb de titres, N = nb total de trades, nᵢ = nb de trades du titre i.
- Pourquoi pas la moyenne brute N/k : les grappes sont très inégales (50 trades sur un titre, 3 sur un autre) ; le terme Σnᵢ²/N pénalise ce déséquilibre. Si toutes les grappes ont la même taille n, alors n₀ = n.
- Rôle : n₀ pondère MSW dans le dénominateur `MSB + (n₀−1)·MSW`. Grosses grappes → n₀ grand → mesure plus exigeante (il faut plus de contraste inter-titres pour un même ρ̂). n₀=1 (un trade/titre) → terme intra disparaît (la corrélation intra-titre n'a pas de sens).

**Q : Votre Student sur les moyennes mensuelles suppose les mois indépendants. Le sont-ils ?**
- R : Non — c'est exactement l'objet de l'étape 1d. Des trades durent plus d'un mois → mois voisins corrélés (ρ(1) jusqu'à 0,56 pour `ma_crossover`). Correction par variance de long terme d'un AR(p) : DEFF temporel jusqu'à 6,4. Aucun verdict ne bascule.

**Q : Pourquoi DEUX tests de stationnarité (DF et KPSS) ?**
- R : Leurs H0 sont **opposées** : Dickey–Fuller pose H0 « racine unité » (p petit = stationnaire), KPSS pose H0 « stationnaire » (p grand = stationnaire). Quand les deux concordent, la conclusion ne dépend pas du choix de l'hypothèse nulle — beaucoup plus robuste qu'un test seul.
- Piège : ne pas lire les deux p-values dans le même sens.

**Q : Le test ADF retient 9 retards pour `rsi_trend`, mais le modèle AR est plafonné à 6 et n'en retient que 4. Contradiction ?**
- R : Non, **deux « retards » différents**, produits par deux procédures aux objectifs opposés. (1) Les 9 retards de l'**ADF** sont un paramètre de *nuisance* : ils servent uniquement à nettoyer les résidus de la régression de Dickey–Fuller pour que son test sur φ soit valide. Ils ne mesurent aucun impact et sont jetés ensuite. (2) L'ordre p̂ = 4 vient du **PACF** et mesure la *mémoire réelle* de la série — c'est lui qui alimente la correction.
- Vérification : Box–Pierce sur les résidus de l'AR(4) de `rsi_trend` donne p = 0,06 sur 15 décalages → le modèle à 4 mois a bien absorbé la mémoire. (C'est la valeur la plus basse du tableau, donc le cas le plus limite, mais elle passe.)
- Piège : ne pas dire « on laisse passer 9 mois d'autocorrélation » — les 9 retards ne sont pas de l'autocorrélation mesurée, mais un correctif interne au test de stationnarité.

**Q : Comment justifiez-vous le plafond de 6 mois pour la recherche de l'ordre ?**
- R : Deux temps. (1) **Substantiel** : la dépendance vient du recouvrement des périodes de détention ; elle ne peut donc pas porter au-delà de la durée des trades, qui dépassent rarement 6 mois. Chercher plus loin = chercher un effet sans cause. (2) **Vérifié a posteriori** : c'est l'argument qui compte, car le premier n'est qu'une plausibilité. Si une mémoire subsistait au-delà de 6, le modèle ne l'aurait pas absorbée et elle apparaîtrait dans ses **résidus** — or Box–Pierce les inspecte sur **15** décalages. Le plafond n'est pas un pari, il est contrôlé.
- Piège : ne pas justifier le plafond par « trop de coefficients ajoutent du bruit » — c'est l'arbitrage que fait déjà la règle de décision décalage par décalage (p-value), donc l'argument serait redondant.

**Q : Pourquoi le critère d'Akaike pour choisir le nombre de retards de l'ADF ?**
- R : Arbitrage entre deux erreurs : trop peu de retards → mémoire non absorbée, résidus autocorrélés, test faussé ; trop → chaque coefficient estimé sur les mêmes T mois ajoute du bruit. AIC = 2 ln σ̂ₖ + k/T (forme du cours de séries temporelles, § estimation ARMA, étape 5) : le 1ᵉʳ terme baisse quand le modèle colle mieux, le 2ᵉ monte avec k → on minimise la somme, donc un retard n'est gardé que s'il apporte plus qu'il ne coûte.
- Sans pénalité, on prendrait toujours le modèle le plus riche — qui colle aussi au **bruit** (surapprentissage).
- Si on demande « pourquoi AIC et pas BIC ? » : le BIC pénalise plus fort (ln T au lieu de 2) donc serait plus parcimonieux ; AIC est ce que prescrit le cours, et le plafond à 6 borne déjà la complexité du modèle retenu.
- Référence : Akaike (1974), *IEEE Trans. Automatic Control*.

**Q : Le test de Dickey–Fuller, c'est un test de Student sur une pente ?**
- R : **Même forme, autre loi.** La statistique t_DF = (φ̂ − 1)/se(φ̂) a exactement la structure d'un Student (écart à la référence ÷ erreur-type) — les auteurs la nomment d'ailleurs *t-ratio*. Mais sous H0 la série n'est **pas** stationnaire (sa variance croît avec le temps), donc les conditions de la loi de Student tombent. Dickey et Fuller ont établi et tabulé la vraie loi : décalée vers les négatifs et asymétrique. Conséquence chiffrée : il faut dépasser ≈ −2,9 pour rejeter à 5 %, là où un Student rejetterait dès −1,65. C'est tout l'apport de leur article, et ce qui vaut son nom au test.

**Q : Pourquoi φ < 1 ⟹ stationnaire ? (démonstration en une ligne)**
- R : Dérouler la récurrence x_t = φ x_{t−1} + η_t donne x_t = η_t + φ η_{t−1} + φ² η_{t−2} + … : le mois courant est la somme de TOUS les chocs passés, chacun pesé par φ^(ancienneté). Si |φ| < 1, ces puissances → 0 : les chocs s'éteignent, la série revient vers sa moyenne. Si φ = 1, toutes les puissances valent 1 : chaque choc s'ajoute définitivement au niveau → dérive.

**Q : « Racine unitaire » et « non stationnaire », c'est pareil ?**
- R : Non, **asymétrie importante**. La racine unitaire (φ = 1) est UNE façon d'être non stationnaire — celle que teste DF. Le nom vient de l'écriture (1 − φB)x_t = η_t : le polynôme 1 − φz a pour racine z = 1/φ, qui vaut exactement 1 si φ = 1 (vocabulaire du cours : « P n'a aucune racine dans le disque unité »). Mais une tendance déterministe, une variance changeante ou une saisonnalité déformée sont aussi non stationnaires SANS racine unitaire. Racine unitaire ⟹ non stationnaire, l'inverse est faux.
- Ce qui sauve le raccourci dans mon rapport : **KPSS teste la stationnarité au sens large** (il couvre tendance et dérive). Quand les deux tests concordent, on a bien conclu sur la stationnarité, pas seulement sur la racine unitaire. Argument de plus en faveur de la règle de concordance.

**Q : Pourquoi un pré-test d'indépendance AVANT toute la machinerie AR ?**
- R : Principe du chapitre : **on ne corrige que ce qui est mesuré** (même logique que le DEFF, appliqué seulement si ρ le justifie). Le raisonnement du recouvrement rend l'autocorrélation *plausible*, pas *certaine*, et elle varie d'une stratégie à l'autre. Box–Pierce sur la série brute (6 décalages, aucun modèle requis) tranche : si l'indépendance n'est pas rejetée, la condition du test 1c est remplie telle quelle → son verdict tient, ni AR ni stationnarité à exiger. Sinon seulement, la branche AR s'applique.
- Bénéfice concret : cela évite d'exiger la stationnarité de séries qui n'ont besoin d'aucune correction (3 stratégies sur 11 sortent par cette branche).

**Q : Quelle différence entre Box–Pierce et le canal 3 du chapitre 2 ?**
- R : Le canal 3 **mesure** (ρ̂(1) = intensité, un seul décalage, sans seuil) ; Box–Pierce **tranche** (6 décalages simultanément, avec un seuil qui intègre T). Une même valeur ρ̂ = 0,15 est significative sur 500 mois et pas sur 100 — la mesure brute ne peut pas le dire. Et une dépendance peut être absente au décalage 1 mais présente aux décalages 2-3 : le canal 3 ne la verrait pas.
- Exemple vécu : l'ancien oracle avait ρ̂(1) = 0,03 (apparemment rien) et pourtant Box–Pierce rejetait l'indépendance (p = 0,015) — sa dépendance était logée plus loin. À l'inverse `hs_classic` a ρ̂(1) = 0,15 mais p = 0,053 : pas significatif sur 172 mois.

**Q : Que fait le protocole si les deux tests de stationnarité divergent ?**
- R : Il **fait sortir la stratégie** avec un verdict « ? » et signale la raison ; l'examen revient à l'humain. Elle n'est ni validée ni rejetée — « non concluant » ≠ « défavorable ». Justification : « ne pas rejeter » n'a jamais valeur de preuve ; deux tests qui ne pointent pas dans la même direction ne prouvent rien, et transformer cette absence de preuve en rejet serait une faute de lecture.
- Cas vécu à citer : l'oracle v1 (t = 122) mettait DF en échec — série trop tassée, pas de bras de levier pour estimer la pente → manque de puissance, pas dérive. Un protocole à un seul test l'aurait écarté silencieusement ; c'est KPSS qui rend l'anomalie visible. **Le témoin a servi à révéler une limite du protocole** — d'où l'oracle v2, à l'avantage plus modeste et donc plus réaliste.

**Q : D'où sort la variance « de long terme » σ²η/(1−ΣΦ)² ?**
- R : La variance de la moyenne d'une série autocorrélée fait intervenir TOUTES les autocovariances : Var(x̄) ≈ (1/T)·Σₕ γ(h) (somme sur tous les retards). Pour un AR(p), cette somme vaut exactement σ²η/(1−ΣΦᵢ)². Le s²/T classique n'en est que le cas particulier « tout γ(h≠0) = 0 », c'est-à-dire l'indépendance. Plus ΣΦ approche 1 (persistance forte), plus la correction explose.

**Q : Pourquoi Box–Pierce sur les résidus, et pourquoi χ²(H − p) ?**
- R : Il valide la condition de la correction : si les résidus de l'AR sont un bruit blanc, le modèle a capturé toute l'autocorrélation, donc la variance de long terme est le bon dénominateur. On retire p degrés de liberté car p paramètres Φ ont été estimés sur les mêmes données.

**Q : Pourquoi ne pas pondérer les moyennes de titres par leur nombre de trades ?**
- R : Ce serait réintroduire le test naïf (les gros titres redomineraient). L'équipondération est le choix le plus prudent : « une unité réelle, un vote ». Pour un outil de VALIDATION, on préfère perdre de la puissance que laisser passer un faux positif.

**Q : Pourquoi la distribution bootstrap est-elle une cloche ? Un tirage peut-il « dépasser le sommet » ?**
- R : Lire les axes : horizontal = la VALEUR de la moyenne d'une réplique,
  vertical = sa FRÉQUENCE sur les 4 000 tirages. Chaque tirage donne UN nombre,
  un point sur l'axe horizontal. Le sommet n'est pas un maximum : c'est la
  valeur la plus fréquente. Un tirage extrême tombe dans la queue — et la
  courbe y est basse parce que c'est rare. La hauteur mesure la rareté, pas
  une borne.
- Pourquoi une cloche : chaque moyenne de réplique moyenne ~500 titres tirés
  indépendamment → TCL appliqué ENTRE les grappes (l'unité indépendante est le
  titre, plus le trade).
- Le point clé : le bootstrap n'a PAS BESOIN de cette normalité. La p-value
  est un comptage (proportion des moyennes ≤ 0), valide quelle que soit la
  forme. C'est le sens exact de « aucune hypothèse de forme ».

**Q : D'où vient la largeur de la cloche ? (la loterie des titres lourds)**
- R : D'une réplique à l'autre, un titre lourd est tiré 0, 1 ou plusieurs
  fois. Quand il manque (ou est sur-tiré), la moyenne de la réplique bouge
  fortement — il emporte tous ses trades. Plus le résultat repose sur peu de
  titres, plus les moyennes fluctuent → cloche plus LARGE (dire « large »,
  pas « aplatie » : l'aire reste 1, c'est l'erreur-type qui grossit) → plus
  de masse sous zéro → p-value plus grande. C'est ainsi que le bootstrap
  matérialise la dépendance intra-titre.
- NUANCE piège (dans le rapport) : cas pervers où un titre domine tellement
  qu'il est présent et dominant dans presque toutes les répliques → les
  moyennes se collent à SA moyenne → cloche trompeusement ÉTROITE autour d'une
  valeur positive. D'où « une cloche étroite ne suffit pas » → c'est la porte
  de l'action (équipondération) qui lève ce doute.

**Q : Pourquoi le bootstrap par grappes préserve-t-il la dépendance ?**
- R : On tire des tickers ENTIERS avec remise : l'intérieur de chaque grappe (et sa dépendance) voyage intact dans chaque réplique. On ne simule jamais l'indépendance entre trades — seule reste l'hypothèse d'indépendance entre titres.

**Q : Pourquoi l'ACP sur les 11 SECTEURS et non sur les ~500 ACTIONS ?**
- R : Trois raisons. (1) Stabilité : 500 actions = matrice 500×500 (250 000 corrélations), mal conditionnée → ACP instable ; 11 secteurs = matrice 11×11, propre. (2) Interprétabilité : « facteur marché » et « défensifs vs cycliques » se lisent d'un coup sur 11 secteurs nommés ; sur 500 tickers, nuage illisible. (3) L'objectif du canal 2 est la GROSSE structure (le facteur marché, cause de la dépendance simultanée), parfaitement captée au niveau sectoriel.
- Revers assumé : l'agrégation NOIE les micro-couples d'actions liées. Un couple parfaitement corrélé mais isolé donnerait un axe à part entière (2 loadings forts, les autres ≈ 0), mais sa part de variance serait infime (noyée dans le bruit de centaines d'axes) → invisible sauf recherche ciblée. L'ACP voit les grosses structures, pas les micro-liens.
- Conséquence : détecter les liens fins entre actifs précis n'est PAS un travail d'ACP (matrice de corrélation par paires / clustering) → hors périmètre de ce mémoire (perspectives).

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



**Q : Au final, qu'avez-vous à dire ? / Que retenez-vous de ce travail ? (LA réponse de clôture)**
- R (≈ 40 secondes, à dire avec calme) : « Ce que je retiens : je ne livre pas une
  stratégie, je livre un **juge**. Ses limites sont réelles — quand les corrections
  s'empilent, le seuil de 5 % n'est plus garanti à la décimale près. Mais deux
  choses le rendent utilisable. D'abord, chaque étage pris **isolément** est
  contrôlé, et dans nos données les trois dépendances ne se cumulent jamais
  fortement : les verdicts restent donc chiffrés. Ensuite, toutes les
  approximations restantes penchent du **même côté, celui de la prudence** :
  l'outil préfère écarter une stratégie honnête que valider une stratégie
  illusoire. Pour un outil de validation, c'est le bon côté où se tromper — un
  faux positif coûte de l'argent réel, un faux négatif ne coûte qu'une occasion.
  Et le témoin montre que cette prudence ne rend pas l'outil aveugle : un
  avantage réel franchit tous les étages. »
- Pièges : ne PAS dire « on ne peut pas quantifier les risques » (trop absolu —
  chaque test est contrôlé ; c'est l'empilement qui perd la garantie *exacte*
  du seuil nominal, et seulement si les trois canaux étaient forts en même
  temps, cas signalé et absent ici). Ne PAS dire « stratégies frauduleuses »
  (la fraude suppose une intention) : dire stratégies **illusoires**, ou « dont
  l'avantage était un artefact d'échantillonnage ou de dépendance ».

**Q : Quelle est votre principale limite ?**
- R : Résultats *in-sample*. Une validation *walk-forward* (hors échantillon, respectant l'ordre temporel) est nécessaire avant tout usage. Les k-fold classiques fuiteraient l'information du futur.

**Q : Autonomie — qu'avez-vous fait seul ?**
- R : [à personnaliser] conception de l'architecture en blocs, construction des bases, choix et implémentation des méthodes, interprétation.
