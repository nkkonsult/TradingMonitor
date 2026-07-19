# Plan de bataille — dernière ligne droite (19 juillet → 3 août 2026)

> Réécrit le 19/07 après le **recentrage du mémoire** (décision actée) :
> un seul chat, branche `main`. **Rendu : 3 août** (PDF + source), soutenance 18 août.
> Objectif interne : **tout boucler le 30 juillet** → 4 jours de marge.

---

## 1. Le recentrage (acté le 19/07)

**Sujet** : *construire un protocole statistique pour juger des stratégies de trading,
sur des données qui violent les hypothèses des tests* (données dépendantes).
Plus de « blocs » : une seule enquête.

| Chapitre | Fichier | Contenu | État |
|---|---|---|---|
| 1. Introduction | `01_introduction.tex` | but (écrit) + **les trois menaces** (trame) | ~60 % |
| 2. Données + structure de dépendance | `02_donnees.tex` | base 38 210, edge apparié, **3 canaux mesurés** (ICC, ACP 73 %, ACF) | trame prête |
| 3. Juger : l'escalade de prudence | `03_juger.tex` | étape 1 (RÉDIGÉE ✅) + étape 1 bis (trame) + lecture du verdict (trame) + synthèse | cœur du travail |
| 4. Contexte : comparer/caractériser | `04_contexte.tex` | ANOVA, χ², ACP/AFC/ACM (ex-étapes 2-6) | ~50 %, trous résultats |
| 5. Protocole, limites, perspectives | `05_protocole.tex` | tableau des 6 étages (fait) + trames ; perspectives = logistique/GEE, signaux n8n, Granger | trame prête |
| 6. Conclusion | `06_conclusion.tex` | bilan + boucle nuisance/ressource | trame prête |
| Annexes | `07_annexes.tex` | Shapiro à jour (38 210) ; à compléter (Tukey, factorielles) | partiel |

**Sortis du rapport** (préservés dans `bloc2/`, `bloc3/`, git) : Bloc 2 entier,
Granger, bloc final logistique → tous mentionnés en perspectives (ch. 5).
**La « double ancre »** : chaque méthode = raisonnement + cours + citation littérature
(Fama-MacBeth, Newey-West, White, Efron — déjà dans `biblio.bib`).

## 2. Règles de travail (inchangées, NON NÉGOCIABLES)

- Le chat explique (conditions données AVEC la théorie) ; **l'utilisateur rédige** ;
  le chat corrige uniquement les fautes.
- L'étape 1 du ch. 3 est **intouchable** (rédaction personnelle terminée).
- Méthodes de cours d'abord ; hors-cours = cité avec sa référence (double ancre).
- Jamais prétendre l'indépendance défendable. Compilation `pdflatex + biber` (pas latexmk).
- Questions jury notées au fil de l'eau dans `rapport/preparation_oral.md`.

## 3. Calendrier (15 jours)

| Jour | Rédaction (LUI) | Support (chat) |
|---|---|---|
| **J1-J3** 19-21/07 | **Ch. 3 étape 1 bis** (le morceau central) | correction fautes au fil ; TODO mécaniques étape 1 (tableau 38 210, renvoi conditions) sur demande |
| **J4** 22/07 | **Ch. 2 §2.3** structure de dépendance | vérif chiffres/figure ACP |
| **J5-J6** 23-24/07 | **Ch. 3** lecture du verdict + positionnement + synthèse | — |
| **J7-J8** 25-26/07 | **Ch. 4** (théorie ANOVA/χ² + lectures ACP/AFC/ACM) | fournir chiffres + figures depuis `bloc1/03_resultats/` |
| **J9** 27/07 | **Ch. 1** trois menaces + **ch. 5** trames | — |
| **J10** 28/07 | **Ch. 6** conclusion + page de garde (« Prénom NOM » !) | annexes complémentaires |
| **J11** 29/07 | relecture chiffres | **compilation ≤ 40 pages**, bijectivité biblio, figures |
| **J12** 30/07 | relecture anti-plagiat intégrale | cohérence texte ↔ `03_resultats/` |
| **J13-J15** 31/07-2/08 | **MARGE** + préparation orale (20 min + Q&A) | `preparation_oral.md` complet |
| **3/08** | **RENDU** | — |

## 4. Points de vigilance

0. **⚠️ RELECTURE « CHIFFRES PÉRIMÉS » (à faire avant rendu, NE PAS OUBLIER)** :
   le rapport a d'abord été écrit sur l'ANCIENNE base (38 035 trades). Le tableau
   de l'étape 1, l'encadré conditions et la phrase TCL du ch. 3 ont été remis sur
   la base actuelle (38 210) le 19/07, mais **tout le reste doit être repassé au
   peigne fin** : chercher les vieux nombres (38 035, n par stratégie 973/8 469/
   7 083…, anciennes p-values et W) partout dans `rapport/*.tex`. Source de vérité :
   `bloc1/03_resultats/*.txt` et `bloc3/03_resultats/*.txt`.
1. **≤ 40 pages** : les tableaux du ch. 3 sont nombreux — si dépassement, basculer
   les tables 1b et 1d en annexe (garder les deux portes dans le corps).
2. Citations : les `\cite` du positionnement sont dans des commentaires-trames →
   ils ne deviennent réels que quand la prose est rédigée ; vérifier à J11 que
   la biblio imprimée = exactement les références citées.
3. `shapiro1965` / `student1908` dans `biblio.bib` : méthodes de cours → ne seront
   probablement jamais citées → retirer du `.bib` avant rendu si non citées.
4. Titre proposé dans `main.tex` (« Juger des stratégies de trading… ») : **à valider/reformuler par l'utilisateur**.
5. Ancien matériau : `bloc2/REDACTION_RAPPORT.md` et les résultats Granger restent
   disponibles pour l'oral (questions sur « pourquoi pas les signaux externes ? »).
