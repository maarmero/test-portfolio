"""Section D of TEST_PLAN.md: robustness (order of rows, running again after trading, decimal inputs)."""
from decimal import Decimal

import pytest

from helpers import PORTFOLIOS, assessment_stocks, stock
from rebalancer import rebalance


@pytest.mark.parametrize("stocks", PORTFOLIOS.values(), ids=PORTFOLIOS.keys())
@pytest.mark.p2
def test_order_of_rows_does_not_matter(stocks):  # TC-29
    assert rebalance(100_000, stocks) == rebalance(100_000, list(reversed(stocks)))


@pytest.mark.p2
def test_second_run_after_trading_needs_no_more_trades():  # TC-30
    account_value = 100_000
    stocks = assessment_stocks()
    trades = rebalance(account_value, stocks)

    # Do the trades: each stock's new Current % is the money it holds now, as a % of the account.
    # Money spent equals money received for this example (TC-02), so the new Current % still adds up to 100.
    after_trading = [
        stock(
            s.symbol,
            s.target_pct,
            (Decimal(s.current_pct) / 100 * account_value + trades[s.symbol] * s.price) / account_value * 100,
            s.price,
        )
        for s in stocks
    ]

    assert set(rebalance(account_value, after_trading).values()) == {0}


@pytest.mark.p3
def test_tiny_percentages_are_exact():  # TC-32
    stocks = [stock("A", 0.01, 0.02, 1), stock("B", 99.99, 99.98, 1)]
    # 0.01% of $100,000 is exactly $10, so exactly 10 shares at $1 each
    assert rebalance(100_000, stocks) == {"A": -10, "B": 10}


@pytest.mark.p3
def test_decimal_inputs_are_used_exactly():  # TC-32
    stocks = [stock("A", "33.33", "33.30", "10.50"), stock("B", "66.67", "66.70", "20.25")]
    # A needs 0.03% = $30 more: 30 / 10.50 = 2.86, so buy 2.  B has $30 too much: 30 / 20.25 = 1.48, so sell 1.
    # With the decimals cut off, A would be 3 (30 / 10), so this checks the decimals are used.
    assert rebalance(100_000, stocks) == {"A": 2, "B": -1}
