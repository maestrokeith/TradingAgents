"""Deterministic in-memory paper broker.

No network calls, credentials, or live-order APIs are present in this module.
It exists to make end-to-end testing safe and reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

from .models import PaperOrder, Side


@dataclass
class PaperBroker:
    cash: Decimal
    positions: dict[str, Decimal] = field(default_factory=dict)
    orders: list[PaperOrder] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.cash < 0:
            raise ValueError("cash cannot be negative")

    def submit_market_order(self, symbol: str, side: Side, quantity: Decimal, market_price: Decimal) -> PaperOrder:
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("symbol is required")
        if side is Side.FLAT:
            raise ValueError("FLAT is not an order side")
        if quantity <= 0 or market_price <= 0:
            raise ValueError("quantity and market_price must be positive")

        notional = quantity * market_price
        current = self.positions.get(symbol, Decimal("0"))
        if side is Side.BUY:
            if notional > self.cash:
                raise ValueError("insufficient paper cash")
            self.cash -= notional
            self.positions[symbol] = current + quantity
        else:
            if quantity > current:
                raise ValueError("paper short selling is disabled")
            self.cash += notional
            self.positions[symbol] = current - quantity

        order = PaperOrder(
            order_id=str(uuid4()),
            symbol=symbol,
            side=side,
            quantity=quantity,
            requested_price=market_price,
            filled_price=market_price,
            status="FILLED",
        )
        self.orders.append(order)
        return order
