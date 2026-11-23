"""The program being tested: works out how many shares to buy or sell.

Result: + means buy, - means sell, 0 means do nothing.
"""
from collections import namedtuple
from decimal import Decimal, ROUND_DOWN

# One stock: its name, Target %, Current % and the price of one share.
Position = namedtuple("Position", "symbol target_pct current_pct price")


class RebalanceError(ValueError):
    """The input is wrong (for example, the percentages do not add up to 100)."""


def to_number(value, name):
    """Turn the input into an exact decimal number, or raise an error."""
    try:
        return Decimal(str(value))
    except Exception:
        raise RebalanceError(f"{name} is not a number: {value!r}")


def rebalance(account_value, stocks, whole_shares=True):
    account_value = to_number(account_value, "account value")
    if account_value <= 0:
        raise RebalanceError("account value must be > 0")
    if not stocks:
        raise RebalanceError("at least one stock is required")
    names = [s.symbol for s in stocks]
    if len(set(names)) != len(names):
        raise RebalanceError("duplicate symbol")

    total_target = 0
    total_current = 0
    result = {}
    for s in stocks:
        target = to_number(s.target_pct, f"{s.symbol} target_pct")
        current = to_number(s.current_pct, f"{s.symbol} current_pct")
        price = to_number(s.price, f"{s.symbol} price")
        if price <= 0:
            raise RebalanceError(f"{s.symbol} price must be > 0")
        if target < 0 or current < 0:
            raise RebalanceError(f"{s.symbol} percentages must be >= 0")
        total_target += target
        total_current += current

        # 1. How much money do we need to buy (+) or sell (-)?
        money_to_trade = (target - current) / 100 * account_value
        # 2. How many shares is that?
        shares = money_to_trade / price
        # 3. Round down towards 0 (whole shares), or keep 4 decimals (part shares).
        if whole_shares:
            shares = shares.quantize(Decimal(1), rounding=ROUND_DOWN)
        else:
            shares = shares.quantize(Decimal("0.0001"))
        result[s.symbol] = shares

    if total_target != 100:
        raise RebalanceError(f"target % must sum to 100, got {total_target}")
    if total_current != 100:
        raise RebalanceError(f"current % must sum to 100, got {total_current}")
    return result
