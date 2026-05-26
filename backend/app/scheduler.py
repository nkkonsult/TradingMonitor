"""Background task: every 5s, snapshot each account's equity into SQLite."""
from __future__ import annotations

import asyncio
import logging
import time

import httpx

from . import alpaca_client as ac
from . import storage

log = logging.getLogger("scheduler")

SNAPSHOT_INTERVAL_SEC = 5
RETENTION_HOURS = 48


async def _snapshot_once(client: httpx.AsyncClient) -> None:
    accounts = storage.load_accounts()
    if not accounts:
        return

    async def one(acc: dict) -> None:
        try:
            data = await ac.get_account(client, acc)
            equity = float(data.get("equity") or 0.0)
            storage.insert_snapshot(acc["id"], int(time.time()), equity)
        except Exception as e:  # noqa: BLE001
            log.debug("snapshot failed for %s: %s", acc.get("id"), e)

    await asyncio.gather(*(one(a) for a in accounts))


async def run_loop(stop_event: asyncio.Event) -> None:
    storage.init_db()
    async with httpx.AsyncClient() as client:
        last_prune = 0.0
        while not stop_event.is_set():
            try:
                await _snapshot_once(client)
                now = time.time()
                if now - last_prune > 3600:
                    storage.prune_snapshots(int(now) - RETENTION_HOURS * 3600)
                    last_prune = now
            except Exception as e:  # noqa: BLE001
                log.warning("snapshot loop iteration failed: %s", e)
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=SNAPSHOT_INTERVAL_SEC)
            except asyncio.TimeoutError:
                pass
