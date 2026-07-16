# Plan de bataille — 2 semaines (9 → 23 juillet 2026)

> Topo établi après relecture complète : projet (blocs 1-2-3), rapport LaTeX (squelette +
> chapitres), synthèses des 15 cours, consignes M1. **Rendu officiel : 3 août 2026**
> (PDF + source). Objectif interne : **tout boucler le 23 juillet** → 10 jours de marge.
> Deux chantiers en parallèle : **chat Rapport** (branche `main`, dossier `rapport/`) et
> **chat Blocs** (branche `bloc2-dev`, dossiers `bloc2/` + `blocfinal/`).

---

## 1. État des lieux (constaté le 9 juillet)

### Côté technique (les blocs)
| Bloc | État | Contenu |
|---|---|---|
| **Bloc 1** — stratégies techniques | ✅ fini | 38 035 trades, 6 méthodes, verdict : seul le RSI bat le hasard |
| **Bloc 2** — signaux d'information | ✅ fini (sur `bloc2-dev`) | 2 921 événements, 3 signaux (contrats, régulations, Congrès), **7 méthodes** (event study, tests, χ², Poisson, contagion ×3) |
| **Bloc 3** — relations inter-actions | ✅ fini | 4 132 jours, 4 méthodes, facteur marché 73 % |
| **Bloc final** — régression | ❌ **PAS COMMENCÉ** | le seul chantier technique restant |

### Côté rapport (`rapport/`, 40 pages max, 10 p. annexes, code interdit)
| Chapitre | État | Reste à faire |
|---|---|---|
| 01 Introduction | ~60 % écrit | affiner but + planification (mentionner les 4 blocs finis) |
| 02 Données | squelette (4 trous) | écrire (les 3 dictionnaires existent déjà dans les blocs) |
| 03 Bloc 1 | ~70 % écrit | **7 trous** : résultats ACP/AFC/ACM à remplir depuis `bloc1/03_resultats/` |
| 04 Bloc 2 | squelette vide | intégrer `bloc2/REDACTION_RAPPORT.md` (déjà rédigé, chiffres réels) |
| 05 Bloc 3 | squelette (2 trous) | écrire depuis `bloc3/SYNTHESE.md` |
| 06 Bloc final | squelette vide | **dépend du Bloc final** (pas commencé) |
| 07 Conclusion | ~50 % | boucler après les ch. 4-6 |
| 08 Annexes | 32 lignes | figures + dictionnaires (≤ 10 pages) |
| biblio.bib | 7 entrées | ajouter fama1970, mackinlay1997, cameron2013 + vérifier bijection citations↔biblio |
| Page de garde | « Prénom NOM » | **remplacer par le vrai nom** |

### Côté git — ⚠️ POINT CRITIQUE
`main` n'a **pas bougé** depuis le squelette du rapport → la fusion `bloc2-dev` → `main`
est un **fast-forward sans aucun conflit possible**. **Il faut fusionner MAINTENANT**
(pas à la fin) : ça débloque l'écriture du chapitre 4 et évite toute divergence future.

---

## 2. Ce qu'on VA faire (le chemin critique)

### A. Fusion immédiate (J1 — 5 minutes, chat Rapport)
```bash
git checkout main && git merge bloc2-dev   # fast-forward, zéro conflit
```
Débloque : ch. 4 (le brouillon LaTeX `bloc2/REDACTION_RAPPORT.md` est prêt à coller).

### B. Bloc final (J1→J5, chat Blocs) — le seul gros chantier technique
**Aucune dépendance externe : toutes les données existent déjà.**
- **Base** : les 38 035 trades du Bloc 1 (`trades.csv`), cible **`win` (0/1)**.
- **Variables candidates** = signaux validés/candidats des blocs :
  stratégie RSI (Bloc 1), régime + interaction (Bloc 1), contexte d'entrée,
  features sectorielles lead-lag (Bloc 3), drapeaux « événement récent sur le titre » (Bloc 2).
