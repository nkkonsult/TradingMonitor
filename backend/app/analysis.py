"""Routeur d'analyse de graphiques (Pilier A — analyse technique).

Pour un ticker, calcule TOUTES les stratégies enregistrées en une fois : rendement,
courbe d'equity (croissance de 1$), repères de trades et moyennes pour le tracé.
Le frontend choisit lesquelles afficher (rien n'est imposé en permanence).

Routes sync (`def`) -> threadpool FastAPI, le download yfinance ne fige pas le serveur.
"""
from __future__ import annotations

import math

from fastapi import APIRouter, HTTPException

from charts import backtest, benchmark, config as ccfg, data, stats, universe
from charts.strategy import head_shoulders, ma_crossover, rsi

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
    "hs_inverse": (head_shoulders, "Épaule-tête-épaule inversé (achat)", {"direction": "bullish"}),
    "hs_classic": (head_shoulders, "Épaule-tête-épaule (vente/short)", {"direction": "bearish"}),
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


def _equity_curve(df, trades, cost_per_side: float = 0.0) -> list[float]:
    """Croissance de 1$ (base 100), pas à pas : plat hors position, scalé pendant un trade.

    Coûts : on paie `cost_per_side` à l'ACHAT (facteur (1-c) au moment de l'entrée) et
    à la VENTE (facteur (1-c) au moment de la sortie). Cohérent avec Trade.net_return.
    """
    close = df["Close"]
    # On garde le prix d'entrée ET la direction (+1 long / -1 short) par trade.
    entries = {t.entry_date: (t.entry_price, t.direction) for t in trades}
    exits = {t.exit_date: (t.entry_price, t.direction) for t in trades}
    realized = 1.0
    in_trade = False
    entry_price = None
    direction = 1
    out = []
    for d in df.index:
        if d in entries:
            in_trade = True
            entry_price, direction = entries[d]
            realized *= 1.0 - cost_per_side  # coût d'entrée
        c = float(close.loc[d])
        # 1 + direction·(c/entrée − 1) : monte avec le prix en long, baisse en short.
        val = realized * (1.0 + direction * (c / entry_price - 1.0)) if in_trade else realized
        out.append(round(val * 100.0, 2))
        if d in exits:
            entry_price, direction = exits[d]
            realized *= (1.0 + direction * (c / entry_price - 1.0)) * (1.0 - cost_per_side)
            in_trade = False
            entry_price = None
    return out


@router.get("/defaults")
def defaults() -> dict:
    # Univers du sélecteur = S&P 500 complet (déjà en cache). Repli sur le prototype
    # si la liste n'est pas récupérable.
    try:
        tickers = universe.load_sp500()
    except Exception:  # noqa: BLE001
        tickers = ccfg.TICKERS
    return {
        "tickers": tickers,
        "ma_short": ccfg.MA_SHORT,
        "ma_long": ccfg.MA_LONG,
        "strategies": [{"key": k, "label": lbl} for k, (_, lbl, _p) in STRATEGIES.items()],
        "cost_bps": round(ccfg.COST_PER_SIDE * 1e4, 2),
    }


@router.get("/{ticker}")
def analyze(
    ticker: str,
    short: int = ccfg.MA_SHORT,
    long: int = ccfg.MA_LONG,
    cost_bps: float = ccfg.COST_PER_SIDE * 1e4,
) -> dict:
    """Analyse complète d'un ticker : toutes les stratégies + benchmark.

    `cost_bps` = coût de transaction par côté, en points de base (1 bp = 0,01 %).
    """
    ticker = ticker.upper()
    if short >= long:
        raise HTTPException(400, "La MM courte doit être plus petite que la MM longue.")
    cost = max(0.0, cost_bps) / 1e4  # bps -> fraction par côté

    df = _load(ticker)
    dates = df.index.strftime("%Y-%m-%d").tolist()
    close = [_round(c) for c in df["Close"].to_numpy()]
    final_close = float(df["Close"].dropna().iloc[-1])

    # Benchmark buy & hold + sa courbe d'equity (base 100). Coût = 1 seul achat au départ
    # (jamais revendu) -> décale le niveau de (1-c), n'affecte pas les ratios annualisés.
    bh = benchmark.buy_and_hold(df)
    first_close = float(df["Close"].dropna().iloc[0])
    bh_equity = [_round(c / first_close * 100.0 * (1.0 - cost)) if c is not None else None for c in close]
    bh["equity"] = bh_equity
    if bh.get("total_return") is not None:
        bh["total_return"] = round((1.0 + bh["total_return"]) * (1.0 - cost) - 1.0, 4)
    # Métriques de risque du benchmark (comparaison à armes égales avec les stratégies).
    bh["risk"] = stats.summarize_equity(bh_equity)

    strategies_out = []
    for i, (key, (strat, label, sparams)) in enumerate(STRATEGIES.items()):
        # Appel uniforme : short/long (UI) + params propres à la variante. Chaque
        # stratégie pioche ce qui la concerne et ignore le reste (via **_).
        call_kwargs = {"short": short, "long": long, **sparams}
        trades = strat.detect_trades(df, **call_kwargs)
        metrics = stats.summarize(backtest.to_dataframe(trades, cost))

        oe = strat.open_entry(df, **call_kwargs)
        booked = metrics.get("rendement_total_cumule") or 0.0
        if oe is not None:
            # Position ouverte : coût d'achat payé, coût de vente pas encore (non clôturée).
            open_return = (final_close / oe[1]) * (1.0 - cost) - 1.0
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
        # Géométrie optionnelle (Head & Shoulders...) : ligne de cou, objectif, pivots.
        shp = strat.shapes(df, **call_kwargs) if hasattr(strat, "shapes") else None

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

        equity = _equity_curve(df, trades, cost)
        # Métriques de niveau série temporelle (Sharpe, Sortino, Max DD...) sur la courbe d'equity.
        risk = stats.summarize_equity(equity)

        strategies_out.append(
            {
                "key": key,
                "label": label,
                "color": _PALETTE[i % len(_PALETTE)],
                "metrics": metrics,
                "risk": risk,
                "strategy_total_with_open": total_with_open,
                "open_position": open_position,
                "trades": [
                    {
                        "entry_date": t.entry_date.strftime("%Y-%m-%d"),
                        "exit_date": t.exit_date.strftime("%Y-%m-%d"),
                        "entry_price": round(t.entry_price, 2),
                        "exit_price": round(t.exit_price, 2),
                        "return_pct": round(t.net_return(cost), 4),
                        "gross_return_pct": round(t.return_pct, 4),
                        "holding_days": t.holding_days,
                        "direction": t.direction,
                    }
                    for t in trades
                ],
                "equity": equity,
                "overlays": overlays,
                "oscillator": osc,
                "shapes": shp,
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
