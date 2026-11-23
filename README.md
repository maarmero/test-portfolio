# Portfolio Rebalancer Tests

Manual and automated test cases for a portfolio rebalancing problem
(Account ABC, $100K, IBM / MSFT / ORCL / AAPL / HD).

## Contents

| File | Purpose |
|------|---------|
| `rebalancer.py` | Small reference implementation (the "application under test") |
| `tests/test_rebalancer.py` | Automated pytest suite (36 tests) |
| `MANUAL_TEST_CASES.md` | Manual test cases with IDs, priority, expected results |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## The logic

```
trade value = (target% − current%) / 100 × total assets
shares      = trade value / unit price      (+ buy, − sell)
```

Expected output for the assessment data:

| Security | Target % | Current % | Variance | Price | Shares |
|----------|---------:|----------:|---------:|------:|-------:|
| IBM  | 20 | 10 | −10 | 150 | **+66** (buy) |
| MSFT | 20 | 20 |   0 |  90 | 0 |
| ORCL | 20 | 30 | +10 | 220 | **−45** (sell) |
| AAPL | 20 | 20 |   0 | 450 | 0 |
| HD   | 20 | 20 |   0 |  70 | 0 |

Exact values are IBM +66.67 and ORCL −45.45; rounded toward zero they give
$9,900 bought and $9,900 sold, so the trade is cash-neutral.

## Assumptions

1. No application code was provided, so `rebalancer.py` stands in for it. The tests target its `rebalance()` contract, not its internals.
2. Whole shares only by default; fractional mode is available for comparison.
3. Rounding is **toward zero** for both buys and sells, so a trade never overshoots the target and the account never spends more than it raises.
4. Leftover cash from rounding is ignored (no reinvestment).
5. "100% is vested" means every holding can be sold.
6. Target % and current % must each sum to exactly 100; otherwise the input is rejected.
7. Prices are positive and the same for buy and sell. No fees, taxes, lots or minimum trade size.
8. Percentages are relative to total assets of the account, including all five positions.
9. `Decimal` arithmetic is used to avoid floating-point errors.
10. No UI exists in the assessment, so there are no automated UI tests. `MANUAL_TEST_CASES.md` section E has a few hypothetical UI-style manual cases.

## Test approach

- **Oracle:** expected values were calculated by hand from the formula, not by calling the code under test.
- **Techniques:** the assessment scenario, equivalence classes (buy / sell / hold), boundary values (< 1 share, exact division, 0% and 100% targets), rounding rules, invalid input, and invariants (cash neutrality, no overshoot, order independence, idempotency).
