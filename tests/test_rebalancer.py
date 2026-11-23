from decimal import Decimal

import pytest

from rebalancer import Position, RebalanceError, rebalance

P = Position


def assessment_portfolio():
    return [
        P("IBM", 20, 10, 150),
        P("MSFT", 20, 20, 90),
        P("ORCL", 20, 30, 220),
        P("AAPL", 20, 20, 450),
        P("HD", 20, 20, 70),
    ]


def net_cash(positions, result):
    """Cash spent on buys minus cash raised from sells (>0 means cash needed)."""
    prices = {p.symbol: Decimal(str(p.price)) for p in positions}
    return sum(result[s] * prices[s] for s in result)


# ---- the assessment scenario -------------------------------------------------

def test_assessment_whole_shares():
    result = rebalance(100_000, assessment_portfolio())
    assert result == {
        "IBM": 66, "MSFT": 0, "ORCL": -45, "AAPL": 0, "HD": 0,
    }


def test_assessment_fractional_shares():
    result = rebalance(100_000, assessment_portfolio(), whole_shares=False)
    assert result["IBM"] == Decimal("66.6667")
    assert result["ORCL"] == Decimal("-45.4545")
    assert result["MSFT"] == result["AAPL"] == result["HD"] == 0


def test_assessment_is_cash_neutral_with_whole_shares():
    # 66 * 150 = 9,900 bought; 45 * 220 = 9,900 sold
    assert net_cash(assessment_portfolio(), rebalance(100_000, assessment_portfolio())) == 0


# ---- sign convention: negative variance = buy, positive = sell --------------

@pytest.mark.parametrize(
    "target, current, expected",
    [
        (30, 20, 66),    # under-weight: buy  (10,000 / 150)
        (20, 30, -66),   # over-weight: sell
        (20, 20, 0),     # on target: nothing
    ],
)
def test_direction(target, current, expected):
    positions = [P("A", target, current, 150), P("B", 100 - target, 100 - current, 1)]
    assert rebalance(100_000, positions)["A"] == expected


# ---- rounding ----------------------------------------------------------------

@pytest.mark.parametrize(
    "price, expected",
    [
        (150, 66),      # 66.67 -> 66 (toward zero, not 67)
        (100, 100),     # exact
        (3000, 3),      # 3.33 -> 3
        (20_000, 0),    # < 1 share -> no trade
    ],
)
def test_buy_rounds_down(price, expected):
    positions = [P("A", 20, 10, price), P("B", 80, 90, 1)]
    assert rebalance(100_000, positions)["A"] == expected


def test_sell_rounds_toward_zero_not_floor():
    positions = [P("A", 10, 20, 150), P("B", 90, 80, 1)]
    assert rebalance(100_000, positions)["A"] == -66  # not -67


def test_never_overshoots_target():
    for pos, shares in rebalance(100_000, assessment_portfolio()).items():
        p = next(x for x in assessment_portfolio() if x.symbol == pos)
        wanted = (Decimal(p.target_pct) - Decimal(p.current_pct)) / 100 * 100_000
        assert abs(shares * p.price) <= abs(wanted)


# ---- scenarios ---------------------------------------------------------------

def test_already_balanced_returns_all_zero():
    positions = [P(s, 20, 20, 100) for s in "ABCDE"]
    assert set(rebalance(100_000, positions).values()) == {0}


def test_single_security_target_100():
    assert rebalance(100_000, [P("A", 100, 100, 50)]) == {"A": 0}


def test_full_rotation_sell_all_buy_all():
    positions = [P("A", 0, 100, 100), P("B", 100, 0, 50)]
    assert rebalance(100_000, positions) == {"A": -1000, "B": 2000}


def test_target_zero_for_one_security_sells_entire_holding():
    positions = [P("A", 0, 25, 100), P("B", 100, 75, 100)]
    assert rebalance(100_000, positions) == {"A": -250, "B": 250}


def test_different_account_size_scales_linearly():
    result = rebalance(1_000_000, assessment_portfolio())
    assert result["IBM"] == 666 and result["ORCL"] == -454


def test_non_round_total_assets():
    result = rebalance("12345.67", [P("A", 50, 40, 10), P("B", 50, 60, 10)])
    assert result == {"A": 123, "B": -123}


