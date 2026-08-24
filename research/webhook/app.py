from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

DATA_DIR = Path(os.getenv("AURA_RESEARCH_DATA_DIR", "./research_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "signals.sqlite3"
WEBHOOK_SECRET = os.getenv("AURA_RESEARCH_WEBHOOK_SECRET", "")

app = FastAPI(title="AURA-GOLD Research Gateway", version="1.0.0")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT NOT NULL,
            symbol TEXT,
            timeframe TEXT,
            direction TEXT,
            score INTEGER,
            price REAL,
            payload TEXT NOT NULL
        )"""
    )
    return conn


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "mode": "research-only"}


@app.post("/webhook")
async def webhook(request: Request, x_aura_secret: str | None = Header(default=None)) -> dict[str, Any]:
    if WEBHOOK_SECRET and x_aura_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid JSON") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON object required")

    # Explicit research-only boundary: this service only records observations.
    direction = str(payload.get("direction", "UNKNOWN"))
    if direction not in {"LONG_OBSERVATION", "SHORT_OBSERVATION", "UNKNOWN"}:
        direction = "UNKNOWN"

    received_at = datetime.now(timezone.utc).isoformat()
    with db() as conn:
        conn.execute(
            "INSERT INTO observations(received_at,symbol,timeframe,direction,score,price,payload) VALUES(?,?,?,?,?,?,?)",
            (
                received_at,
                payload.get("symbol"),
                payload.get("timeframe"),
                direction,
                payload.get("score"),
                payload.get("price"),
                json.dumps(payload, separators=(",", ":")),
            ),
        )

    return {"accepted": True, "mode": "research-only", "received_at": received_at}


@app.get("/observations")
def observations(limit: int = 100) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 500))
    with db() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, received_at, symbol, timeframe, direction, score, price FROM observations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
