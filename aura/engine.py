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
    """Run TradingAgents and normalize the final rating for paper evaluation.

    Confidence is supplied by the caller from a separately validated scoring
    layer. This adapter never invents confidence from an LLM label.
    """

    def __init__(self, graph: TradingAgentsGraph):
        self.graph = graph

    def analyze(
        self,
        symbol: str,
        trade_date: str,
        price: Decimal,
        confidence: Decimal,
    ) -> SignalSnapshot:
        final_state, rating = self.graph.propagate(symbol, trade_date)
        side = _side_from_rating(rating)
        decision_text = final_state.get("final_trade_decision", "")
        run_id = hashlib.sha256(
            f"{symbol.upper()}|{trade_date}|{rating}|{decision_text}".encode()
        ).hexdigest()[:16]
        return SignalSnapshot(
            symbol=symbol,
            side=side,
            confidence=confidence,
            price=price,
            rationale=decision_text,
            source_run_id=run_id,
        )
