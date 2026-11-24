"""Shared setup for the tests.

Words used in the tests:
  Target % = the share of the account you want in a stock (target_pct in the code)
  Current % = the share of the account that is in the stock now (current_pct in the code)
  A result of +66 means buy 66 shares, -45 means sell 45 shares, 0 means do nothing.
"""
from decimal import Decimal

from rebalancer import Position


def stock(symbol, target, current, price):
    """One stock: its name, Target %, Current % and the price of one share."""
    return Position(symbol, target, current, price)


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


def money_needed(s, account_value):
    """Dollars to buy (+) or sell (-) to take one stock from its Current % to its Target %."""
    return (Decimal(str(s.target_pct)) - Decimal(str(s.current_pct))) / 100 * Decimal(str(account_value))


def dollars_off_target_after_trades(stocks, trades, account_value):
    """After doing the trades, how many dollars is each stock away from its Target %?

    Returns {symbol: dollars}. 0 means exactly on target.
    """
    return {
        s.symbol: trades[s.symbol] * Decimal(str(s.price)) - money_needed(s, account_value)
        for s in stocks
    }
