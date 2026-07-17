"""NORMALISATION — fabrique la BASE d'analyse `evenements.csv` a partir des CSV bruts.

Chaque source a son propre format (contrats -> nom d'entreprise ; regulations -> secteur ;
congres -> ticker direct...). Ici on ramene TOUT a un format commun, une ligne = un
EVENEMENT exploitable par l'etude d'evenement :

    signal      : quelle source (congres / contrat / regulation / earnings)
    ticker      : l'action cotee concernee (necessaire pour les prix)
    date        : date de l'evenement (AAAA-MM-JJ)
    sens        : direction attendue du signal (achat/vente, beat/miss, significant...)
    secteur     : secteur GICS (pour les analyses par secteur)
    intensite   : montant / importance (pour Poisson et ponderations)

Choix de conception :
  - CONTRATS : l'attributaire est un NOM d'entreprise -> on le mappe vers un ticker du
    S&P 500 par nom normalise (Lockheed Martin Corp -> LMT). Non-cotes = ecartes (assume).
  - REGULATIONS : pas de ticker unique -> l'evenement porte sur un SECTEUR. On duplique
    l'evenement sur un panier de tickers representatifs du secteur (proxy sectoriel).
  - On ne garde que les evenements dans la periode ou l'on a des prix (>= 2010).

Entree :  bloc2/01_donnees/brut_*.csv   (produits par collecteur.py)
Sortie :  bloc2/01_donnees/evenements.csv
Lance  :  python bloc2/01_donnees/construire_evenements.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ICI = Path(__file__).resolve().parent
OUT = ICI / "evenements.csv"
DATE_MIN = "2010-01-01"          # borne basse = debut de l'historique de prix

sys.path.insert(0, str(ICI.parents[1] / "backend"))
from charts import universe  # noqa: E402


# --------------------------------------------------------------------------------------
# Outils de mapping NOM d'entreprise -> TICKER (pour les contrats)
# --------------------------------------------------------------------------------------
_SUFFIXES = re.compile(
    r"\b(corporation|corp|company|co|inc|incorporated|llc|ltd|the|systems?|"
    r"holdings?|group|plc|sa|technologies|technology)\b", re.I)


def _norme(nom: str) -> str:
    """Nom normalise pour comparaison : minuscules, sans suffixes juridiques ni ponctuation."""
    s = (nom or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = _SUFFIXES.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def _table_sp500() -> tuple[dict[str, str], dict[str, str]]:
    """Renvoie (nom_normalise -> ticker, ticker -> secteur) pour tout le S&P 500."""
    path = universe._cache_file()
    if not path.exists():
        universe.load_sp500()
    df = pd.read_csv(path)
    df["Symbol"] = df["Symbol"].astype(str).str.replace(".", "-", regex=False)
    name_col = next((c for c in ("Security", "Name") if c in df.columns), None)
    sec_col = next((c for c in ("GICS Sector", "Sector") if c in df.columns), None)
    nom2tk = {_norme(n): t for n, t in zip(df[name_col], df["Symbol"])}
    tk2sec = dict(zip(df["Symbol"], df[sec_col].astype(str)))
    return nom2tk, tk2sec


def _match_ticker(recipient: str, nom2tk: dict[str, str]) -> str | None:
    """Mappe un attributaire de contrat vers un ticker S&P 500 (exact puis inclusion)."""
    n = _norme(recipient)
    if not n:
        return None
    if n in nom2tk:
        return nom2tk[n]
    # inclusion : "lockheed martin" dans le nom du contrat "lockheed martin aeronautics"
    for nom, tk in nom2tk.items():
        if len(nom) >= 5 and (nom in n or n in nom):
            return tk
    return None


# Paniers sectoriels : tickers liquides representatifs, pour projeter une REGULATION
# (qui frappe un secteur entier) sur des actions concretes. Choix documente/limite.
PANIERS_SECTEUR = {
    "Information Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "AMD"],
    "Health Care": ["UNH", "JNJ", "LLY", "PFE", "MRK"],
    "Financials": ["JPM", "BAC", "WFC", "GS", "MS"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Industrials": ["BA", "CAT", "GE", "LMT", "RTX"],
    "Communication Services": ["GOOGL", "META", "NFLX", "T", "VZ"],
    "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
}


def build_contrats(nom2tk, tk2sec) -> pd.DataFrame:
    f = ICI / "brut_contrats.csv"
    if not f.exists():
        return pd.DataFrame()
    df = pd.read_csv(f)
    df = df[df["date"] >= DATE_MIN].copy()
    df["ticker"] = df["recipient"].map(lambda r: _match_ticker(r, nom2tk))
    df = df.dropna(subset=["ticker"])
    out = pd.DataFrame({
        "signal": "contrat",
        "evenement_id": df["award_id"].astype(str),   # 1 contrat = 1 evenement (porte 1)
        "ticker": df["ticker"],
        "date": df["date"].str[:10],
        "sens": "attribution",              # un contrat = signal positif (revenus futurs)
        "secteur": df["ticker"].map(tk2sec),
        "intensite": pd.to_numeric(df["amount"], errors="coerce"),
    })
    return out


def build_regulations(tk2sec) -> pd.DataFrame:
    f = ICI / "brut_regulations.csv"
    if not f.exists():
        return pd.DataFrame()
    df = pd.read_csv(f)
    df = df[df["date"] >= DATE_MIN].copy()
    rows = []
    for _, r in df.iterrows():
        secteur = r["secteur"]
        panier = PANIERS_SECTEUR.get(secteur, [])
        # sens : une regle FINALE "significative" pese plus (contrainte) qu'une simple proposee
        sig = bool(r.get("significant")) if pd.notna(r.get("significant")) else False
        sens = "significant" if sig else "standard"
        for tk in panier:
            rows.append({
                "signal": "regulation",
                "evenement_id": str(r["doc_id"]),   # 1 REGLE = 1 evenement, quel que soit
                "ticker": tk,                        # le nb de tickers du panier (anti
                "date": str(r["date"])[:10],         # pseudo-replication)
                "sens": sens,
                "secteur": secteur,
                "intensite": 1.0 if not sig else 2.0,
            })
    return pd.DataFrame(rows)


def build_congres(tk2sec) -> pd.DataFrame:
    f = ICI / "brut_congres.csv"
    if not f.exists():
        return pd.DataFrame()
    df = pd.read_csv(f)
    # DATE = DIVULGATION, pas la date du trade de l'elu : le marche (et nous) ne voit
    # la transaction qu'a sa publication STOCK Act. C'est la seule date exploitable
    # pour un signal ; le trade_date mesurerait le talent de l'elu, pas le signal.
    df = df.dropna(subset=["ticker", "disclosure_date"])
    df = df[df["disclosure_date"] >= DATE_MIN].copy()
    # sens : achat vs vente (le coeur du signal Congres)
    typ = df["transaction"].astype(str).str.lower()
    sens = typ.map(lambda t: "achat" if "purchase" in t or "buy" in t
                   else ("vente" if "sale" in t or "sell" in t else "autre"))
    out = pd.DataFrame({
        "signal": "congres",
        "evenement_id": (df["politician"].astype(str) + "|" + df["ticker"].astype(str)
                         + "|" + df["disclosure_date"].str[:10]),
        "ticker": df["ticker"].astype(str).str.replace(".", "-", regex=False),
        "date": df["disclosure_date"].str[:10],
        "sens": sens,
        "secteur": df["ticker"].map(tk2sec),
        "intensite": 1.0,
    })
    return out[out["sens"].isin(["achat", "vente"])]


def build_earnings(tk2sec) -> pd.DataFrame:
    f = ICI / "brut_earnings.csv"
    if not f.exists():
        return pd.DataFrame()
    df = pd.read_csv(f)
    df = df[df["date"] >= DATE_MIN].copy()
    out = pd.DataFrame({
        "signal": "earnings",
        "evenement_id": df["ticker"].astype(str) + "|" + df["date"].str[:10],
        "ticker": df["ticker"],
        "date": df["date"].str[:10],
        "sens": df["sens"],                 # beat / miss / inline
        "secteur": df["ticker"].map(tk2sec),
        "intensite": 1.0,
    })
    return out[out["sens"].isin(["beat", "miss"])]


def main() -> None:
    nom2tk, tk2sec = _table_sp500()
    parts = [
        build_contrats(nom2tk, tk2sec),
        build_regulations(tk2sec),
        build_congres(tk2sec),
        build_earnings(tk2sec),
    ]
    df = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    df = df.dropna(subset=["ticker", "date"]).drop_duplicates()
    df = df.sort_values(["signal", "date"]).reset_index(drop=True)
    df.to_csv(OUT, index=False, encoding="utf-8")

    print("=" * 60)
    print("evenements.csv construit :", len(df), "evenements")
    print("=" * 60)
    print(df.groupby("signal").size().to_string())
    print("\nperiode :", df["date"].min(), "->", df["date"].max())
    print("tickers distincts :", df["ticker"].nunique())
    print("-> ecrit dans", OUT)


if __name__ == "__main__":
    main()
