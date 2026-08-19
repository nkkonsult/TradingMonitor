# Fiche méthodes — le raisonnement scientifique derrière chaque méthode

> Chaque méthode suit le même gabarit : **la question** qu'elle pose, **le
> raisonnement** (pourquoi cette méthode et pas une autre), **la mécanique**
> (formule et comment on la lit), **chez nous** (le résultat), **vigilance**
> (le piège). Les ⭐ renvoient à tes dix questions du 18/08.
>
> Ordre = ordre du protocole. C'est aussi l'ordre des diapos.

---

## 1. L'edge (Monte Carlo apparié)

- **Question** : combien la stratégie rapporte-t-elle DE PLUS qu'une entrée au
  hasard de même exposition ?
- **Raisonnement** : sur un marché haussier, le gain brut confond deux choses —
  le talent de timing et la marée qui soulève tous les bateaux. Pour isoler le
  timing, on compare chaque trade à son propre contrefactuel : même titre, même
  durée, même sens, seule la date d'entrée est tirée au sort (200 fois, on
  moyenne). Ce qui reste ne peut venir que du choix de la date.
- **Mécanique** : edge = return_net − rand_return, trade par trade.
- **Chez nous** : ~97 % des titres montent sur la période → tester le rendement
  brut n'aurait rien prouvé. Toute la suite teste l'edge, jamais le gain.
- **Vigilance** : un edge positif ≠ stratégie rentable (on peut « perdre moins
  que le hasard ») ; et l'edge est net de la dérive, pas des frais.

## 2. Test de Student (unilatéral, sur la moyenne de l'edge)

- **Question** : l'edge moyen théorique µ (inconnu) est-il > 0, sachant qu'on
  n'observe que ē (la moyenne d'un échantillon) ?
- **Raisonnement** : ē seul n'est pas interprétable — +0,012, c'est loin de
  zéro ? Ça dépend de la dispersion. On convertit donc l'écart en **nombre
  d'erreurs-types** : une échelle universelle sur laquelle une loi de référence
  existe. H0 : µ = 0 ; H1 : µ > 0 (unilatéral : seul un avantage nous intéresse).
- **Mécanique** : t = ē/(s/√n) ~ Student(n−1) sous H0. s au dénominateur est
  lui-même estimé (d'où Student et pas normale : le rapport de deux quantités
  aléatoires a des queues plus épaisses) ; le √n récompense la quantité de
  données. p-value = P(t aussi grand | H0) ; petite → le hasard n'est plus
  crédible.
- **Chez nous** : 3 survivants sur 11 au seuil de Bonferroni (oracle,
  rsi_classic 1,2·10⁻⁸, rsi_strict 5,5·10⁻¹⁰).
- **Vigilance** : deux conditions — normalité (traitée par le TCL) et
  indépendance (LE sujet du mémoire). Et erreur-type (s/√n, incertitude sur la
  moyenne) ≠ écart-type (s, dispersion des données).

## 3. Shapiro–Wilk puis TCL

- **Question** : la condition de normalité de Student est-elle remplie ?
- **Raisonnement en 3 temps** : (1) la condition formelle porte sur les
  observations → on la teste (Shapiro) ; (2) elle échoue partout — attendu en
  finance, queues lourdes ; (3) mais la statistique t ne dépend des données
  qu'à travers leur MOYENNE, et le TCL garantit la quasi-normalité de la
  moyenne à grand n quelle que soit la loi de départ. La condition utile est
  donc satisfaite.
- **Mécanique** : W = b²/SCE compare la dispersion « attendue si normal »
  (via les valeurs triées) à la dispersion classique ; elles ne coïncident que
  sous normalité → W ≃ 1 = normal (H0). TCL : (ē−µ)/(σ/√n) → N(0,1) — c'est
  exactement la statistique t avec s à la place de σ : le TCL justifie la
  forme même du test.
- **Chez nous** : rejet partout, W de 0,50 (ma_crossover) à 0,95 (dt_top) —
  même 0,95 est rejeté : à grand n, Shapiro sur-rejette. n de 978 à 8 513 :
  TCL largement applicable (variance finie garantie : rendements bornés).
