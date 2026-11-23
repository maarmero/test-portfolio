"""Section D of MANUAL_TEST_CASES.md: extra checks (order of rows, very big and very small numbers)."""
from decimal import Decimal

from helpers import assessment_stocks, stock
from rebalancer import rebalance


def test_order_of_rows_does_not_matter():  # TC-40
    normal_order = rebalance(100_000, assessment_stocks())
    reversed_order = rebalance(100_000, list(reversed(assessment_stocks())))
    assert normal_order == reversed_order


def test_running_again_after_trading_needs_almost_nothing():  # TC-41
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks)

    # Work out each stock's new Have % after doing the trades.
    new_have = {
        s.symbol: (Decimal(s.current_pct) / 100 * 100_000 + trades[s.symbol] * s.price) / 1000
        for s in stocks
    }
    # A little money is left over from rounding, so scale the Have % back up to add to 100.
    scale = 100 / sum(new_have.values())
    after_trading = [stock(s.symbol, s.target_pct, new_have[s.symbol] * scale, s.price) for s in stocks]

    second_run = rebalance(100_000, after_trading)
    assert all(abs(shares) <= 1 for shares in second_run.values())


def test_huge_account():  # TC-42
    result = rebalance(10**12, assessment_stocks())
    # 10% of $1,000,000,000,000 is $100,000,000,000. Divide by the price, round down.
    assert result["IBM"] == 666_666_666
    assert result["ORCL"] == -454_545_454
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


def test_tiny_percentages_are_exact():  # TC-43
    stocks = [stock("A", 0.01, 0.02, 1), stock("B", 99.99, 99.98, 1)]
    # 0.01% of $100,000 is exactly $10, so exactly 10 shares at $1 each
    assert rebalance(100_000, stocks) == {"A": -10, "B": 10}


def test_percentages_and_prices_with_decimals():  # TC-43
    stocks = [stock("A", "33.33", "33.34", "10.50"), stock("B", "66.67", "66.66", "20.25")]
    result = rebalance(100_000, stocks)
    assert result["A"] == 0 and result["B"] == 0  # only about $10 to trade, less than one share


def test_same_input_gives_the_same_answer_every_time():  # TC-44
    first = rebalance(100_000, assessment_stocks())
    for _ in range(10):
        assert rebalance(100_000, assessment_stocks()) == first
