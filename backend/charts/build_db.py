"""Construit la base de détections (SQLite) : la « Porte B » de l'étude statistique.

Usage :
    python -m charts.build_db            # scan complet du S&P 500
    python -m charts.build_db --sample 50   # sous-ensemble (validation rapide)

Écrit une table `detections` (1 ligne / trade) dans `charts/results.db`. Cette base est
ensuite lue par pandas (read_sql) pour les tests : agrégé, apparié vs buy&hold, ANOVA
par régime, par secteur, etc. Régénérable -> gitignorée.
"""
from __future__ import annotations

import argparse
import sqlite3

from . import config, scan, universe

DB_PATH = config.ROOT / "results.db"
TABLE = "detections"


def build(tickers: list[str] | None = None) -> int:
    """Scanne l'univers et (ré)écrit la table. Renvoie le nombre de lignes."""
    tickers = tickers or universe.load_sp500()
    df = scan.scan_universe(tickers)
    con = sqlite3.connect(DB_PATH)
    try:
        df.to_sql(TABLE, con, if_exists="replace", index=False)
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_strategy ON {TABLE}(strategy)")
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_regime ON {TABLE}(regime_entry)")
        con.commit()
    finally:
        con.close()
    print(f"[db] {len(df)} lignes écrites dans {DB_PATH} (table '{TABLE}')")
    return len(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Construit la base de détections (SQLite)")
    parser.add_argument("--sample", type=int, default=0, help="N premiers tickers seulement")
    args = parser.parse_args()

    tk = universe.load_sp500()
    if args.sample:
        tk = tk[: args.sample]
    build(tk)
