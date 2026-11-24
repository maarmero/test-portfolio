"""Section B of TEST_PLAN.md: rounding (66.67 shares must become 66)."""
from decimal import Decimal

import pytest

from helpers import assessment_stocks, stock
from rebalancer import rebalance


@pytest.mark.parametrize(
    "price, expected",
    [
        (150, 66),      # TC-20: $10,000 / 150 = 66.67, rounds down to 66, not 67
        (100, 100),     # TC-23: divides evenly
        (3000, 3),      # 3.33 rounds down to 3
        (20_000, 0),    # TC-22: only half a share, so no trade
    ],
)
def test_buying_rounds_down(price, expected):  # TC-20, TC-22, TC-23
    # A needs $10,000 more. B is only there to make the percentages add up to 100.
    stocks = [stock("A", 20, 10, price), stock("B", 80, 90, 1)]
    assert rebalance(100_000, stocks)["A"] == expected


def test_selling_rounds_down_towards_zero():  # TC-21
    # A has $10,000 too much. 66.67 becomes -66, not -67.
    stocks = [stock("A", 10, 20, 150), stock("B", 90, 80, 1)]
    assert rebalance(100_000, stocks)["A"] == -66


def test_never_trade_more_than_needed():  # TC-24
    for symbol, shares in rebalance(100_000, assessment_stocks()).items():
        s = next(x for x in assessment_stocks() if x.symbol == symbol)
        money_needed = (Decimal(s.target_pct) - Decimal(s.current_pct)) / 100 * 100_000
        assert abs(shares * s.price) <= abs(money_needed)