- **Vigilance** : ne JAMAIS dire « les données sont normales ». Dire : « la
  moyenne l'est, et c'est elle que le test utilise ».

## 4. Correction de Bonferroni

- **Question** : avec 11 tests, comment garder un risque GLOBAL de faux
  positif ≤ 5 % ?
- **Raisonnement** : sous H0 partout, P(aucun faux positif) = 0,95¹¹ ≈ 0,57 →
  risque global 43 %. On inverse le problème : on fixe le global à 5 % et on en
  déduit le seuil individuel via l'inégalité de Boole (P(∪Aᵢ) ≤ ΣP(Aᵢ)).
- **Mécanique** : α' = 0,05/11 ≈ 0,0045. Vérif : 1 − (1−0,0045)¹¹ ≈ 0,049 < 0,05
  (légèrement conservateur).
- **Vigilance** : le calcul exact passe par le complémentaire (puissance), pas
  par l'addition (0,05 × 11 = 0,55 n'est qu'un majorant). Et on ne corrige QUE
  la famille des 11 verdicts : Shapiro, Box–Pierce, DF, KPSS sont des
  diagnostics de condition (seuil 5 %) — les corriger faciliterait la
  validation des conditions, l'inverse de la prudence.

---

## 5. Les trois canaux de dépendance (mesure AVANT correction)

⭐ **Ta question 1 — le chevauchement est-il une dépendance AVANT l'agrégation ?**

Oui, et c'est le point clé : la dépendance existe **au niveau des trades**,
l'agrégation mensuelle n'est que l'instrument qui sert à la MESURER puis à la
traiter.

Prends deux trades : A ouvert le 10 janvier, clos le 10 avril ; B ouvert le
1er février, clos le 1er mai. Leurs fenêtres de détention se recouvrent du
1er février au 10 avril. Or le rendement d'un trade est fabriqué par tout ce
qui se passe pendant sa détention — et pendant la fenêtre commune, A et B
subissent LE MÊME marché (dont on a mesuré qu'un facteur commun porte 73 % des
mouvements). Une partie de la « matière première » de leurs rendements est
identique → Cov(edge_A, edge_B) ≠ 0. Aucune agrégation n'est nécessaire pour
que cette covariance existe.

Différence avec le canal 2 : le canal 2 est la version **simultanée** (deux
trades ouverts le même jour subissent le même choc à l'ouverture — retard
zéro) ; le canal 3 est la version **décalée** (deux trades ouverts à des dates
différentes mais dont les détentions se recouvrent — c'est elle qui fait se
ressembler les mois voisins). Pourquoi alors mesurer le canal 3 sur la série
mensuelle ? Parce qu'une autocorrélation se calcule sur une série indexée par
le temps : on agrège par mois POUR mesurer, pas parce que la dépendance
naîtrait de l'agrégation. Et dans le protocole, les deux canaux temporels
passent par la même porte (période) : le simultané est réglé par l'agrégation
mensuelle elle-même (un mois = un vote), le décalé par la correction de série
temporelle qui suit.

## 6. Corrélation intra-grappe ρ̂ (ICC)

- **Question** : à quel point deux trades d'un même titre se ressemblent-ils ?
- **Raisonnement** : c'est la décomposition de la variance de l'ANOVA. Si les
  titres ne « comptent » pas, la variation entre titres (MSB) ≈ la variation
  dans les titres (MSW). Si les trades d'un titre se ressemblent, MSW
  s'effondre relativement à MSB. On normalise pour obtenir une échelle 0–1
  (un simple rapport MSB/MSW n'aurait pas d'échelle interprétable).
- **Mécanique** : ρ̂ = (MSB − MSW)/(MSB + (n₀−1)MSW), n₀ = taille moyenne
  ajustée des grappes.
- **Chez nous** : ≈ 0 partout sauf rsi_strict (0,134).
- **Vigilance** : ρ̂ ≈ 0 n'écarte QUE le canal 1 — les deux autres restent.

