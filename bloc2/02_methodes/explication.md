# Les méthodes du Bloc 2, page par page

> Une méthode = un fichier `etape*.py`. Chacun lit `01_donnees/evenements.csv`, calcule
> les rendements anormaux via le moteur commun, applique **une** méthode vue en cours, et
> écrit son verdict dans `03_resultats/`. Ce document dit **ce que fait** chaque page et
> **le résultat obtenu** — sans avoir à lire le code.

## `_moteur.py` — le moteur d'étude d'événement (brique commune)
Calcule, pour chaque événement `(ticker, date)`, le **rendement anormal cumulé (CAR)** :
modèle de marché `R_i = α + β·R_marché` estimé sur J−250→J−11, puis `AR = R_réel − attendu`
sur la fenêtre J−1→J+5, et `CAR = Σ AR`. Réutilisé par les étapes 2 à 4 (pas de copier-coller).

## `etape1_event_study.py` — le signal déplace-t-il le cours ?
**Méthode** : étude d'événement + test de Student/Wilcoxon du CAR moyen contre 0 (bilatéral,
Bonferroni). Sort aussi la **courbe du CAR moyen** jour par jour (`etape1_car.png`).
**Résultat** : contrats CAR moyen ≈ **+0,3 %** (p≈0,35, *non significatif*) ; régulations
≈ **−0,15 %** (p≈0,2, *non significatif*). → l'information publique semble **déjà price-in**
(cohérent avec l'efficience semi-forte des marchés).

## `etape2_tests.py` — le signal bat-il le hasard selon son SENS ?
**Méthode** : pour chaque `(signal, sens)`, test 1-échantillon du CAR (Shapiro documenté,
Student, Wilcoxon, Bonferroni).
**Résultat** : les régulations **« significatives »** ont un CAR moyen de **−0,47 %**
(p≈0,02) — un effet baissier **détectable au seuil 5 % brut mais rejeté après Bonferroni**.
C'est le signal le plus proche de la significativité : une contrainte réglementaire forte
tend à peser sur le secteur. Les régulations « standard » : effet nul.

## `etape3_chi2.py` — le sens du signal est-il lié à l'issue ?
**Méthode** : table de contingence `sens × issue (CAR>0/CAR≤0)`, khi-deux d'indépendance +
**V de Cramér** (intensité).
**Résultat** : pour les régulations, sens et issue sont **indépendants** (V≈0,01,
négligeable). Le χ² prendra toute sa valeur quand le signal **Congrès (achat/vente)** sera
branché (croisement plus riche). En l'état : pas de lien exploitable.

## `etape4_poisson.py` — le nombre d'événements dépend-il du secteur ?
**Méthode** : GLM de **Poisson** sur le comptage d'événements par ticker, expliqué par le
secteur ; test de **sur-dispersion** puis contrôle en **binomiale négative**.
**Résultat** : forte **concentration sectorielle** (Consumer Discretionary ×1,6, Energy ×1,6,
IT ×1,3 ; p<0,01). Mais **sur-dispersion massive (ratio ≈ 27)** : passée en binomiale
négative (AIC 506 vs 1796), le nombre d'effets significatifs tombe de **5 à 2**. Leçon :
« significatif en Poisson » ≠ « robuste » — la concentration réelle est plus modeste.

## `etape5_contagion.py` — le signal sur A fait-il réagir les actifs LIÉS à A ?
**Recadrage** : on ne teste plus si le signal est tradable *sur A*, mais s'il **se propage**
vers les actifs liés. Pour chaque titre-source A, deux familles de cibles : les **pairs
corrélés** (data-driven, les 3 titres les plus corrélés à A) et les **thèmes / matières
premières** (`liens_thematiques.py` : Tesla→lithium, défense→ITA…). On mesure le CAR de
chaque cible autour de la date du signal sur A.
**Résultat** : impact **simultané confirmé** — pairs corrélés CAR **+0,27 %** (p=0,003) et
thèmes/matières **+0,26 %** (p=0,0006). → Quand A reçoit un signal, son écosystème bouge
(ex. contrat Lockheed → Northrop, GD, ETF défense réagissent).

## `etape6_leadlag.py` — A précède-t-il B (contagion décalée) ?
**Méthode** : on décompose l'AR de la cible en **immédiat** (J0–J1) vs **décalé** (J2–J5),
et on teste (esprit **Granger**) si le choc de A en J0 prédit le rendement de B en J+1.
**Résultat** : l'impact est surtout **immédiat/synchrone** (pairs p=0,008, thèmes p=8e−10) ;
l'effet **décalé J2–J5 n'est pas significatif**. La régression Granger montre un **léger
entraînement A→B le lendemain sur les pairs corrélés** (pente +0,033, p=0,049), mais un
rebond (pente négative) sur les thèmes. → La contagion est réelle mais **essentiellement
synchrone** ; l'entraînement décalé exploitable est marginal.

## `etape7_carte_contagion.py` — cartographie fine (quels couples A→B ?)
**Méthode** : pour chaque couple (titre-source A, cible B), CAR moyen de B autour des dates
de signal de A + test de Student ; classement des couples les plus contagieux + **carte de
chaleur** (`etape7_heatmap.png`).
**Résultat** : canaux nets et interprétables — **UNH→HUM +2,8 %** (assureurs santé),
**JNJ/LLY/PFE→MRK +1,6 %** (labos pharma), et un effet de **substitution dans la défense**
(**BA→RTX −0,7 %**, LMT/BA → ETF défense ITA en baisse). 8 couples significatifs sur 44.

## Verdict commun (voir `../SYNTHESE.md`)
Sur les données **actuellement branchées** (contrats + régulations, sources gratuites), les
signaux d'information publics **ne dégagent pas d'edge significatif** après correction : le
marché les a largement anticipés. Le seul frémissement (régulation significative → −0,47 %)
mérite un suivi. Les scripts sont **prêts** à intégrer Congrès/earnings dès que la clé FMP
est fournie, sans réécriture.
