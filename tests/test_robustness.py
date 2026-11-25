"""Section D of TEST_PLAN.md: robustness (order of rows, running again after trading, decimal inputs)."""
from decimal import Decimal

import pytest

from helpers import assessment_stocks, stock
from rebalancer import rebalance


@pytest.mark.p2
def test_order_of_rows_does_not_matter():  # TC-30
    normal_order = rebalance(100_000, assessment_stocks())
    reversed_order = rebalance(100_000, list(reversed(assessment_stocks())))
    assert normal_order == reversed_order


@pytest.mark.p2
def test_second_run_after_trading_is_within_one_share():  # TC-31
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks)

    # Work out each stock's new Current % after doing the trades.
    new_current = {
        s.symbol: (Decimal(s.current_pct) / 100 * 100_000 + trades[s.symbol] * s.price) / 1000
        for s in stocks
    }
    # A little money is left over from rounding, so scale the Current % back up to add to 100.
    scale = 100 / sum(new_current.values())
    after_trading = [stock(s.symbol, s.target_pct, new_current[s.symbol] * scale, s.price) for s in stocks]

    second_run = rebalance(100_000, after_trading)
    assert all(abs(shares) <= 1 for shares in second_run.values())


@pytest.mark.p3
def test_tiny_percentages_are_exact():  # TC-33
    stocks = [stock("A", 0.01, 0.02, 1), stock("B", 99.99, 99.98, 1)]
    # 0.01% of $100,000 is exactly $10, so exactly 10 shares at $1 each
    assert rebalance(100_000, stocks) == {"A": -10, "B": 10}


@pytest.mark.p3
def test_decimal_inputs_are_used_exactly():  # TC-33
    stocks = [stock("A", "33.33", "33.30", "10.50"), stock("B", "66.67", "66.70", "20.25")]
    # A needs 0.03% = $30 more: 30 / 10.50 = 2.86, so buy 2.  B has $30 too much: 30 / 20.25 = 1.48, so sell 1.
    # With the decimals cut off, A would be 3 (30 / 10), so this checks the decimals are used.
    assert rebalance(100_000, stocks) == {"A": 2, "B": -1}