## 7. Effet de sondage (DEFF)

⭐ **Ta question 2 — d'où vient la formule DEFF = 1 + (m̄−1)ρ̂ ?**

- **Question** : de combien la variance de la moyenne est-elle sous-estimée
  quand on traite n trades groupés en grappes comme n trades indépendants ?
- **Dérivation (à savoir refaire au tableau)** : n trades en k titres de m
  trades chacun (n = km). Hypothèses : Var(xᵢ) = σ² ; Cov(xᵢ,xⱼ) = ρσ² si même
  titre, 0 sinon. On développe la variance de la somme :

      Var(Σxᵢ) = Σᵢ Var(xᵢ) + Σᵢ Σ_{j≠i} Cov(xᵢ,xⱼ)
               = nσ² + n(m−1)ρσ²

  (chaque trade a exactement m−1 « partenaires » de grappe, chacun apportant
  ρσ² ; les couples inter-titres apportent 0). D'où :

      Var(x̄) = Var(Σxᵢ)/n² = (σ²/n)·[1 + (m−1)ρ]

  Le crochet est le DEFF : le rapport entre cette variance réelle et la
  variance du sondage aléatoire simple σ²/n.
- **Contrôles de cohérence** (à dégainer si on te pousse) : ρ = 0 → DEFF = 1
  (indépendance, rien à corriger). ρ = 1 → DEFF = m → Var(x̄) = σ²/k : les m
  trades d'un titre ne portent qu'UNE information, il ne reste que k
  informations réelles. m = 1 → DEFF = 1 (une grappe d'un trade ne peut pas
  porter de dépendance interne). Grappes inégales → on remplace m par m̄.
- **Usage** : n_eff = n/DEFF ; erreur-type × √DEFF ; on refait Student.
- **Chez nous** : DEFF = 1,00 (rsi_classic), 1,15 (rsi_strict), 1,67 (oracle) —
  verdicts inchangés.
- **Vigilance** : le DEFF corrige la variance mais GARDE la pondération (un
  titre à 200 trades pèse 200 fois plus). C'est la porte action qui changera
  la question.

## 8. Bootstrap par grappes (Efron)

- **Question** : même verdict, mais sans aucune hypothèse sur la forme de la
  dépendance ?
- **Raisonnement** : au lieu de corriger une formule, on reconstruit la
  distribution d'échantillonnage empiriquement. On tire avec remise des TITRES
  ENTIERS (la dépendance interne de chaque grappe voyage intacte dans la
  réplique) ; 4 000 tirages → 4 000 moyennes d'edge → une cloche. Sa largeur
  EST l'erreur-type sous dépendance intra-titre.
- **Mécanique** : p-value = proportion de répliques dont la moyenne ≤ 0,
  comparée au seuil de Bonferroni.
- **Chez nous** : < 2,5·10⁻⁴ pour les trois survivantes — confirme le DEFF.
- **Vigilance** : suppose les titres indépendants entre eux (faux à cause du
  marché — traité par la porte période) ; et une cloche étroite peut venir
  d'une concentration sur peu de titres → d'où la méthode suivante.

## 9. Les deux portes (agrégation équipondérée)

- **Question** : l'avantage se généralise-t-il, ou tient-il à quelques titres
  (ou quelques mois) sur-représentés ?
- **Raisonnement** : on change la question posée. Une unité réelle, un vote :
  edge moyen par titre → Student sur les 431–501 moyennes (porte action) ;
  edge moyen par mois d'entrée → Student sur les 138–197 moyennes (porte
  période). La dépendance interne d'une grappe ne peut plus rien fausser. On
  perd de l'information : choix assumé — pour un outil de VALIDATION, faux
  négatif < faux positif.
- **Chez nous** : oracle passe les deux portes (p ≈ 0). rsi_classic tombe aux
  deux (p_A = 0,059 ; p_B = 0,039 — loin de 0,0045) : pseudo-réplication.
  rsi_strict passe l'action (3,9·10⁻⁴) mais échoue la période (0,26) :
  avantage réel mais épisodique.
