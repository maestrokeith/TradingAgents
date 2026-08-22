"""Immutable models for the live execution boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class LiveSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class LiveOrderIntent:
    intent_id: str
    symbol: str
    side: LiveSide
    quantity: Decimal
    limit_price: Decimal | None
    stop_loss: Decimal
    rationale: str
    risk_amount: Decimal
    source_run_id: str
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.intent_id.strip():
            raise ValueError("intent_id is required")
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.stop_loss <= 0:
            raise ValueError("stop_loss must be positive")
        if self.risk_amount < 0:
            raise ValueError("risk_amount cannot be negative")


@dataclass(frozen=True, slots=True)
class Confirmation:
    intent_id: str
    confirmation_code: str
    confirmed_by: str
    confirmed_at: datetime


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    intent_id: str
    accepted: bool
    broker_order_id: str | None
    status: str
    message: str
