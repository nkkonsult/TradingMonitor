"""Sort la base `eval` (results.db) en CSV lisible -> trades.csv (CE QUI ENTRE).

Lance-le toi-meme pour regenerer le CSV :
    .venv/Scripts/python.exe bloc1/01_donnees/exporter_base.py

C'est la seule chose qui touche a la base SQLite : ensuite tu travailles uniquement
sur trades.csv (ouvrable dans Excel), pour que la matiere premiere soit VISIBLE.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

DB = Path(__file__).resolve().parents[2] / "backend" / "charts" / "results.db"
OUT = Path(__file__).resolve().parent / "trades.csv"


def main() -> None:
    con = sqlite3.connect(DB)
    try:
        df = pd.read_sql("SELECT * FROM eval", con)
    finally:
        con.close()
    df.to_csv(OUT, index=False, encoding="utf-8")
    print(f"{len(df)} trades -> {OUT}")
    print("strategies :")
    print(df.groupby("strategy").size().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
