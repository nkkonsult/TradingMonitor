# BLOC 2 — Signaux d'information · l'usine, étage par étage

> Même principe que les Blocs 1 et 3 : on sépare ce qui **ENTRE** (les signaux d'info
> collectés via les agents n8n), ce que la **MACHINE** fait (les méthodes du cours), et ce
> qui **SORT** (les verdicts). Tout est ouvrable et relançable. Ici, on ne juge plus des
> stratégies techniques ni des liens entre actions, mais la **valeur prédictive de
> l'information exogène**. Deux questions complémentaires :
> 1. **Impact direct** (étapes 1-4) : quand un signal tombe sur un titre, *ce titre* bouge-t-il anormalement ?
> 2. **Impact de contagion** (étapes 5-6) : quand un signal touche A, quels **autres** actifs liés à A (pairs corrélés, matières premières, ETF de thème) réagissent — en même temps, ou après (*A précède-t-il B ?*) ? Mesurer les **répercussions** d'un signal sur le reste du marché.

```
        01_donnees/                    02_methodes/                    03_resultats/
 ┌──────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
 │ collecteur.py (n8n/API)  │─▶│ _moteur.py (CAR)       │─▶│ .txt + courbe CAR .png │
 │ construire_evenements.py │  │ etape1 event study     │  │                        │
 │ evenements.csv           │  │ etape2 tests (par sens)│  │                        │
 │ dictionnaire.md          │  │ etape3 chi2            │  │                        │
 │ + prix via charts.data   │  │ etape4 poisson         │  │                        │
 │ liens_thematiques.py     │  │ etape5 contagion       │  │                        │
 │                          │  │ etape6 lead-lag        │  │                        │
 └──────────────────────────┘  └────────────────────────┘  └────────────────────────┘
         CE QUI ENTRE               CE QUE LA MACHINE FAIT          CE QUI SORT
```

## 01_donnees/ — CE QUI ENTRE
- **`collecteur.py`** : va chercher chaque signal là où il vit — API publiques gratuites
  (**USASpending** pour les contrats, **Federal Register** pour les régulations) en direct,
  et **FMP** (via la clé n8n) pour le Congrès et les résultats. Écrit des CSV bruts.
- **`construire_evenements.py`** : normalise tous les bruts en **`evenements.csv`** — la base
  d'analyse (1 ligne = 1 événement : `signal, ticker, date, sens, secteur, intensite`). Fait
  le mapping *nom d'entreprise → ticker* (contrats) et la projection sectorielle (régulations).
- **`dictionnaire.md`** : chaque colonne expliquée + les limites assumées.
- Les **prix** (le juge de l'étude d'événement) viennent de `backend/charts/data.get_ohlcv`
  — le même socle que les Blocs 1 et 3.

## 02_methodes/ — CE QUE LA MACHINE FAIT
`explication.md` documente chaque page (méthode + résultat obtenu).
- `_moteur.py`             — calcule le **rendement anormal cumulé (CAR)** par événement (modèle de marché).
- `etape1_event_study.py`  — le signal déplace-t-il le cours ? (CAR moyen vs 0 + courbe)
- `etape2_tests.py`        — bat-il le hasard selon son **sens** ? (Student/Wilcoxon, Bonferroni)
- `etape3_chi2.py`         — le sens est-il lié à l'**issue** ? (khi-deux + V de Cramér)
- `etape4_poisson.py`      — les événements se **concentrent**-ils par secteur ? (Poisson + binom. nég.)
- `etape5_contagion.py`    — le signal sur A fait-il **réagir les actifs liés à A** ? (CAR des pairs corrélés + matières premières autour de J0 — *impact simultané*)
- `etape6_leadlag.py`      — **A précède-t-il B** ? (AR immédiat vs décalé + prédictibilité Granger — *contagion dans le temps*)

## 03_resultats/ — CE QUI SORT
Verdicts `.txt` + la courbe `etape1_car.png` (CAR moyen autour de l'événement).

## Comment relancer
```bash
# 1) collecter (sources gratuites ; ajoute FMP_API_KEY pour Congrès/earnings)
python bloc2/01_donnees/collecteur.py
# 2) fabriquer la base d'analyse
python bloc2/01_donnees/construire_evenements.py
# 3) lancer les 4 méthodes
python bloc2/02_methodes/etape1_event_study.py
python bloc2/02_methodes/etape2_tests.py
python bloc2/02_methodes/etape3_chi2.py
python bloc2/02_methodes/etape4_poisson.py
```

## Deux niveaux de lecture
- **Pour le mémoire** : les 4 méthodes ci-dessus (signaux gratuits déjà branchés). Verdict
  dans `SYNTHESE.md`.
- **Pour les futures stratégies** : `CATALOGUE_SIGNAUX.md` recense **les 28 signaux** du
  rapport n8n (méthode stat applicable, source, coût, statut) — la feuille de route prod.

## Place dans le projet
Bloc **dissociable** (voir `../ARCHITECTURE.md`). Il produit des **signaux d'information**
dont la valeur est mesurée ici ; ceux qui seront **validés** alimenteront la **régression
finale** — laquelle ne vient qu'à la fin, sur les signaux retenus par chaque bloc.
