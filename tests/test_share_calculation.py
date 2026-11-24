"""Section A of TEST_PLAN.md: share calculation (how many shares to buy or sell)."""
from decimal import Decimal

import pytest

from helpers import (
    assessment_stocks,
    dollars_off_target_after_trades,
    money_needed,
    money_spent_minus_money_received,
    stock,
    total_bought_and_sold,
)
from rebalancer import rebalance


# ---- the assessment example --------------------------------------------------

@pytest.mark.p1
def test_reference_example_result():  # TC-01, TC-02, TC-13 (a)
    stocks = assessment_stocks()
    result = rebalance(100_000, stocks)
    assert result == {"IBM": 66, "MSFT": 0, "ORCL": -45, "AAPL": 0, "HD": 0}
    # TC-13 (a): 66 shares bought and 45 sold in total
    assert total_bought_and_sold(result) == (66, 45)
    # TC-02: 66 x $150 = $9,900 spent, 45 x $220 = $9,900 received
    assert money_spent_minus_money_received(stocks, result) == 0


@pytest.mark.p2
def test_part_shares_are_kept_to_four_decimals():  # TC-03
    result = rebalance(100_000, assessment_stocks(), whole_shares=False)
    assert result["IBM"] == Decimal("66.6667")
    assert result["ORCL"] == Decimal("-45.4545")
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


# ---- total bought and total sold ---------------------------------------------

SEVERAL_BUYS_AND_SELLS = [
    stock("A", 40, 30, 100),  # need $10,000 more: 10,000 / 100 = buy 100
    stock("B", 30, 20, 50),   # need $10,000 more: 10,000 / 50  = buy 200
    stock("C", 10, 25, 200),  # have $15,000 too much: 15,000 / 200 = sell 75
    stock("D", 20, 25, 100),  # have $5,000 too much: 5,000 / 100 = sell 50
]


@pytest.mark.p1
def test_totals_with_several_buys_and_sells():  # TC-13 (b)
    result = rebalance(100_000, SEVERAL_BUYS_AND_SELLS)
    assert result == {"A": 100, "B": 200, "C": -75, "D": -50}
    assert total_bought_and_sold(result) == (300, 125)


# ---- nothing to change -------------------------------------------------------

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
    "account_value, expected",
    [
        # TC-10
        (1_000_000, {"IBM": 666, "MSFT": 0, "ORCL": -454, "AAPL": 0, "HD": 0}),
        # TC-42: $1,000,000,000,000. 10% is $100,000,000,000, divided by the price
        (10**12, {"IBM": 666_666_666, "MSFT": 0, "ORCL": -454_545_454, "AAPL": 0, "HD": 0}),
    ],
    ids=["one_million", "one_trillion"],
)
@pytest.mark.p2
def test_large_account_values(account_value, expected):  # TC-10, TC-42
    assert rebalance(account_value, assessment_stocks()) == expected


@pytest.mark.p3
def test_account_value_with_cents():  # TC-11
    stocks = [stock("A", 50, 40, "1234.55"), stock("B", 50, 60, 10)]
    # A: 10% of $12,345.67 is $1,234.567, which is just over one share at $1,234.55, so buy 1.
    #    Without the cents, 10% of $12,345 is $1,234.50, which is under one share, so it would be 0.
    # B: 10% is $1,234.567 / $10 = 123.46, so sell 123 (the cents do not change this one).
    assert rebalance("12345.67", stocks) == {"A": 1, "B": -123}


# ---- ending up on target (the assessment asks: what gets every stock to zero variance?) ----

PORTFOLIOS = {
    "assessment example": assessment_stocks(),
    "several buys and sells": SEVERAL_BUYS_AND_SELLS,
    "one buy at an uneven price": [stock("A", 20, 10, 150), stock("B", 80, 90, 1)],
    "swap everything": [stock("A", 0, 100, 100), stock("B", 100, 0, 50)],
    "odd prices": [stock("A", 33, 20, 7), stock("B", 33, 50, 13), stock("C", 34, 30, 29)],
}


@pytest.mark.parametrize("stocks", PORTFOLIOS.values(), ids=PORTFOLIOS.keys())
@pytest.mark.p1
def test_trades_never_overshoot_and_end_close_to_target(stocks):  # TC-14, TC-15, TC-24
    account_value = 100_000

    whole = rebalance(account_value, stocks)
    off_by = dollars_off_target_after_trades(stocks, whole, account_value)
    for s in stocks:
        # TC-24: never trade more than needed
        assert abs(whole[s.symbol] * s.price) <= abs(money_needed(s, account_value)), s.symbol
        # TC-15: whole shares end less than the price of one share away from the Target %
        assert abs(off_by[s.symbol]) < s.price, s.symbol

    # TC-14: part shares are rounded to 4 decimals, so each stock ends within half of 0.0001 shares
    part = rebalance(account_value, stocks, whole_shares=False)
    off_by_part = dollars_off_target_after_trades(stocks, part, account_value)
    for s in stocks:
        assert abs(off_by_part[s.symbol]) <= s.price * Decimal("0.00005"), s.symbol