- **Vigilance** : pourquoi pas d'agrégation croisée titre×mois ? Grappes trop
  petites, rouvrirait les portes ; la règle du ET est plus exigeante. Le cas
  résiduel (dépendance propre à UN titre pendant UN mois) relève du double
  clustering de Petersen — cité en limite.

---

## 10. Box–Pierce (sur la série mensuelle brute)

⭐ **Ta question 3 — pourquoi les autocorrélations sont-elles « du bruit » sous H0 ?**

- **Question** : les mois sont-ils indépendants ? (On ne corrige que ce qui
  est mesuré.)
- **Le point clé** : même une série PARFAITEMENT indépendante ne donne jamais
  ρ̂(h) = 0 exactement. L'estimateur

      ρ̂(h) = Σₜ (xₜ−x̄)(xₜ₊ₕ−x̄) / Σₜ (xₜ−x̄)²

  est une somme de T−h produits croisés. Sous H0 (indépendance), chaque
  produit (xₜ−x̄)(xₜ₊ₕ−x̄) a une espérance nulle — les deux facteurs sont
  indépendants et centrés — mais sa réalisation ne l'est pas : les produits
  positifs et négatifs ne se compensent qu'imparfaitement sur un échantillon
  fini. C'est le même phénomène qu'une moyenne d'échantillon qui n'est jamais
  exactement µ. Le TCL appliqué à cette somme donne l'ordre de grandeur du
  résidu : Var(ρ̂(h)) ≈ 1/T, donc √T·ρ̂(h) → N(0,1). « Du bruit d'ordre
  1/√T » signifie exactement cela : sur T = 195 mois, des ρ̂ de ±0,07 sont
  ATTENDUS sans aucune dépendance réelle.
- **Mécanique** : d'où le test : T·ρ̂(h)² ~ χ²(1), et la somme sur h = 1…6
  (carrés pour que les signes ne se compensent pas, asymptotiquement
  indépendants entre h) : S_BP = T·Σρ̂(h)² ~ χ²(6) sous H0. Rejet si p < 5 %.
  Six décalages car la dépendance vient du recouvrement des détentions, qui
  dépassent rarement 6 mois (plafond vérifié a posteriori sur les résidus).
- **Chez nous** : la moitié des séries autocorrélées (branche correction) ;
  l'autre moitié — dont oracle et rsi_strict — garde son verdict tel quel.
- **Vigilance** : « série brute » = la série mensuelle telle quelle, avant
  tout modèle — par opposition aux résidus du modèle AR (étape 15).

## 11. Dickey–Fuller (augmenté)

⭐ **Ta question 4 — comment fonctionne la régression ?**

