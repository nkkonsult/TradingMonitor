# Bloc 2 — Les signaux d'information ont-ils une valeur ? (synthèse)

> Section de rapport autonome. Elle résume le **Bloc 2** : la question, les données, les
> quatre analyses statistiques appliquées, et le **verdict commun** qui en ressort. Le détail
> du code est en annexe (`bloc2/02_methodes/`), le détail des données dans `01_donnees/`.

## 1. La question du bloc

Le Bloc 1 a montré que l'analyse **technique** seule ne sépare pas les gagnants des perdants.
On se tourne donc vers l'**information exogène** : quand une information tombe sur une action
— un **contrat public** est attribué, un **membre du Congrès** déclare une transaction, une
**régulation fédérale** est publiée, une **entreprise** publie ses résultats — le cours
réagit-il *au-delà* de ce que le marché explique ? Autrement dit, ces signaux ont-ils une
**valeur prédictive**, ou l'information est-elle **déjà intégrée** dans les prix (efficience
des marchés) ?

## 2. Les données

Les signaux sont collectés via les **agents n8n** du projet (mêmes sources : USASpending,
Federal Register, FMP…), puis **figés en CSV** et normalisés en une base d'événements :
**1 ligne = 1 événement** `(signal, ticker, date, sens, secteur)`. Les signaux gratuits
(contrats, régulations) sont pleinement branchés ; les signaux à clé (Congrès, résultats)
sont **prêts** (mêmes scripts, il suffit de la clé FMP).

- **Contrats publics** (USASpending) : ~180 attributions ≥ 100 M$ rattachées à des sociétés
  cotées (essentiellement la **défense** : Lockheed, Boeing, RTX, Northrop…).
- **Régulations fédérales** (Federal Register) : ~2000 règles finales/proposées, réparties
  sur 7 secteurs, dont une part « significatives ».

Un **troisième signal** est branché via un pont n8n vers l'API FMP : les **transactions du
Congrès** (43 trades achat/vente datés) — la source-or de l'étude d'événement, mais dont FMP
ne livre que les trades récents (échantillon modeste, limite assumée).

La variable-juge est le **CAR** (*Cumulative Abnormal Return*) : le rendement du titre autour
de l'événement **moins** le rendement « normal » prédit par le modèle de marché
(`R = α + β·R_marché`). Un `CAR ≠ 0` signale une réaction anormale imputable au signal.

## 3. Les quatre analyses et leurs résultats

| # | Méthode (vue en cours) | Question | Résultat |
|---|---|---|---|
| 1 | **Étude d'événement** (CAR, Student/Wilcoxon) | Le signal déplace-t-il le cours ? | Contrats **+0,3 %** (p≈0,35), régulations **−0,15 %** (p≈0,2) : **non significatif**. L'info est déjà price-in. |
| 2 | **Tests par sens** (Shapiro, Student, Wilcoxon, Bonferroni) | Le *sens* du signal porte-t-il un edge ? | **Achat du Congrès → +2,0 %** (le CAR le plus élevé ; Wilcoxon p≈0,016 mais n=19, rejeté après Bonferroni). Régulation « significative » **−0,47 %** (p≈0,02, rejeté aussi). |
| 3 | **Khi-deux** (+ V de Cramér) | Le sens est-il lié à l'issue (hausse/baisse) ? | Congrès achat/vente : achats **14 hausses / 5 baisses**, V≈0,20 (**faible mais non négligeable**), à confirmer sur plus de données. Régulations : indépendant. |
| 4 | **Régression de Poisson** (+ binomiale négative) | Les événements se concentrent-ils par secteur ? | **Oui** (Consumer Disc. ×1,6, Energy ×1,6, IT ×1,3). Mais **sur-dispersion (≈27)** : en binomiale négative, effets significatifs 5 → 2. |

### Détail méthodologique (pour l'oral)
- **Étape 1** teste un effet dans *les deux sens* (bilatéral) : un signal peut faire monter
  *ou* baisser. La courbe `etape1_car.png` visualise le CAR moyen jour par jour.
- **Étape 2** : Shapiro rejette la normalité (grand n) → on s'appuie sur le **TCL** pour
  Student, **Wilcoxon** confirme. Le durcissement **Bonferroni** neutralise le seul effet
  marginal (régulation significative), ce qui est la conclusion *prudente* correcte.
