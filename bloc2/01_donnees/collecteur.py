"""COLLECTE — CE QUI ENTRE (Bloc 2) : les signaux d'information -> CSV bruts.

Une SOURCE = une fonction. Chaque fonction va chercher la donnee la ou elle vit
(API publique gratuite, ou workflow n8n qui detient la cle) et ecrit un CSV BRUT
(le plus fidele possible a la source) dans 01_donnees/brut_<source>.csv.

La NORMALISATION (mise au format commun `evenements.csv`) est faite ensuite par
`construire_evenements.py`. On separe volontairement les deux etapes :
  - collecteur.py     = va chercher la matiere (peut dependre du reseau / des cles)
  - construire_...    = fabrique la base d'analyse (deterministe, rejouable hors-ligne)

Sources du Groupe 1 (signaux EVENEMENTIELS = ticker + date + sens) :
  1. Trades du Congres        -> FMP (cle n8n)          [collecte_congres]
  2. Contrats publics         -> USASpending (gratuit)  [collecte_contrats]         OK
  3. Regulations federales    -> Federal Register (grat.)[collecte_regulations]     OK
  (4-7 : lois, surprises de resultats, contrats prives, catalyseurs -> a brancher
   quand la cle FMP/Finnhub/Congress.gov est fournie ; memes fonctions, meme patron.)

Lance :  python bloc2/01_donnees/collecteur.py            (collecte tout ce qui est gratuit)
         python bloc2/01_donnees/collecteur.py contrats   (une seule source)
"""
from __future__ import annotations

import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

ICI = Path(__file__).resolve().parent
TODAY = date.today().isoformat()

# --- Cles API (optionnelles) : lues dans l'environnement si presentes -------------
# Si tu exportes FMP_API_KEY / FINNHUB_API_KEY, la collecte des sources payantes
# s'active automatiquement. Sinon on collecte seulement les sources gratuites.
import os

FMP_API_KEY = os.environ.get("FMP_API_KEY", "").strip()
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()


def _log(msg: str) -> None:
    print(msg, flush=True)


# ======================================================================================
# SOURCE 2 — CONTRATS PUBLICS  (USASpending.gov, gratuit, sans cle)
# ======================================================================================
def collecte_contrats(annees: int = 6, min_montant: int = 100_000_000,
                      pages: int = 5) -> pd.DataFrame:
    """Attributions de contrats federaux US (gros contrats -> attributaires cotes).

    Reprend la requete du workflow n8n "Get Government Contracts" (memes champs).
    On vise les GROS montants (>=100 M$) car ce sont eux qui ont une chance de bouger
    le cours d'une societe cotee du S&P 500 (Lockheed, Boeing, Northrop...).
    """
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    debut = (date.today() - timedelta(days=365 * annees)).isoformat()
    fields = [
        "Award ID", "Recipient Name", "Award Amount", "Base Obligation Date",
        "Last Modified Date", "Period of Performance Start Date",
        "Awarding Agency", "Awarding Sub Agency", "NAICS Code", "NAICS Description",
        "Place of Performance State Code", "Description",
    ]
    rows: list[dict] = []
    for page in range(1, pages + 1):
        body = {
            "filters": {
                "time_period": [{"start_date": debut, "end_date": TODAY}],
                "award_type_codes": ["A", "B", "C", "D"],
                "award_amounts": [{"lower_bound": min_montant}],
            },
            "fields": fields,
            "page": page, "limit": 100, "sort": "Award Amount",
            "order": "desc", "subawards": False,
        }
        r = requests.post(url, json=body, timeout=60)
        r.raise_for_status()
        res = r.json().get("results", [])
        if not res:
            break
        for c in res:
            obl = c.get("Base Obligation Date")
            lastmod = c.get("Last Modified Date")
            best = obl or (lastmod[:10] if lastmod else None)
            rows.append({
                "award_id": c.get("Award ID"),
                "recipient": c.get("Recipient Name"),
                "amount": c.get("Award Amount"),
                "date": best,
                "agency": c.get("Awarding Agency"),
                "sub_agency": c.get("Awarding Sub Agency"),
                "naics_code": c.get("NAICS Code"),
                "naics_desc": c.get("NAICS Description"),
                "state": c.get("Place of Performance State Code"),
                "description": (c.get("Description") or "")[:200],
            })
        _log(f"  [contrats] page {page} : {len(res)} contrats")
        time.sleep(0.4)  # courtoisie API
    df = pd.DataFrame(rows)
    out = ICI / "brut_contrats.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    _log(f"[contrats] {len(df)} contrats -> {out}")
    return df


