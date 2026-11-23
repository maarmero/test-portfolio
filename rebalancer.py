"""Reference implementation of the portfolio rebalancer under test.

Positive result = BUY shares, negative = SELL shares, 0 = no trade.
See README.md for the assumptions behind the rounding rule.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Iterable, Union

Number = Union[int, float, str, Decimal]


class RebalanceError(ValueError):
    """Raised when the input portfolio is invalid."""


@dataclass(frozen=True)
class Position:
    symbol: str
    target_pct: Number
    current_pct: Number
    price: Number


def _dec(value: Number, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise RebalanceError(f"{field} is not a number: {value!r}") from exc


def rebalance(
    total_assets: Number,
    positions: Iterable[Position],
    whole_shares: bool = True,
) -> Dict[str, Decimal]:
    """Return shares to trade per symbol to reach zero target variance.

    whole_shares=True rounds toward zero (never overshoots the target).
    whole_shares=False returns exact fractional shares.
    """
    positions = list(positions)
    total = _dec(total_assets, "total_assets")
    if total <= 0:
        raise RebalanceError("total_assets must be > 0")
    if not positions:
        raise RebalanceError("at least one position is required")

    symbols = [p.symbol for p in positions]
    if len(set(symbols)) != len(symbols):
        raise RebalanceError("duplicate symbol")

    target_sum = Decimal(0)
    current_sum = Decimal(0)
    parsed = []
    for p in positions:
        target = _dec(p.target_pct, f"{p.symbol} target_pct")
        current = _dec(p.current_pct, f"{p.symbol} current_pct")
        price = _dec(p.price, f"{p.symbol} price")
        if price <= 0:
            raise RebalanceError(f"{p.symbol} price must be > 0")
        if target < 0 or current < 0:
            raise RebalanceError(f"{p.symbol} percentages must be >= 0")
        target_sum += target
        current_sum += current
        parsed.append((p.symbol, target, current, price))

    if target_sum != 100:
        raise RebalanceError(f"target % must sum to 100, got {target_sum}")
    if current_sum != 100:
        raise RebalanceError(f"current % must sum to 100, got {current_sum}")

    result: Dict[str, Decimal] = {}
    for symbol, target, current, price in parsed:
        # variance = current - target; negative -> buy, positive -> sell
        trade_value = (target - current) / 100 * total
        shares = trade_value / price
        if whole_shares:
            shares = shares.quantize(Decimal(1), rounding=ROUND_DOWN)  # toward zero
        else:
            shares = shares.quantize(Decimal("0.0001"))
        result[symbol] = shares + 0  # normalises -0 to 0
    return result