- **Étape 4** illustre un piège classique : la **sur-dispersion**. La Poisson « voit » 5
  effets sectoriels ; la **binomiale négative**, plus honnête sur la variance, n'en retient
  que 2. « Significatif » n'est pas « robuste ».

## 4. La question centrale : la contagion (un signal sur A déplace-t-il B ?)

L'objectif n'est pas seulement de savoir si un signal est *tradable sur son propre titre*,
mais de mesurer ses **répercussions** : quand un signal touche un titre **A**, les actifs
**liés à A** — ses **pairs corrélés** (data-driven) et ses **matières premières / thèmes**
(ex. Tesla→lithium, défense→ETF ITA) — bougent-ils en réaction ? Deux méthodes
supplémentaires (étapes 5 et 6) répondent.

| # | Méthode | Question | Résultat |
|---|---|---|---|
| 5 | **Contagion simultanée** (CAR des cibles autour de J0) | Les actifs liés à A réagissent-ils ? | **OUI** : pairs corrélés CAR **+0,27 %** (p≈0,003), thèmes/matières **+0,26 %** (p≈0,0006). L'écosystème de A bouge. |
| 6 | **Contagion décalée / lead-lag** (immédiat J0-J1 vs décalé J2-J5 + Granger) | A précède-t-il B ? | Effet surtout **synchrone** (immédiat significatif) ; décalé J2-J5 **non significatif**. Léger entraînement A→B le lendemain sur les **pairs corrélés** (pente Granger +0,03, p≈0,05). |
| 7 | **Cartographie fine** (CAR par couple A→B + carte de chaleur) | Quels couples A→B précis sont contagieux ? | Canaux nets : **UNH→HUM +2,8 %**, labos pharma s'entraînent (**JNJ/LLY/PFE→MRK +1,6 %**) ; défense en **substitution** (**BA→RTX −0,7 %**, LMT/BA→ETF défense ITA baisse). Carte : `etape7_heatmap.png`. |

> **La contagion est réelle : un signal sur A déplace significativement les actifs liés à A
> (pairs corrélés et matières premières).** Mais elle est **essentiellement synchrone** (le
> jour même) ; l'entraînement décalé, seul vraiment exploitable, n'est que **marginal** (A
> précède faiblement B d'un jour, sur les pairs corrélés uniquement).

## 5. Le verdict commun

Les six méthodes convergent :

> **Impact direct** — sur les signaux publics testés (contrats, régulations), aucun ne dégage
> d'edge significatif *sur son propre titre* après correction : le marché a **anticipé**
> l'information. **Impact de contagion** — en revanche, un signal **se propage** aux actifs
> liés (pairs, matières premières), surtout de façon **synchrone**. Et ces événements ne
> tombent pas au hasard : ils se **concentrent** sur quelques secteurs (défense, énergie, tech).

## 6. Limites assumées

- **Anticipation / fenêtre** : le CAR est mesuré J−1→J+5 ; une information peut fuiter avant
  (délit d'initié, anticipation) → l'effet « jour de l'annonce » est dilué. Tester des
  fenêtres plus larges est une piste.
- **Mapping et projection** : contrats rattachés par nom (défense cotée surtout) ; régulations
  projetées sur des paniers sectoriels → événements corrélés intra-secteur.
- **Contagion** : les *pairs corrélés* sont data-driven (corrélation des rendements) ; les
  *liens thématiques* (A→matière première) sont un **choix économique déclaré**
  (`liens_thematiques.py`), donc discutable et limité aux titres suivis.
- **Signaux à clé non encore branchés** : le **Congrès (achat/vente)** et les **surprises de
  résultats** sont *le* cas d'école de l'étude d'événement ; le code les intègre dès que la
  clé FMP est fournie. Le verdict actuel ne porte donc **que** sur l'information publique
  « lente » (contrats, régulations), pas encore sur l'information « à sens » (achat/vente).

## 7. Ce que ça implique pour la suite

L'information publique « lente » est déjà dans les prix : peu d'edge. La **valeur** se
trouvera plutôt dans les signaux **à sens et à délai court** (transactions du Congrès,
surprises de résultats) — prêts à être mesurés — et dans la **combinaison** des signaux
validés. La **régression finale** (Bloc final) ne retiendra que les signaux ayant prouvé leur
valeur ; à ce stade, le Bloc 2 apporte surtout un **outil réutilisable** (moteur d'event
study) et une **cartographie** (les 28 signaux, cf. `CATALOGUE_SIGNAUX.md`).
