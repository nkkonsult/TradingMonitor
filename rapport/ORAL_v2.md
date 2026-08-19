# Texte de soutenance — 20 minutes

> **Mode d'emploi.** Le texte à dire est en paragraphes normaux. Les repères
> `[DIAPO n]` indiquent le changement de diapositive (on les fera ensuite).
> Les blocs `📌 NOTE` ne sont PAS à dire : ce sont les réponses à tes
> questions « (claude …) », à connaître pour les questions du jury.
> Minutage indicatif en tête de chaque section. Total ≈ 2 800 mots ≈ 19 min
> à débit normal (150 mots/min), ce qui laisse une marge.

---

## 0. Ouverture — 0:00 → 1:00

**[DIAPO 1 : titre, nom, master, date]**

Bonjour. Je vais vous présenter le travail réalisé pendant mon stage :
la construction d'un protocole statistique de validation de stratégies de
trading.

Voici le plan. Je poserai d'abord rapidement le contexte et les données.
Ensuite, plutôt que de présenter les méthodes comme un catalogue, j'ai
choisi de les dérouler comme un dialogue entre un trader amateur et un
statisticien : l'amateur propose une preuve que sa stratégie fonctionne, le
statisticien trouve la faille, et chaque faille appelle une méthode plus
exigeante que la précédente. C'est ce que j'appelle dans mon rapport
l'escalade de prudence. Je terminerai par les résultats, les limites du
protocole et ses perspectives.

**[DIAPO 2 : plan en 4 points]**

---

## 1. Contexte — 1:00 → 3:00

**[DIAPO 3 : schéma agent IA → stratégies → protocole (filtre)]**

Le contexte, en quelques mots. Mon stage avait pour objectif de construire
un agent IA capable de faire du trading, c'est-à-dire un programme autonome
qui décide seul d'acheter ou de vendre des titres en bourse. Un agent IA,
c'est une intelligence artificielle à laquelle on donne des consignes et
des capacités d'action.

Pour faire du trading, cet agent devra construire des stratégies : des
règles de décision qui, à partir des seules données disponibles au moment
de la décision, prédisent l'évolution du marché.

Et c'est là qu'arrive le sujet de ce mémoire. Avant de laisser un agent
appliquer une stratégie avec de l'argent réel, il faut pouvoir répondre à
une question : cette stratégie a-t-elle réellement un pouvoir de
prédiction, ou son résultat n'est-il qu'un accident ? Ma contribution
n'est donc pas une stratégie gagnante ; c'est l'outil de validation, la
chaîne de tests qui rend ce verdict, avec la vérification de toutes ses
conditions d'application.

📌 **NOTE — pourquoi cette formulation.** Elle cadre exactement ce que le
jury notera : « pertinence des méthodes, justification, vérification des
conditions d'application ». Tu annonces dès la première minute que c'est ça,
ton sujet.

---

## 2. Les données — 3:00 → 5:30

**[DIAPO 4 : tableau des 11 stratégies + chiffres clés de la base]**

Passons aux données sur lesquelles le protocole va être éprouvé.

Comme l'agent n'a pas encore créé ses propres stratégies, j'ai constitué un
banc d'essai : dix stratégies classiques d'analyse technique — des règles
fondées sur l'indicateur RSI, des croisements de moyennes mobiles, des
figures chartistes, des cassures de support et de résistance. Je précise
que ces stratégies ne sont pas l'objet d'étude : elles fournissent des jeux
de données réels pour montrer que l'outil discrimine correctement.

J'y ai ajouté une onzième stratégie, un témoin que j'appelle l'oracle : il
triche, il regarde le cours des jours à venir avant d'entrer en position.
Son avantage est donc réel par construction. Il sert à vérifier que le
protocole ne rejette pas tout par excès de sévérité : un outil qui dirait
toujours non serait inutile.

Ces onze stratégies sont appliquées en backtesting sur les titres du
S&P 500, l'indice des cinq cents plus grandes capitalisations américaines —
501 titres exactement — de janvier 2010 à juillet 2026. On obtient une base
de 45 008 trades, entre 978 et 8 513 par stratégie. L'unité statistique,
c'est le trade : une position ouverte sur un titre à une date, refermée à
une autre, avec son rendement.

