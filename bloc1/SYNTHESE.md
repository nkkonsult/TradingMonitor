# Bloc 1 — Les stratégies d'analyse technique ont-elles une valeur ? (synthèse)

> Section de rapport autonome. Elle résume le **Bloc 1** : la question, les données, les
> cinq analyses statistiques appliquées, et le **verdict commun** qui en ressort. Le détail
> du code est en annexe (`bloc1/02_methodes/`), le détail des données dans `01_donnees/`.

## 1. La question du bloc

Les stratégies d'**analyse technique** (indicateurs et figures chartistes lues sur les
graphiques de prix) ont-elles un **réel pouvoir prédictif**, ou ne font-elles **pas mieux
que le hasard** ? On ne juge pas une stratégie sur son rendement brut — trompeur, car
l'univers d'étude (S&P 500) est massivement haussier — mais sur son **avantage face à un
tirage au hasard de même exposition** (l'`edge`).

## 2. Les données

Chaque trade simulé par une stratégie = **une ligne**. Au total **38 035 trades**, produits
par **10 stratégies** sur **503 actions** (2010–2026). Pour chaque trade on dispose de :
- son **rendement net** (frais déduits) et son **`edge`** = rendement − rendement d'un trade
  au hasard de même titre, même durée, même sens (moyenne de 200 tirages) ;
- son **contexte d'entrée** : régime de marché, secteur, volatilité, niveau de RSI, distance
  à la moyenne 200 jours ;
- son **issue** : gagnant / perdant.

> L'`edge` est la variable-juge : `edge > 0` ⇔ la stratégie bat le hasard à exposition égale,
> donc isole le **talent de timing** indépendamment de la tendance de fond du marché.

## 3. Les cinq analyses et leurs résultats

| # | Méthode (vue en cours) | Question | Résultat |
|---|---|---|---|
| 1 | **Tests d'hypothèse** (Shapiro, Student, Wilcoxon, Bonferroni) | Chaque stratégie bat-elle le hasard ? | **Seul le RSI** (classique +1,3 %, strict +13 %) a un edge significativement positif. Aucune figure chartiste. |
| 2 | **ANOVA + Tukey** | Les stratégies diffèrent-elles entre elles ? | Oui (F = 47, p ≈ 10⁻⁸⁵). Surtout : **le classement dépend du régime** de marché (interaction p ≈ 10⁻⁶⁹). |
| 3 | **Khi-deux** (+ V de Cramer) | Gagner dépend-il du contexte ? | Du **secteur : non** (indépendant). Du **régime : un peu** (lien faible). De la **stratégie : beaucoup** (lien fort). |
| 4 | **ACP** | Le contexte d'entrée sépare-t-il gagnants et perdants ? | **Non** (d de Cohen = −0,12, négligeable). Volatilité, RSI et tendance d'entrée ne suffisent pas à prédire l'issue. |
| 5 | **AFC + ACM** (analyse des correspondances) | Quelles stratégies / modalités vont avec quel résultat ? | Cartes : les **RSI** voisinent les gains, les figures (sr, hs) voisinent les pertes ; **« gagnant »** voisine `rsi_classic`/`rsi_trend`/`db_bottom`. Secteurs au centre (confirme le χ²). |

### Détail méthodologique (pour l'oral)
- **Étape 1.** Shapiro rejette la normalité partout (attendu à grand n) → on s'appuie sur le
  **Théorème Central Limite** pour le test de Student, **Wilcoxon** confirme (résultat robuste).
  Seuil durci par **Bonferroni** (0,05/10) contre les faux positifs des tests multiples.
- **Étape 2.** L'**interaction stratégie × régime** est le résultat le plus important : une
  stratégie n'est pas « bonne dans l'absolu », sa valeur dépend de l'état du marché.
- **Étape 4.** L'ACP n'utilise **que le contexte d'entrée** (pas l'issue), donc teste
  honnêtement si l'on peut prédire le résultat *avant* de le connaître. La réponse est non.
- **Étapes 3 et 5** se répondent : le χ² **mesure** le lien, l'AFC/ACM le **cartographient**.

## 4. Le verdict commun

Les cinq méthodes, par des chemins indépendants, pointent **la même conclusion** :

> **Le RSI (retour à la moyenne) se détache ; les figures chartistes — épaule-tête-épaule,
> doubles sommets/creux, supports/résistances — ne battent pas le hasard.** Et le contexte
> d'entrée seul ne permet pas de prédire l'issue d'un trade.

Cette **convergence** (un seul verdict sous cinq angles) est un gage de solidité.

## 5. Limites assumées

- **Biais de sélection** : le S&P 500 actuel est haussier à 97,4 % (médiane +635 %). L'edge
  du RSI est donc en partie **structurel** (acheter les creux d'actions qui dérivent à la
  hausse) plutôt qu'une vraie « prédiction ». L'analyse **par régime** atténue ce biais.
- **In-sample** : ces cinq analyses portent sur l'ensemble de la période. La validation
  **hors-échantillon** (walk-forward) reste le juge final ; elle a déjà montré que les figures
  ne prédisent rien même après optimisation des réglages.
- **Pas de vérité-terrain** des figures (en partie subjectives) → définition opératoire
  reproductible plutôt que taux d'erreur absolu.

## 6. Ce que ça implique pour la suite

Si l'analyse technique seule ne sépare pas les gagnants des perdants, il faut **d'autres
sources d'information**. C'est l'objet des blocs suivants : **Bloc 2** (signaux d'information :
contrats publics, transactions du Congrès, lois, actualités) et **Bloc 3** (relations entre
actions). La **régression finale** combinera uniquement les signaux **validés** par chaque
bloc (voir `../ARCHITECTURE.md`).
