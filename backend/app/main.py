"""FastAPI app exposing read-only Alpaca paper-trading data for multiple accounts."""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import alpaca_client as ac
from . import analysis, chat, data_api, scheduler, services, storage


class NewAccount(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    api_key: str = Field(min_length=4)
    api_secret: str = Field(min_length=4)
    base_url: str = "https://paper-api.alpaca.markets"


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.init_db()
    stop_event = asyncio.Event()
    task = asyncio.create_task(scheduler.run_loop(stop_event))
    try:
        yield
    finally:
        stop_event.set()
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except asyncio.TimeoutError:
            task.cancel()


app = FastAPI(title="TradingMonitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(data_api.router)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "ts": int(time.time())}


@app.get("/accounts")
async def list_accounts() -> list[dict]:
    return [storage.public_account(a) for a in storage.load_accounts()]


@app.post("/accounts", status_code=201)
async def create_account(payload: NewAccount) -> dict:
    acc = storage.add_account(
        label=payload.label.strip(),
        api_key=payload.api_key.strip(),
        api_secret=payload.api_secret.strip(),
        base_url=payload.base_url.strip() or "https://paper-api.alpaca.markets",
    )
    return storage.public_account(acc)


@app.delete("/accounts/{account_id}", status_code=204)
async def delete_account(account_id: str):
    ok = storage.delete_account(account_id)
    if not ok:
        raise HTTPException(404, "account not found")
    return None


def _require_account(account_id: str) -> dict:
    acc = storage.get_account(account_id)
    if not acc:
        raise HTTPException(404, "account not found")
    return acc


@app.get("/accounts/{account_id}/summary")
async def get_summary(account_id: str) -> dict:
    acc = _require_account(account_id)
    async with httpx.AsyncClient() as client:
        try:
            raw = await ac.get_account(client, acc)
        except ac.AlpacaError as e:
            raise HTTPException(502, f"alpaca error: {e}")
    return services.build_summary(raw)


@app.get("/accounts/{account_id}/positions")
async def get_positions(account_id: str) -> list[dict]:
    acc = _require_account(account_id)
    async with httpx.AsyncClient() as client:
        try:
            raw = await ac.get_positions(client, acc)
        except ac.AlpacaError as e:
            raise HTTPException(502, f"alpaca error: {e}")
    return services.build_positions(raw)


@app.get("/accounts/{account_id}/orders")
async def get_orders(account_id: str, limit: int = 50) -> list[dict]:
    acc = _require_account(account_id)
    limit = max(1, min(500, limit))
    async with httpx.AsyncClient() as client:
        try:
            raw = await ac.get_orders(client, acc, limit=limit)
        except ac.AlpacaError as e:
            raise HTTPException(502, f"alpaca error: {e}")
    return services.build_orders(raw)


@app.get("/accounts/{account_id}/history")
async def get_history(account_id: str, period: str = "1M", timeframe: str | None = None) -> dict:
    acc = _require_account(account_id)
    async with httpx.AsyncClient() as client:
        try:
            raw = await ac.get_portfolio_history(client, acc, period=period, timeframe=timeframe)
        except ac.AlpacaError as e:
            raise HTTPException(502, f"alpaca error: {e}")
    history = services.build_history(raw)
    if period in ("1D", "intraday"):
        today_start = int(
            datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        )
        snaps = storage.get_snapshots(account_id, today_start)
        history = services.merge_history_with_snapshots(history, snaps)
    return history


@app.get("/overview")
async def get_overview() -> dict:
    accounts = storage.load_accounts()
    if not accounts:
        return {
            "total_equity": 0.0,
            "total_cash": 0.0,
            "total_pnl_today": 0.0,
            "total_pnl_today_pct": 0.0,
            "total_pnl_total": 0.0,
            "par_compte": [],
            "positions_agregees": [],
        }
    async with httpx.AsyncClient() as client:
        per_account = await asyncio.gather(
            *(services.fetch_account_overview(client, a) for a in accounts)
        )
    return services.build_global_overview(list(per_account))