# ======================================================================================
# SOURCE 3 — REGULATIONS FEDERALES  (Federal Register, gratuit, sans cle)
# ======================================================================================
# Un THEME de regulation = un ensemble de secteurs cotes impactes. On interroge
# plusieurs mots-cles sectoriels (le workflow n8n en prend un seul a la fois).
REGUL_THEMES = {
    "semiconductor": "Information Technology",
    "pharmaceutical": "Health Care",
    "drug": "Health Care",
    "bank": "Financials",
    "oil and gas": "Energy",
    "emissions": "Energy",
    "airline": "Industrials",
    "telecommunications": "Communication Services",
    "electric vehicle": "Consumer Discretionary",
}


def collecte_regulations(par_theme: int = 100) -> pd.DataFrame:
    """Regles finales/proposees du Federal Register par theme sectoriel.

    Reprend la logique du workflow n8n "Get Federal Regulations" : on ne garde que
    les documents de type Rule / Proposed Rule (les vraies decisions reglementaires),
    et on rattache chacun a un SECTEUR GICS via le mot-cle interroge.
    """
    base = "https://www.federalregister.gov/api/v1/documents.json"
    rows: list[dict] = []
    for terme, secteur in REGUL_THEMES.items():
        params = {
            "conditions[term]": terme,
            "conditions[type][]": ["RULE", "PRORULE"],
            "order": "newest",
            "per_page": par_theme,
            "fields[]": ["title", "abstract", "agency_names", "publication_date",
                         "effective_on", "document_number", "type", "significant",
                         "html_url"],
        }
        r = requests.get(base, params=params, timeout=60)
        r.raise_for_status()
        res = r.json().get("results", [])
        for d in res:
            rows.append({
                "doc_id": d.get("document_number"),
                "theme": terme,
                "secteur": secteur,
                "title": d.get("title"),
                "type": d.get("type"),
                "agencies": "; ".join(d.get("agency_names") or []),
                "date": d.get("publication_date"),
                "effective_date": d.get("effective_on"),
                "significant": d.get("significant"),
                "url": d.get("html_url"),
            })
        _log(f"  [regul] '{terme}' ({secteur}) : {len(res)} regles")
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    out = ICI / "brut_regulations.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    _log(f"[regul] {len(df)} regulations -> {out}")
    return df


# ======================================================================================
# SOURCE 1 — TRADES DU CONGRES  (FMP ; cle detenue par n8n)
# ======================================================================================
# La cle FMP vit dans les credentials n8n et n'est PAS lisible via l'API (securite).
# Deux voies :
#   (A) via un WEBHOOK n8n qui appelle le sous-workflow 'Get Congress Trades' (qui a la
#       cle en interne) et renvoie le JSON brut. C'est la voie utilisee ici (reproductible
#       sans exposer la cle). Renseigne l'URL du webhook ci-dessous.
#   (B) en direct si tu exportes FMP_API_KEY dans l'environnement.
# NB : l'endpoint FMP 'senate-latest/house-latest' ne renvoie que les trades RECENTS
# (25/appel, pas d'historique profond) -> echantillon modeste, documente comme limite.
CONGRES_WEBHOOK = os.environ.get("CONGRES_WEBHOOK_URL", "").strip()


