# Architecture du projet — en BLOCS dissociables

> Idée directrice : le projet est découpé en **blocs indépendants**. Chaque bloc a **ses propres données** et on lui applique **ses propres méthodes statistiques**. On peut **vérifier chaque bloc séparément**. À la toute fin — et **seulement à la fin** — un **gros bloc de régression** combine les signaux retenus par chaque bloc pour produire l'**équation prédictive**.

```
┌────────────────────────────────────────────────────────────────┐
│  BLOC 1 — STRATÉGIES GRAPHIQUES (analyse technique)            │ ◀── on est ICI
│  Données : les trades des stratégies (MM, RSI, figures, S/R)  │
│  Méthodes : tests (Shapiro, Student, Welch, Fisher), ANOVA +  │
│             Tukey, χ², ACP, Monte Carlo                        │
│  Sortie : QUELS signaux techniques ont de la valeur (vs hasard)│
└────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────┐
│  BLOC 2 — SIGNAUX D'INFORMATION (événementiel)                │
│  Données : contrats gouv., Congress trades, lois/régulations,  │
│            news (via les agents n8n)                           │
│  Méthodes : event study, tests, χ²…                            │
│  Sortie : QUELS signaux d'info ont de la valeur               │
└────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────┐
│  BLOC 3 — RELATIONS INTER-ACTIONS                             │
│  Données : séries de prix BRUTES (montée/descente dans le      │
│            temps), pas des stratégies                          │
│  Méthodes : corrélations, causalité de Granger, ACP sur        │
│             rendements, ARIMA (ACF/PACF, stationnarité)        │
│  Sortie : LIENS entre actions/secteurs (A précède-t-il B ?)   │
└────────────────────────────────────────────────────────────────┘
                              │
                  (tous les signaux RETENUS)
                              ▼
┌════════════════════════════════════════════════════════════════┐
║  BLOC FINAL — RÉGRESSION sur TOUS les signaux                  ║
║  Régression multiple (PROC REG) + logistique (PROC LOGISTIC)   ║
║  → l'ÉQUATION PRÉDICTIVE  Y = α + β₁·X₁ + β₂·X₂ + …            ║
║  (chaque signal validé = un Xᵢ ; Stepwise insère/rejette)      ║
└════════════════════════════════════════════════════════════════┘
```

## Règles du jeu
- **Chaque bloc est autonome** : sa propre base, ses propres méthodes, sa propre conclusion. On le **valide avant** de passer au suivant.
- **La régression finale ne mélange QUE des signaux déjà validés** par leur bloc (on n'y met pas de bruit).
- **Ordre de travail :** Bloc 1 → (Bloc 2, Bloc 3) → Bloc final. On **ne commence pas la régression** tant que les blocs ne sont pas faits.

## État actuel
- **Bloc 1** : données prêtes (trades des 10 stratégies, base `eval`). À faire : appliquer les méthodes statistiques (tests, ANOVA, χ², ACP).
- **Bloc 2** : agents n8n existants (contrats, Congress, lois, news) — à brancher plus tard.
- **Bloc 3** : séries de prix déjà en cache (503 titres) — méthodes à appliquer plus tard.
- **Bloc final** : **plus tard**, une fois les blocs validés.
