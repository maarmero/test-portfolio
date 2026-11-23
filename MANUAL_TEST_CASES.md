# Manual Test Cases — Portfolio Rebalancer

## How to read these

The app looks at an account that holds several stocks and tells you how many shares
to buy or sell so the account matches the mix you want.

- **Want %** (target): the share of the account's total money you want in that stock.
- **Have %** (current): the share of the account's total money that is in that stock now.
- **Price**: the cost of one share.
- **Result**: a **plus** number means buy that many shares, a **minus** number means sell.
  0 means do nothing.
- **Whole shares**: the app only trades whole shares and rounds down (towards 0), so it
  never trades more than needed. For example, 66.67 shares becomes 66.
- The account is worth **$100,000** unless a test says otherwise.
- Example of how a row is written: `IBM 20/10 @150` means want 20%, have 10%, price $150.

Priority: P1 = must pass, P2 = important, P3 = nice to have.

## A. Main calculation

| ID | Title | Pri | What to do | What should happen |
|----|-------|-----|------------|--------------------|
| TC-01 | The assessment example | P1 | Enter the 5 stocks: IBM 20/10 @150, MSFT 20/20 @90, ORCL 20/30 @220, AAPL 20/20 @450, HD 20/20 @70 | IBM **+66** (buy), ORCL **−45** (sell), MSFT, AAPL and HD **0** |
| TC-02 | Money in equals money out | P1 | Take the TC-01 result and work out the money: shares bought × price, and shares sold × price | 66 × 150 = $9,900 spent on IBM; 45 × 220 = $9,900 received from ORCL; difference $0 |
| TC-03 | Part shares allowed | P2 | Run TC-01 with whole shares turned off | IBM +66.6667, ORCL −45.4545, the rest 0 |
| TC-04 | Nothing to change | P1 | Every stock has Have % equal to Want % | Every result is 0 |
| TC-05 | One to buy, one to sell | P1 | A: want 30, have 20, price 150. B: want 70, have 80, price 1 | A +66, B −10,000 |
| TC-06 | Buy or sell direction | P1 | Use one stock with Have % lower than Want %, and one with Have % higher | Have lower than Want gives a buy (+), Have higher than Want gives a sell (−) |
| TC-07 | Only one stock | P3 | One stock, want 100, have 100 | 0 shares |
| TC-08 | Swap everything | P2 | A: want 0, have 100, price 100. B: want 100, have 0, price 50 | A −1000, B +2000 |
| TC-09 | Want 0% of one stock | P2 | A: want 0, have 25, price 100. B: want 100, have 75, price 100 | A −250 (sell it all), B +250 |
| TC-10 | Bigger account | P2 | Run TC-01 with an account worth $1,000,000 | IBM +666, ORCL −454 |
| TC-11 | Account value with cents | P3 | Account worth $12,345.67. A: want 50, have 40, price 10. B: want 50, have 60, price 10 | A +123, B −123 |
| TC-12 | Lots of stocks | P3 | 10 stocks, each want 10 and have 10 | All results 0 |
| TC-13 | Total bought and total sold | P1 | (a) Run TC-01 and add up all the plus numbers, then all the minus numbers. (b) Run A 40/30 @100, B 30/20 @50, C 10/25 @200, D 20/25 @100 | (a) 66 bought in total, 45 sold in total. (b) A +100, B +200, C −75, D −50; 300 bought in total, 125 sold in total |

## B. Rounding

| ID | Title | Pri | What to do | What should happen |
|----|-------|-----|------------|--------------------|
| TC-20 | Buying: round down | P1 | Need to buy $10,000 of a stock priced $150 (that is 66.67 shares) | +66, not 67 |
| TC-21 | Selling: round down | P1 | Need to sell $10,000 of a stock priced $150 | −66, not −67 |
| TC-22 | Less than one share | P1 | Need to buy $10,000 of a stock priced $20,000 | 0 shares |
| TC-23 | Divides evenly | P2 | Need to buy $10,000 of a stock priced $100 | +100 |
| TC-24 | Never trade too much | P1 | Try any example | For every stock, the money value of the shares traded is never more than the money value needed |

