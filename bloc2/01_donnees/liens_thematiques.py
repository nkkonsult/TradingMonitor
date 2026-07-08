"""LIENS THEMATIQUES — quels actifs "en amont/aval" un titre est-il cense entrainer ?

L'etude de contagion (etapes 5-6) demande de savoir, pour un titre A qui recoit un
signal, quels ACTIFS THEMATIQUES pourraient bouger en reaction : matieres premieres
qu'il consomme/produit, ETF de son theme, etc. On ne peut pas le deviner statistiquement
(c'est un lien economique) -> on le declare ici, table ouverte et documentee.

Chaque proxy est un ETF/actif NEGOCIABLE recuperable via charts.data.get_ohlcv (verifie).
Ex : Tesla -> lithium (LIT) ; ExxonMobil -> petrole (USO) ; Nvidia -> semi (SOXX).

C'est un CHOIX economique (limite assumee au rapport), pas une verite. Les liens
purement statistiques (qui bouge avec qui) sont, eux, fournis par le Bloc 3.
"""
from __future__ import annotations

# --- ETF / actifs thematiques (proxies negociables de matieres premieres & themes) ---
THEMES = {
    "LIT": "Lithium / batteries",
    "SOXX": "Semi-conducteurs",
    "USO": "Petrole brut",
    "GLD": "Or",
    "COPX": "Cuivre / miniers",
    "URA": "Uranium",
    "XLE": "Secteur energie (ETF)",
    "XLK": "Secteur technologie (ETF)",
    "XLF": "Secteur finance (ETF)",
    "XLV": "Secteur sante (ETF)",
    "ITA": "Aerospatiale & defense (ETF)",
    "XLI": "Secteur industrie (ETF)",
}

# --- Liens titre -> themes qu'il est cense entrainer (economiques) -------------------
# Cle = ticker present dans les evenements ; valeur = liste de proxies thematiques.
LIENS = {
    # Auto / batteries
    "TSLA": ["LIT", "COPX", "XLK"],
    # Tech / semi (consomment des semi, entrainent le theme semi)
    "NVDA": ["SOXX", "XLK"], "AMD": ["SOXX", "XLK"], "AVGO": ["SOXX", "XLK"],
    "AAPL": ["SOXX", "XLK"], "MSFT": ["XLK"], "ORCL": ["XLK"], "ACN": ["XLK"],
    # Energie / petrole
    "XOM": ["USO", "XLE"], "CVX": ["USO", "XLE"], "COP": ["USO", "XLE"],
    "EOG": ["USO", "XLE"], "SLB": ["USO", "XLE"],
    # Defense / aerospatiale (contrats gouvernementaux)
    "LMT": ["ITA", "XLI"], "RTX": ["ITA", "XLI"], "NOC": ["ITA", "XLI"],
    "GD": ["ITA", "XLI"], "BA": ["ITA", "XLI"], "HII": ["ITA", "XLI"],
    "LHX": ["ITA", "XLI"], "LDOS": ["ITA", "XLI"], "TXT": ["ITA", "XLI"],
    "GE": ["XLI"], "HON": ["XLI"], "CAT": ["COPX", "XLI"],
    # Finance
    "JPM": ["XLF"], "BAC": ["XLF"], "GS": ["XLF"], "MS": ["XLF"], "WFC": ["XLF"],
    # Sante
    "JNJ": ["XLV"], "PFE": ["XLV"], "MRK": ["XLV"], "LLY": ["XLV"], "UNH": ["XLV"],
    "MRNA": ["XLV"], "REGN": ["XLV"], "HUM": ["XLV"], "MCK": ["XLV"], "ABBV": ["XLV"],
    # Materiaux
    "NUE": ["COPX", "XLI"],
    # Conso / communication (liens plus laches -> ETF large de leur secteur)
    "AMZN": ["XLK"], "HD": [], "MCD": [], "NKE": [],
    "GOOGL": ["XLK"], "META": ["XLK"], "NFLX": ["XLK"], "T": [], "VZ": [],
}


def themes_de(ticker: str) -> list[str]:
    """Liste des proxies thematiques lies a un ticker (vide si aucun declare)."""
    return LIENS.get(ticker, [])


def tous_les_proxies() -> list[str]:
    """Tous les ETF/actifs thematiques utilises (pour precharger les prix)."""
    return sorted(THEMES.keys())
