"""Shared setup for the tests.

Words used in the tests:
  want  = the share of the account you want in a stock (called target_pct in the code)
  have  = the share of the account that is in the stock now (called current_pct in the code)
  A result of +66 means buy 66 shares, -45 means sell 45 shares, 0 means do nothing.
"""
from decimal import Decimal

from rebalancer import Position


def stock(symbol, want, have, price):
    """One stock: its name, Want %, Have % and the price of one share."""
    return Position(symbol, want, have, price)


def assessment_stocks():
    """The five stocks from the assessment (account worth $100,000)."""
    return [
        stock("IBM", 20, 10, 150),
        stock("MSFT", 20, 20, 90),
        stock("ORCL", 20, 30, 220),
        stock("AAPL", 20, 20, 450),
        stock("HD", 20, 20, 70),
    ]


def money_spent_minus_money_received(stocks, result):
    """Money spent on buying minus money received from selling. 0 means they cancel out."""
    prices = {s.symbol: Decimal(str(s.price)) for s in stocks}
    return sum(result[symbol] * prices[symbol] for symbol in result)


def total_bought_and_sold(result):
    """Add up all the buys and all the sells. Returns (shares bought, shares sold)."""
    bought = sum(shares for shares in result.values() if shares > 0)
    sold = -sum(shares for shares in result.values() if shares < 0)
    return bought, sold


def distance_from_target_after_trades(stocks, trades, account_value=100_000):
    """After doing the trades, how far is each stock from what we want?

    Returns {symbol: (percentage points off, dollars off)}. 0 means exactly on target.
    """
    out = {}
    for s in stocks:
        value_now = Decimal(s.current_pct) / 100 * account_value + trades[s.symbol] * s.price
        value_wanted = Decimal(s.target_pct) / 100 * account_value
        dollars_off = value_now - value_wanted
        out[s.symbol] = (dollars_off / account_value * 100, dollars_off)
    return out
