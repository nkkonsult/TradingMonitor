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

## Verdict commun (voir `../SYNTHESE.md`)
Sur les données **actuellement branchées** (contrats + régulations, sources gratuites), les
signaux d'information publics **ne dégagent pas d'edge significatif** après correction : le
marché les a largement anticipés. Le seul frémissement (régulation significative → −0,47 %)
mérite un suivi. Les scripts sont **prêts** à intégrer Congrès/earnings dès que la clé FMP
est fournie, sans réécriture.