def test_decimal_percentages_and_prices():
    positions = [P("A", "33.33", "33.34", "10.50"), P("B", "66.67", "66.66", "20.25")]
    result = rebalance(100_000, positions)
    assert result["A"] == 0 and result["B"] == 0  # +/-10 USD < 1 share


def test_many_securities():
    n = 10
    positions = [P(f"S{i}", 10, 10, 10) for i in range(n)]
    assert set(rebalance(100_000, positions).values()) == {0}


def test_result_contains_every_input_symbol():
    assert set(rebalance(100_000, assessment_portfolio())) == {"IBM", "MSFT", "ORCL", "AAPL", "HD"}


def test_input_order_does_not_change_result():
    forward = rebalance(100_000, assessment_portfolio())
    backward = rebalance(100_000, list(reversed(assessment_portfolio())))
    assert forward == backward


def test_idempotent_after_applying_trades():
    """Applying the trades and re-running should give ~no further trades."""
    positions = assessment_portfolio()
    trades = rebalance(100_000, positions)
    new_pct = [
        P(p.symbol, p.target_pct,
          (Decimal(p.current_pct) / 100 * 100_000 + trades[p.symbol] * p.price) / 1000, p.price)
        for p in positions
    ]
    # whole-share rounding leaves < 1 share of drift, so scale pcts back to 100
    total_pct = sum(Decimal(p.current_pct) for p in new_pct)
    normalised = [P(p.symbol, p.target_pct, Decimal(p.current_pct) * 100 / total_pct, p.price)
                  for p in new_pct]
    again = rebalance(100_000, normalised)
    assert all(abs(v) <= 1 for v in again.values())


# ---- the yellow question: zero target variance after trading ----------------

def variance_after_trades(positions, trades, total=100_000):
    """Return {symbol: (variance in % points, residual dollars vs target)}."""
    out = {}
    for p in positions:
        value = Decimal(p.current_pct) / 100 * total + trades[p.symbol] * p.price
        target_value = Decimal(p.target_pct) / 100 * total
        out[p.symbol] = ((value - target_value) / total * 100, value - target_value)
    return out


def test_fractional_trades_reach_zero_variance():
    positions = assessment_portfolio()
    trades = rebalance(100_000, positions, whole_shares=False)
    for symbol, (variance, _) in variance_after_trades(positions, trades).items():
        # 4-decimal share rounding leaves at most ~0.00001 percentage points
        assert abs(variance) < Decimal("0.001"), symbol


def test_whole_share_trades_leave_less_than_one_share_of_variance():
    positions = assessment_portfolio()
    trades = rebalance(100_000, positions)
    for p in positions:
        _, residual_dollars = variance_after_trades(positions, trades)[p.symbol]
        assert abs(residual_dollars) < p.price, p.symbol


# ---- invalid input -----------------------------------------------------------

@pytest.mark.parametrize("total", [0, -1, "abc", None])
def test_invalid_total_assets(total):
    with pytest.raises(RebalanceError):
        rebalance(total, assessment_portfolio())


def test_target_not_100():
    positions = assessment_portfolio()
    positions[0] = P("IBM", 25, 10, 150)
    with pytest.raises(RebalanceError, match="target"):
        rebalance(100_000, positions)


def test_current_not_100():
    positions = assessment_portfolio()
    positions[0] = P("IBM", 20, 15, 150)
    with pytest.raises(RebalanceError, match="current"):
        rebalance(100_000, positions)


@pytest.mark.parametrize("price", [0, -5, "x", None])
def test_invalid_price(price):
    positions = assessment_portfolio()
    positions[1] = P("MSFT", 20, 20, price)
    with pytest.raises(RebalanceError):
        rebalance(100_000, positions)


def test_negative_percentage():
    positions = [P("A", -10, 50, 10), P("B", 110, 50, 10)]
    with pytest.raises(RebalanceError):
        rebalance(100_000, positions)


def test_duplicate_symbol():
    positions = [P("A", 50, 50, 10), P("A", 50, 50, 10)]
    with pytest.raises(RebalanceError, match="duplicate"):
        rebalance(100_000, positions)


def test_empty_portfolio():
    with pytest.raises(RebalanceError):
        rebalance(100_000, [])