- **Question** : la série est-elle stationnaire (les chocs s'éteignent-ils) ?
- **La régression, concrètement** : on fabrique T−1 couples (x_{t−1}, x_t) —
  chaque mois apparié à son prédécesseur — et on trace le nuage : x_{t−1} en
  abscisse, x_t en ordonnée. La régression de cours (moindres carrés) y
  ajuste la droite x_t = φ·x_{t−1} + η_t en minimisant Σ(x_t − φx_{t−1})² :

      φ̂ = Σ x_{t−1}·x_t / Σ x_{t−1}²   (pente = covariance/variance)
      se(φ̂) = σ̂_η / √(Σ x_{t−1}²)

  La pente φ̂ dit : « quand un mois est haut de 1, combien le mois suivant en
  garde-t-il en moyenne ? » En pratique on régresse plutôt la DIFFÉRENCE :
  Δx_t = δ·x_{t−1} + η_t avec δ = φ−1, et on teste δ = 0 contre δ < 0 —
  strictement équivalent, plus stable numériquement. Version « augmentée » :
  on ajoute Δx_{t−1}, …, Δx_{t−k} comme régresseurs pour nettoyer
  l'autocorrélation des résidus (k choisi par AIC, 0 à 9 chez nous).
- **Pourquoi PAS la loi de Student** (le bijou pour ce jury) : t_DF =
  (φ̂−1)/se(φ̂) a la FORME d'un t de régression. Mais la loi de Student du
  cours suppose un régresseur stationnaire. Sous H0 (φ=1), le régresseur
  x_{t−1} est une marche aléatoire : sa variance croît avec t, les conditions
  s'effondrent. Dickey et Fuller ont établi et tabulé la vraie loi
  asymptotique — décalée vers les négatifs : il faut ≈ −2,9 pour rejeter à
  5 %, là où une normale unilatérale rejetterait dès −1,65. Utiliser Student
  ici conclurait « stationnaire » beaucoup trop facilement.
- **Chez nous** : rejet (p ≤ 0,005) pour toutes les séries concernées.

## 12. KPSS

- **Question** : la même, mais avec H0 inversée (H0 = stationnaire).
- **Mécanique** : cumuls des écarts à la moyenne S_t = Σ_{s≤t}(x_s − x̄). Si la
  série oscille autour d'un niveau, les écarts + et − se compensent, les
  cumuls restent bornés ; si elle dérive, les écarts s'empilent du même côté
  et les cumuls s'emballent. Statistique = Σ S_t²/(T²·variance de long terme),
  loi tabulée. Testé autour d'une constante (pas d'une tendance : rien ne
  laisse attendre qu'un avantage dérive régulièrement).
- **Chez nous** : aucun rejet → concordance avec DF partout.

## 13. La règle de concordance

⭐ **Ta question 5 — pourquoi chaque test seul ne suffit-il pas ?**

Le principe de fond : un test ne contrôle que son erreur de type I — il ne
sait GARANTIR qu'un rejet. « Ne pas rejeter » mélange deux situations
indiscernables : « H0 est vraie » et « je n'ai pas assez de puissance pour
voir qu'elle est fausse ». Ne pas rejeter n'est jamais une preuve.

- **DF seul ne suffit pas** : son H0 est la non-stationnarité. S'il ne rejette
  pas, on ne sait pas si la série a vraiment une racine unitaire ou si le test
  a manqué de puissance (série courte, φ proche de 1, ou série dégénérée —
  cas vécu de l'oracle v1 ci-dessous). Conclure « non stationnaire » sur ce
  non-rejet, c'est transformer une absence de preuve en preuve. De plus son
  rejet n'écarte QUE la racine unitaire — une forme de non-stationnarité parmi
  d'autres (tendance déterministe, variance changeante).
- **KPSS seul ne suffit pas** : symétriquement, son H0 est la stationnarité ;
  ne pas rejeter peut signifier « stationnaire » comme « pas la puissance de
  détecter une dérive modeste ». Conclure « stationnaire » sur ce seul
  non-rejet a le même vice.
- **Pourquoi la concordance règle le problème** : on exige que DF REJETTE
  (énoncé contrôlé : « pas de racine unitaire, à 5 % près ») ET que KPSS ne
  rejette pas. La conclusion s'appuie ainsi sur au moins un rejet contrôlé, et
  les angles morts des deux tests ne se recouvrent pas : DF couvre la racine
  unitaire, KPSS couvre la dérive et la tendance. Pour se tromper, il faudrait
  que les deux se trompent en même temps, dans des directions opposées.
- **Divergence** → les données ne permettent pas de trancher → verdict « ? »,
  non concluant, renvoyé à l'humain. JAMAIS un rejet (non concluant ≠
  défavorable).

⭐ **Ta question 6 — les deux oracles, et l'erreur de conception du premier**

- **Oracle v1** : seuil +25 % sur 30 jours. Conséquence : il ne tradait que
  les rebonds extrêmes (sorties de krach : 2009, 2020). Edge écrasant
  (t ≈ 120), mais trades concentrés sur quelques mois de régime
  exceptionnel : la série mensuelle était « tassée » — presque plate en
  dehors de ces bouffées. Or la régression de Dickey–Fuller a besoin de
  variabilité dans x_{t−1} pour estimer sa pente (φ̂ et son erreur-type
  reposent sur Σx_{t−1}²) : sur une série sans relief, l'erreur-type explose,
  le test perd toute puissance et ne peut pas rejeter la racine unitaire —
  alors que la série est évidemment stationnaire. DF disait « ? », KPSS
  disait « stationnaire » : divergence, verdict non concluant.
- **L'erreur de conception** : un témoin doit vivre dans le même domaine que
  les stratégies qu'il calibre. En le rendant trop parfait, on avait produit
  une série dégénérée, hors du domaine de puissance des outils qu'il devait
  précisément éprouver.
- **Oracle v2** : seuil +5 %, horizon 30 jours, ~1 an de repos entre deux
  entrées (volume comparable aux vraies stratégies). Entrées réparties sur
  tous les régimes : témoin réaliste, avantage toujours franchement positif —
  il franchit tous les étages.
- **La leçon à vendre au jury** : c'est le protocole à DEUX tests qui a rendu
  l'anomalie VISIBLE (un protocole à un seul test aurait écarté le témoin en
  silence). Le témoin a servi à réviser le protocole : c'est exactement le
  rôle d'un contrôle.

