"""Walk-forward glissant + balayage de paramètres pour les figures chartistes.

Principe (anti-sur-apprentissage) : à chaque année de TEST, on choisit les paramètres
sur les N années PRÉCÉDENTES (train), puis on évalue HORS-ÉCHANTILLON sur l'année de
test. On glisse d'un an et on agrège tous les trades hors-échantillon.

- Sélection des params = sur le train uniquement (rendement net moyen).
- Verdict = edge vs hasard (même durée/sens) sur les trades hors-échantillon.

⚠️ Approximation assumée : la détection d'une figure entrant en année de test utilise la
série complète (les pivots se confirment ±w jours autour, tous AVANT la cassure → pas de
look-ahead sur la décision d'entrée ; léger effet de bord possible sur la dernière épaule).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats as st

from . import config, data, universe
from .stats_aggregate import _rand_return
from .strategy import double_top_bottom, head_shoulders

TRAIN_WIN = 5  # années d'entraînement glissantes
TEST_YEARS = list(range(2015, 2026))  # années hors-échantillon évaluées

# 4 figures + grilles (fenêtre de pivot × tolérance) ; direction fixée.
PATTERNS = {
    "hs_inverse": (head_shoulders, {"direction": "bullish"},
                   [{"pivot_window": w, "shoulder_tol": s} for w in (5, 8, 12) for s in (0.03, 0.05, 0.08)]),
    "hs_classic": (head_shoulders, {"direction": "bearish"},
                   [{"pivot_window": w, "shoulder_tol": s} for w in (5, 8, 12) for s in (0.03, 0.05, 0.08)]),
    "db_bottom": (double_top_bottom, {"direction": "bottom"},
                  [{"pivot_window": w, "level_tol": l} for w in (5, 8, 12) for l in (0.03, 0.05, 0.07)]),
    "dt_top": (double_top_bottom, {"direction": "top"},
               [{"pivot_window": w, "level_tol": l} for w in (5, 8, 12) for l in (0.03, 0.05, 0.07)]),
}


def _trades_in(module, df, base, params, y0, y1):
    """Trades dont l'ENTRÉE est dans [y0, y1) (années), détectés sur df."""
    out = []
    for t in module.detect_trades(df, **base, **params):
        if y0 <= t.entry_date.year < y1:
            out.append(t)
    return out


def walk_forward(tickers: list[str] | None = None, cost: float = config.COST_PER_SIDE,
                 seed: int = 7, log_every: int = 50) -> pd.DataFrame:
    """Renvoie 1 ligne par trade HORS-ÉCHANTILLON (avec edge vs hasard)."""
    tickers = tickers or universe.load_sp500()
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    total = len(tickers)
    # pré-charge les df
    for i, tk in enumerate(tickers, 1):
        try:
            df = data.get_ohlcv(tk)
        except Exception:  # noqa: BLE001
            continue
        close = df["Close"].to_numpy()
        pos = {d: j for j, d in enumerate(df.index)}
        for key, (module, base, grid) in PATTERNS.items():
            for ty in TEST_YEARS:
                train = df[(df.index.year >= ty - TRAIN_WIN) & (df.index.year < ty)]
                if len(train) < 250:
                    continue
                # sélection : meilleur réglage sur le train (rendement net moyen)
                best, best_m = None, -1e18
                for p in grid:
                    tr = module.detect_trades(train, **base, **p)
                    if not tr:
                        continue
                    m = float(np.mean([t.net_return(cost) for t in tr]))
                    if m > best_m:
                        best_m, best = m, p
                if best is None:
                    continue
                # test hors-échantillon : trades entrant dans l'année ty, réglage figé
                for t in _trades_in(module, df, base, best, ty, ty + 1):
                    dur = pos[t.exit_date] - pos[t.entry_date]
                    rnet = t.net_return(cost)
                    rexp = _rand_return(close, dur, t.direction, rng, cost)
                    rows.append({
                        "ticker": tk, "strategy": key, "test_year": ty,
                        "params": str(best), "return_net": round(rnet, 6),
                        "rand_return": round(rexp, 6) if rexp == rexp else None,
                        "edge": round(rnet - rexp, 6) if rexp == rexp else None,
                        "win": int(rnet > 0),
                    })
        if log_every and (i % log_every == 0 or i == total):
            print(f"[wf] {i}/{total} — {len(rows)} trades OOS", flush=True)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for k, g in df.groupby("strategy"):
        e = g["edge"].dropna()
        t, p = st.ttest_1samp(e, 0.0) if len(e) > 1 else (float("nan"), float("nan"))
        out.append({
            "strategy": k, "n_OOS": len(g),
            "ret_net_moy": round(g["return_net"].mean(), 4),
            "edge_moy": round(e.mean(), 4),
            "%_gagnants": round(g["win"].mean(), 3),
            "p_value": float(p), "significatif_5%": bool(p < 0.05),
        })
    return pd.DataFrame(out).sort_values("edge_moy", ascending=False)


if __name__ == "__main__":
    import sqlite3
    d = walk_forward()
    con = sqlite3.connect(config.ROOT / "results.db")
    try:
        d.to_sql("walkforward", con, if_exists="replace", index=False)
    finally:
        con.close()
    print(f"[wf] {len(d)} trades hors-échantillon -> table 'walkforward'")
    print(summarize(d).to_string(index=False))
