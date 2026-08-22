from decimal import Decimal

from aura.live.gateway import HumanConfirmedGateway
from aura.live.models import Confirmation, LiveOrderIntent, LiveSide


class FakeBroker:
    def __init__(self):
        self.submissions = []

    def submit(self, intent):
        self.submissions.append(intent)
        return "paper-test-order"


def intent():
    return LiveOrderIntent(
        intent_id="intent-001",
        symbol="XAUUSD",
        side=LiveSide.BUY,
        quantity=Decimal("0.01"),
        limit_price=Decimal("3400"),
        stop_loss=Decimal("3380"),
        rationale="test",
        risk_amount=Decimal("10"),
        source_run_id="run-001",
    )


def test_disabled_gateway_never_submits():
    broker = FakeBroker()
    gateway = HumanConfirmedGateway(broker, Decimal("100"), enabled=False)
    result = gateway.execute(intent(), Confirmation("intent-001", "YES", "human", intent().created_at))
    assert not result.accepted
    assert broker.submissions == []


def test_confirmation_required_before_submission():
    broker = FakeBroker()
    gateway = HumanConfirmedGateway(broker, Decimal("100"), enabled=True)
    prepared = gateway.prepare(intent())
    assert prepared["confirmation_required"] == "true"
    assert broker.submissions == []


def test_matching_confirmation_allows_submission():
    broker = FakeBroker()
    gateway = HumanConfirmedGateway(broker, Decimal("100"), enabled=True)
    i = intent()
    result = gateway.execute(i, Confirmation(i.intent_id, "YES", "operator", i.created_at))
    assert result.accepted
    assert result.broker_order_id == "paper-test-order"
    assert len(broker.submissions) == 1


def test_wrong_intent_confirmation_is_rejected():
    broker = FakeBroker()
    gateway = HumanConfirmedGateway(broker, Decimal("100"), enabled=True)
    i = intent()
    result = gateway.execute(i, Confirmation("other-intent", "YES", "operator", i.created_at))
    assert not result.accepted
    assert broker.submissions == []
