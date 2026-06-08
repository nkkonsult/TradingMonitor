"""Routeur d'analyse de graphiques (Pilier A — analyse technique).

Pour un ticker, calcule TOUTES les stratégies enregistrées en une fois : rendement,
courbe d'equity (croissance de 1$), repères de trades et moyennes pour le tracé.
Le frontend choisit lesquelles afficher (rien n'est imposé en permanence).

Routes sync (`def`) -> threadpool FastAPI, le download yfinance ne fige pas le serveur.
"""
from __future__ import annotations

import math

from fastapi import APIRouter, HTTPException

from charts import backtest, benchmark, config as ccfg, data, stats
from charts.strategy import ma_crossover, rsi

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Registre des stratégies. Chaque module expose detect_trades / open_entry / indicators
# avec une signature à mots-clés (+ **_ pour ignorer les params non utilisés), donc on
# peut toutes les appeler de façon uniforme via **params.
# Ajouter une stratégie/variante = ajouter une ligne ici (le front l'affiche tout seul).
# Le 3e élément = params propres à la variante ; short/long (contrôle MM de l'UI) sont
# toujours injectés en plus, les stratégies qui ne s'en servent pas les ignorent.
STRATEGIES = {
    "ma_crossover": (ma_crossover, "Croisement de moyennes mobiles", {}),
    "rsi_classic": (rsi, "RSI 30/70", {"lower": 30, "upper": 70}),
    "rsi_strict": (rsi, "RSI 20/80 (strict)", {"lower": 20, "upper": 80}),
    "rsi_trend": (rsi, "RSI 30/70 + filtre MM200", {"lower": 30, "upper": 70, "trend_ma": 200}),
}

# Couleur par stratégie (courbe d'equity + repères). Étendre si beaucoup de stratégies.
_PALETTE = ["#2563eb", "#16a34a", "#db2777", "#7c3aed", "#ea580c", "#0891b2", "#ca8a04"]
# Couleurs des overlays (moyennes) sur le graphique du cours.
_OVERLAY_COLORS = ["#2563eb", "#ea580c", "#7c3aed", "#0891b2"]


def _load(ticker: str):
    try:
        return data.get_ohlcv(ticker.upper())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(404, f"Données indisponibles pour {ticker}: {e}")


def _round(x) -> float | None:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), 2)


def _equity_curve(df, trades) -> list[float]:
    """Croissance de 1$ (base 100), pas à pas : plat hors position, scalé pendant un trade."""
    close = df["Close"]
    entries = {t.entry_date: t.entry_price for t in trades}
    exits = {t.exit_date: t.entry_price for t in trades}
    realized = 1.0
    in_trade = False
    entry_price = None
    out = []
    for d in df.index:
        if d in entries:
            in_trade = True
            entry_price = entries[d]
        c = float(close.loc[d])
        val = realized * (c / entry_price) if in_trade else realized
        out.append(round(val * 100.0, 2))
        if d in exits:
            realized *= c / entry_price
            in_trade = False
            entry_price = None
    return out


@router.get("/defaults")
def defaults() -> dict:
    return {
        "tickers": ccfg.TICKERS,
        "ma_short": ccfg.MA_SHORT,
        "ma_long": ccfg.MA_LONG,
        "strategies": [{"key": k, "label": lbl} for k, (_, lbl, _p) in STRATEGIES.items()],
    }


@router.get("/{ticker}")
def analyze(ticker: str, short: int = ccfg.MA_SHORT, long: int = ccfg.MA_LONG) -> dict:
    """Analyse complète d'un ticker : toutes les stratégies + benchmark."""
    ticker = ticker.upper()
    if short >= long:
        raise HTTPException(400, "La MM courte doit être plus petite que la MM longue.")

    df = _load(ticker)
    dates = df.index.strftime("%Y-%m-%d").tolist()
    close = [_round(c) for c in df["Close"].to_numpy()]
    final_close = float(df["Close"].dropna().iloc[-1])

    # Benchmark buy & hold + sa courbe d'equity (base 100).
    bh = benchmark.buy_and_hold(df)
    first_close = float(df["Close"].dropna().iloc[0])
    bh_equity = [_round(c / first_close * 100.0) if c is not None else None for c in close]
    bh["equity"] = bh_equity

    strategies_out = []
    for i, (key, (strat, label, sparams)) in enumerate(STRATEGIES.items()):
        # Appel uniforme : short/long (UI) + params propres à la variante. Chaque
        # stratégie pioche ce qui la concerne et ignore le reste (via **_).
        call_kwargs = {"short": short, "long": long, **sparams}
        trades = strat.detect_trades(df, **call_kwargs)
        metrics = stats.summarize(backtest.to_dataframe(trades))

        oe = strat.open_entry(df, **call_kwargs)
        booked = metrics.get("rendement_total_cumule") or 0.0
        if oe is not None:
            open_return = final_close / oe[1] - 1.0
            total_with_open = round((1 + booked) * (1 + open_return) - 1.0, 4)
            open_position = {
                "entry_date": oe[0].strftime("%Y-%m-%d"),
                "entry_price": round(oe[1], 2),
                "current_price": round(final_close, 2),
                "unrealized_return": round(open_return, 4),
            }
        else:
            total_with_open = round(booked, 4)
            open_position = None

        # Oscillateur optionnel (RSI...) : panneau séparé 0-100 côté front.
        osc = strat.oscillator(df, **call_kwargs) if hasattr(strat, "oscillator") else None

        ind = strat.indicators(df, **call_kwargs)
        overlays = [
            {
                "name": col,
                "key": f"{key}__{col}",
                "color": _OVERLAY_COLORS[j % len(_OVERLAY_COLORS)],
                "data": [_round(v) for v in ind[col].to_numpy()],
            }
            for j, col in enumerate(ind.columns)
        ]

        strategies_out.append(
            {
                "key": key,
                "label": label,
                "color": _PALETTE[i % len(_PALETTE)],
                "metrics": metrics,
                "strategy_total_with_open": total_with_open,
                "open_position": open_position,
                "trades": [
                    {
                        "entry_date": t.entry_date.strftime("%Y-%m-%d"),
                        "exit_date": t.exit_date.strftime("%Y-%m-%d"),
                        "entry_price": round(t.entry_price, 2),
                        "exit_price": round(t.exit_price, 2),
                        "return_pct": round(t.return_pct, 4),
                        "holding_days": t.holding_days,
                    }
                    for t in trades
                ],
                "equity": _equity_curve(df, trades),
                "overlays": overlays,
                "oscillator": osc,
            }
        )

    return {
        "ticker": ticker,
        "short": short,
        "long": long,
        "dates": dates,
        "close": close,
        "benchmark": bh,
        "strategies": strategies_out,
    }
