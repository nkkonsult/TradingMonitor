# Dictionnaire de données — `trades.csv`

> 1 ligne = 1 trade (une stratégie a ouvert puis fermé une position sur un titre).
> Tu dois pouvoir expliquer **chaque colonne** au jury : voici de quoi il s'agit.

| Colonne | Type | Unité | Signification | Comment c'est calculé |
|---|---|---|---|---|
| `ticker` | texte | — | Le titre (ex. `AAPL`) | Symbole boursier de l'action |
| `sector` | texte (catégorie) | — | Secteur GICS (ex. `Health Care`) | Table de correspondance S&P 500 |
| `strategy` | texte (catégorie) | — | La stratégie qui a produit le trade | 1 des 10 (voir liste ci-dessous) |
| `params_version` | texte | — | Version des réglages (`v1`) | Trace de reproductibilité : quels seuils ont produit ce trade |
| `regime_entry` | texte (catégorie) | `haussier`/`baissier` | État du marché le jour de l'entrée | S&P 500 au-dessus / en dessous de sa MM200 (causal) |
| `direction` | entier | `+1`/`-1` | Sens du trade | `+1` = achat (long), `-1` = vente à découvert (short) |
| `holding_days` | entier | jours | Durée de détention | nb de jours entre entrée et sortie |
| `vol_entry` | décimal | proportion/jour | **Volatilité à l'entrée** (variable de contexte) | écart-type des rendements quotidiens sur les 20 jours précédant l'entrée |
| `rsi_entry` | décimal | 0–100 | **Niveau de RSI à l'entrée** (contexte) | RSI de Wilder (14 j) le jour de l'entrée — bas = survente, haut = surachat |
| `dist_ma200` | décimal | proportion | **Distance à la MM200** (force de tendance) | `(cours − moyenne 200 j) / moyenne 200 j` à l'entrée ; >0 = au-dessus (tendance haussière) |
| `return_net` | décimal | proportion | **Rendement net du trade** (variable clé) | `(prix_sortie/prix_entrée − 1)` ajusté du sens, **moins les frais** (2 × coût/côté) |
| `rand_return` | décimal | proportion | Rendement d'un trade **AU HASARD** équivalent | Même titre, même durée, même sens, **200 tirages** à dates aléatoires → moyenne |
| `edge` | décimal | proportion | **L'avantage vs le hasard** (variable juge) | `edge = return_net − rand_return`. `> 0` = la stratégie bat le pile-ou-face |
| `win` | binaire | `0`/`1` | Le trade est-il gagnant ? | `1` si `return_net > 0`, sinon `0` |

## Pourquoi `edge` est LA variable importante
Un rendement positif ne prouve **rien** : sur le S&P 500, ~97 % des titres montent sur la
période — acheter *n'importe quand* rapporte souvent. La vraie question est : **la stratégie
fait-elle mieux que d'entrer au hasard, à durée et exposition égales ?** C'est exactement ce
que mesure `edge`. Tester `edge` vs 0 = tester si la stratégie a un **talent** réel.
→ C'est le cœur du Bloc 1.

## Les 10 stratégies (`strategy`)
| clé | libellé | type de signal |
|---|---|---|
| `ma_crossover` | Croisement de moyennes mobiles | sortie (overlay) |
| `rsi_classic` | RSI 30/70 | sortie |
| `rsi_strict` | RSI 20/80 | sortie |
| `rsi_trend` | RSI 30/70 + filtre MM200 | sortie |
| `hs_inverse` | Épaule-tête-épaule inversé (achat) | entrée |
| `hs_classic` | Épaule-tête-épaule (short) | sortie |
| `db_bottom` | Double creux (achat) | entrée |
| `dt_top` | Double sommet (short) | sortie |
| `sr_breakout` | Cassure de résistance → hausse | entrée |
| `sr_breakdown` | Cassure de support → baisse (short) | entrée |

## Le « hasard » comme référence (à savoir défendre)
Pour chaque trade réel, on simule **200 trades fictifs** : même action, même durée, même
sens, mais à des **dates de départ tirées au sort**. La moyenne de leurs rendements =
`rand_return` = « ce que ça aurait rapporté sans aucun talent de timing ». La stratégie n'a
de valeur que si `return_net` dépasse `rand_return` **de façon statistiquement significative**
(c'est ce qu'on teste à l'Étape 1).
