"""Section B of TEST_PLAN.md: rounding (66.67 shares must become 66)."""
import pytest

from helpers import stock
from rebalancer import rebalance


@pytest.mark.parametrize(
    "target, current, price, expected",
    [
        (20, 10, 150, 66),         # TC-14: buy. $10,000 / 150 = 66.67, rounds down to 66, not 67
        (20, 10, 100, 100),        # TC-17: buy. Divides evenly
        (20, 10, 20_000, 0),       # TC-16: buy. Only half a share, so no trade
        (10, 20, 150, -66),        # TC-15: sell. -66.67 rounds towards zero to -66, not -67
        (10, 20, 20_000, 0),       # TC-16: sell. Only half a share, so no trade
    ],
    ids=[
        "buy_rounds_down",
        "buy_divides_evenly",
        "buy_less_than_one_share",
        "sell_rounds_towards_zero",
        "sell_less_than_one_share",
    ],
)
@pytest.mark.p1
def test_whole_shares_round_towards_zero(target, current, price, expected):  # TC-05, TC-14, TC-15, TC-16, TC-17
    # A needs $10,000 more (buy) or has $10,000 too much (sell).
    # B is only there to make both columns add up to 100.
    stocks = [stock("A", target, current, price), stock("B", 100 - target, 100 - current, 1)]
    assert rebalance(100_000, stocks)["A"] == expected
