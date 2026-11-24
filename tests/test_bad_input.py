"""Section C of TEST_PLAN.md: bad input. The app must reject mistakes with an error."""
import pytest

from helpers import assessment_stocks, stock
from rebalancer import RebalanceError, rebalance


@pytest.mark.p1
def test_target_percent_not_adding_up_to_100():  # TC-30
    stocks = assessment_stocks()
    stocks[0] = stock("IBM", 25, 10, 150)  # Target % now adds up to 105
    with pytest.raises(RebalanceError, match="target"):
        rebalance(100_000, stocks)


@pytest.mark.p1
def test_current_percent_not_adding_up_to_100():  # TC-31
    stocks = assessment_stocks()
    stocks[0] = stock("IBM", 20, 15, 150)  # Current % now adds up to 105
    with pytest.raises(RebalanceError, match="current"):
        rebalance(100_000, stocks)


@pytest.mark.parametrize("price", [0, -5, "x", None])  # TC-32, TC-33, TC-34, TC-39
@pytest.mark.p1
def test_bad_price(price):
    stocks = assessment_stocks()
    stocks[1] = stock("MSFT", 20, 20, price)
    with pytest.raises(RebalanceError):
        rebalance(100_000, stocks)


@pytest.mark.parametrize("account_value", [0, -1, "abc", None])  # TC-35, TC-39
@pytest.mark.p1
def test_bad_account_value(account_value):
    with pytest.raises(RebalanceError):
        rebalance(account_value, assessment_stocks())


@pytest.mark.p2
def test_negative_percentage():  # TC-36
    stocks = [stock("A", -10, 50, 10), stock("B", 110, 50, 10)]
    with pytest.raises(RebalanceError):
        rebalance(100_000, stocks)


@pytest.mark.p2
def test_same_stock_twice():  # TC-37
    stocks = [stock("A", 50, 50, 10), stock("A", 50, 50, 10)]
    with pytest.raises(RebalanceError, match="duplicate"):
        rebalance(100_000, stocks)


@pytest.mark.p2
def test_no_stocks():  # TC-38
    with pytest.raises(RebalanceError, match="at least one stock"):
        rebalance(100_000, [])


@pytest.mark.parametrize("field", ["target_pct", "current_pct"])  # the code's names for Target % and Current %
@pytest.mark.parametrize("empty_value", ["", None])
@pytest.mark.p2
def test_empty_percentage_names_the_field(field, empty_value):  # TC-39
    values = {"target_pct": 20, "current_pct": 10}
    values[field] = empty_value
    stocks = assessment_stocks()
    stocks[0] = stock("IBM", values["target_pct"], values["current_pct"], 150)
    with pytest.raises(RebalanceError, match=f"IBM {field}"):
        rebalance(100_000, stocks)
