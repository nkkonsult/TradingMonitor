"""Thin async wrapper over Alpaca REST using httpx.

We use the raw REST API rather than alpaca-py's sync clients to keep everything
async and parallelizable with asyncio.gather. Alpaca paper endpoints are stable
and well documented.
"""
from __future__ import annotations

from typing import Any

import httpx


class AlpacaError(Exception):
    pass


def _headers(acc: dict[str, Any]) -> dict[str, str]:
    return {
        "APCA-API-KEY-ID": acc["api_key"],
        "APCA-API-SECRET-KEY": acc["api_secret"],
        "accept": "application/json",
    }


def _base(acc: dict[str, Any]) -> str:
    url = acc.get("base_url", "https://paper-api.alpaca.markets").rstrip("/")
    # Accept both ".../v2" and "..." — our request paths already include "/v2/...".
    if url.endswith("/v2"):
        url = url[:-3]
    return url


async def _get(
    client: httpx.AsyncClient, acc: dict[str, Any], path: str, params: dict | None = None
) -> Any:
    url = f"{_base(acc)}{path}"
    try:
        r = await client.get(url, headers=_headers(acc), params=params, timeout=10.0)
    except httpx.HTTPError as e:
        raise AlpacaError(str(e)) from e
    if r.status_code >= 400:
        raise AlpacaError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()


async def get_account(client: httpx.AsyncClient, acc: dict[str, Any]) -> dict[str, Any]:
    return await _get(client, acc, "/v2/account")


async def get_positions(
    client: httpx.AsyncClient, acc: dict[str, Any]
) -> list[dict[str, Any]]:
    data = await _get(client, acc, "/v2/positions")
    return data if isinstance(data, list) else []


async def get_orders(
    client: httpx.AsyncClient, acc: dict[str, Any], limit: int = 50
) -> list[dict[str, Any]]:
    params = {"status": "all", "limit": limit, "direction": "desc"}
    data = await _get(client, acc, "/v2/orders", params=params)
    return data if isinstance(data, list) else []


async def get_portfolio_history(
    client: httpx.AsyncClient,
    acc: dict[str, Any],
    period: str = "1M",
    timeframe: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"period": period}
    if timeframe:
        params["timeframe"] = timeframe
    return await _get(client, acc, "/v2/account/portfolio/history", params=params)