📌 **NOTE — si on te demande pourquoi ces stratégies « d'internet ».** Ne
dis jamais « trouvées rapidement sur internet » : dis « des règles
classiques à peu de paramètres, non ajustées sur l'échantillon » — c'est
précisément ce qui limite le risque de sur-apprentissage, et c'est écrit
dans tes limites.

Un dernier point avant de commencer : à l'avenir, nos stratégies seront
construites à partir de données, qu'il faudra alors exclure de la zone de
test. Ici les stratégies relèvent de règles fixes, le problème ne se pose
pas encore ; j'y reviendrai dans les perspectives.

Le décor est planté. Le dialogue peut commencer.

---

## 3. Le dialogue, acte I : battre le hasard — 5:30 → 10:00

### Le gain positif ne prouve rien

**[DIAPO 5 : courbe du S&P 500 sur la période, tendance haussière]**

L'amateur ouvre le dialogue : « Ma stratégie a gagné de l'argent sur la
période, donc elle fonctionne. » C'est l'argument qu'on retrouve dans
toutes les publicités douteuses en ligne.

Le statisticien répond : encore faut-il que ce gain dépasse ce qu'une
entrée au hasard aurait rapporté. Sur notre période, le S&P 500 est
fortement haussier : une stratégie peut gagner sans avoir capté le moindre
signal, simplement parce que tout monte. Pour prouver quelque chose, il
faut battre le hasard.

### L'avantage : l'edge

