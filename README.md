# Portfolio Rebalancer Tests

Manual and automated test cases for a portfolio rebalancing problem
(Account ABC, $100K, IBM / MSFT / ORCL / AAPL / HD).

## Contents

| File | Purpose |
|------|---------|
| `rebalancer.py` | Small reference implementation (the "application under test") |
| `tests/` | Automated pytest suite (47 tests), one file per section of the manual cases: `test_main_calculation.py` (A), `test_rounding.py` (B), `test_bad_input.py` (C), `test_extra_checks.py` (D). `helpers.py` holds the shared setup |
| `MANUAL_TEST_CASES.md` | Manual test cases with IDs, priority, expected results |

## Run

Requires Python 3.9+.

macOS / Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Windows (PowerShell):

```powershell
py -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
```

On Windows cmd, use `.venv\Scripts\activate.bat` instead of the activate line.

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

**To reach zero target variance:** buy 66 IBM and sell 45 ORCL. With whole shares
IBM and ORCL end up $100 away from target (0.1%), less than one share, so variance is
only exactly zero with fractional shares. Both cases are tested.

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

## Manual vs automated

- **Manual cases** (`MANUAL_TEST_CASES.md`) are the test design. A person runs them by hand the first time, or when something changes, and judges the result.
- **Automated tests** (`tests/`) repeat the same checks quickly and the same way on every change. The "Automated?" column in the manual file points each manual case to its test.
- **Manual only:** the screen checks (section E, because the assessment has no UI) and the questions for the product owner. Every calculation, rounding, bad-input and extra check (sections A to D) has an automated test.
- Most calculation, rounding and bad-input cases exist in both on purpose. In a real project the manual run would be a one-off and the automated test would stay as the regression check.

## How I would test the real application

1. **Get the rules in writing first.** Agree the rounding rule, whether part shares are allowed, and what happens to leftover cash. Most wrong answers here would come from unclear rules, not from bad maths. The open questions are at the end of `MANUAL_TEST_CASES.md`.
2. **Check the main answer first.** The assessment example (buy 66 IBM, sell 45 ORCL), then the buy / sell / nothing-to-do cases. If these are wrong, nothing else matters.
3. **Then the risky areas.** Rounding (the number is almost never whole), money in versus money out, and very large or very small values.
4. **Then bad input.** Percentages that do not add up to 100, a price of 0, empty fields, the same stock twice. The app should stop with a clear message, not give a wrong answer.
5. **Automate what repeats.** Calculation, rounding and bad-input checks run on every change. Keep manual testing for things a person has to judge, such as how a screen looks and whether an error message makes sense.

**How the tests here were chosen.** The expected answers were worked out by hand from the formula, not by running the code, so a mistake in the code can be caught. The cases cover the assessment example, buy / sell / do nothing, edge cases (less than one share, dividing evenly, wanting 0% or 100%), rounding, and bad input. A few sanity checks sit on top: money in equals money out, never trading more than needed, row order does not matter, and running again after trading needs almost nothing.

**Not covered here:** fees, taxes, minimum trade sizes, real market prices, and how the numbers get into the app (a file, an API or a screen). I would ask about each before testing it.
