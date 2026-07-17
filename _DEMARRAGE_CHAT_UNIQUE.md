# Passation — CHAT UNIQUE (remplace les 2 chats parallèles)

> À lire par le nouveau chat ouvert dans **`D:\Trading Agent\TradingMonitor`** (worktree
> principal, branche `main`). Ce fichier est LA source de vérité sur l'état du projet
> au 17 juillet 2026. Les deux anciens chats (rapport sur `main`, Bloc 2 sur `bloc2-dev`)
> sont abandonnés au profit d'un seul.

## 0. Première action (obligatoire, 1 minute)
```bash
git merge bloc2-dev        # fast-forward : bloc2-dev contient déjà tout main + 6 commits
# ensuite, facultatif, quand plus besoin :
git worktree remove "D:/Trading Agent/TradingMonitor-bloc2"
git branch -d bloc2-dev
```

## 1. La mission
Mémoire M1 Statistique (Strasbourg). **Rendu : 3 août 2026** (PDF + source LaTeX),
**soutenance : 18 août**. Consignes officielles : `D:\Trading Agent\Consignes_M1_25_26.pdf`
(40 pages max, 10 p. annexes, pas de code complet, biblio↔citations bijective).

**L'angle (acté)** : on construit un **OUTIL DE VALIDATION statistique** de stratégies et
de signaux — on ne cherche PAS une stratégie gagnante. Les 10 stratégies (Bloc 1), les
signaux d'information (Bloc 2) et les relations inter-actions (Bloc 3) sont des **bancs
d'essai** de l'outil. Un verdict négatif rendu proprement = l'outil fonctionne.

## 2. Méthode de travail avec l'utilisateur (NON NÉGOCIABLE)
- Pour chaque méthode statistique : le chat **explique d'abord** en langage naturel
  (« on se demande… → la méthode répond »), **conditions d'application données EN MÊME
  TEMPS que la théorie** (jamais après coup).
- **C'est L'UTILISATEUR qui rédige** dans les `.tex` ; le chat corrige uniquement les
  fautes, sans changer son raisonnement (anti-plagiat strict).
- Méthodes ancrées dans `_synthese_cours/` en priorité ; hors-cours = dernier recours.
  Pas de `\cite` pour les méthodes standard de cours.
- **Ne JAMAIS prétendre que l'indépendance des trades/événements est défendable.**
- Noter au fil de l'eau les questions probables du jury dans `rapport/preparation_oral.md`.
- Compilation : `pdflatex` + `biber` directement (PAS latexmk, Perl absent).
- L'utilisateur veut des réponses **concises**, avancer **par étapes**, être **consulté
  à chaque décision**.

## 3. État des lieux (17 juillet 2026)

### Le verdict scientifique global (corrigé de la dépendance)
La découverte structurante du projet : les observations (trades, événements) ne sont pas
indépendantes → tous les tests naïfs étaient trop optimistes. Correction par **« les deux
portes »** : porte A = *une unité réelle, un vote* (par titre / par règle), porte B =
*un mois, un vote*. Verdict au standard corrigé :
- **Bloc 1** (`bloc1/03_resultats/etape1c_agregation.txt`) : **plus AUCUNE stratégie ne
  passe les deux portes** (rsi_classic = faux positif du test naïf ; rsi_strict passe la
  porte titre mais échoue à la porte mois). DEFF mensuel jusqu'à 6,5. Les moyennes
  mensuelles restent autocorrélées (ACF₁ jusqu'à 0,56) car des trades durent > 1 mois →
  une étape 1d (pipeline séries temporelles Giraudo : KPSS/DF, ACF/PACF, AR(p) Yule-Walker,
  variance corrigée, Box-Pierce) était en cours côté ancien chat rapport — **vérifier si
  `bloc1/02_methodes/etape1d_serie_mensuelle.py` existe, sinon la faire**.
- **Bloc 2** (`bloc2/03_resultats/etape8_portes_dependance.txt`) : **aucun signal ne passe
  les deux portes**. Régulations dédupliquées (653 règles réelles vs 2 700 pseudo-lignes).
  **Congrès daté à la DIVULGATION** (seule date visible du marché) : le +2,0 % mesuré au
  trade_date disparaît (−1,8 %, ns) — c'était le talent de l'initié, pas un signal
  exploitable. Contagion (étapes 5-7) requalifiée **exploratoire** (tests d'ensemble
  instables — pseudo-réplication non corrigée à ce niveau).
- **Bloc 3** : fait (corrélations, Granger, ACP 73 % facteur marché, ARIMA). Les méthodes
  de séries temporelles assument la dépendance — pas de correction nécessaire.
- **Bloc final** : PAS commencé. Décision en suspens : version légère (logistique
  `win ~ contexte`, PROC GENMOD-style) ou suppression. À trancher avec l'utilisateur.

### Le rapport (`rapport/`)
- `03_bloc1.tex` : étape 1 rédigée PAR L'UTILISATEUR (edge, Student, Shapiro, TCL,
  Bonferroni) + angle « outil de validation ». Reste : section dépendance (trame à
  fournir, il rédige), étapes 2-6, mise à jour des tableaux (ancienne base 38 035 →
  **38 210 trades, 501 titres**, base régénérée avec dates d'entrée/sortie).
- `04_bloc2.tex` : squelette vide. **Le brouillon complet est prêt** dans
  `bloc2/REDACTION_RAPPORT.md` (chiffres réels, section « deux portes » incluse) —
  l'utilisateur rédige à partir de cette trame.
- `01_introduction.tex` : à recadrer sur l'angle « outil » + les deux questions.
- `02_donnees.tex`, `05_bloc3.tex`, `06_blocfinal.tex`, `07_conclusion.tex`, annexes,
  biblio (7 entrées) : squelettes/trous. Voir `_PLAN_2_SEMAINES.md` (dépendances,
  calendrier) — décalé d'une semaine, il reste ~17 jours.
- Détails cosmétiques à ne pas oublier : « Prénom NOM » page de garde ; typo « RSF »
  dans la conclusion ; titre du mémoire à élargir aux signaux d'information ; encadré
  intro « Blocs 2-3 en état d'avancement » obsolète (ils sont finis).

### Les données / le code
- Bloc 1 : `bloc1/` (base 38 210 trades + etape1b/1c dépendance). Bloc 2 : `bloc2/`
  (8 étapes, collecteur n8n/API documenté). Bloc 3 : `bloc3/`.
- Prix : `backend/charts/data.get_ohlcv(ticker)` (yfinance + cache Parquet).
- Congrès (FMP) : la clé vit dans n8n, non lisible ; collecte via pont webhook temporaire
  (méthode documentée dans `bloc2/01_donnees/collecteur.py`, voie `CONGRES_WEBHOOK_URL`).
- Les 28 signaux du rapport n8n de l'utilisateur : cartographiés dans
  `bloc2/CATALOGUE_SIGNAUX.md` (roadmap post-mémoire).

## 4. Priorités des ~17 jours restants (proposition, à valider avec l'utilisateur)
1. **Rédaction d'abord** (le vrai goulot) : ch. 3 section dépendance → ch. 4 (trame prête)
   → ch. 2/5 → intro/conclusion → annexes/biblio. L'utilisateur écrit, le chat explique.
2. `etape1d` série mensuelle (si absente) — dernier maillon méthodo du Bloc 1.
3. Décision Bloc final (léger ou supprimé) → ch. 6 en conséquence.
4. Compilation, ≤ 40 pages, relecture, `preparation_oral.md`.
