"""Business logic: shape Alpaca responses into the dashboard's view models."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from . import alpaca_client as ac
from . import storage


def _f(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def build_summary(account_raw: dict[str, Any]) -> dict[str, Any]:
    equity = _f(account_raw.get("equity"))
    last_equity = _f(account_raw.get("last_equity"))
    cash = _f(account_raw.get("cash"))
    buying_power = _f(account_raw.get("buying_power"))
    pnl_today = equity - last_equity
    pnl_today_pct = (pnl_today / last_equity * 100.0) if last_equity else 0.0
    # Alpaca doesn't directly expose total P&L vs initial deposit cheaply;
    # we approximate "total P&L" as equity - cumulative cash deposits if available,
    # else fallback to (equity - 100000) for paper accounts (default starting cash).
    initial = _f(account_raw.get("initial_margin"))  # not exact; placeholder
    # Better: paper accounts start at 100k by default
    starting_equity = 100000.0
    pnl_total = equity - starting_equity
    pnl_total_pct = (pnl_total / starting_equity * 100.0) if starting_equity else 0.0
    return {
        "equity": equity,
        "cash": cash,
        "buying_power": buying_power,
        "last_equity": last_equity,
        "pnl_today": pnl_today,
        "pnl_today_pct": pnl_today_pct,
        "pnl_total": pnl_total,
        "pnl_total_pct": pnl_total_pct,
        "status": account_raw.get("status"),
        "currency": account_raw.get("currency", "USD"),
    }


def build_positions(positions_raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for p in positions_raw:
        out.append(
            {
                "symbol": p.get("symbol"),
                "qty": _f(p.get("qty")),
                "side": p.get("side"),
                "avg_entry_price": _f(p.get("avg_entry_price")),
                "current_price": _f(p.get("current_price")),
                "market_value": _f(p.get("market_value")),
                "cost_basis": _f(p.get("cost_basis")),
                "unrealized_pl": _f(p.get("unrealized_pl")),
                "unrealized_plpc": _f(p.get("unrealized_plpc")) * 100.0,
            }
        )
    return out


def _agent_from_client_order_id(coid: str | None) -> str | None:
    if not coid:
        return None
    if "_" in coid:
        prefix = coid.split("_", 1)[0]
        if prefix and len(prefix) <= 32:
            return prefix
    return None


def build_orders(orders_raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for o in orders_raw:
        out.append(
            {
                "id": o.get("id"),
                "client_order_id": o.get("client_order_id"),
                "agent": _agent_from_client_order_id(o.get("client_order_id")),
                "submitted_at": o.get("submitted_at"),
                "filled_at": o.get("filled_at"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "qty": _f(o.get("qty")),
                "filled_qty": _f(o.get("filled_qty")),
                "type": o.get("type") or o.get("order_type"),
                "status": o.get("status"),
                "filled_avg_price": _f(o.get("filled_avg_price")),
                "limit_price": _f(o.get("limit_price")),
            }
        )
    return out


def build_history(history_raw: dict[str, Any]) -> dict[str, Any]:
    timestamps = history_raw.get("timestamp") or []
    equity = history_raw.get("equity") or []
    profit_loss = history_raw.get("profit_loss") or []
    points = []
    for i, ts in enumerate(timestamps):
        eq = equity[i] if i < len(equity) else None
        if eq is None:
            continue
        points.append(
            {
                "ts": int(ts),
                "equity": _f(eq),
                "profit_loss": _f(profit_loss[i] if i < len(profit_loss) else 0),
            }
        )
    return {
        "base_value": _f(history_raw.get("base_value")),
        "timeframe": history_raw.get("timeframe"),
        "points": points,
    }


def merge_history_with_snapshots(
    history: dict[str, Any], snapshots: list[tuple[int, float]]
) -> dict[str, Any]:
    """Append local 5s snapshots after the last Alpaca history point for smoother live feel."""
    points = list(history.get("points", []))
    last_ts = points[-1]["ts"] if points else 0
    for ts, eq in snapshots:
        if ts > last_ts:
            points.append({"ts": ts, "equity": eq, "profit_loss": 0.0})
    history["points"] = points
    return history


# --- Per-account aggregation used by /overview ---


async def fetch_account_overview(
    client: httpx.AsyncClient, acc: dict[str, Any]
) -> dict[str, Any]:
    try:
        account_raw, positions_raw, orders_raw = await asyncio.gather(
            ac.get_account(client, acc),
            ac.get_positions(client, acc),
            ac.get_orders(client, acc, limit=200),
        )
    except ac.AlpacaError as e:
        return {
            "id": acc["id"],
            "label": acc["label"],
            "statut_connexion": "erreur",
            "error": str(e)[:200],
            "equity": 0.0,
            "pnl_today": 0.0,
            "pnl_today_pct": 0.0,
            "pnl_total": 0.0,
            "nb_positions": 0,
            "nb_ordres_du_jour": 0,
            "positions": [],
        }

    summary = build_summary(account_raw)
    positions = build_positions(positions_raw)
    orders = build_orders(orders_raw)
    today = datetime.now(timezone.utc).date().isoformat()
    nb_today = sum(1 for o in orders if (o.get("submitted_at") or "").startswith(today))
    return {
        "id": acc["id"],
        "label": acc["label"],
        "statut_connexion": "ok",
        "equity": summary["equity"],
        "cash": summary["cash"],
        "pnl_today": summary["pnl_today"],
        "pnl_today_pct": summary["pnl_today_pct"],
        "pnl_total": summary["pnl_total"],
        "nb_positions": len(positions),
        "nb_ordres_du_jour": nb_today,
        "positions": positions,
    }


def aggregate_positions(per_account: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_symbol: dict[str, dict[str, Any]] = {}
    for acc in per_account:
        for p in acc.get("positions", []):
            sym = p["symbol"]
            slot = by_symbol.setdefault(
                sym,
                {
                    "symbol": sym,
                    "total_qty": 0.0,
                    "total_market_value": 0.0,
                    "total_unrealized_pl": 0.0,
                    "accounts": [],
                },
            )
            slot["total_qty"] += p["qty"]
            slot["total_market_value"] += p["market_value"]
            slot["total_unrealized_pl"] += p["unrealized_pl"]
            slot["accounts"].append({"id": acc["id"], "label": acc["label"], "qty": p["qty"]})
    out = list(by_symbol.values())
    out.sort(key=lambda x: abs(x["total_market_value"]), reverse=True)
    for x in out:
        x["nb_accounts"] = len(x["accounts"])
    return out


def build_global_overview(per_account: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [a for a in per_account if a["statut_connexion"] == "ok"]
    total_equity = sum(a["equity"] for a in ok)
    total_cash = sum(a.get("cash", 0.0) for a in ok)
    total_pnl_today = sum(a["pnl_today"] for a in ok)
    total_pnl_total = sum(a["pnl_total"] for a in ok)
    last_equity_total = total_equity - total_pnl_today
    total_pnl_today_pct = (
        (total_pnl_today / last_equity_total * 100.0) if last_equity_total else 0.0
    )
    return {
        "total_equity": total_equity,
        "total_cash": total_cash,
        "total_pnl_today": total_pnl_today,
        "total_pnl_today_pct": total_pnl_today_pct,
        "total_pnl_total": total_pnl_total,
        "par_compte": [
            {k: v for k, v in a.items() if k != "positions"} for a in per_account
        ],
        "positions_agregees": aggregate_positions(per_account),
    }
