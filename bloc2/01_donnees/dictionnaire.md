# Dictionnaire des données — Bloc 2

> Chaque colonne de la base d'analyse `evenements.csv`, plus les CSV bruts dont elle
> est issue. Objectif : pouvoir **défendre chaque champ** au jury (d'où il vient, ce
> qu'il mesure, comment il est calculé).

## `evenements.csv` — LA base d'analyse (1 ligne = 1 événement)

| Colonne | Type | Description | Comment c'est calculé |
|---|---|---|---|
| `signal` | texte | Source du signal : `contrat`, `regulation`, `congres`, `earnings` | La famille de signal d'information (cf. rapport n8n). |
| `ticker` | texte | Action cotée (S&P 500) concernée | Direct (congres/earnings) ou **mappé depuis le nom** de l'attributaire (contrats) / **projeté** sur un panier sectoriel (regulations). |
| `date` | date | Date de l'événement (AAAA-MM-JJ) | Date de transaction (congres), d'obligation (contrat), de publication (regulation), de résultat (earnings). |
| `sens` | texte | Direction du signal | `attribution` (contrat) ; `significant`/`standard` (regul) ; `achat`/`vente` (congres) ; `beat`/`miss` (earnings). |
| `secteur` | texte | Secteur GICS du ticker | `universe.load_sectors()` (constituants S&P 500). |
| `intensite` | nombre | Poids de l'événement | Montant du contrat ($) ; 1 ou 2 selon la significativité d'une regul ; 1 sinon. Sert à la pondération et à la Poisson. |

**Le CAR** (rendement anormal cumulé) n'est PAS stocké : il est **recalculé** par le moteur
(`02_methodes/_moteur.py`) à partir des prix, pour chaque événement, à la volée.

## CSV bruts (sortie de `collecteur.py`, avant normalisation)

- **`brut_contrats.csv`** — USASpending.gov (gratuit). Champs : `award_id, recipient,
  amount, date, agency, sub_agency, naics_code, naics_desc, state, description`.
  Reprend la requête du workflow n8n *Get Government Contracts* (contrats ≥ 100 M$).
- **`brut_regulations.csv`** — Federal Register (gratuit). Champs : `doc_id, theme, secteur,
  title, type, agencies, date, effective_date, significant, url`. Type ∈ {Rule, Proposed
  Rule}. Reprend le workflow n8n *Get Federal Regulations*, élargi à 9 thèmes sectoriels.
- **`brut_congres.csv`** — FMP (clé détenue par n8n). Champs : `chamber, politician, ticker,
  transaction, amount, date, disclosure_date`. Collecté via un **pont webhook n8n** (le
  sous-workflow *Get Congress Trades* détient la clé) ou en direct si `FMP_API_KEY` est
  exportée — cf. `collecteur.py`. FMP ne livre que les trades **récents** → échantillon
  modeste (~43 trades), documenté comme limite.
- **`brut_earnings.csv`** — FMP (clé requise). Champs : `ticker, date, eps_actual,
  eps_estimated, sens`.

## Prix (le « juge » de l'étude d'événement)

Fournis par `backend/charts/data.get_ohlcv(ticker)` (yfinance, cache Parquet) — **réutilisé
tel quel** du socle des Blocs 1 et 3. Le rendement du **marché** vient de la colonne `MARCHE`
de `bloc3/01_donnees/rendements_secteurs.csv` (moyenne S&P 500), sinon de l'ETF `SPY`.

## Limites assumées (à mentionner au rapport)

- **Mapping nom→ticker (contrats)** : basé sur le nom normalisé ; les attributaires non
  cotés au S&P 500 sont écartés (l'échantillon contrats se concentre sur la défense cotée).
- **Projection sectorielle (regulations)** : une règle frappe un secteur entier ; on la
  projette sur un panier de tickers représentatifs → événements corrélés dans un secteur
  (biais à garder en tête pour l'interprétation).
- **Congrès/earnings** : nécessitent la clé FMP (dans n8n). Sans elle, la chaîne tourne déjà
  sur les 2 sources gratuites ; avec elle, les mêmes scripts intègrent ces signaux sans modif.
- **Biais du survivant** : univers = S&P 500 **actuel** (hérité du socle, déjà documenté).
