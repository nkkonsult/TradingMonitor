# Plan de bataille — dernière ligne droite (19 juillet → 3 août 2026)

> Réécrit le 19/07 après le **recentrage du mémoire** (décision actée) :
> un seul chat, branche `main`. **Rendu rapport : 3 août** (PDF + source).
> **Oral : 15 août** → 12 jours APRÈS le rendu pour la diapo + l'exposé
> (hors chemin critique : rien à préparer avant le 3/08, on alimente juste
> `preparation_oral.md` au fil de l'eau).
> Objectif interne rapport : **tout boucler le 30 juillet** → 4 jours de marge.

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

## 3. Calendrier (réécrit le 21/07 — état réel de l'avancée)

### DÉJÀ FAIT (au 21/07)
- Intro **§1.1 (but)** + **§1.2 (trois menaces)** rédigées. §1.3 en trame (à faire en dernier).
- Ch. 3 **étape 1 (Student/Shapiro/TCL/Bonferroni)** rédigée + paragraphe de clôture.
- **Oracle témoin** créé, base à 40 362 trades, tableaux du ch. 3 à jour, encadré ch. 4.

### RESTE À RÉDIGER (13 jours, rendu 3/08 — marge intégrée)
| Jour | À boucler | Charge |
|---|---|---|
| **Mer 22/07** | **Ch. 2** entier (§2.1 base+edge, §2.2 secteurs, §2.3 les 3 canaux) | moyenne |
| **Jeu 23/07** | **Ch. 3 étape 1 bis** : la question + 4 méthodes (DEFF, bootstrap, deux portes, série mensuelle) | **LOURDE (cœur)** |
| **Ven 24/07** | **Ch. 3 étape 1 bis** : lecture des 3 tableaux + positionnement littérature | moyenne |
| **Sam 25/07** | **Ch. 3** : lecture du verdict (ARIMA/efficience) + synthèse. → **ch. 3 fini** | moyenne |
| **Dim 26/07** | **Ch. 4** : recalcul étapes 2-6 SANS oracle (chat) + rédaction ANOVA & χ² | moyenne |
| **Lun 27/07** | **Ch. 4** : lectures ACP/AFC/ACM + synthèse → **ch. 4 fini** | moyenne |
| **Mar 28/07** | **Ch. 5** (protocole, limites+survivorship, perspectives) + **Ch. 6** (conclusion) | légère×2 |
| **Mer 29/07** | **§1.3** (annonce du plan, EN DERNIER) + page de garde « Prénom NOM » + relecture chiffres périmés | légère |
| **Jeu 30/07** | **Compilation propre** : ≤ 40 pages, bijectivité biblio, figures, encadrés→texte | technique |
| **Ven 31/07** | **Relecture orthographe + registre** intégrale (passe « anti-oral ») | attention |
| **Sam 1 – Dim 2/08** | **MARGE** (imprévus, 2ᵉ relecture) | tampon |
| **Lun 3/08** | **RENDU** | — |

**Point critique = jeu 23** (étape 1 bis). Si ça déborde → étaler sur 23-24, la marge (1-2/08) absorbe.
**Après le 3/08** : 12 jours pour diapo + exposé (oral 15/08), hors de ce calendrier.

### (ancien détail support, conservé)
| Jour | Support (chat) |
|---|---|
| au fil | correction fautes ; fournir chiffres/figures depuis `bloc1/03_resultats/` ; recalcul étapes 2-6 sans oracle |
| **J12** 30/07 | relecture anti-plagiat intégrale | cohérence texte ↔ `03_resultats/` |
| **J13-J15** 31/07-2/08 | **MARGE** + préparation orale (20 min + Q&A) | `preparation_oral.md` complet |
| **3/08** | **RENDU** | — |

## 4. Points de vigilance

-1. **⚠️ ÉTAPES 2-6 (ch. 4) À RECALCULER SANS L'ORACLE** : l'oracle témoin
   (edge ~+26 %) a été ajouté à la base (11 stratégies) ; il DOIT rester dans le
   ch. 3 (jugement) mais être EXCLU du ch. 4 (ANOVA, χ², ACP/AFC/ACM) où il
   écraserait tout. Les scripts `bloc1/02_methodes/etape2..6*.py` incluront
   désormais l'oracle si on les relance -> filtrer `strategy != 'oracle'` avant
   de régénérer les chiffres du ch. 4. Encadré déjà posé dans `04_contexte.tex`.
   Les chiffres actuels du ch. 4 (F≈47, χ²…) datent d'AVANT l'oracle = encore
   valides tant qu'on ne relance pas les scripts bruts.
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
