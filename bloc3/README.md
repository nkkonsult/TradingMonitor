# BLOC 3 — Relations inter-actions · l'usine, étage par étage

> Même principe que le Bloc 1 : on sépare ce qui **ENTRE** (les données), ce que la
> **MACHINE** fait (les méthodes), et ce qui **SORT** (les résultats). Tout est ouvrable
> et relançable. Ici on n'étudie plus des stratégies, mais les **liens entre les morceaux
> du marché** : qui bouge avec qui, qui précède qui, quels facteurs communs, et peut-on
> prévoir le marché avec son propre passé.

```
            01_donnees/                  02_methodes/                  03_resultats/
   ┌──────────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
   │ rendements_secteurs.csv  │──▶│ etape1 correlations  │──▶│ .txt + cartes .png   │
   │ (11 secteurs + MARCHE)   │   │ etape2 granger       │   │                      │
   │ dictionnaire.md          │   │ etape3 ACP rendements│   │                      │
   │ construire_base.py       │   │ etape4 ARIMA         │   │                      │
   └──────────────────────────┘   └──────────────────────┘   └──────────────────────┘
            CE QUI ENTRE              CE QUE LA MACHINE FAIT          CE QUI SORT
```

## 01_donnees/ — CE QUI ENTRE
- **`rendements_secteurs.csv`** : la matière première. 1 ligne = 1 jour de bourse ;
  1 colonne = le **rendement quotidien** d'un secteur (11) + une colonne **MARCHE**
  (moyenne de toutes les actions). 4132 jours, 2010→2026. Ouvrable dans Excel.
- **`dictionnaire.md`** : ce que contient chaque colonne.
- **`construire_base.py`** : la machine qui fabrique ce CSV à partir du cache de prix
  (503 actions → rendements → agrégation par secteur).

> *Pourquoi le secteur et pas chaque action ?* 503 actions = plus de 250 000 paires :
> illisible et instable. Le secteur (11 séries) est l'unité **interprétable** pour parler
> de relations, et reste ouvrable. La granularité « 503 actions » sera utile au Bloc final.

## 02_methodes/ — CE QUE LA MACHINE FAIT
`explication.md` documente chaque page (méthode + résultat).
- `etape1_correlations.py`  — quels secteurs bougent ensemble ? (corrélation de Pearson)
- `etape2_granger.py`       — un secteur en précède-t-il un autre ? (causalité de Granger)
- `etape3_acp_rendements.py`— le « facteur marché » (ACP sur les rendements)
- `etape4_arima.py`         — peut-on prévoir le marché avec son passé ? (ADF, ACF/PACF, ARIMA)

## 03_resultats/ — CE QUI SORT
Verdicts `.txt` + graphiques `.png` (carte de chaleur, loadings ACP, ACF/PACF).

## Place dans le projet
Bloc **dissociable** (voir `../ARCHITECTURE.md`). Il produit des **signaux de relation**
(lead-lag, facteur marché) qui pourront alimenter la **régression finale** — laquelle ne
vient qu'à la fin, sur les signaux validés par chaque bloc.