## 14. Autocorrélation partielle (PACF) et choix de l'ordre

⭐ **Ta question 7 — expliquer la PACF**

- **Le problème qu'elle résout** : l'autocorrélation simple ρ(2) est
  contaminée par l'effet de chaîne. Si chaque mois dépend du précédent avec un
  poids 0,6, alors ρ(2) ≈ 0,36 : le mois t « semble » lié à t−2, mais ce lien
  transite ENTIÈREMENT par t−1 — il n'y a aucun effet direct. Pour choisir
  combien de mois de mémoire mettre dans le modèle, il faut l'impact PROPRE de
  chaque décalage, pas l'impact hérité.
- **Définition opératoire** : τ(h) = corrélation entre x_t et x_{t−h} UNE FOIS
  RETIRÉE l'influence linéaire des mois intermédiaires. Concrètement : on
  régresse x_t sur (x_{t−1},…,x_{t−h+1}), on régresse x_{t−h} sur les mêmes,
  et on corrèle les deux résidus — ce qui reste de t et ce qui reste de t−h
  quand les intermédiaires ont tout expliqué. Équivalence utile : τ(h) est le
  DERNIER coefficient d'un AR(h) ajusté sur la série.
- **Pourquoi elle identifie l'ordre** : pour un AR(p), τ(h) = 0 pour tout
  h > p (elle « se coupe » net après p) — alors que ρ(h) décroît sans jamais
  s'annuler. Le dernier τ significatif estime donc p.
- **Décision** : sous H0 (τ(h)=0), √T·τ̂(h) ~ N(0,1) → bande ±1,96/√T sur le
  corrélogramme partiel ; on retient le dernier décalage significatif,
  plafond 6, décalages intermédiaires conservés (on préfère surestimer la
  mémoire que la tronquer).
- **Chez nous** : p̂ de 0 à 3 (ma_crossover : 3).

## 15. Modèle AR(p) et équations de Yule–Walker

⭐ **Ta question 8 — pourquoi l'espérance fait-elle apparaître l'autocorrélation ?**

- **Les définitions d'abord** (tout est là) : pour une série stationnaire
  CENTRÉE (on a retiré la moyenne),

      γ(h) = Cov(x_t, x_{t−h}) = E[x_t · x_{t−h}]     (autocovariance)
      ρ(h) = γ(h)/γ(0)                                  (autocorrélation)

  La covariance de deux variables centrées EST l'espérance de leur produit —
  c'est la définition. Donc « multiplier par x_{t−h} et prendre l'espérance »
  n'est pas un tour de magie : c'est littéralement CALCULER une
  autocovariance.
