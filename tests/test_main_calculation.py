"""Section A of TEST_PLAN.md: the main calculation (how many shares to buy or sell)."""
from decimal import Decimal

import pytest

from helpers import (
    assessment_stocks,
    distance_from_target_after_trades,
    money_spent_minus_money_received,
    stock,
    total_bought_and_sold,
)
from rebalancer import rebalance


# ---- the assessment example --------------------------------------------------

@pytest.mark.p1
def test_reference_example_buys_and_sells_the_expected_shares():  # TC-01
    result = rebalance(100_000, assessment_stocks())
    assert result == {"IBM": 66, "MSFT": 0, "ORCL": -45, "AAPL": 0, "HD": 0}


@pytest.mark.p1
def test_money_spent_equals_money_received():  # TC-02
    # 66 shares x $150 = $9,900 spent, 45 shares x $220 = $9,900 received
    result = rebalance(100_000, assessment_stocks())
    assert money_spent_minus_money_received(assessment_stocks(), result) == 0


@pytest.mark.p2
def test_part_shares_are_kept_to_four_decimals():  # TC-03
    result = rebalance(100_000, assessment_stocks(), whole_shares=False)
    assert result["IBM"] == Decimal("66.6667")
    assert result["ORCL"] == Decimal("-45.4545")
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


# ---- total bought and total sold ---------------------------------------------

@pytest.mark.p1
def test_total_bought_and_sold():  # TC-13 (a)
    assert total_bought_and_sold(rebalance(100_000, assessment_stocks())) == (66, 45)


@pytest.mark.p1
def test_totals_with_several_buys_and_sells():  # TC-13 (b)
    stocks = [
        stock("A", 40, 30, 100),  # need $10,000 more: 10,000 / 100 = buy 100
        stock("B", 30, 20, 50),   # need $10,000 more: 10,000 / 50  = buy 200
        stock("C", 10, 25, 200),  # have $15,000 too much: 15,000 / 200 = sell 75
        stock("D", 20, 25, 100),  # have $5,000 too much: 5,000 / 100 = sell 50
    ]
    result = rebalance(100_000, stocks)
    assert result == {"A": 100, "B": 200, "C": -75, "D": -50}
    assert total_bought_and_sold(result) == (300, 125)


# ---- buy, sell or do nothing -------------------------------------------------

@pytest.mark.parametrize(
    "target, current, expected",
    [
        (30, 20, 66),    # current below target: buy ($10,000 / $150 = 66.67)
        (20, 30, -66),   # current above target: sell
        (20, 20, 0),     # current equals target: do nothing
    ],
)
@pytest.mark.p1
def test_buy_sell_or_nothing_depending_on_current_vs_target(target, current, expected):  # TC-06
    stocks = [stock("A", target, current, 150), stock("B", 100 - target, 100 - current, 1)]
    assert rebalance(100_000, stocks)["A"] == expected


@pytest.mark.parametrize("how_many_stocks", [1, 5, 10])
@pytest.mark.p1
def test_nothing_to_change_gives_all_zeros(how_many_stocks):  # TC-04, TC-07, TC-12
    share = 100 // how_many_stocks  # every stock has the same Target % and Current %
    stocks = [stock(f"S{i}", share, share, 100) for i in range(how_many_stocks)]
    assert set(rebalance(100_000, stocks).values()) == {0}


# ---- other situations --------------------------------------------------------

@pytest.mark.parametrize(
    "stocks, expected",
    [
        ([stock("A", 0, 100, 100), stock("B", 100, 0, 50)], {"A": -1000, "B": 2000}),  # TC-08: swap everything
        ([stock("A", 0, 25, 100), stock("B", 100, 75, 100)], {"A": -250, "B": 250}),   # TC-09: one stock to 0%
    ],
)
@pytest.mark.p2
def test_target_zero_percent_sells_the_whole_holding(stocks, expected):  # TC-08, TC-09
    assert rebalance(100_000, stocks) == expected


@pytest.mark.parametrize(
    "account_value, ibm, orcl",
    [
        (1_000_000, 666, -454),                # TC-10
        (10**12, 666_666_666, -454_545_454),   # TC-42: $1,000,000,000,000. 10% is $100,000,000,000, divided by the price
    ],
)
@pytest.mark.p2
def test_large_account_values(account_value, ibm, orcl):  # TC-10, TC-42
    result = rebalance(account_value, assessment_stocks())
    assert result["IBM"] == ibm and result["ORCL"] == orcl
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


@pytest.mark.p3
def test_account_value_with_cents():  # TC-11
    stocks = [stock("A", 50, 40, 10), stock("B", 50, 60, 10)]
    assert rebalance("12345.67", stocks) == {"A": 123, "B": -123}


# ---- ending up on target (the yellow question in the assessment) -------------

@pytest.mark.p1
def test_part_share_trades_end_on_target():  # TC-14
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks, whole_shares=False)
    for symbol, (points_off, _) in distance_from_target_after_trades(stocks, trades).items():
        # shares are rounded to 4 decimals, so we are off by about 0.00001 points at most
        assert abs(points_off) < Decimal("0.001"), symbol


@pytest.mark.p1
def test_whole_share_trades_end_less_than_one_share_from_target():  # TC-15
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks)
    off_by = distance_from_target_after_trades(stocks, trades)
    for s in stocks:
        _, dollars_off = off_by[s.symbol]
        assert abs(dollars_off) < s.price, s.symbol