**[DIAPO 6 : définition de l'edge, schéma trade réel vs 200 trades fictifs]**

D'accord, dit l'amateur : mesurons ce que le hasard aurait fait. Pour
chaque trade réel, on génère 200 trades fictifs de même exposition — même
titre, même durée, même sens — mais dont la date d'entrée est tirée au
sort. La moyenne de leurs rendements définit le gain du hasard pour ce
trade. On définit alors l'avantage, l'edge : le rendement obtenu par la
stratégie, moins ce gain du hasard. Un edge positif signifie que le timing
de la stratégie apporte une information que la dérive du marché n'explique
pas. C'est sur l'edge, et jamais sur le gain brut, que porteront tous les
tests.

Mais, répond le statisticien, même un edge moyen positif peut n'être qu'un
tirage chanceux. Il faut un test.

### Le test de Student

**[DIAPO 7 : hypothèses H0/H1, statistique t, p-value]**

On distingue deux quantités : l'edge moyen observé sur l'échantillon, que
je note e-barre, qui est connu ; et l'edge moyen théorique de la stratégie,
mu, qui est inconnu — c'est lui qu'on veut atteindre. On oppose H0 : mu
égal zéro, la stratégie ne fait pas mieux que le hasard, à H1 : mu
strictement positif. Le test est unilatéral, car seul un avantage positif
nous intéresse.

La statistique de test, c'est t égale e-barre divisé par s sur racine de
n : le nombre d'erreurs-types qui séparent l'edge moyen observé de zéro.
Sous H0, elle suit une loi de Student à n moins un degrés de liberté. Si la
p-value est très faible, le hasard n'est plus une explication crédible, et
on conclut que l'edge théorique est positif.

Ce test suppose deux conditions : un critère de normalité, et
l'indépendance des trades. On va les prendre au sérieux l'une après
l'autre — c'est tout le fil de la suite.

### La normalité : Shapiro–Wilk, puis le TCL

**[DIAPO 8 : tableau Shapiro (W et p-values) + énoncé du TCL]**

D'abord la normalité. Je la teste avec Shapiro–Wilk, dont la statistique W
compare deux mesures de dispersion qui ne coïncident que sous normalité —
H0 étant ici, attention, la normalité elle-même. Résultat : rejet pour les
onze stratégies. Et c'était prévisible : à des tailles de 1 000 à 8 000
trades, le moindre écart à la normale rend la p-value négligeable — même
dt_top, avec un W de 0,95, est rejetée.

Est-ce que cela invalide Student ? Non, et voici pourquoi : la statistique
t ne dépend des données qu'à travers leur moyenne. Or le théorème central
limite garantit que la moyenne d'un grand échantillon est quasi normale,
quelle que soit la loi de départ. Et la quantité qui converge vers la
normale dans le TCL, e-barre moins mu sur sigma sur racine de n, c'est
exactement la statistique de Student, avec s à la place de sigma. Le TCL ne
sauve pas le test de justesse : il justifie sa forme même. Avec nos
effectifs, de 978 à 8 513 trades, la condition qui compte réellement est
satisfaite.

📌 **NOTE — ta remarque « attention à la quantité de données pour le
TCL ».** Exact, et c'est dans le rapport : un outil générique doit écarter
les stratégies trop peu fournies. C'est même une des perspectives : ajouter
un garde-fou d'effectif. Si on te demande « combien il faut », réponds :
pas de seuil universel, plus la loi de départ est asymétrique et à queues
lourdes plus il faut de données ; ici on est entre 978 et 8 513, largement
au-delà des ordres de grandeur usuels.

### Bonferroni : onze tests, pas un

**[DIAPO 9 : calcul 1 − 0,95¹¹ ≈ 0,43, inégalité de Boole, α' ≈ 0,0045]**

Dernier piège de cet acte : nous ne faisons pas un test, mais onze.
Plaçons-nous dans le pire des cas, où aucune stratégie n'a d'avantage réel.
Chaque test pris isolément a 95 % de chances de ne pas se tromper ; mais la
probabilité de ne commettre aucune erreur sur les onze vaut 0,95 puissance
onze, soit environ 0,57. Le risque d'au moins un faux positif monte donc à
43 %. Presque une chance sur deux de déclarer un gagnant qui n'existe pas.

On raisonne alors à l'envers : on fixe le risque global à 5 % et on en
déduit le seuil individuel. L'inégalité de Boole majore la probabilité
d'une union par la somme des probabilités : il suffit donc que les seuils
individuels somment à 0,05. En les prenant égaux, on obtient la correction
de Bonferroni : alpha prime égale 0,05 sur 11, soit environ 0,0045.

📌 **NOTE — ta question : pourquoi on n'applique pas Bonferroni à chaque
test du protocole ?** Parce qu'on ne corrige que la **famille des décisions
finales** : les onze verdicts « la stratégie bat-elle le hasard ». Shapiro,
Box–Pierce, Dickey–Fuller, KPSS sont des tests de **condition**, des
diagnostics internes : ils ne déclarent aucune stratégie gagnante, donc ils
ne contribuent pas au risque de faux positif que Bonferroni contrôle. Et il
y a un argument de sens : durcir le seuil de Shapiro, c'est faciliter la
conclusion « c'est normal » — on rendrait les conditions PLUS faciles à
valider, l'inverse de la prudence. Les tests de condition restent donc au
seuil usuel de 5 %, le seuil de Bonferroni est réservé au verdict.

### Premier verdict

**[DIAPO 10 : tableau étape 1 — verdicts du Student naïf]**

Le verdict de ce premier acte : l'oracle bat le hasard très largement —
heureusement, il triche. Et deux vraies stratégies survivent au seuil de
Bonferroni : rsi_classic, avec une p-value de dix puissance moins huit, et
rsi_strict, dix puissance moins dix. Les huit autres sont éliminées.

L'amateur triomphe : deux stratégies gagnantes ! Le statisticien tempère :
ce verdict repose sur une condition que nous n'avons pas encore vérifiée —
l'indépendance des trades. C'est l'acte II, et c'est le cœur du mémoire.

---

## 4. Le dialogue, acte II : la dépendance — 10:00 → 15:00

### Trois canaux, mesurés avant de corriger

**[DIAPO 11 : les 3 canaux + ACP des secteurs (73 %) + tableau ρ̂ et ρ̂(1)]**

Nos trades se ressemblent par trois canaux, et le réflexe du cours de
sondages est de les mesurer avant de corriger quoi que ce soit.

Premier canal, la dépendance de titre : deux trades sur une même action
subissent les mêmes chocs propres à la société. Les titres forment donc des
grappes. Je mesure cette ressemblance par la corrélation intra-grappe rho,
issue de la décomposition de la variance de l'ANOVA : elle compare la
variation entre titres et la variation à l'intérieur des titres. Résultat :
quasi nulle partout, sauf rsi_strict, à 0,134.

Deuxième canal, la dépendance de marché : deux trades ouverts au même
moment subissent la même journée de bourse. Je la mesure sur les rendements
sectoriels : la corrélation moyenne entre les onze secteurs vaut 0,70, et
une ACP montre qu'un seul axe, le facteur marché, capte 73 % de la
variance. Ce n'est pas une hypothèse, c'est une mesure : les trois quarts
des mouvements sont portés par une force commune.

Troisième canal, la dépendance temporelle : nos trades durent, 123 jours en
moyenne, 78 % dépassent le mois. Un trade ouvert en janvier et clos en
avril lie janvier aux mois suivants. L'autocorrélation d'ordre un des
séries mensuelles monte jusqu'à 0,56 pour ma_crossover.

📌 **NOTE — ta question : le chevauchement, c'est sur la même action ou
entre deux actions ? Et la différence avec la dépendance 2 ?** Les deux
sont de nature temporelle mais à des retards différents. La dépendance de
marché est **simultanée** : deux trades ouverts au même moment, sur
n'importe quels titres, subissent le même choc — retard zéro. Le
chevauchement est **retardé** : un trade encore ouvert relie son mois
d'entrée aux mois suivants, donc deux mois **voisins** se ressemblent — et
cela vaut pour tous les trades de la stratégie, quelle que soit l'action,
puisque la série mensuelle agrège tous les titres. Dans le protocole, les
deux passent par la même porte, la porte de la période : la dépendance
simultanée est traitée par l'agrégation mensuelle elle-même, la dépendance
retardée par la correction de série temporelle qui vient après.

Ces trois canaux empruntent en réalité deux portes seulement : la porte de
l'action — des trades du même titre — et la porte de la période — des
trades de la même époque. Le problème pour Student est toujours le même :
il compte 7 000 trades comme 7 000 informations distinctes alors qu'elles
se répètent ; l'erreur-type est sous-estimée, la statistique gonflée, la
p-value trop optimiste.

### Première réponse : corriger la variance — le DEFF

**[DIAPO 12 : DEFF = 1 + (m̄−1)ρ̂, n_eff, puis cloche bootstrap]**

Pour la porte de l'action, trois méthodes, par exigence croissante.

D'abord l'effet de sondage, le DEFF : en sondage par grappes, la variance
réelle de la moyenne vaut la variance sous indépendance multipliée par un
plus m-barre moins un fois rho, où m-barre est le nombre moyen de trades
par titre. Tout se passe comme si on ne disposait que de n sur DEFF
informations. On refait le test de Student avec l'erreur-type gonflée de
racine de DEFF. Résultat : comme rho est quasi nul pour rsi_classic, rien
ne change ; rsi_strict encaisse un DEFF de 1,15 et survit aussi.

Ensuite, une vérification qui ne suppose aucune forme : le bootstrap par
grappes, la méthode d'Efron. On tire avec remise des titres entiers —
quand un titre est tiré, tous ses trades le suivent, donc la dépendance
interne voyage intacte dans chaque réplique. Quatre mille tirages, quatre
mille moyennes d'edge : on obtient une cloche centrée sur la moyenne
initiale, mais dont la largeur, elle, reflète la dépendance.

📌 **NOTE — ta question : comment on « corrige » avec le bootstrap ?** On
ne corrige pas une formule : la cloche **est** la distribution
d'échantillonnage corrigée. La p-value, c'est directement la proportion des
4 000 tirages dont la moyenne passe sous zéro, comparée au seuil de
Bonferroni. Si la dépendance élargit la cloche, cette proportion augmente
toute seule. C'est ce qui rend la méthode précieuse : aucune hypothèse sur
la forme de la dépendance intra-titre.

Les deux verdicts positifs tiennent encore. Mais le statisticien voit une
dernière faille : ces deux méthodes conservent la pondération des données —
un titre à 200 trades pèse 200 fois plus qu'un titre à un trade. Si
l'avantage est concentré sur quelques titres très tradés, la cloche peut
être étroite sans que l'avantage se généralise.

### Deuxième réponse : changer la question — les deux portes

**[DIAPO 13 : schéma des deux portes + tableau p_A / p_B]**

D'où la méthode des deux portes : l'agrégation équipondérée. Une unité
réelle, un vote. Pour la porte de l'action, on calcule l'edge moyen de
chaque titre et le test de Student porte sur ces moyennes : chaque titre
vote une fois, qu'il ait un trade ou deux cents. Pour la porte de la
période, on agrège par mois d'entrée : chaque mois vote une fois. On perd
beaucoup d'information — c'est un choix assumé : pour un outil de
validation, on préfère le risque de faux négatif au risque de faux
positif. Et le TCL reste applicable : il reste 431 à 501 titres et 138 à
197 mois selon les stratégies. Pour être validée, une stratégie doit
franchir les deux portes, chacune au seuil de Bonferroni.

📌 **NOTE — ta question : pourquoi il n'y a pas de dépendance entre les
titres, comme entre les mois ?** Il y en a une — c'est le facteur marché —
mais elle est de nature **temporelle** : deux titres ne sont liés que
s'ils sont tradés à la même période. Or c'est exactement ce que la porte de
la période traite. C'est l'objection levée dans le rapport : chaque porte
prend en charge sa source de dépendance, et c'est pour cela qu'on exige les
deux. Seule échapperait une dépendance propre à l'intersection — un effet
qui n'existerait que pour un titre donné pendant un mois donné — cas
traité par le double clustering de Petersen, cité dans mes limites.

Et là, le tableau change tout. L'oracle passe les deux portes, p-values
pratiquement nulles : son avantage est réel titre par titre et mois par
mois. Mais rsi_classic tombe aux deux portes : p vaut 0,059 côté titres,
0,039 côté mois — loin du seuil de 0,0045. Ses 7 117 trades n'étaient pas
7 117 témoignages indépendants. Dès que chaque titre, puis chaque mois, ne
vote qu'une fois, l'avantage s'efface : c'était un faux positif de
pseudo-réplication. Et rsi_strict a un profil différent, plus
intéressant : elle passe brillamment la porte de l'action, p égale quatre
dix-millièmes — son avantage est partagé par beaucoup de titres — mais
échoue à la porte de la période, p égale 0,26. Avantage réel mais
épisodique, concentré sur quelques mois : inexploitable en l'état. Le
protocole l'écarte, avec une note qui suggère une réétude.

---

## 5. Le dialogue, acte III : la série mensuelle — 15:00 → 18:00

**[DIAPO 14 : chaîne de la méthode : Box–Pierce → DF + KPSS → PACF →
Yule–Walker → variance de long terme → Box–Pierce résidus]**

Reste une fragilité, que l'amateur n'aurait jamais vue : la porte de la
période elle-même suppose les mois indépendants entre eux. Or le
chevauchement des trades lie les mois voisins. La suite des avantages
mensuels est une série temporelle, et il faut la traiter comme telle. La
méthode se déroule en trois questions : y a-t-il une dépendance ? peut-on
la modéliser ? de combien corriger ?

Première question : y a-t-il réellement quelque chose à corriger ? On ne
corrige que ce qui est mesuré. Le test de Box et Pierce répond sur la série
brute — j'insiste : la série mensuelle telle quelle, avant tout modèle. Sa
statistique cumule les six premières autocorrélations, élevées au carré
pour que les signes ne se compensent pas, et multipliées par la longueur T
de la série. Sous H0, chaque autocorrélation n'est que du bruit d'ordre un
sur racine de T, et la somme suit un khi-deux à six degrés de liberté ; on
rejette si la p-value passe sous 5 %. Pourquoi six décalages ? Parce que la
dépendance vient du recouvrement des durées de détention, qui dépassent
rarement six mois : chercher plus loin, c'est chercher un effet sans cause
— et je vérifierai ce plafond en fin de méthode. Résultat : la moitié des
séries seulement sont autocorrélées ; les autres, dont l'oracle et
rsi_strict, gardent leur verdict tel quel, sans correction.

Pour les séries autocorrélées, la correction exige que le lien entre deux
mois ne dépende que de leur écart, pas de leur date : c'est la
stationnarité. Je la vérifie par deux tests aux hypothèses nulles
opposées. Dickey–Fuller régresse le mois courant sur le précédent ; en
déroulant la récurrence, le mois courant est la somme de tous les chocs
passés, chacun pesé par phi élevé à son ancienneté : si phi est inférieur à
un, les chocs s'éteignent, la série est stationnaire ; si phi vaut un,
chaque choc s'ajoute définitivement, la série dérive. Sa statistique a
exactement la forme d'un rapport de Student — phi chapeau moins un sur son
erreur-type — mais elle n'en suit pas la loi : sous H0 la série n'est
justement pas stationnaire, sa variance croît avec le temps, les conditions
de Student tombent. Dickey et Fuller ont tabulé la vraie loi, décalée vers
les négatifs. Le KPSS, lui, cumule les écarts à la moyenne : bornés si la
série oscille autour d'un niveau, ils s'emballent si elle dérive — et son
H0 est la stationnarité. Ne pas rejeter n'ayant jamais valeur de preuve, je
ne conclus que lorsque les deux tests concordent ; s'ils divergent, le
protocole s'abstient et signale, plutôt que de trancher sur une base
fragile. Ici, toutes les séries concernées concordent : stationnaires.

📌 **NOTE — ta question : la stationnarité suffit-elle s'il y a une
tendance ?** Une tendance déterministe rendrait la série non stationnaire
**sans** racine unitaire — Dickey–Fuller pourrait la manquer, mais c'est
exactement ce que KPSS attrape : ses cumuls d'écarts à la moyenne
s'emballent sous une dérive. C'est l'intérêt de la concordance : DF couvre
la racine unitaire, KPSS couvre la stationnarité au sens large. Et je teste
KPSS autour d'une constante, pas d'une tendance, car rien ne laisse
attendre qu'un avantage dérive régulièrement au fil des années.

📌 **NOTE — ta question : existe-t-il une méthode qui donne « à coup sûr »
le bon résultat en cas de divergence ?** Non — aucun test ne peut prouver
H0, c'est structurel. On pourrait ajouter un troisième test
(Phillips–Perron), mais on déplacerait le problème. La bonne réponse est
celle du protocole : verdict « non concluant », renvoyé à l'humain — et
surtout PAS « rejet » : ton brouillon disait « on rejettera par crainte » ;
c'est contraire au rapport, ne le dis pas. Cas vécu à raconter si on te
tend la perche : l'oracle version 1, à l'avantage énorme (t = 122), mettait
DF en échec — série trop tassée, manque de puissance, pas dérive. Un
protocole à un seul test l'aurait écarté en silence ; c'est KPSS qui a
rendu l'anomalie visible. Le témoin a servi à révéler une limite du
protocole, d'où un oracle version 2 plus réaliste.

La stationnarité acquise, on modélise. L'ordre du modèle — combien de mois
de mémoire — est donné par l'autocorrélation partielle, qui mesure l'impact
propre de chaque décalage en retranchant l'influence des mois
intermédiaires. Sous H0 d'absence d'impact, racine de T fois tau chapeau
suit une normale centrée réduite : on garde les décalages significatifs à
5 %, plafonnés à six. On écrit alors le modèle autorégressif : le mois
courant est une somme pondérée des p mois précédents, plus un bruit. Les
poids ne se lisent pas directement dans les données, mais les
autocorrélations, si. Les équations de Yule–Walker font le pont : on
multiplie le modèle par le mois décalé de h, on prend l'espérance, le bruit
disparaît car il est indépendant du passé, et il reste un système linéaire
— autant d'équations que de poids inconnus. On résout, et on remonte aux
poids.

📌 **NOTE — ta question : l'équation du décalage nul qui donne le bruit.**
Même manipulation mais avec h = 0 : on multiplie le modèle par x_t
lui-même et on prend l'espérance. À gauche, la variance de la série
gamma(0). À droite, la part expliquée par les mois passés, somme des Phi_i
gamma(i), **plus** sigma² du bruit — qui ne disparaît pas cette fois, car
x_t contient eta_t. D'où : sigma²_eta = gamma(0) × (1 − somme des
Phi_i rho(i)). Lecture : la variance du bruit, c'est la variance totale
moins ce que le passé explique — ce qui reste imprévisible.

La somme des poids mesure la persistance totale, et donne la variance de
long terme : sigma² du bruit divisé par un moins la somme des Phi, le tout
au carré. Si les poids sont nuls on retrouve s² sur T, la formule usuelle ;
plus la persistance est forte, plus la correction explose. Le rapport entre
cette variance et la variance brute est l'exact analogue temporel du DEFF.
On refait alors le test de Student mensuel avec cette erreur-type. Dernier
contrôle : Box et Pierce à nouveau, mais sur les résidus du modèle, sur
quinze décalages — bien au-delà du plafond de six — avec quinze moins p
degrés de liberté, puisque p paramètres ont été estimés. Aucun rejet : les
modèles ont bien absorbé toute la mémoire, la correction est légitime.

**[DIAPO 15 : tableau final — DEFF_t jusqu'à 6,4, aucun verdict ne bascule,
oracle validé]**

Résultat : la variance mensuelle était bien sous-estimée — d'un facteur
jusqu'à 6,4 pour ma_crossover — mais aucun verdict ne bascule. Au terme de
l'escalade, plus aucune stratégie ne subsiste. Sauf le témoin : l'oracle a
franchi les six étages. L'outil sait donc dire non aux faux positifs, et
oui à un avantage réel. C'est la démonstration que je cherchais.

---

## 6. Lecture, limites, conclusion — 18:00 → 20:00

**[DIAPO 16 : marché — S_BP = 93,7, ρ(1) = −0,08, 0,6 %, efficience faible]**

Aucune vraie stratégie ne passe : est-ce un échec de l'outil, ou une
propriété du marché ? J'ai posé la question au marché lui-même, sur 4 132
jours de rendements. Box et Pierce rejette massivement l'indépendance :
statistique 93,7, p-value nulle. Le marché a donc de la mémoire ! Mais
regardons l'amplitude et non la seule p-value : l'autocorrélation d'ordre
un vaut moins 0,08 — la veille explique 0,6 % du lendemain. La stratégie
qui exploiterait ce rebond rapporterait 0,007 % par jour, moins que le
moindre frais de transaction. C'est l'efficience faible au sens de Fama :
prévisible au sens statistique, pas au sens où l'on pourrait en tirer de
l'argent. Le protocole n'a pas été trop sévère : il a constaté une absence
qui était attendue. Et c'est la même leçon qu'au premier acte : à grand
échantillon, significativité et taille d'effet sont deux choses
différentes.

**[DIAPO 17 : le protocole en 6 étages (tableau du rapport)]**

Ce que je livre à l'agent, au final, ce n'est pas le verdict sur ces onze
stratégies : c'est la procédure. Six étages, chacun réparant une menace
précise : l'edge apparié contre la dérive du marché, Student et le TCL
contre l'aléa d'échantillonnage, Bonferroni contre la multiplicité, le DEFF
et le bootstrap contre la dépendance intra-titre, les deux portes contre la
pseudo-réplication, la correction de série temporelle contre
l'autocorrélation résiduelle. Et quand une condition n'est pas vérifiable,
le protocole s'abstient et signale, plutôt que de trancher.

Ses limites, je les connais. Les résultats sont in-sample : avant tout
usage réel il faudra une validation hors échantillon, en avançant période
après période — une validation croisée classique mélangerait le futur et le
passé. Le biais du survivant : la composition actuelle du S&P 500 est
appliquée à toute la période. Les frais, modélisés simplement. Et
l'empilement des corrections, chacune exacte isolément, qui perd la
garantie du seuil nominal si les trois canaux se manifestaient fortement en
même temps — cas signalé, et absent de nos données.

**[DIAPO 18 : conclusion + perspectives]**

Je conclus. Le test de référence déclarait deux stratégies gagnantes. La
seule vérification de la condition d'indépendance a renversé les deux
verdicts : un faux positif de pseudo-réplication, et un avantage réel mais
trop épisodique. Pendant ce temps, le témoin construit pour gagner a
franchi tous les étages. Un outil de validation se juge à sa capacité
d'attraper ses propres erreurs tout en reconnaissant le vrai : la
démonstration est faite. La suite est tracée : validation hors échantillon,
garde-fou d'effectif, et les signaux futurs de l'agent — qui, quels qu'ils
soient, repasseront tous par cet outil.

Merci de votre attention. Je suis à votre disposition pour vos questions.

---

## Récapitulatif des corrections par rapport à ton brouillon

1. **« 10 tests » → 11 tests** : Bonferroni est calculé sur les onze
   stratégies, témoin compris — alpha prime = 0,05/11 ≈ 0,0045 (rapport,
   chap. 3). Le risque global est 43 %, pas 40 %.
2. **Divergence des tests de stationnarité** : verdict « non concluant »,
   jamais « rejet ». (Corrigé, avec le cas oracle v1 en réserve.)
3. **« données normales et indépendantes »** → la condition utile est la
   normalité de la **moyenne** (TCL) ; formulation corrigée.
4. **Dates complétées** : janvier 2010 → juillet 2026, 45 008 trades,
   501 titres.
5. **« stratégies basiques d'internet »** → « stratégies classiques
   d'analyse technique, règles fixes à peu de paramètres ».
6. **Le bootstrap ne « corrige » pas** : il fournit directement la
   distribution, la p-value est la proportion de tirages sous zéro.
7. **Ajouté ce qui manquait** : les résultats (tableaux des portes, chute
   de rsi_classic et rsi_strict), la validation de l'oracle, la lecture
   efficience du marché, le protocole récapitulé, les limites, la
   conclusion. Ton brouillon s'arrêtait à la variance de long terme.
