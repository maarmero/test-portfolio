"""Section C of TEST_PLAN.md: input validation. The app must reject invalid input with an error."""
import pytest

from helpers import stock
from rebalancer import RebalanceError, rebalance


@pytest.mark.parametrize("total", [105, 95], ids=["adds_up_to_105", "adds_up_to_95"])
@pytest.mark.p1
def test_target_percent_not_adding_up_to_100(total):  # TC-19
    stocks = [stock("A", total - 50, 50, 10), stock("B", 50, 50, 10)]  # Target % adds up to `total`
    with pytest.raises(RebalanceError, match="target % must sum to 100"):
        rebalance(100_000, stocks)


@pytest.mark.parametrize("total", [105, 95], ids=["adds_up_to_105", "adds_up_to_95"])
@pytest.mark.p1
def test_current_percent_not_adding_up_to_100(total):  # TC-20
    stocks = [stock("A", 50, total - 50, 10), stock("B", 50, 50, 10)]  # Current % adds up to `total`
    with pytest.raises(RebalanceError, match="current % must sum to 100"):
        rebalance(100_000, stocks)


@pytest.mark.parametrize("price", [0, -5, "abc", None])  # TC-21, TC-22, TC-23, TC-28
@pytest.mark.p1
def test_invalid_price(price):
    stocks = [stock("A", 50, 50, 10), stock("B", 50, 50, price)]
    with pytest.raises(RebalanceError, match="B price"):
        rebalance(100_000, stocks)


@pytest.mark.parametrize("account_value", [0, -1, None])  # TC-24, TC-28
@pytest.mark.p1
def test_invalid_account_value(account_value):
    with pytest.raises(RebalanceError, match="account value"):
        rebalance(account_value, [stock("A", 50, 50, 10), stock("B", 50, 50, 10)])


@pytest.mark.parametrize(
    "stocks",
    [
        [stock("A", -10, 50, 10), stock("B", 110, 50, 10)],   # Target % is negative
        [stock("A", 50, -10, 10), stock("B", 50, 110, 10)],   # Current % is negative
    ],
    ids=["negative_target", "negative_current"],
)
@pytest.mark.p2
def test_negative_percentage(stocks):  # TC-25
    # Both columns still add up to 100, so only the "not below 0" check can reject these.
    with pytest.raises(RebalanceError, match="must be >= 0"):
        rebalance(100_000, stocks)


@pytest.mark.p2
def test_same_stock_twice():  # TC-26
    stocks = [stock("A", 50, 50, 10), stock("A", 50, 50, 10)]
    with pytest.raises(RebalanceError, match="duplicate"):
        rebalance(100_000, stocks)


@pytest.mark.p2
def test_no_stocks():  # TC-27
    with pytest.raises(RebalanceError, match="at least one stock"):
        rebalance(100_000, [])


@pytest.mark.parametrize("field", ["target_pct", "current_pct"])  # the code's names for Target % and Current %
@pytest.mark.p2
def test_empty_percentage_names_the_field(field):  # TC-28
    values = {"target_pct": 50, "current_pct": 50}
    values[field] = ""
    stocks = [stock("A", values["target_pct"], values["current_pct"], 10), stock("B", 50, 50, 10)]
    with pytest.raises(RebalanceError, match=f"A {field}"):
        rebalance(100_000, stocks)
