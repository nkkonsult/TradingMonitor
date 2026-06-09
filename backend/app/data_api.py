"""Exposition LECTURE SEULE de la base de détections (transparence dans le dashboard).

Laisse voir ce qu'on a réellement : combien de trades, par stratégie / régime / secteur,
et la table elle-même (filtrable, paginée). Lit `charts/results.db` produit par build_db.
"""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException

from charts import config as ccfg

router = APIRouter(prefix="/data", tags=["data"])

DB_PATH = ccfg.ROOT / "results.db"  # charts/results.db


def _con() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(
            404, "Base de détections absente. Lance `python -m charts.build_db`."
        )
    return sqlite3.connect(DB_PATH)


@router.get("/summary")
def summary() -> dict:
    con = _con()
    try:
        c = con.cursor()
        total = c.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        by_strategy = c.execute(
            "SELECT strategy, COUNT(*) FROM detections GROUP BY strategy ORDER BY 2 DESC"
        ).fetchall()
        by_regime = c.execute(
            "SELECT regime_entry, COUNT(*) FROM detections GROUP BY regime_entry ORDER BY 2 DESC"
        ).fetchall()
        by_sector = c.execute(
            "SELECT sector, COUNT(*) FROM detections GROUP BY sector ORDER BY 2 DESC"
        ).fetchall()
        n_tickers = c.execute("SELECT COUNT(DISTINCT ticker) FROM detections").fetchone()[0]
        dmin, dmax = c.execute(
            "SELECT MIN(entry_date), MAX(exit_date) FROM detections"
        ).fetchone()
        pv = [r[0] for r in c.execute("SELECT DISTINCT params_version FROM detections").fetchall()]
    finally:
        con.close()
    return {
        "total": total,
        "n_tickers": n_tickers,
        "date_min": dmin,
        "date_max": dmax,
        "params_version": pv,
        "by_strategy": [{"key": k, "count": n} for k, n in by_strategy],
        "by_regime": [{"key": k, "count": n} for k, n in by_regime],
        "by_sector": [{"key": k, "count": n} for k, n in by_sector],
    }


@router.get("/detections")
def detections(
    strategy: str | None = None,
    regime: str | None = None,
    sector: str | None = None,
    ticker: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    con = _con()
    try:
        clauses, params = [], []
        for col, val in (
            ("strategy", strategy),
            ("regime_entry", regime),
            ("sector", sector),
            ("ticker", ticker),
        ):
            if val:
                clauses.append(f"{col} = ?")
                params.append(val)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        limit = max(1, min(500, limit))
        offset = max(0, offset)

        total = con.execute(f"SELECT COUNT(*) FROM detections{where}", params).fetchone()[0]
        cur = con.execute(
            f"SELECT * FROM detections{where} ORDER BY entry_date LIMIT ? OFFSET ?",
            params + [limit, offset],
        )
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        con.close()
    return {"total": total, "columns": cols, "rows": rows, "limit": limit, "offset": offset}
