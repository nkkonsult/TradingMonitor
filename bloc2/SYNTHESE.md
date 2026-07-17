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
Congrès** (41 trades achat/vente), datées à la **divulgation** STOCK Act — la seule date que
le marché (et un trader) peut voir ; la date du trade de l'élu mesurerait son talent, pas un
signal exploitable. FMP ne livre que les trades récents (échantillon modeste, limite assumée).

La variable-juge est le **CAR** (*Cumulative Abnormal Return*) : le rendement du titre autour
de l'événement **moins** le rendement « normal » prédit par le modèle de marché
(`R = α + β·R_marché`). Un `CAR ≠ 0` signale une réaction anormale imputable au signal.

## 3. Les quatre analyses et leurs résultats

| # | Méthode (vue en cours) | Question | Résultat |
|---|---|---|---|
| 1 | **Étude d'événement** (CAR, Student/Wilcoxon) | Le signal déplace-t-il le cours ? | Contrats **+0,3 %** (p≈0,35), régulations **−0,15 %** (p≈0,2) : **non significatif**. L'info est déjà price-in. |
| 2 | **Tests par sens** (Shapiro, Student, Wilcoxon, Bonferroni) | Le *sens* du signal porte-t-il un edge ? | Régulation « significative » **−0,47 %** (p≈0,02, rejeté après Bonferroni). Aucun sens ne survit. |
| 3 | **Khi-deux** (+ V de Cramér) | Le sens est-il lié à l'issue (hausse/baisse) ? | **Indépendant** partout (V faibles). |
| 4 | **Régression de Poisson** (+ binomiale négative) | Les événements se concentrent-ils par secteur ? | **Oui** (Consumer Disc. ×1,6, Energy ×1,6, IT ×1,3). Mais **sur-dispersion (≈27)** : en binomiale négative, effets significatifs 5 → 2. |
| 8 | **Les deux portes de la dépendance** (1 événement = 1 vote ; 1 mois = 1 vote) | Les verdicts tiennent-ils une fois l'indépendance rétablie ? | **Aucun signal ne passe les deux portes.** Régulations dédupliquées (653 règles, pas 2 700 lignes) : p=0,04 > seuil. **Congrès daté à la divulgation : le +2,0 % disparaît (−1,8 %, ns)** — le gain mesuré au trade_date était le timing de l'élu, pas un signal exploitable. |

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
| 5 | **Contagion simultanée** (CAR des cibles autour de J0) | Les actifs liés à A réagissent-ils ? | **Instable** : les verdicts d'ensemble changent de signe selon la définition de la base d'événements (avant/après déduplication). Sans les deux portes, ces tests héritent de la pseudo-réplication → **exploratoire, non concluant**. |
| 6 | **Contagion décalée / lead-lag** (immédiat J0-J1 vs décalé J2-J5 + Granger) | A précède-t-il B ? | Ce qui est stable : l'effet, quand il existe, est **synchrone** (donc déjà dans les prix) ; le décalé J2-J5 n'est jamais significatif. **Pas de signal exploitable.** |
| 7 | **Cartographie fine** (CAR par couple A→B + carte de chaleur) | Quels couples A→B précis sont contagieux ? | Quelques canaux récurrents à titre exploratoire : **UNH→HUM** (+3,2 %, p≈0,006), labos pharma s'entraînent (**LLY→MRK** +1,9 %) ; énergie en substitution (**CVX/EOG→SLB** −2,4 %). Carte : `etape7_heatmap.png`. |

> **Verdict prudent : la contagion, quand elle apparaît, est synchrone — donc déjà intégrée
> aux prix — et ses tests d'ensemble sont instables** (ils changent avec la définition de la
> base d'événements, car ils héritent de la pseudo-réplication non corrigée). Seuls quelques
> canaux par couple (UNH→HUM, LLY→MRK) reviennent de façon récurrente, à titre exploratoire.
> Rien d'exploitable en décalé.

## 5. Le verdict commun

Toutes les méthodes convergent, y compris après fermeture des **deux portes de la
dépendance** (même discipline que le Bloc 1 : un événement = un vote, un mois = un vote) :

> **Impact direct** — aucun signal d'information testé (contrats, régulations, Congrès à la
> date de divulgation) ne dégage d'edge significatif *sur son propre titre* une fois
> l'indépendance rétablie : le marché a **anticipé** l'information. **Impact de contagion** —
> un signal **se propage** aux actifs liés (pairs, matières premières), surtout de façon
> **synchrone** (donc déjà dans les prix, non exploitable en décalé). Et ces événements ne
> tombent pas au hasard : ils se **concentrent** sur quelques secteurs (défense, énergie, tech).

C'est le résultat attendu d'un **outil de validation qui fonctionne** : appliqué à de
l'information publique, il conclut — proprement — qu'elle est déjà incorporée (efficience
semi-forte). Un outil qui dit « non » à bon escient est un outil validé.

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
