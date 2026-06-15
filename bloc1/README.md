# BLOC 1 — Stratégies graphiques · l'usine, étage par étage

> But de ce dossier : que tu puisses **tout voir et tout défendre** à l'oral. Comme une
> usine, on sépare ce qui **ENTRE**, ce que la **MACHINE** fait, et ce qui **SORT**.
> Rien n'est caché dans une boîte noire : chaque étage est un fichier que tu peux ouvrir,
> lire, et relancer toi-même.

```
                01_donnees/                02_methodes/              03_resultats/
            ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
   PRIX ──▶ │  trades.csv      │ ──▶  │ etape1_tests.py  │ ──▶  │ etape1_*.txt/png │
            │  (la matière)    │      │ etape2_anova.py  │      │ (les verdicts)   │
            │  dictionnaire.md │      │ ...              │      │                  │
            └──────────────────┘      └──────────────────┘      └──────────────────┘
              CE QUI ENTRE              CE QUE LA MACHINE FAIT      CE QUI SORT
```

## Les 3 étages

### 01_donnees/ — CE QUI ENTRE (la matière première)
- **`trades.csv`** : LA base. 1 ligne = 1 trade qu'une stratégie a déclenché sur un titre.
  Ouvrable dans Excel / LibreOffice. C'est l'élément qui entre dans la machine.
- **`dictionnaire.md`** : à quoi sert chaque colonne, son unité, comment elle est calculée.
  → tu dois pouvoir expliquer CHAQUE colonne au jury.
- **`exporter_base.py`** : la mini-machine qui sort `trades.csv` depuis la base `results.db`.
  (La base elle-même est fabriquée en amont par `backend/charts/stats_aggregate.py` :
  détection des figures + comparaison au hasard — c'est documenté dans `METHODOLOGIE.md`.)

### 02_methodes/ — CE QUE LA MACHINE FAIT (une méthode = un fichier)
Chaque script lit `trades.csv`, applique UNE méthode vue en cours, et écrit son résultat
dans `03_resultats/`. **`explication.md`** documente chaque page (ce qu'elle fait + le
résultat obtenu) — sans avoir à lire le code.
- `etape1_tests.py` — chaque stratégie bat-elle le hasard ? (Shapiro, Student, Wilcoxon, Bonferroni)
- `etape2_anova.py` — les stratégies diffèrent-elles ? (ANOVA 1 & 2 facteurs + Tukey)
- `etape3_chi2.py`  — gagner dépend-il du contexte ? (khi-deux + V de Cramer)
- `etape4_acp.py`   — le contexte d'entrée sépare-t-il gagnants/perdants ? (ACP, numpy)
- `etape5_afc.py`   — quelle stratégie va avec quel rendement ? (AFC, numpy)
- `etape6_acm.py`   — quelles modalités vont avec « gagnant » ? (ACM, numpy)

### 03_resultats/ — CE QUI SORT (les verdicts)
Tableaux et graphiques produits par les méthodes. C'est ce que tu mets dans le rapport.

## Règle du jeu
La **régression n'est PAS dans ce bloc** : elle viendra à la toute fin, sur les signaux
retenus par TOUS les blocs (voir `../ARCHITECTURE.md`). Ici on ne fait que **mesurer la
valeur des signaux techniques** avec les méthodes du cours.
