# Manual Test Cases — Portfolio Rebalancer

Sign convention: **+ = buy, − = sell**. Total assets = $100,000 unless stated.
Rounding: whole shares, toward zero (see README assumptions).

Priority: P1 = must pass before release, P2 = important, P3 = nice to have.

## A. Functional — core calculation

| ID | Title | Pri | Steps / Input | Expected result |
|----|-------|-----|---------------|-----------------|
| TC-01 | Assessment scenario | P1 | Enter the 5 securities from the assessment (IBM 20/10 @150, MSFT 20/20 @90, ORCL 20/30 @220, AAPL 20/20 @450, HD 20/20 @70) | IBM **+66**, ORCL **−45**, MSFT/AAPL/HD **0** |
| TC-02 | Cash neutrality | P1 | Take TC-01 output; compute buys − sells in $ | 66×150 = 9,900 bought; 45×220 = 9,900 sold; net = $0 |
| TC-03 | Fractional mode | P2 | Run TC-01 with whole shares off | IBM +66.6667, ORCL −45.4545, others 0 |
| TC-04 | Already balanced | P1 | All securities current% = target% | All outputs 0, no buy/sell actions shown |
| TC-05 | Single under-weight, single over-weight | P1 | A: target 30 / current 20 @150; B: target 70 / current 80 @1 | A +66, B −10,000 |
| TC-06 | Sign convention | P1 | Negative variance row; positive variance row | Negative variance → BUY, positive → SELL |
| TC-07 | Single security | P3 | One security, target 100, current 100 | 0 shares |
| TC-08 | Full rotation | P2 | A target 0 / current 100 @100; B target 100 / current 0 @50 | A −1000, B +2000 |
| TC-09 | Target 0% for one security | P2 | A target 0 / current 25 @100; B 100 / 75 @100 | A −250, B +250 |
| TC-10 | Different account size | P2 | TC-01 with total assets $1,000,000 | IBM +666, ORCL −454 |
| TC-11 | Non-round total | P3 | Total $12,345.67; A 50/40 @10; B 50/60 @10 | A +123, B −123 |
| TC-12 | Many securities | P3 | 10 securities, all 10% / 10% | All 0 |

## B. Rounding

| ID | Title | Pri | Input | Expected |
|----|-------|-----|-------|----------|
| TC-20 | Buy fraction rounds down | P1 | $10,000 to buy @150 (66.67) | +66, not 67 |
| TC-21 | Sell fraction rounds toward zero | P1 | $10,000 to sell @150 | −66, not −67 |
| TC-22 | Less than one share | P1 | $10,000 to buy @20,000 | 0 shares |
| TC-23 | Exact division | P2 | $10,000 to buy @100 | +100 |
| TC-24 | Never overshoots target | P1 | Any scenario | \|shares × price\| ≤ \|dollar amount needed\| for every row |

## C. Input validation (negative tests)

| ID | Title | Pri | Input | Expected |
|----|-------|-----|-------|----------|
| TC-30 | Target % ≠ 100 | P1 | Targets sum to 105 | Clear error, no trades produced |
| TC-31 | Current % ≠ 100 | P1 | Current sum to 95 | Clear error, no trades produced |
| TC-32 | Price = 0 | P1 | MSFT price 0 | Error (no divide-by-zero crash) |
| TC-33 | Negative price | P1 | Price −5 | Error |
| TC-34 | Non-numeric price | P2 | Price "abc" | Error |
| TC-35 | Total assets 0 / negative | P1 | Total = 0, then −1 | Error |
| TC-36 | Negative percentage | P2 | Target −10 | Error |
| TC-37 | Duplicate symbol | P2 | IBM listed twice | Error |
| TC-38 | Empty portfolio | P2 | No securities | Error |
| TC-39 | Blank / missing field | P2 | Leave target % empty | Error naming the field |

## D. Non-functional / exploratory

| ID | Title | Pri | What to check |
|----|-------|-----|---------------|
| TC-40 | Row order independence | P2 | Reorder rows → same result per security |
| TC-41 | Idempotency | P2 | Apply TC-01 trades, rerun → at most ±1 share drift per security |
| TC-42 | Very large account ($10^12) | P3 | No overflow / precision loss |
| TC-43 | Very small percentages (0.01) | P3 | Correct, no float rounding drift (decimal arithmetic) |
| TC-44 | Repeatability | P2 | Same input 10× → identical output |

## E. Questions for the product owner (open assumptions)

1. Are fractional shares allowed for any security?
2. Is rounding toward zero acceptable, or should it be round-to-nearest?
3. What happens with leftover cash after rounding (reinvest, hold, ignore)?
4. Do "vested" restrictions matter? (Assessment says 100% is vested — treated as all sellable.)
5. Are tax lots, fees or minimum trade sizes in scope? (Assumed: no.)
