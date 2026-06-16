# Bloc 3 — Relations entre actions : structure et prévisibilité du marché (synthèse)

> Section de rapport autonome. Elle résume le **Bloc 3** : la question, les données, les
> quatre analyses, et le verdict. Détail du code en annexe (`bloc3/02_methodes/`).

## 1. La question du bloc

Au lieu d'étudier des stratégies (Bloc 1), on regarde la **structure du marché lui-même** :
les morceaux du marché bougent-ils ensemble ? l'un précède-t-il l'autre ? existe-t-il des
**facteurs communs** ? et le marché est-il **prévisible à partir de son propre passé** ?

## 2. Les données

Les rendements quotidiens **agrégés par secteur** : 11 séries sectorielles + une série
`MARCHE` (moyenne de toutes les actions), sur **4132 jours** (2010–2026), construites depuis
les cours des 503 sociétés. Le secteur est l'unité **interprétable** pour parler de relations
(11 séries plutôt que 503² paires).

## 3. Les quatre analyses

| # | Méthode | Question | Résultat |
|---|---|---|---|
| 1 | **Corrélation** de Pearson | Quels secteurs bougent ensemble ? | Corrélation moyenne **0,70** : le marché bouge « d'un bloc ». Cycliques (Industrials, Financials) très couplés ; défensifs (Utilities, Energy) moins. |
| 2 | **Causalité de Granger** | Un secteur en précède-t-il un autre ? | **48 paires / 110** significatives ; **Financials mène** (précède 10 secteurs). Mais effet gonflé par la taille d'échantillon → à valider. |
| 3 | **ACP** | Quel est le facteur commun ? | **PC1 = 73 %** = le **facteur marché** (risque systématique) ; PC2 (8 %) oppose défensifs et cycliques (axe risk-on/risk-off). |
| 4 | **ARIMA** (ADF, ACF/PACF) | Prévoir le marché avec son passé ? | Prix = **marche aléatoire** ; rendement = **bruit blanc** (autocorr. ≈ 0). **Efficience faible.** |

## 4. Le verdict du bloc

Deux messages cohérents :

> **(a) Le marché est très couplé** : 73 % du risque est systématique (commun à tous les
> secteurs), la diversification sectorielle est limitée. **(b) Le marché est peu prévisible
> par lui-même** : sa série de rendements est quasi un bruit blanc.

Il **existe** une structure de lead-lag (les financières semblent mener), mais sa significativité
statistique tient surtout à la **taille de l'échantillon** ; rien ne garantit qu'elle soit
**exploitable**. Conclusion pratique : **prévoir le marché exige des signaux externes** (les
stratégies du Bloc 1, l'information du Bloc 2), pas la seule dynamique des prix.

## 5. Limites assumées

- **Granger ≠ causalité réelle**, et la forte puissance du test (4132 jours) rend beaucoup de
  liens « significatifs » sans qu'ils soient économiquement utiles → nécessité de mesurer
  l'**effet de taille** et de **valider hors-échantillon**.
- Agrégation **sectorielle** : on perd les relations action-par-action (choix de lisibilité ;
  la granularité fine sera mobilisée au Bloc final si utile).
- Relations supposées **linéaires** et **stables dans le temps** (or les corrélations montent
  en période de crise — extension possible : corrélations glissantes par régime).

## 6. Apport au projet

Le Bloc 3 fournit deux **signaux de relation** réutilisables par la régression finale : le
**facteur marché** (exposition systématique) et les **liens de lead-lag** (à condition de les
valider). Comme les autres blocs, il ne décide rien seul : il prépare des variables
candidates pour l'**équation finale** (voir `../ARCHITECTURE.md`).