- **Méthodes (toutes vues en cours)** :
  1. **Régression logistique** (GLM binomial, style `PROC GENMOD`) — coefficients en log-odds,
     sélection **AIC** + colinéarité **VIF** ;
  2. **Lasso CV** (cours apprentissage pénalisé) — sélection parcimonieuse ;
  3. Validation **TimeSeriesSplit** (ordre chronologique respecté, pas de fuite du futur).
- **Livrables** : `blocfinal/{01_donnees,02_methodes,03_resultats}` + `SYNTHESE.md`
  + `REDACTION_RAPPORT.md` (brouillon LaTeX ch. 6) — même usine que les autres blocs.
- Le fait que le Lasso/stepwise **rejette** les signaux invalidés est un RÉSULTAT
  (le pipeline ne laisse pas entrer de bruit) — à assumer tel quel dans le rapport.

### C. Rédaction (J1→J9, chat Rapport) — dans cet ordre
1. **Ch. 4 Bloc 2** (J1-J2) : coller/adapter `bloc2/REDACTION_RAPPORT.md` (prêt).
2. **Ch. 2 Données** (J2-J3) : compiler les 3 dictionnaires (`bloc*/01_donnees/dictionnaire.md`).
3. **Ch. 5 Bloc 3** (J3-J4) : depuis `bloc3/SYNTHESE.md`.
4. **Ch. 3 trous ACP/AFC/ACM** (J4-J5) : chiffres dans `bloc1/03_resultats/etape4-6*.txt`.
5. **Ch. 6 Bloc final** (J6-J7) : depuis `blocfinal/REDACTION_RAPPORT.md` (2ᵉ fusion J5-J6).
6. **Intro + Conclusion** (J8) : boucler, cohérence des renvois.
7. **Annexes + biblio + page de garde** (J8-J9).

### D. Finitions (J10→J12)
- **J10** : compilation complète (`pdflatex → biber → pdflatex ×2`), **compte de pages ≤ 40**,
  vérif bijection citations↔biblio, placement des figures.
- **J11** : relecture intégrale — cohérence chiffres du texte ↔ fichiers `03_resultats/`,
  reformulation personnelle (anti-plagiat strict).
- **J12** : préparation orale — compléter `preparation_oral.md` avec les Q&A Bloc 2
  (event study, Poisson/binomiale négative, contagion) et Bloc final (logistique, VIF,
  validation temporelle). Structure de l'exposé 20 min.
- **J13-J14 : marge** (imprévus, seconde relecture). Rendu possible dès le 23/07.

---

## 3. Ce qu'on PEUT faire (bonus, seulement si en avance)

| Bonus | Coût | Valeur | Quand |
|---|---|---|---|
| **MCD/MLD + SQL sur le Bloc 2** | ½ journée | ⭐ forte — le ch. 4 l'annonce déjà, cours Claeys = angle « vu en cours » | J5, si Bloc final fini |
| Surprises de résultats (earnings) via pont n8n | ½ journée | moyenne — enrichit l'event study | après J10 seulement |
| Congress « by-name » (élus ciblés) | ½ journée | faible — volume restera petit | non prioritaire |

Le MCD/MLD est le seul bonus **réellement rentable** : le squelette du ch. 4 promet une
« modélisation MCD/MLD, normalisation » — soit on la fait (½ journée), soit on retire la
promesse du chapitre. Décision à prendre à J5.

## 4. Ce qu'on NE FERA PAS (assumé, avec la justification prête pour l'oral)

- **Signaux payants** (options flow, dark pools, alt-data — Polygon/Unusual Whales/Quiver) :
  pas de budget → documentés dans `bloc2/CATALOGUE_SIGNAUX.md` comme roadmap post-mémoire.
- **Historique profond du Congrès** : limite structurelle FMP (trades récents seulement,
  n≈43) → limite assumée, écrite dans le rapport.
- **Walk-forward complet sur tous les blocs** : trop lourd → validation temporelle
  (TimeSeriesSplit) sur le Bloc final uniquement, walk-forward cité en perspective.
