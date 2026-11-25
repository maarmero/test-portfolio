"""Section B of TEST_PLAN.md: rounding (66.67 shares must become 66)."""
import pytest

from helpers import stock
from rebalancer import rebalance


@pytest.mark.parametrize(
    "price, expected",
    [
        (150, 66),      # TC-15: $10,000 / 150 = 66.67, rounds down to 66, not 67
        (100, 100),     # TC-18: divides evenly
        (20_000, 0),    # TC-17: only half a share, so no trade
    ],
    ids=["rounds_down", "divides_evenly", "less_than_one_share"],
)
@pytest.mark.p1
def test_buying_rounds_down(price, expected):  # TC-05, TC-15, TC-17, TC-18
    # A needs $10,000 more. B is only there to make the percentages add up to 100.
    stocks = [stock("A", 20, 10, price), stock("B", 80, 90, 1)]
    assert rebalance(100_000, stocks)["A"] == expected


@pytest.mark.p1
def test_selling_rounds_down_towards_zero():  # TC-05, TC-16
    # A has $10,000 too much. 66.67 becomes -66, not -67.
    stocks = [stock("A", 10, 20, 150), stock("B", 90, 80, 1)]
    assert rebalance(100_000, stocks)["A"] == -66
