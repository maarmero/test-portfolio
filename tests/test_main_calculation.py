"""Section A of MANUAL_TEST_CASES.md: the main calculation (how many shares to buy or sell)."""
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

def test_assessment_example_gives_66_buy_and_45_sell():  # TC-01
    result = rebalance(100_000, assessment_stocks())
    assert result == {"IBM": 66, "MSFT": 0, "ORCL": -45, "AAPL": 0, "HD": 0}


def test_assessment_example_money_in_equals_money_out():  # TC-02
    # 66 shares x $150 = $9,900 spent, 45 shares x $220 = $9,900 received
    result = rebalance(100_000, assessment_stocks())
    assert money_spent_minus_money_received(assessment_stocks(), result) == 0


def test_assessment_example_with_part_shares():  # TC-03
    result = rebalance(100_000, assessment_stocks(), whole_shares=False)
    assert result["IBM"] == Decimal("66.6667")
    assert result["ORCL"] == Decimal("-45.4545")
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


def test_every_stock_appears_in_the_result():
    result = rebalance(100_000, assessment_stocks())
    assert set(result) == {"IBM", "MSFT", "ORCL", "AAPL", "HD"}


# ---- total bought and total sold ---------------------------------------------

def test_assessment_example_total_bought_and_sold():  # TC-13 (a)
    assert total_bought_and_sold(rebalance(100_000, assessment_stocks())) == (66, 45)


def test_total_bought_and_sold_with_several_buys_and_sells():  # TC-13 (b)
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
    "want, have, expected",
    [
        (30, 20, 66),    # have less than we want: buy ($10,000 / $150 = 66.67)
        (20, 30, -66),   # have more than we want: sell
        (20, 20, 0),     # have exactly what we want: do nothing
    ],
)
def test_buy_sell_or_nothing_depending_on_have_vs_want(want, have, expected):  # TC-05, TC-06
    stocks = [stock("A", want, have, 150), stock("B", 100 - want, 100 - have, 1)]
    assert rebalance(100_000, stocks)["A"] == expected


def test_nothing_to_change_gives_all_zeros():  # TC-04
    stocks = [stock(name, 20, 20, 100) for name in "ABCDE"]
    assert set(rebalance(100_000, stocks).values()) == {0}


# ---- other situations --------------------------------------------------------

def test_single_stock_gives_zero():  # TC-07
    assert rebalance(100_000, [stock("A", 100, 100, 50)]) == {"A": 0}


def test_swap_everything():  # TC-08
    stocks = [stock("A", 0, 100, 100), stock("B", 100, 0, 50)]
    assert rebalance(100_000, stocks) == {"A": -1000, "B": 2000}


def test_want_zero_percent_sells_the_whole_holding():  # TC-09
    stocks = [stock("A", 0, 25, 100), stock("B", 100, 75, 100)]
    assert rebalance(100_000, stocks) == {"A": -250, "B": 250}


def test_bigger_account():  # TC-10
    result = rebalance(1_000_000, assessment_stocks())
    assert result["IBM"] == 666 and result["ORCL"] == -454


def test_account_value_with_cents():  # TC-11
    stocks = [stock("A", 50, 40, 10), stock("B", 50, 60, 10)]
    assert rebalance("12345.67", stocks) == {"A": 123, "B": -123}


def test_ten_stocks_with_nothing_to_change():  # TC-12
    stocks = [stock(f"S{i}", 10, 10, 10) for i in range(10)]
    assert set(rebalance(100_000, stocks).values()) == {0}


# ---- ending up on target (the yellow question in the assessment) -------------

def test_part_share_trades_end_on_target():
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks, whole_shares=False)
    for symbol, (points_off, _) in distance_from_target_after_trades(stocks, trades).items():
        # shares are rounded to 4 decimals, so we are off by about 0.00001 points at most
        assert abs(points_off) < Decimal("0.001"), symbol


def test_whole_share_trades_end_less_than_one_share_from_target():
    stocks = assessment_stocks()
    trades = rebalance(100_000, stocks)
    off_by = distance_from_target_after_trades(stocks, trades)
    for s in stocks:
        _, dollars_off = off_by[s.symbol]
        assert abs(dollars_off) < s.price, s.symbol