- **GARCH / SARIMA** : pas dans le cours de séries temporelles → hors périmètre.
- **Onglet « Statistiques » du dashboard** (METHODOLOGIE §15.4) : hors mémoire, post-rendu.
- **Sentiment / news scraping** : pas de source fiable gratuite → catalogue, perspective.

## 5. Dépendances (qui bloque qui)

```
FUSION bloc2-dev→main (J1, 5 min)
   └─► Ch.4 Bloc 2 (rapport)
BLOC FINAL (J1→J5, aucune dépendance externe)
   └─► FUSION #2 (J5-J6)
         └─► Ch.6 Bloc final (rapport)
               └─► Conclusion + Intro finales (J8)
                     └─► Annexes/biblio (J8-J9)
                           └─► Compilation + pages ≤ 40 (J10)
                                 └─► Relecture anti-plagiat (J11)
                                       └─► Préparation orale (J12)
Ch.2 / Ch.5 / trous Ch.3 : AUCUNE dépendance → en parallèle dès J2
```

**Règles anti-conflit entre les deux chats (inchangées)** :
- `rapport/**` = chat Rapport uniquement. `bloc2/**`, `blocfinal/**` = chat Blocs uniquement.
- `ARCHITECTURE.md` / `METHODOLOGIE.md` : après la fusion J1, le chat Blocs n'y touche plus
  que pour la section Bloc final.
- Fusions **toujours** faites côté `main` par le chat Rapport (jamais de checkout ici).

## 6. Points de vigilance méthodologiques (pour l'oral et le rapport)

1. **L'event study n'est pas nommée telle quelle dans les cours** → la présenter comme
   l'assemblage de méthodes vues : régression linéaire (modèle de marché) + test de
   Student/Wilcoxon sur le CAR + Bonferroni. Ne pas revendiquer une méthode hors-cours.
2. **Wilcoxon et V de Cramér** = contrôles internes, pas méthodes revendiquées (position
   déjà actée pour le Bloc 1 — rester cohérent au Bloc 2).
3. **Poisson → binomiale négative** : le réflexe sur-dispersion (ratio ≈ 27, effets 5→2)
   est un point fort à valoriser, `PROC GENMOD` le couvre côté cours.
4. **Significativité ≠ taille d'effet** : fil rouge des trois blocs, à marteler.
5. **Le titre du mémoire** ne mentionne pas les signaux d'information → à ajuster
   (« …des stratégies techniques aux signaux d'information et aux relations
   inter-sectorielles ») — décision chat Rapport.
6. **« Prénom NOM »** sur la page de garde → à remplacer (2 minutes, souvent oublié).

## 7. Calendrier récapitulatif

| Jour | Chat Blocs (`bloc2-dev`→`blocfinal`) | Chat Rapport (`main`) |
|---|---|---|
| **J1** 10/07 | Démarrer Bloc final (base + features) | **FUSION** + coller ch. 4 |
| **J2** 11/07 | Logistique + VIF/AIC | Ch. 2 données |
| **J3** 12/07 | Lasso + TimeSeriesSplit | Ch. 5 Bloc 3 |
| **J4** 13/07 | Résultats + SYNTHESE blocfinal | Trous ch. 3 (ACP/AFC/ACM) |
| **J5** 14/07 | REDACTION_RAPPORT blocfinal + (bonus MCD/SQL) | **FUSION #2** |
| **J6-J7** 15-16/07 | Q&A orales blocs 2/final (brouillon) | Ch. 6 Bloc final |
| **J8** 17/07 | — (support) | Intro + Conclusion |
| **J9** 18/07 | — | Annexes + biblio + page de garde |
| **J10** 19/07 | — | Compilation, ≤ 40 pages, biblio↔citations |
| **J11** 20/07 | — | Relecture anti-plagiat + cohérence chiffres |
| **J12** 21/07 | — | Préparation orale (20 min + Q&A) |
| **J13-J14** 22-23/07 | **MARGE** | **MARGE** → rendu possible, deadline 03/08 |
