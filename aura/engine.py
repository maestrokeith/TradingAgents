"""Adapter from TradingAgents research output to the AURA paper boundary."""

from __future__ import annotations

import hashlib
from decimal import Decimal

from tradingagents.graph.trading_graph import TradingAgentsGraph

from .models import SignalSnapshot, Side


def _side_from_rating(rating: str) -> Side:
    normalized = rating.strip().lower()
    if normalized in {"buy", "overweight"}:
        return Side.BUY
    if normalized in {"sell", "underweight"}:
        return Side.SELL
    return Side.FLAT


class AuraResearchEngine:
    """Run TradingAgents and normalize the final rating for paper evaluation."""

    def __init__(self, graph: TradingAgentsGraph):
        self.graph = graph

    def analyze(self, symbol: str, trade_date: str, price: Decimal) -> SignalSnapshot:
        final_state, rating = self.graph.propagate(symbol, trade_date)
        side = _side_from_rating(rating)
        decision_text = final_state.get("final_trade_decision", "")
        # Stable run identity for audit correlation without storing raw prompts.
        run_id = hashlib.sha256(
            f"{symbol.upper()}|{trade_date}|{rating}|{decision_text}".encode()
        ).hexdigest()[:16]
        return SignalSnapshot(
            symbol=symbol,
            side=side,
            confidence=Decimal("0.70") if side is not Side.FLAT else Decimal("0.50"),
            price=price,
            rationale=decision_text,
            source_run_id=run_id,
        )
