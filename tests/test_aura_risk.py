from decimal import Decimal

import pytest

from aura.models import SignalSnapshot, Side
from aura.risk import RiskEngine, RiskLimits


def signal(**overrides):
    values = dict(
        symbol="AAPL",
        side=Side.BUY,
        confidence=Decimal("0.90"),
        price=Decimal("100"),
        stop_loss=Decimal("99"),
    )
    values.update(overrides)
    return SignalSnapshot(**values)


def test_approves_within_hard_limits():
    decision = RiskEngine().evaluate(signal(), Decimal("10000"))
    assert decision.approved
    assert decision.max_quantity > 0
    assert decision.risk_amount <= Decimal("100")


def test_rejects_low_confidence():
    decision = RiskEngine().evaluate(signal(confidence=Decimal("0.69")), Decimal("10000"))
    assert not decision.approved


def test_rejects_missing_stop():
    decision = RiskEngine().evaluate(signal(stop_loss=None), Decimal("10000"))
    assert not decision.approved


def test_rejects_invalid_buy_stop_direction():
    decision = RiskEngine().evaluate(signal(stop_loss=Decimal("101")), Decimal("10000"))
    assert not decision.approved


def test_rejects_invalid_sell_stop_direction():
    decision = RiskEngine().evaluate(
        signal(side=Side.SELL, stop_loss=Decimal("99")), Decimal("10000")
    )
    assert not decision.approved


def test_accepts_valid_sell_stop_direction():
    decision = RiskEngine().evaluate(
        signal(side=Side.SELL, stop_loss=Decimal("101")), Decimal("10000")
    )
    assert decision.approved


def test_rejects_daily_loss_breach():
    decision = RiskEngine().evaluate(
        signal(), Decimal("10000"), realized_daily_pnl=Decimal("-300")
    )
    assert not decision.approved


def test_flat_is_safe_noop():
    decision = RiskEngine().evaluate(signal(side=Side.FLAT), Decimal("10000"))
    assert decision.approved
    assert decision.max_quantity == 0


def test_limits_are_validated_with_slots():
    with pytest.raises(ValueError):
        RiskLimits(max_trade_risk_fraction=Decimal("1.1"))