- **La manipulation** : on part du modèle x_t = Φ₁x_{t−1} + … + Φ_p x_{t−p} + η_t,
  on multiplie les deux membres par x_{t−h} (h ≥ 1), on prend l'espérance :

      E[x_t x_{t−h}] = Σᵢ Φᵢ E[x_{t−i} x_{t−h}] + E[η_t x_{t−h}]
      γ(h)           = Σᵢ Φᵢ γ(h−i)               + 0

  Le terme de bruit disparaît car η_t est indépendant de tout le passé, donc
  E[η_t x_{t−h}] = E[η_t]·E[x_{t−h}] = 0. On divise par γ(0) :
  ρ(h) = Σᵢ Φᵢ ρ(h−i), pour h = 1…p → p équations linéaires, p inconnues Φᵢ
  (avec ρ(0) = 1 et ρ(−k) = ρ(k)). On y met les ρ̂ mesurés, on résout.
- **L'estimateur de ρ en pratique** :
  ρ̂(h) = Σ_{t=1}^{T−h}(x_t−x̄)(x_{t+h}−x̄) / Σ_{t=1}^{T}(x_t−x̄)².
- **Cas p = 1 éclairant** : le système se réduit à Φ₁ = ρ(1).
- **L'équation du décalage nul** (h = 0) : même manipulation avec x_t
  lui-même. Cette fois le bruit ne disparaît pas (x_t contient η_t, donc
  E[η_t x_t] = σ²_η) :

      γ(0) = Σᵢ Φᵢ γ(i) + σ²_η   ⟹   σ²_η = γ(0)·(1 − Σᵢ Φᵢ ρ(i))

  Lecture : la variance du bruit = la variance totale moins la part que le
  passé explique — ce qui reste imprévisible.

⭐ **Ta question 9 — pourquoi pas ARMA ou ARIMA ?**

Réponse en quatre temps, du plus décisif au plus pratique :
1. **ARIMA d'abord** : le « I » (intégration) consiste à différencier une
   série NON stationnaire pour la rendre stationnaire. Nos séries SONT
   stationnaires — on vient de le vérifier par DF + KPSS. Donc d = 0, et
   ARIMA se réduit à ARMA. Différencier une série déjà stationnaire serait
   une erreur (sur-différenciation : on injecte une autocorrélation négative
   artificielle).
2. **L'objectif n'est pas la prévision mais une correction de variance** : il
   faut un modèle qui ABSORBE l'autocorrélation, pas le meilleur prédicteur.
   Le critère d'adéquation est vérifié A POSTERIORI : Box–Pierce sur les
   résidus ne rejette rien → l'AR seul a déjà capté toute la mémoire
   mesurable. Un terme MA n'aurait rien à expliquer : sa valeur ajoutée
   serait indétectable dans nos données.
3. **Théorie** : tout MA ou ARMA inversible s'écrit comme un AR(∞) ; pour des
   mémoires courtes et modérées comme les nôtres, un AR d'ordre faible en est
   une excellente approximation. On ne perd rien de structurel.
4. **Parcimonie et ancrage cours** : l'AR s'estime par Yule–Walker — un
   système LINÉAIRE résoluble à la main. Un MA s'estime par des méthodes
   itératives non linéaires (les η_t ne sont pas observés). À pouvoir
   explicatif égal (cf. point 2), on prend le modèle le plus simple.
   Et si Box–Pierce sur résidus AVAIT rejeté, le protocole le signale et
   c'est précisément là qu'ARMA serait devenu la suite logique.

## 16. Variance de long terme et test corrigé

⭐ **Ta question 10 — le raisonnement mathématique après le calcul des poids**

Le fil, en trois pas — l'objectif est UNE quantité : Var(x̄), la variance de
la moyenne mensuelle, car c'est elle qui fait le dénominateur du test.

**Pas 1 — pourquoi s²/T est faux sous dépendance.** Par définition :

    Var(x̄) = (1/T²)·Σₜ Σₛ Cov(x_t, x_s)

La double somme contient T termes diagonaux γ(0) — c'est tout ce que garde la
formule usuelle s²/T — mais aussi TOUS les termes croisés γ(h), h ≠ 0. Sous
autocorrélation positive, on les jette à tort : la variance est sous-estimée.
En comptant les termes (il y a ≈ T couples à chaque écart h), on obtient pour
T grand :

    Var(x̄) ≈ (1/T)·Σ_{h=−∞}^{+∞} γ(h)  =  γ_lr / T

