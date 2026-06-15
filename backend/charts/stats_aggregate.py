"""Phase A — évaluation agrégée : pour chaque trade, son « edge » vs le hasard.

Pour CHAQUE trade (les 8 stratégies × 503 titres), on estime ce qu'un trade IDENTIQUE
mais AU HASARD aurait rapporté (même titre, même durée, même sens, 200 tirages, fenêtres
sans chevauchement implicite — ici un seul trade donc pas de chevauchement) :
    edge = return_net(signal) − rand_return(hasard)
edge > 0 = le signal bat le hasard (= talent). On agrège ensuite par stratégie (+ régime,
secteur) avec un test de significativité. C'est LE juge du pouvoir prédictif.
"""
from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd
from scipy import stats as st

from . import config, data, regime as regime_mod, universe
from .registry import PARAMS_VERSION, STRATEGIES
from .strategy import rsi as rsi_mod

DB_PATH = config.ROOT / "results.db"
TABLE = "eval"
R_DRAWS = 200  # tirages au hasard par trade pour estimer le rendement attendu


def _rand_return(close: np.ndarray, dur: int, direction: int, rng, cost: float, r: int = R_DRAWS) -> float:
    """Rendement net moyen d'un trade au hasard : même durée, même sens, r tirages."""
    n = len(close)
    if dur < 1 or dur >= n - 1:
        return float("nan")
    starts = rng.integers(0, n - dur, size=r)
    gross = close[starts + dur] / close[starts] - 1.0
    net = (1.0 + direction * gross) * (1.0 - cost) ** 2 - 1.0
    return float(np.mean(net))


def build_eval(tickers: list[str] | None = None, cost: float = config.COST_PER_SIDE,
               seed: int = 2026, log_every: int = 50,
               only: list[str] | None = None, mode: str = "replace") -> pd.DataFrame:
    """Construit la table d'évaluation (1 ligne/trade avec son edge vs hasard).

    `only`  : ne calcule QUE ces stratégies (par défaut : toutes).
    `mode`  : "replace" = reconstruit toute la table ; "append" = AJOUTE à l'existant
              (les lignes des stratégies `only` sont d'abord retirées -> ré-exécution
              idempotente, pas de doublon). -> permet d'agrandir la base sans tout refaire.
    """
    tickers = tickers or universe.load_sp500()
    keys = list(STRATEGIES) if only is None else only
    reg = regime_mod.regime_series()
    sectors = universe.load_sectors()
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    total = len(tickers)
    for i, tk in enumerate(tickers, 1):
        try:
            df = data.get_ohlcv(tk)
        except Exception:  # noqa: BLE001
            continue
        close = df["Close"].to_numpy()
        pos = {d: j for j, d in enumerate(df.index)}
        sector = sectors.get(tk, "?")
        # FEATURES par trade (etat du titre le jour de l'ENTREE) -> pour l'ACP / la regression :
        close_s = df["Close"]
        f_vol = close_s.pct_change().rolling(20).std().to_numpy()        # volatilite 20j
        f_ma200 = close_s.rolling(200).mean().to_numpy()
        f_dist = (close - f_ma200) / f_ma200                            # distance relative a la MM200
        f_rsi = rsi_mod.rsi_series(close_s).to_numpy()                  # RSI de Wilder a l'entree

        def _at(arr, p):  # valeur d'une feature a la position p, None si NaN
            v = arr[p]
            return round(float(v), 6) if v == v else None

        for key in keys:
            strat, _label, params = STRATEGIES[key]
            call = {"short": config.MA_SHORT, "long": config.MA_LONG, **params}
            for t in strat.detect_trades(df, **call):
                ep = pos[t.entry_date]
                dur = pos[t.exit_date] - ep
                rnet = t.net_return(cost)
                rexp = _rand_return(close, dur, t.direction, rng, cost)
                rows.append(
                    {
                        "ticker": tk,
                        "sector": sector,
                        "strategy": key,
                        "params_version": PARAMS_VERSION,
                        "regime_entry": regime_mod.regime_at(reg, t.entry_date),
                        "direction": t.direction,
                        "holding_days": t.holding_days,
                        "vol_entry": _at(f_vol, ep),
                        "rsi_entry": _at(f_rsi, ep),
                        "dist_ma200": _at(f_dist, ep),
                        "return_net": round(rnet, 6),
                        "rand_return": round(rexp, 6) if rexp == rexp else None,  # NaN -> None
                        "edge": round(rnet - rexp, 6) if rexp == rexp else None,
                        "win": int(rnet > 0),
                    }
                )
        if log_every and (i % log_every == 0 or i == total):
            print(f"[eval] {i}/{total} — {len(rows)} trades", flush=True)
    df_out = pd.DataFrame(rows)
    con = sqlite3.connect(DB_PATH)
    try:
        if mode == "append":
            # idempotent : on retire d'abord d'éventuelles lignes de ces stratégies
            exists = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (TABLE,)
            ).fetchone()
            if exists:
                qm = ",".join("?" * len(keys))
                con.execute(f"DELETE FROM {TABLE} WHERE strategy IN ({qm})", keys)
                con.commit()
            df_out.to_sql(TABLE, con, if_exists="append", index=False)
        else:
            df_out.to_sql(TABLE, con, if_exists="replace", index=False)
    finally:
        con.close()
    print(f"[eval] {len(df_out)} lignes ({mode}) dans {DB_PATH} (table '{TABLE}')")
    return df_out


def add_strategies(keys: list[str], **kw) -> pd.DataFrame:
    """Ajoute UNE ou plusieurs stratégies à la base sans tout recalculer.

    Ex :  python -c "from charts.stats_aggregate import add_strategies as a; a(['ma_supertrend'])"
    Ré-exécutable sans risque (remplace les lignes de ces stratégies si déjà présentes).
    """
    return build_eval(only=keys, mode="append", **kw)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Verdict par stratégie : rendement, hasard, edge moyen + significativité (test t)."""
    out = []
    for k, g in df.groupby("strategy"):
        e = g["edge"].dropna()
        t, p = st.ttest_1samp(e, 0.0) if len(e) > 1 else (float("nan"), float("nan"))
        out.append(
            {
                "strategy": k,
                "n": len(g),
                "ret_net_moy": round(g["return_net"].mean(), 4),
                "hasard_moy": round(g["rand_return"].mean(), 4),
                "edge_moy": round(e.mean(), 4),
                "%_gagnants": round(g["win"].mean(), 3),
                "t": round(float(t), 2),
                "p_value": float(p),
                "significatif_5%": bool(p < 0.05),
            }
        )
    return pd.DataFrame(out).sort_values("edge_moy", ascending=False)


if __name__ == "__main__":
    d = build_eval()
    print(summarize(d).to_string(index=False))
