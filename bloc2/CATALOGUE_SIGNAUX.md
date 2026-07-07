# Catalogue des signaux — du rapport n8n à la statistique

> Ce catalogue relie **les 28 signaux** identifiés dans le rapport n8n (« Rapport 2 ») à une
> **méthode statistique** vue en cours et à un **statut de traitement**. Double usage :
> (1) montrer au jury que le périmètre du mémoire est un choix *raisonné* dans un ensemble
> plus large ; (2) servir de **feuille de route** pour brancher ces signaux dans les futures
> stratégies de trading.

## Légende du statut
- ✅ **analysé** — données branchées + méthodes appliquées dans ce Bloc 2.
- 🔑 **prêt (clé requise)** — code de collecte écrit ; s'active dès que la clé API (dans n8n)
  est fournie. Même chaîne d'analyse, aucune réécriture.
- 📈 **relève d'un autre bloc** — signal de série temporelle → méthodes du Bloc 3.
- 💰 **bloqué (payant)** — donnée derrière un abonnement (Polygon, Unusual Whales, Quiver).
- 🧭 **hors périmètre M1** — signal utile en prod mais non statistique-événementiel.

## Comment lire la colonne « Méthode »
`event study` = rendement anormal cumulé (le cœur du Bloc 2). `χ²` = lien sens↔issue.
`Poisson` = comptage d'événements. `corrélation/ARIMA/Granger` = méthodes du Bloc 3
(séries temporelles). `régression` = brique du Bloc final.

---

## 🏛️ Politique / Réglementaire
| Signal | Source (rapport) | Méthode stat | Statut |
|---|---|---|---|
| **Trades Congrès** | FMP / Quiver / Unusual Whales | event study (achat/vente) + χ² | 🔑 prêt (clé FMP) |
| **Contrats publics** | USASpending.gov | **event study + Poisson** | ✅ **analysé** |
| **Régulation secteur** | Federal Register | **event study + χ² + Poisson** | ✅ **analysé** |
| **Lois en cours** | LegiScan / Congress.gov | event study (date d'étape) | 🔑 prêt (clé Congress.gov) |

## 🏢 Business / Off-market
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| **Contrats privés** | FMP / Finnhub | event study | 🔑 prêt (clé FMP/Finnhub) |

## 📈 Marché / Flux
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Price action | Polygon / FMP | (analyse technique = **Bloc 1**) | 📈 Bloc 1 |
| Volume anormal | Polygon / Finnhub | event study sur pic de volume | 💰 bloqué (Polygon) |
| Options flow | Unusual Whales / Polygon | event study | 💰 bloqué (UW) |
| Dark pools | Polygon / Unusual Whales | event study | 💰 bloqué |
| Liquidité marché | Polygon / FMP | série temporelle | 💰 / 📈 |

## 🧾 Fondamentaux entreprise
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| **Résultats entreprise** (surprises) | FMP / Finnhub | **event study (beat/miss) + χ²** | 🔑 prêt (clé FMP) |
| Croissance revenus | FMP / Finnhub | régression (Bloc final) | 🔑 / 📈 |
| Endettement entreprise | FMP / Intrinio | régression (covariable) | 🔑 |
| Catalyseurs futurs | Finnhub / FMP | event study (date programmée) | 🔑 prêt (clé Finnhub) |
| Position concurrentielle | Finnhub / FMP | ACP / comparaison pairs | 🔑 / 📈 |

## 🌍 Macro
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Macro économie | FRED / Trading Economics | série temporelle (**Bloc 3**) | 📈 Bloc 3 |
| Taux d'intérêt | FRED / FXMacroData | ARIMA / corrélation | 📈 Bloc 3 |
| Inflation | FRED / Trading Economics | série temporelle | 📈 Bloc 3 |
| Géopolitique | Finnhub / NewsData.io | event study (chocs) | 🧭 / 💰 |

## 🧠 Sentiment
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Sentiment retail | StockTwits / Adanos | corrélation sentiment↔rendement | 💰 / 🧭 |
| Sentiment média | Finnhub / Adanos | event study sur news | 🔑 / 🧭 |

## 🧪 Données avancées
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Données alternatives | Quiver / Finnhub | event study / régression | 💰 bloqué (Quiver) |

## ⚙️ Structure marché
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Momentum marché | Polygon / FMP | série temporelle (Bloc 3) | 📈 Bloc 3 |
| Corrélation secteur | FMP / Finnhub | **corrélation (déjà fait Bloc 3)** | 📈 Bloc 3 ✅ |
| Volatilité implicite | Polygon / Unusual Whales | série temporelle | 💰 bloqué |

## 🎯 Exécution
| Signal | Source | Méthode stat | Statut |
|---|---|---|---|
| Timing entrée | Finnhub / FMP | (combinaison de signaux = Bloc final) | 🧭 Bloc final |
| Gestion risque | Polygon / FMP | (dimensionnement, pas un signal) | 🧭 |

---

## Bilan pour le mémoire
Sur 28 signaux : **2 pleinement analysés** (contrats, régulations — sources gratuites),
**6 prêts à l'emploi** dès qu'une clé API est fournie (Congrès, résultats, lois, contrats
privés, catalyseurs, sentiment média), **~7 relèvent du Bloc 3** (macro/séries), et **~8 sont
bloqués derrière un abonnement payant** (options, dark pools, alt-data). Le périmètre M1 est
donc l'intersection *event-study-able × donnée accessible* — le sous-ensemble le plus
défendable statistiquement.

## Bilan pour la prod (futures stratégies)
Le **moteur d'event study** (`02_methodes/_moteur.py`) est **générique** : tout signal réduit
à `(ticker, date, sens)` y passe sans réécriture. Débloquer un signal payant plus tard (ex.
options flow) = écrire une fonction de collecte dans `collecteur.py` et l'ajouter à
`construire_evenements.py`. Les 6 signaux 🔑 sont à un pas (la clé) d'être mesurés.
