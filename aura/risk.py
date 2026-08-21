"""Deterministic risk gate for paper-trading research.

The gate is intentionally independent of the LLM. A model can propose a
trade, but it cannot override hard portfolio constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

from .models import RiskDecision, SignalSnapshot, Side


@dataclass(frozen=True, slots=True)
class RiskLimits:
    max_position_fraction: Decimal = Decimal("0.10")
    max_trade_risk_fraction: Decimal = Decimal("0.01")
    min_confidence: Decimal = Decimal("0.70")
    min_stop_distance_fraction: Decimal = Decimal("0.002")
    max_daily_loss_fraction: Decimal = Decimal("0.03")

    def __post_init__(self) -> None:
        for name, value in (
            ("max_position_fraction", self.max_position_fraction),
            ("max_trade_risk_fraction", self.max_trade_risk_fraction),
            ("min_confidence", self.min_confidence),
            ("min_stop_distance_fraction", self.min_stop_distance_fraction),
            ("max_daily_loss_fraction", self.max_daily_loss_fraction),
        ):
            if not Decimal("0") <= value <= Decimal("1"):
                raise ValueError(f"{name} must be between 0 and 1")


class RiskEngine:
    """Evaluate normalized signals against hard, deterministic limits."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()

    def evaluate(
        self,
        signal: SignalSnapshot,
        equity: Decimal,
        realized_daily_pnl: Decimal = Decimal("0"),
    ) -> RiskDecision:
        if equity <= 0:
            return RiskDecision(False, "equity must be positive")
        if realized_daily_pnl <= -(equity * self.limits.max_daily_loss_fraction):
            return RiskDecision(False, "daily loss limit reached")
        if signal.side is Side.FLAT:
            return RiskDecision(True, "flat signal; no order", Decimal("0"), Decimal("0"))
        if signal.confidence < self.limits.min_confidence:
            return RiskDecision(False, "confidence below hard minimum")
        if signal.stop_loss is None:
            return RiskDecision(False, "stop loss is required")

        if signal.side is Side.BUY and signal.stop_loss >= signal.price:
            return RiskDecision(False, "buy stop loss must be below entry price")
        if signal.side is Side.SELL and signal.stop_loss <= signal.price:
            return RiskDecision(False, "sell stop loss must be above entry price")

        stop_distance = abs(signal.price - signal.stop_loss) / signal.price
        if stop_distance < self.limits.min_stop_distance_fraction:
            return RiskDecision(False, "stop distance below hard minimum")

        risk_budget = equity * self.limits.max_trade_risk_fraction
        risk_per_unit = signal.price * stop_distance
        raw_qty = risk_budget / risk_per_unit
        position_cap_qty = (equity * self.limits.max_position_fraction) / signal.price
        quantity = min(raw_qty, position_cap_qty)
        quantity = quantity.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
        if quantity <= 0:
            return RiskDecision(False, "computed quantity is zero")

        return RiskDecision(
            True,
            "approved by deterministic risk gate",
            quantity,
            risk_per_unit * quantity,
        )