## C. Bad input (the app should reject mistakes)

| ID | Title | Pri | What to do | What should happen |
|----|-------|-----|------------|--------------------|
| TC-30 | Want % does not add up | P1 | Want % values add up to 105 | Clear error message, no buy or sell results |
| TC-31 | Have % does not add up | P1 | Have % values add up to 95 | Clear error message, no buy or sell results |
| TC-32 | Price of 0 | P1 | MSFT price is 0 | Error message, the app does not crash |
| TC-33 | Negative price | P1 | Price is −5 | Error message |
| TC-34 | Price is text | P2 | Price is "abc" | Error message |
| TC-35 | Account value of 0 or less | P1 | Account value 0, then −1 | Error message each time |
| TC-36 | Negative percentage | P2 | Want % is −10 | Error message |
| TC-37 | Same stock twice | P2 | IBM entered two times | Error message |
| TC-38 | No stocks | P2 | Submit with no stocks entered | Error message |
| TC-39 | Empty field | P2 | Leave one Want % empty | Error message that says which field is empty |

## D. Extra checks

| ID | Title | Pri | What to do | What should happen |
|----|-------|-----|------------|--------------------|
| TC-40 | Order of rows | P2 | Run TC-01, then enter the same stocks in a different order | Each stock gets the same result as before |
| TC-41 | Run it twice | P2 | Do the TC-01 trades, update the Have % to match, then run again | Each stock is at most 1 share away from done |
| TC-42 | Huge account | P3 | Account worth $1,000,000,000,000 | Correct results, no strange numbers |
| TC-43 | Tiny percentages | P3 | Percentages with decimals, such as 0.01 | Correct results, no small rounding errors |
| TC-44 | Same answer every time | P2 | Run the same input 10 times | Same result every time |

## E. Screen checks (only if the app had a screen)

The assessment has no screen. These checks apply if the app were a web page with a form
for the stocks and a results column called "Number of shares to buy/sell".

| ID | Title | Pri | What to do | What should happen |
|----|-------|-----|------------|--------------------|
| TC-50 | Results are easy to read | P2 | Run TC-01 on the screen | You can tell buys from sells (a plus or minus sign, or the words Buy and Sell); a result of 0 shows as 0 or "—", not an empty box |
| TC-51 | Numbers look right | P2 | Use an account of $1,000,000 and prices with cents | Large numbers have separators ($1,000,000), prices show 2 decimals, shares show as whole numbers |
| TC-52 | Error shown on the screen | P1 | Enter Want % values that add up to 105 | An error appears next to the problem, the app does not calculate, and the numbers you typed stay in place |
| TC-53 | Required fields | P2 | Leave a price empty and press the button | The empty field is highlighted with a message, and no results are shown |
| TC-54 | Odd typing | P2 | Type "abc", "1e3", "-5" and "1,5" into number fields | Each is accepted or rejected the same way every time, and no crash or "NaN" shows |
| TC-55 | Change and run again | P1 | Run TC-01, change IBM's Have % to 20, then run again | Results update and nothing from the first run is left over |
| TC-56 | Add and delete a row | P2 | Add a sixth stock, then delete one | The results update, and the deleted stock no longer appears |
| TC-57 | Clear the form | P3 | Press Reset after a run | Inputs and results are cleared, or go back to the starting values |
| TC-58 | Use the keyboard only | P3 | Do TC-01 with Tab and Enter, no mouse | Tab moves in a sensible order, Enter runs the calculation, and you can see which field is selected |
| TC-59 | Small screens | P3 | Open the page on a computer and on a phone-sized window | Everything stays readable and the results column is not cut off |
| TC-60 | Double click | P3 | Click the button twice quickly | One correct result, no repeated rows |

## F. Questions to ask the product owner

1. Can we trade part of a share, or only whole shares?
2. Is rounding down okay, or should it round to the nearest whole share?
3. What should happen to the small amount of money left over after rounding?
4. The assessment says the account is "100% vested". We read that as: everything can be sold. Is that right?
5. Do taxes, fees or a minimum trade size matter? (We assumed they do not.)
