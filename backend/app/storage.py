"""Account file storage + SQLite snapshot DB."""
from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
SNAPSHOTS_DB = DATA_DIR / "snapshots.db"

_accounts_lock = threading.Lock()
_db_lock = threading.Lock()


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.write_text("[]", encoding="utf-8")


def load_accounts() -> list[dict[str, Any]]:
    _ensure_files()
    with _accounts_lock:
        raw = ACCOUNTS_FILE.read_text(encoding="utf-8")
    try:
        data = json.loads(raw or "[]")
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def save_accounts(accounts: list[dict[str, Any]]) -> None:
    _ensure_files()
    with _accounts_lock:
        ACCOUNTS_FILE.write_text(
            json.dumps(accounts, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def get_account(account_id: str) -> dict[str, Any] | None:
    for acc in load_accounts():
        if acc.get("id") == account_id:
            return acc
    return None


def add_account(
    label: str,
    api_key: str,
    api_secret: str,
    base_url: str = "https://paper-api.alpaca.markets",
) -> dict[str, Any]:
    accounts = load_accounts()
    new_id = uuid.uuid4().hex[:8]
    acc = {
        "id": new_id,
        "label": label,
        "api_key": api_key,
        "api_secret": api_secret,
        "base_url": base_url,
    }
    accounts.append(acc)
    save_accounts(accounts)
    return acc


def delete_account(account_id: str) -> bool:
    accounts = load_accounts()
    new_list = [a for a in accounts if a.get("id") != account_id]
    if len(new_list) == len(accounts):
        return False
    save_accounts(new_list)
    with _db_lock, sqlite3.connect(SNAPSHOTS_DB) as conn:
        conn.execute("DELETE FROM snapshots WHERE account_id = ?", (account_id,))
        conn.commit()
    return True


def public_account(acc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": acc.get("id"),
        "label": acc.get("label"),
        "base_url": acc.get("base_url"),
    }


# --- SQLite snapshots ---

def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _db_lock, sqlite3.connect(SNAPSHOTS_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                ts INTEGER NOT NULL,
                equity REAL NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_snap_acc_ts ON snapshots(account_id, ts)"
        )
        conn.commit()


def insert_snapshot(account_id: str, ts: int, equity: float) -> None:
    with _db_lock, sqlite3.connect(SNAPSHOTS_DB) as conn:
        conn.execute(
            "INSERT INTO snapshots (account_id, ts, equity) VALUES (?, ?, ?)",
            (account_id, ts, equity),
        )
        conn.commit()


def get_snapshots(account_id: str, since_ts: int) -> list[tuple[int, float]]:
    with _db_lock, sqlite3.connect(SNAPSHOTS_DB) as conn:
        cur = conn.execute(
            "SELECT ts, equity FROM snapshots WHERE account_id = ? AND ts >= ? ORDER BY ts ASC",
            (account_id, since_ts),
        )
        return [(int(r[0]), float(r[1])) for r in cur.fetchall()]


def prune_snapshots(older_than_ts: int) -> None:
    with _db_lock, sqlite3.connect(SNAPSHOTS_DB) as conn:
        conn.execute("DELETE FROM snapshots WHERE ts < ?", (older_than_ts,))
        conn.commit()
