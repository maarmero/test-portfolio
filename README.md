# Portfolio Rebalancer Tests

[![Tests](https://github.com/maarmero/test-portfolio/actions/workflows/tests.yml/badge.svg)](https://github.com/maarmero/test-portfolio/actions/workflows/tests.yml)

Manual and automated cases to test rebalancing a portfolio

## Contents

| File | Purpose |
|------|---------|
| `rebalancer.py` | Small reference implementation (the "application under test") |
| `tests/` | Automated pytest suite, grouped by section of `TEST_PLAN.md`: `test_share_calculation.py` (A), `test_rounding.py` (B), `test_input_validation.py` (C), `test_robustness.py` (D). `helpers.py` holds the shared setup |
| `TEST_PLAN.md` | test cases with IDs, priority, expected results and automation coverage |

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

### Running a subset

Every test is tagged with the priority from `TEST_PLAN.md` (`p1`, `p2` or `p3`). If one test
covers several plan rows, it takes the highest priority of those rows.

```bash
pytest -m p1             # the must-pass checks only (a quick smoke run)
pytest -m "p2 or p3"     # everything else
```

`tests/test_plan_matches_tests.py` fails if a tag and the plan disagree, or if the plan names
a test that does not exist, so the two cannot drift apart without being noticed.

## The logic

For each stock:

```
money to trade = (Target % − Current %) / 100 × account value
shares         = money to trade / price of one share      (+ buy, − sell)
```

*Variance* is how far a stock is from its target: Current % minus Target %. A negative
variance means buy, a positive one means sell.

**Sign convention:** the formula uses Target % − Current %, which is the opposite sign of
the assessment's variance (Current % − Target %). So the output is **+ for buy and − for sell**,
while variance is **− for buy and + for sell**. Both describe the same trade. For example,
IBM has a variance of −10 and a result of +66.

Expected output for the assessment data:

| Security | Target % | Current % | Variance | Price | Shares |
|----------|---------:|----------:|---------:|------:|-------:|
| IBM  | 20 | 10 | −10 | 150 | **+66** (buy) |
| MSFT | 20 | 20 |   0 |  90 | 0 |
| ORCL | 20 | 30 | +10 | 220 | **−45** (sell) |
| AAPL | 20 | 20 |   0 | 450 | 0 |
| HD   | 20 | 20 |   0 |  70 | 0 |

The exact numbers are IBM +66.67 and ORCL −45.45. Rounded down they become 66 and 45,
which is $9,900 spent on IBM and $9,900 received from ORCL, so the money spent equals
the money received.

**To get every stock to its Target % (zero variance):** buy 66 IBM and sell 45 ORCL. With whole
shares, IBM and ORCL each end up $100 (0.1%) away from the Target %, which is less than
the price of one share. They only land exactly on the Target % if part shares are allowed.
Both cases are tested.

## Assumptions

1. No application code was provided, so `rebalancer.py` is a simple program I wrote to take its place. The tests only look at what `rebalance()` returns, not how it works inside.
2. Whole shares only by default. Part shares can be turned on for comparison.
3. Rounding is **down** (towards 0) for both buys and sells, so a trade never goes beyond what is needed and the account never spends more than it receives.
4. The small amount of money left over after rounding is ignored.
5. "100% is vested" means every holding can be sold.
6. The Target % values must add up to exactly 100, and so must the Current % values. Otherwise the input is rejected. The assessment does not say this directly; I assumed it because the account is fully invested ("100% is vested") and the example data adds up to 100.
7. Prices are above 0 and the same for buying and selling. No fees, taxes or minimum trade size.
8. Percentages are shares of the whole account value, counting all five stocks.
9. The program uses exact decimal numbers, so there are no tiny rounding errors (for example with 0.01%).
10. No UI exists in the assessment, so there are no automated UI tests. `TEST_PLAN.md` section E has a few hypothetical UI-style manual cases.

## Manual vs automated

- **Test plan** (`TEST_PLAN.md`) includes the cases, whether they are automated or not as well as questions for the PO.
- The **Automated tests** are located in `tests/`
- The strictly **Manual test cases** are the screen checks (section E, because the assessment has no UI). Every share calculation, rounding, input validation and robustness check (sections A to D) has an automated test.
- Most share calculation, rounding and input validation cases exist in both manual and automated cases on purpose. In a real project the manual run would be a one-off and the automated tests would become part of CI/CD (see how I also added GitHub Actions workflow to run the tests)

## How I would test the real application

1. **Get the rules in writing first.** Agree the rounding rule, whether part shares are allowed, and what happens to leftover cash. Most wrong answers here would come from unclear rules, not from bad maths. The open questions are at the end of `TEST_PLAN.md`.
2. **Check the main answer first.** The assessment example (buy 66 IBM, sell 45 ORCL), then the buy / sell / nothing-to-do cases. If these are wrong, nothing else matters.
3. **Then the risky areas.** Rounding (the number is almost never whole), money in versus money out, and very large or very small values.
4. **Then input validation.** Percentages that do not add up to 100, a price of 0, empty fields, the same stock twice. The app should stop with a clear message, not give a wrong answer.
5. **Automate what repeats.** Share calculation, rounding and input validation checks are added onto the automated suite which runs on every PR merge.

**How the tests here were chosen.** The expected answers were worked out by hand from the formula, not by running the code, so a mistake in the code can be caught. The cases cover the assessment example, buy / sell / do nothing, edge cases (less than one share, dividing evenly, a target of 0% or 100%), rounding, and input validation. A few sanity checks sit on top: money in equals money out, never trading more than needed, row order does not matter, and running again after trading needs almost nothing.

**Not covered here:** fees, taxes, minimum trade sizes, real market prices, and how the numbers get into the app (a file, an API or a screen).
