# Dictionnaire de données — `rendements_secteurs.csv`

> 1 ligne = 1 jour de bourse. 1 colonne = le **rendement quotidien** d'un secteur (ou du
> marché). Un rendement quotidien = `(cours du jour / cours de la veille) − 1`. Exemple :
> `0.012` = +1,2 % ce jour-là. Période : 2010-01-05 → 2026-06-09 (4132 jours).

| Colonne | Type | Signification |
|---|---|---|
| `date` | date | Le jour de bourse (index). |
| `Communication Services` | décimal | Rendement quotidien **moyen** des actions du secteur. |
| `Consumer Discretionary` | décimal | idem — consommation discrétionnaire (cyclique). |
| `Consumer Staples` | décimal | idem — consommation de base (défensif). |
| `Energy` | décimal | idem — énergie. |
| `Financials` | décimal | idem — finance/banques. |
| `Health Care` | décimal | idem — santé. |
| `Industrials` | décimal | idem — industrie. |
| `Information Technology` | décimal | idem — technologie. |
| `Materials` | décimal | idem — matériaux. |
| `Real Estate` | décimal | idem — immobilier. |
| `Utilities` | décimal | idem — services aux collectivités (défensif). |
| `MARCHE` | décimal | Rendement quotidien moyen de **toutes** les actions = proxy de l'indice global. |

## Comment c'est calculé (et pourquoi le secteur)
Pour chaque action : rendement quotidien = variation relative du cours de clôture ajusté.
Puis, chaque jour, on fait la **moyenne des actions d'un même secteur** → la série du secteur.
La colonne `MARCHE` = moyenne de toutes les actions (le « tout »).

> **Pourquoi agréger par secteur ?** Étudier les liens entre 503 actions reviendrait à
> regarder >250 000 paires (illisible, instable). Les 11 secteurs sont l'unité la plus
> **interprétable** pour parler de relations (« l'énergie suit-elle la finance ? ») et
> restent **ouvrables** dans un tableur. On peut régénérer le fichier avec
> `construire_base.py`.