La somme de TOUTES les autocovariances s'appelle la variance de long terme.

**Pas 2 — pourquoi γ_lr = σ²_η/(1 − ΣΦᵢ)² pour un AR(p).** L'argument de
l'effet cumulé d'un choc : dans l'AR, un choc η de +1 élève le mois courant
de 1 ; le mois suivant en garde ΣΦ, le suivant (ΣΦ)², etc. Sa contribution
TOTALE à la somme des mois vaut donc la série géométrique :

    1 + (ΣΦ) + (ΣΦ)² + … = 1/(1 − ΣΦ)

La somme Σx_t est ainsi, pour T grand, une somme de T chocs indépendants
entrant chacun avec le poids total 1/(1−ΣΦ) :

    Var(Σx_t) ≈ T · σ²_η/(1−ΣΦ)²   ⟹   Var(x̄) ≈ σ²_η / [T·(1−ΣΦ)²]

Vérification exacte sur l'AR(1) (à savoir refaire) : γ(h) = φ^|h|·γ(0) avec
γ(0) = σ²_η/(1−φ²) ; Σ_h γ(h) = γ(0)·(1+φ)/(1−φ) = σ²_η/(1−φ)². ✓

**Pas 3 — le test corrigé.** On remplace le dénominateur et on relit :

    se_corr = √(γ_lr/T)          t = x̄ / se_corr
    DEFF_t  = γ_lr/γ(0)          T_eff = T/DEFF_t   (degrés de liberté)
    p-value confrontée au seuil de Bonferroni (0,0045)

Cohérences : Φ = 0 → γ_lr = σ²_η = γ(0) → on retrouve s²/T exactement, et
DEFF_t = 1. Plus ΣΦ approche 1 (persistance forte), plus γ_lr explose. Le
DEFF_t est l'exact analogue temporel du DEFF de sondage : le facteur de
sous-estimation de la variance quand on ignore la dépendance.

- **Chez nous** : DEFF_t jusqu'à 6,4 (ma_crossover : erreur-type × 2,5).
  Aucun verdict ne bascule. L'oracle passe (DEFF_t = 1, p = 9,4·10⁻⁸⁵).

## 17. Box–Pierce sur les résidus (validation du modèle)

- **Question** : le modèle a-t-il bien absorbé TOUTE la mémoire ?
- **Raisonnement** : la correction n'est légitime que si les résidus η̂_t sont
  un bruit blanc. On pose aux résidus exactement la question posée à la série
  brute — circularité au bon sens du terme : « y a-t-il de la mémoire ? »
  puis « en reste-t-il ? ».
- **Mécanique** : mêmes statistiques, deux différences. 15 décalages au lieu
  de 6 (pratique usuelle 15–20) → le plafond de 6 n'a rien pu laisser
  échapper. Et χ²(15−p̂) : on retranche les p̂ paramètres estimés sur les
  mêmes données, qui rendent les résidus artificiellement propres.
- **Chez nous** : aucun rejet (pire cas : rsi_trend, p = 0,06 — limite mais
  passe). Corrections validées.

---

# Le fil à retenir (si tu ne retiens qu'une chose)

Le protocole entier tient en une phrase : **le test de Student est juste si
son dénominateur dit vrai** — et chaque étage du protocole répare une façon
dont ce dénominateur peut mentir. La dérive du marché fausse le numérateur
(→ edge apparié). La non-normalité menace la loi de référence (→ TCL). La
multiplicité fausse le seuil (→ Bonferroni). La dépendance intra-titre, la
concentration, et l'autocorrélation mensuelle font toutes la même chose :
elles font croire à n informations quand il y en a moins → erreur-type
sous-estimée → t gonflé → faux positifs (→ DEFF, bootstrap, portes, variance
de long terme). Quand une condition n'est pas vérifiable, on s'abstient et on
signale. Chaque méthode du mémoire est une déclinaison de cette unique idée.