def collecte_congres(pages: int = 10) -> pd.DataFrame:
    """Transactions declarees par les membres du Congres (STOCK Act).

    Voie A (webhook n8n) si CONGRES_WEBHOOK_URL est defini ; sinon voie B (FMP direct)
    si FMP_API_KEY ; sinon source ignoree (les sources gratuites suffisent a la chaine).
    """
    rows: list[dict] = []

    if CONGRES_WEBHOOK:
        for page in range(pages):
            try:
                r = requests.post(CONGRES_WEBHOOK,
                                  json={"chamber": "both", "page": page}, timeout=120)
                d = r.json()
                if isinstance(d, list):
                    d = d[0] if d else {}
                trades = d.get("trades", [])
            except Exception:  # noqa: BLE001
                break
            if not trades:
                break
            for t in trades:
                rows.append({
                    "chamber": t.get("chamber"),
                    "politician": t.get("politician"),
                    "ticker": t.get("ticker"),
                    "transaction": t.get("transaction"),
                    "amount": t.get("amount"),
                    "date": t.get("trade_date"),
                    "disclosure_date": t.get("disclosure_date"),
                })
            _log(f"  [congres] page {page} : {len(trades)} trades")
            time.sleep(0.5)

    elif FMP_API_KEY:
        for chambre, ep in (("Senate", "senate-latest"), ("House", "house-latest")):
            for page in range(pages):
                url = f"https://financialmodelingprep.com/stable/{ep}"
                params = {"page": page, "limit": 100, "apikey": FMP_API_KEY}
                r = requests.get(url, params=params, timeout=60)
                if r.status_code != 200:
                    break
                res = r.json()
                if not res:
                    break
                for t in res:
                    rows.append({
                        "chamber": chambre,
                        "politician": f"{t.get('firstName','')} {t.get('lastName','')}".strip(),
                        "ticker": t.get("symbol"),
                        "transaction": t.get("type"),
                        "amount": t.get("amount"),
                        "date": t.get("transactionDate"),
                        "disclosure_date": t.get("disclosureDate"),
                    })
                time.sleep(0.3)
    else:
        _log("[congres] ni CONGRES_WEBHOOK_URL ni FMP_API_KEY -> source ignoree.")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if len(df):
        df = df[df["ticker"].notna() & (df["ticker"] != "N/A")]
        out = ICI / "brut_congres.csv"
        df.to_csv(out, index=False, encoding="utf-8")
        _log(f"[congres] {len(df)} trades -> {out}")
    return df


# ======================================================================================
# SOURCE 5 — SURPRISES DE RESULTATS  (FMP, cle requise)
# ======================================================================================
def collecte_earnings(tickers: list[str] | None = None) -> pd.DataFrame:
    """Surprises de resultats (EPS reel vs estime) via FMP, pour les tickers du S&P 500.

    Necessite FMP_API_KEY. Signal event-study par excellence : date de publication +
    sens (beat si reel > estime, miss sinon).
    """
    if not FMP_API_KEY:
        _log("[earnings] FMP_API_KEY absente -> source ignoree.")
        return pd.DataFrame()
    if tickers is None:
        sys.path.insert(0, str(ICI.parents[1] / "backend"))
        from charts import universe  # noqa: E402
        tickers = universe.load_sp500()[:100]  # limite pour rester dans les quotas

    rows: list[dict] = []
    for i, tk in enumerate(tickers, 1):
        url = "https://financialmodelingprep.com/stable/earnings-surprises"
        params = {"symbol": tk, "apikey": FMP_API_KEY}
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code != 200:
                continue
            for e in r.json():
                actual = e.get("actualEarningResult")
                est = e.get("estimatedEarning")
                if actual is None or est is None:
                    continue
                rows.append({
                    "ticker": tk,
                    "date": e.get("date"),
                    "eps_actual": actual,
                    "eps_estimated": est,
                    "sens": "beat" if actual > est else ("miss" if actual < est else "inline"),
                })
        except requests.RequestException:
            continue
        if i % 25 == 0:
            _log(f"  [earnings] {i}/{len(tickers)} tickers")
        time.sleep(0.2)
    df = pd.DataFrame(rows)
    out = ICI / "brut_earnings.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    _log(f"[earnings] {len(df)} surprises -> {out}")
    return df


# ======================================================================================
# ORCHESTRATION
# ======================================================================================
SOURCES = {
    "contrats": collecte_contrats,
    "regulations": collecte_regulations,
    "congres": collecte_congres,
    "earnings": collecte_earnings,
}


def main() -> None:
    demande = sys.argv[1:] or ["contrats", "regulations", "congres", "earnings"]
    _log("=" * 70)
    _log("COLLECTE BLOC 2 — sources : " + ", ".join(demande))
    _log("Cles detectees : FMP=%s  Finnhub=%s"
          % ("oui" if FMP_API_KEY else "NON", "oui" if FINNHUB_API_KEY else "NON"))
    _log("=" * 70)
    for nom in demande:
        fn = SOURCES.get(nom)
        if fn is None:
            _log(f"[skip] source inconnue : {nom}")
            continue
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            _log(f"[ERREUR] {nom} : {e}")


if __name__ == "__main__":
    main()
