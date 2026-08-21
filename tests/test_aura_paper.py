from decimal import Decimal

import pytest

from aura.models import Side
from aura.paper import PaperBroker


def test_buy_and_sell_round_trip():
    broker = PaperBroker(Decimal("1000"))
    buy = broker.submit_market_order("AAPL", Side.BUY, Decimal("2"), Decimal("100"))
    assert buy.status == "FILLED"
    assert broker.cash == Decimal("800")
    assert broker.positions["AAPL"] == Decimal("2")

    sell = broker.submit_market_order("AAPL", Side.SELL, Decimal("2"), Decimal("110"))
    assert sell.status == "FILLED"
    assert broker.cash == Decimal("1020")
    assert broker.positions["AAPL"] == Decimal("0")


def test_short_selling_is_disabled():
    broker = PaperBroker(Decimal("1000"))
    with pytest.raises(ValueError, match="short selling"):
        broker.submit_market_order("AAPL", Side.SELL, Decimal("1"), Decimal("100"))
