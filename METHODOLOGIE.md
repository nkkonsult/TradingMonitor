# Méthodologie détaillée — Analyse de la valeur prédictive des stratégies d'analyse technique

> **À qui s'adresse ce document ?** À une personne **non spécialiste** (maître de stage, lecteur du rapport). Il explique, comme un cours, **chaque outil**, **chaque stratégie**, **chaque graphique** et **chaque test statistique** utilisés, et surtout **pourquoi** on les utilise. Aucun prérequis n'est supposé.
>
> *Document vivant : enrichi au fur et à mesure de l'avancement.*

---

## Table des matières
1. [Le but du projet (la question de recherche)](#1-le-but-du-projet)
2. [Les outils informatiques (vulgarisés)](#2-les-outils-informatiques)
3. [Les données : d'où viennent les chiffres](#3-les-données)
4. [Qu'est-ce qu'une « stratégie » et comment on la teste](#4-quest-ce-quune-stratégie)
5. [Les stratégies, une par une](#5-les-stratégies-une-par-une)
6. [Les coûts de transaction](#6-les-coûts-de-transaction)
7. [Mesurer la performance : les métriques](#7-les-métriques)
8. [Le cœur du problème : à quoi comparer une stratégie ?](#8-à-quoi-comparer-une-stratégie)
9. [La « fonction de hasard » expliquée en détail](#9-la-fonction-de-hasard)
10. [La base de données de résultats](#10-la-base-de-données)
11. [Les tests statistiques (reliés au cours)](#11-les-tests-statistiques)
12. [La validation rigoureuse : le walk-forward](#12-le-walk-forward)
13. [Les pièges méthodologiques traités](#13-les-pièges-méthodologiques)
14. [Les résultats à ce jour](#14-les-résultats-à-ce-jour)
15. [Les prochaines étapes](#15-les-prochaines-étapes)

---

## 1. Le but du projet

**La question :** *Les stratégies d'« analyse technique » (déduire les futurs mouvements de prix à partir de l'historique des cours et de figures sur les graphiques) ont-elles un réel pouvoir de prédiction, ou ne font-elles pas mieux que le hasard ?*

C'est une vraie question scientifique, débattue depuis longtemps (référence académique : **Park & Irwin, 2007**, qui montrent que les preuves en faveur de l'analyse technique sont au mieux mitigées). L'esprit du stage : **appliquer une boîte à outils statistique** (celle apprise en cours : tests d'hypothèses, régression, ANOVA…) à un **domaine nouveau** (la bourse) pour **trancher avec des chiffres**, pas avec des opinions.

**Le principe directeur :** on ne croit rien sur parole. Une stratégie n'est déclarée « bonne » que si elle bat un **point de comparaison honnête** de façon **statistiquement significative** (c'est-à-dire pas par chance).

---

## 2. Les outils informatiques

*(Vulgarisation pour comprendre « avec quoi » on travaille.)*

- **Python** : un langage de programmation. C'est l'outil qui « fait les calculs » : télécharger les prix, appliquer les règles d'une stratégie, calculer les statistiques. On l'a choisi parce qu'il a des **bibliothèques** toutes prêtes pour les maths et les stats : `pandas` (manipuler des tableaux de données), `numpy` (calcul numérique rapide), `scipy.stats` (les tests statistiques), `statsmodels` (la régression, équivalent des procédures SAS).

- **git** et **GitHub** : un **carnet de versions**. À chaque étape importante, on « enregistre » (un *commit*) l'état exact du code, avec un message qui décrit ce qu'on a fait. GitHub est le site qui héberge ces sauvegardes en ligne. Avantage : on peut revenir en arrière, travailler depuis n'importe quel ordinateur, et **tracer toute l'évolution** du travail. *(C'est aussi une preuve de sérieux pour le rapport : tout est horodaté et documenté.)*

- **Le dashboard (tableau de bord)** : une petite **application web** qu'on a construite pour **visualiser** les analyses (choisir une action, voir les stratégies, les graphiques, les statistiques). Elle a deux moitiés :
  - le **backend** (Python + *FastAPI*) : la partie « cerveau » qui calcule ;
  - le **frontend** (React) : la partie « écran » qu'on voit dans le navigateur.

- **SQLite** : une **base de données** rangée dans un simple fichier. On y stocke le résultat de chaque transaction simulée (une ligne par *trade*), pour pouvoir ensuite faire des statistiques dessus sans tout recalculer.

---

## 3. Les données

- **Source :** `yfinance`, une bibliothèque gratuite qui récupère l'historique boursier (Yahoo Finance).
- **Quoi :** le **cours de clôture quotidien** de chaque action, **ajusté** des dividendes et des divisions d'actions (pour que la série soit cohérente dans le temps).
- **Période :** depuis **2010** jusqu'à aujourd'hui (~2026).
- **Univers :** les **503 sociétés du S&P 500** (les plus grandes entreprises américaines cotées). On a d'abord prototypé sur 10 valeurs, puis basculé sur les 503 pour avoir **beaucoup de données** (= puissance statistique).
- **Cache :** les données sont **enregistrées sur le disque** après le premier téléchargement, pour ne pas re-télécharger à chaque fois.

> ⚠️ **Biais du survivant / de sélection (à signaler) — QUANTIFIÉ :** on prend les sociétés **actuellement** dans le S&P 500. Mesure faite : **97,4 % de ces titres ont MONTÉ** sur la période (médiane **+635 %**), seulement 2,6 % ont baissé. C'est un univers **massivement biaisé vers les gagnantes** : les sociétés sorties de l'indice (faillites, rachats) manquent. Conséquence : le Buy & Hold paraît « imbattable » par **artefact de sélection** (pas par génie), et les stratégies qui « achètent les creux » (RSI) sont **avantagées** par cette dérive haussière. **Nos résultats positifs sont donc à lire comme conditionnels à cet univers.** Le contournement principal = l'**analyse par régime** (les périodes baissières testent les signaux *sans* l'aide de la dérive). Un univers vraiment non-biaisé exigerait des données payantes (CRSP) incluant les titres délistés.

---

## 4. Qu'est-ce qu'une « stratégie »

Une **stratégie** est une **règle précise** qui dit **quand acheter** et **quand vendre**. Exemple : « acheter quand l'indicateur X dépasse 30, vendre quand il dépasse 70 ».

**Point crucial pour la validité scientifique :** nos règles sont **100 % déterministes** — ce sont uniquement des **comparaisons de nombres**, jamais un avis humain ou une intelligence artificielle. Conséquence : sur les **mêmes données**, on obtient **toujours les mêmes trades**. C'est la condition pour que les statistiques aient un sens (**reproductibilité**).

**Comment on « teste » une stratégie (backtest) :** on **rejoue l'histoire**. On applique la règle sur les prix passés, on note chaque transaction (date et prix d'achat, date et prix de vente), et on calcule ce qu'elle aurait rapporté. C'est ce qu'on appelle un **backtest**.

**Long et short :**
- un trade **long** = on **achète**, on gagne si le prix **monte** ;
- un trade **short** (vente à découvert) = on **vend à découvert**, on gagne si le prix **baisse**.

---

## 5. Les stratégies, une par une

Pour chaque stratégie : *l'idée*, *la règle exacte*, *les paramètres* (les « réglages » chiffrés), *pourquoi*.

### 5.0 Buy & Hold (« acheter et garder ») — la référence
- **Idée :** ne rien faire d'actif. On achète au début, on garde jusqu'à la fin.
- **Pourquoi :** c'est l'**étalon**. La vraie question pratique d'un investisseur est : *« est-ce que ma stratégie compliquée fait mieux que simplement tenir l'action ? »*. Sans cet étalon, dire « +120 % » ne veut rien dire.

### 5.1 Croisement de moyennes mobiles (suiveur de tendance)
- **Une moyenne mobile** = la moyenne des prix sur les N derniers jours ; elle « lisse » la courbe. Une **MM courte** (ex. 50 jours) réagit vite, une **MM longue** (ex. 200 jours) donne la tendance de fond.
- **Règle :** **acheter** quand la MM courte passe **au-dessus** de la MM longue (« golden cross »), **vendre** quand elle repasse **en-dessous** (« death cross »).
- **Paramètres :** MM courte = **50 jours**, MM longue = **200 jours**.
- **Pourquoi :** stratégie « de tendance » la plus classique — on suppose qu'une tendance qui s'installe se poursuit.

### 5.2 RSI (retour à la moyenne)
- **Le RSI** (Relative Strength Index) est un indicateur **entre 0 et 100** qui mesure si une action a « trop monté trop vite » (**surachat**, > 70) ou « trop baissé » (**survente**, < 30). Calcul standard sur **14 jours** (lissage de Wilder).
- **Règle :** **acheter** quand le RSI **repasse au-dessus** du seuil bas (il sort de la survente → on parie sur le rebond), **vendre** quand il **repasse sous** le seuil haut.
- **Paramètres / variantes :** seuils **30/70** (classique), **20/80** (plus stricts → moins de signaux), et **30/70 + filtre** (n'acheter que si le cours est au-dessus de sa MM200, pour éviter d'acheter en plein effondrement).
- **Pourquoi :** stratégie « de retour à la moyenne » — on suppose que les excès se corrigent.

### 5.3 Épaule-tête-épaule (figure chartiste)
- **La figure :** trois sommets — une « tête » (le plus haut) encadrée de deux « épaules » plus basses — annoncerait un **retournement à la baisse**. La version **inversée** (trois creux) annoncerait une **hausse**.
- **Comment on la détecte automatiquement :** on repère les **pivots** (sommets et creux locaux), puis on vérifie des **conditions géométriques chiffrées** : la tête doit dépasser les épaules, les deux épaules doivent être à hauteur comparable, la **ligne de cou** (qui relie les creux) doit être à peu près horizontale, etc. Le signal se déclenche à la **cassure** de la ligne de cou.
- **Paramètres :** fenêtre de pivot = **±10 jours**, tolérance entre épaules = **5 %**, proéminence minimale de la tête = **3 %**, symétrie temporelle, horizontalité de la ligne de cou ≤ **6 %**.
- **Variantes :** « classique » (baissière → trade **short**) et « inversée » (haussière → trade **long**).

### 5.4 Double sommet / double creux (figure chartiste)
- **La figure :** deux sommets à hauteur proche (double **sommet**, baissier) ou deux creux (double **creux**, haussier), séparés par un creux/pic intermédiaire. Détection identique en esprit au H&S, mais avec **3 pivots** au lieu de 5.
- **Paramètres :** fenêtre de pivot ±10 jours, écart entre les deux extrêmes ≤ **4 %**, profondeur du pivot central ≥ **4 %**.
- **Variantes :** double creux → **achat (long)**, double sommet → **vente (short)**.

### 5.5 Support / résistance — canaux de Donchian (cassure et rebond)
- **Support** = niveau **sous** lequel le cours a du mal à descendre (les acheteurs reviennent → ça rebondit) ; **Résistance** = niveau **au-dessus** duquel il a du mal à monter (les vendeurs reviennent → ça rebondit). On les rend chiffrés par les **canaux de Donchian** : résistance = **plus-haut des N derniers jours**, support = **plus-bas des N derniers jours**.
- **Deux usages OPPOSÉS de la même figure :**
  - **Cassure (breakout)** : on achète quand le cours **franchit** la résistance → *« le marché a pris sa décision »*. C'est un **suiveur de tendance** (on achète *après* le mouvement, donc « haut »).
  - **Rebond (bounce)** : on achète quand le cours **touche le support et repart** ; on vend à la résistance. C'est un **retour à la moyenne** (acheter « bas »).
- **Paramètres :** fenêtre **N = 20 jours**, **tampon de confirmation = 0,5 %**, fenêtre de sortie = 10 jours.
- **Le tampon de confirmation (anti « chasse au stop ») :** comme tout le monde connaît ces niveaux, de gros acteurs poussent parfois le prix **juste au-delà** pour déclencher les stop-loss groupés, puis le marché repart à l'envers (« fausse cassure »). On exige donc que la clôture dépasse le niveau **d'un tampon** (pas une simple mèche), et ce **des deux côtés** (support ET résistance).
- **Intérêt pour le rapport :** la stratégie teste DIRECTEMENT l'opposition **tendance (cassure) vs retour à la moyenne (rebond)** sur une même figure. *(Extension v2 : supports/résistances **obliques** = lignes de tendance, plus subjectives à détecter.)*

> **Pourquoi ce choix de stratégies ?** Elles couvrent un **gradient** : des règles d'indicateurs simples (MM, RSI) jusqu'aux **figures visuelles complexes** que les traders « lisent » à l'œil (épaule-tête-épaule, doubles, support/résistance). L'angle du rapport : *« les figures compliquées battent-elles une simple règle d'indicateur — ou même le hasard ? »*.

---

## 6. Les coûts de transaction

Chaque achat/vente coûte (écart entre prix d'achat et de vente = « slippage », frais de courtage). On déduit un coût de **5 points de base par côté** (1 point de base = 0,01 % ; donc ≈ 0,10 % l'aller-retour). Sans cela, on surestimerait les stratégies qui tradent beaucoup. **Tous les rendements affichés sont nets de ces coûts.**

---

## 7. Les métriques

*(Ce qu'on calcule pour résumer une performance, et pourquoi chacune compte.)*

- **Rendement (return)** : le gain en %. Sur un trade, ou cumulé.
- **CAGR** (taux de croissance annuel composé) : le rendement ramené à « par an », pour comparer des durées différentes.
- **Volatilité** : l'ampleur des variations (le « risque » de fluctuation).
- **Sharpe** : *rendement / risque total*. Plus c'est haut, mieux c'est — on gagne plus **par unité de risque** pris.
- **Sortino** : comme le Sharpe, mais ne pénalise que les variations **à la baisse** (on ne « punit » pas la volatilité quand elle joue en notre faveur).
- **Calmar** : *rendement annuel / pire perte subie*. Mesure le rendement rapporté au pire creux.
- **Max Drawdown (pire creux)** : la plus forte baisse entre un sommet et un creux. Mesure la douleur maximale.
- **VaR 95 %** : la perte quotidienne qui n'est dépassée que **1 jour sur 20**. Une mesure de risque extrême.
- **Profit factor** : *somme des gains / somme des pertes*. > 1 = profitable.
- **Taux de réussite** : % de trades gagnants.

> **Nuance importante :** certaines métriques se calculent sur la **liste des trades** (taux de réussite, profit factor), d'autres exigent la **courbe de valeur jour par jour** (Sharpe, Max Drawdown…). On distingue donc « niveau trade » et « niveau série temporelle ».

---

## 8. À quoi comparer une stratégie ?

C'est le **cœur méthodologique** du projet, et il a évolué au fil de la réflexion.

### Étape 1 — « vs Buy & Hold » : insuffisant
Comparer au Buy & Hold mélange **deux choses** : (a) le **talent** de la stratégie et (b) la **tendance** de l'action. Sur une action qui monte fort, *presque rien* ne bat le Buy & Hold (sortir = rater des hausses), **quel que soit le talent**. Donc « battre / perdre vs Buy & Hold » dépend surtout de la **tendance**, pas de la qualité du signal. Le Buy & Hold ne gagne d'ailleurs **pas toujours** (vrai surtout sur les grosses actions haussières).

### Étape 2 — la bonne idée : « vs le HASARD »
Pour isoler le **talent**, on compare la stratégie à une version **au hasard ayant exactement la même activité** : même **nombre** de trades, mêmes **durées**, mais à des **dates tirées au sort**. Comme l'**exposition est identique**, la seule différence est le **choix du moment** (le *timing*). Si la stratégie bat ce hasard, alors le signal porte une **vraie information**. → **C'est notre juge principal.**

### Synthèse
| Comparaison | Question à laquelle elle répond |
|---|---|
| **vs Hasard** | *Le signal a-t-il un vrai talent ?* (scientifique — **le juge**) |
| vs Buy & Hold | *Est-ce utile vs ne rien faire ?* (pratique — contexte, dépend de la tendance) |

---

## 9. La fonction de hasard

*(Expliquée pas à pas, car c'est notre instrument de mesure central.)*

1. On part des trades du signal : **N** trades, chacun de durée connue.
2. On fabrique une version au hasard : **N** trades aussi, **mêmes durées**, mais placés à des **dates aléatoires** dans l'historique.
3. On calcule le gain de cette version.
4. On **répète 200 fois** (200 versions au hasard) pour ne pas dépendre de la chance d'un seul tirage.
5. On résume les 200 résultats par une **zone** : le **5ᵉ percentile** (bas) et le **95ᵉ percentile** (haut) → la zone contient **90 %** des tirages ; la **médiane** est la ligne centrale.

**Lecture :** si le signal sort de la zone **par le haut** → il bat le hasard. S'il est **dans** la zone → indiscernable de la chance.

> **Un biais trouvé puis corrigé :** au départ, les fenêtres au hasard pouvaient se **chevaucher**, ce qui réduisait le temps investi (~6 % de moins) et **tirait la zone vers le bas** (le signal paraissait artificiellement bon). On a corrigé en plaçant les fenêtres **sans chevauchement** → exposition **rigoureusement identique**. *(Détail qui montre le souci de rigueur, à mettre dans le rapport.)*

**Mesure synthétique — l'« edge » :** pour chaque trade, on calcule
`edge = rendement du signal − rendement attendu au hasard (même durée, même sens)`.
Un **edge > 0** = le trade a fait mieux que le hasard. On agrège ensuite ces edges sur tous les trades.

---

## 10. La base de données

Chaque trade simulé devient **une ligne** dans une table (`detections`) avec : l'action, le secteur, la stratégie, le sens, les dates, le rendement net, le régime de marché à l'entrée, etc. **Pourquoi ?** Parce qu'on ne fait pas de statistiques sur un calcul éphémère : il faut un **tableau figé** de **34 300 trades** qu'on peut charger, filtrer et tester. C'est le pont entre « simuler » et « analyser ».

---

## 11. Les tests statistiques

*(Reliés aux notions vues en cours — c'est ici que la « boîte à outils » s'applique.)*

### 11.1 Le test de Student (t-test)
- **Ce qu'il fait :** dire si une moyenne est **significativement différente de zéro** (ou de la moyenne d'un autre groupe), c'est-à-dire **pas due au hasard de l'échantillon**.
- **Notre usage :** l'`edge` moyen d'une stratégie est-il **significativement > 0** ? On pose :
  - **H0** (hypothèse nulle) : l'edge moyen = 0 (le signal ne vaut pas mieux que le hasard) ;
  - **H1** (hypothèse alternative) : l'edge moyen ≠ 0.
- **La p-value :** la probabilité d'observer un edge aussi grand **si H0 était vraie**. Si **p < 0,05**, on **rejette H0** : l'effet est jugé réel (significatif au seuil de 5 %).
- **Pourquoi c'est pertinent :** c'est exactement l'outil pour distinguer « ça marche » de « j'ai eu de la chance sur cet échantillon ».

### 11.2 La correction de Bonferroni (tests multiples)
- **Le problème :** si on teste **beaucoup** de stratégies, certaines passeront le seuil de 5 % **par pur hasard** (tester 20 choses inutiles → en moyenne 1 « significative » par chance).
- **La correction :** on **durcit** le seuil en le divisant par le nombre de tests (ex. 8 stratégies → seuil = 0,05 / 8 ≈ 0,006). Un résultat n'est retenu que s'il passe ce seuil plus strict.

### 11.3 L'ANOVA (à venir, étape « par régime »)
- **Ce qu'elle fait :** comparer les moyennes de **plus de deux groupes** d'un coup, et tester un **effet d'interaction** (ex. *l'avantage d'une stratégie dépend-il du régime de marché ?*).
- **Notre usage prévu :** ANOVA **stratégie × régime** (haussier / baissier) — *le classement des stratégies s'inverse-t-il selon que le marché monte ou baisse ?*

### 11.4 La régression (à venir)
- **Régression linéaire multiple** : expliquer une quantité (le rendement) par plusieurs facteurs en même temps (régime, secteur, durée…), repérer les facteurs importants (sélection de modèle, critère **AIC**), vérifier qu'ils ne se répètent pas (**VIF**).
- **Régression logistique** : prédire une issue **binaire** (le trade est-il **gagnant** oui/non ?) et exprimer l'effet de chaque facteur en **odds ratios** (« en marché baissier, les chances que le signal marche sont ×N »).
- **Pourquoi :** si chaque signal pris seul est faible, les **combiner** peut révéler une valeur. C'est aussi l'équation qui pourrait, à terme, piloter un agent automatique.

---

## 12. Le walk-forward

**Le problème à éviter (sur-apprentissage / *overfitting*) :** si on **choisit les meilleurs réglages** d'une stratégie **sur les mêmes données** qui servent à conclure, on triche sans le vouloir — on trouve des réglages qui « marchent » par chance sur le passé, mais qui ne tiendront pas sur l'avenir.

**La solution — le walk-forward glissant :**
1. On **choisit les paramètres sur une fenêtre passée** (ex. 5 ans : 2010-2014) — *uniquement* sur cette fenêtre d'entraînement.
2. On **applique ce réglage à l'année suivante** (2015), **jamais vue** → résultats **hors-échantillon**.
3. On **glisse d'un an** (train 2011-2015 → test 2016) et on recommence jusqu'à 2025.
4. On **agrège tous les trades hors-échantillon** → **verdict honnête**.

**Pourquoi c'est la référence :** les paramètres ne sont **jamais** choisis sur les données qui jugent. Donc si une figure ne marche **à aucun réglage** en hors-échantillon, c'est **la figure** qui est nulle, pas le réglage. *(Réponse directe à « la stratégie est mauvaise, ou juste mal réglée ? ».)*

---

## 13. Les pièges méthodologiques traités

- **Pas de vérité-terrain pour les figures** : un épaule-tête-épaule est en partie **subjectif** (deux traders n'en voient pas les mêmes). Donc impossible de mesurer un « taux d'erreur » absolu. On en fait une **définition opératoire reproductible** et on teste la **robustesse** aux réglages. *(C'est un point du rapport, pas un défaut caché.)*
- **Biais du survivant** (cf. §3).
- **Biais de look-ahead** (regarder le futur sans le vouloir) : le **régime de marché** est calculé de façon **causale** (avec l'information disponible à l'instant t seulement).
- **Un seul titre ne prouve rien** : sur une action, quelques trades = du bruit. D'où l'**agrégation sur 503 titres**.
- **Path-dependence** (dépendance au chemin) : certaines courbes (overlay) sont dominées par 2-3 décisions → fragiles. D'où le choix de juger sur la **distribution des rendements**, pas une seule courbe.
- **Data snooping** : ne pas inventer/inverser des stratégies après coup sur les mêmes données → d'où le **walk-forward**.

---

## 14. Les résultats à ce jour

### Verdict « in-sample » (sur tout 2010-2026), edge vs hasard, test de Student :
- 🟢 **RSI (30/70 et 20/80) bat le hasard, significativement** : le retour à la moyenne (acheter en survente) porte une vraie information.
- 🔴 **Croisement de MM** et **double sommet** : **significativement pires** que le hasard (ils entrent **après** le mouvement → ils achètent « haut »).
- ⚪ Épaule-tête-épaule, double creux : **indiscernables du hasard**.

### Verdict « hors-échantillon » (walk-forward, paramètres optimisés honnêtement) sur les figures :
- **Épaule-tête-épaule (les 2) : aucun pouvoir prédictif** (non significatif).
- **Double creux & double sommet : significativement PIRES que le hasard.**
- **Message fort :** les figures ne prédisent rien **même après optimisation des réglages** → *« ce n'est pas un problème de paramètres, c'est la figure elle-même »*.
- **Leçon méthodologique :** le double creux, légèrement neutre en in-sample, devient nettement **négatif** en hors-échantillon → **optimiser sur le passé a empiré** le résultat → cela **prouve que le walk-forward était indispensable**.

### Nuance honnête sur le RSI
Son avantage vient en grande partie d'un effet **structurel** : il **entre dans les creux** (survente), alors que le hasard entre à un prix moyen. Sur des actions qui **dérivent vers le haut**, acheter les creux capte mieux le rebond. À confirmer **hors-échantillon** (étape suivante) — c'est le seul résultat positif, il doit être validé.

---

## 15. Les prochaines étapes
1. **Valider le RSI hors-échantillon** (confirmer le seul signal positif).
2. **Analyse par régime** (ANOVA) : l'avantage tient-il en marché baissier ?
3. **Analyse par secteur**.
4. **Régression** (logistique puis linéaire) : qu'est-ce qui fait gagner un trade ?
5. **Onglet « Statistiques »** dans le dashboard pour tout visualiser.

---

*Fin de la version actuelle. Ce document est mis à jour à chaque étape du projet.*
