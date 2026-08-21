"""Typed, serializable domain models for the AURA paper-trading boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    FLAT = "FLAT"


@dataclass(frozen=True, slots=True)
class SignalSnapshot:
    """A normalized research result; no broker-specific fields are allowed."""

    symbol: str
    side: Side
    confidence: Decimal
    price: Decimal
    stop_loss: Decimal | None = None
    target: Decimal | None = None
    rationale: str = ""
    source_run_id: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        if not symbol or len(symbol) > 32:
            raise ValueError("symbol must be 1-32 characters")
        object.__setattr__(self, "symbol", symbol)
        if not (Decimal("0") <= self.confidence <= Decimal("1")):
            raise ValueError("confidence must be between 0 and 1")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.stop_loss is not None and self.stop_loss <= 0:
            raise ValueError("stop_loss must be positive")
        if self.target is not None and self.target <= 0:
            raise ValueError("target must be positive")


@dataclass(frozen=True, slots=True)
class RiskDecision:
    approved: bool
    reason: str
    max_quantity: Decimal = Decimal("0")
    risk_amount: Decimal = Decimal("0")


@dataclass(frozen=True, slots=True)
class PaperOrder:
    order_id: str
    symbol: str
    side: Side
    quantity: Decimal
    requested_price: Decimal
    filled_price: Decimal
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def notional(self) -> Decimal:
        return self.quantity * self.filled_price
