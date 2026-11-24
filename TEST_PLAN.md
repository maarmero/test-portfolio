# Test Plan — Portfolio Rebalancer

## How to read these

The app looks at an account that holds several stocks and tells you how many shares
to buy or sell so the account matches the mix you want.

- **Target %**: the share of the account's total money you want in that stock.
- **Current %**: the share of the account's total money that is in that stock now.
- **Variance**: Current % minus Target %. A negative variance means buy, a positive one means sell.
- **Price**: the cost of one share.
- **Result**: a **plus** number means buy that many shares, a **minus** number means sell.
  0 means do nothing.
- **Whole shares**: the app only trades whole shares and rounds down (towards 0), so it
  never trades more than needed. For example, 66.67 shares becomes 66.
- The account is worth **$100,000** unless a test says otherwise.
- Example of how a row is written: `IBM 20/10 @150` means target 20%, current 10%, price $150.

Priority: P1 = must pass, P2 = important, P3 = nice to have.

**Automated?** column: the pytest test (in the `tests/` folder, one file per section: `test_main_calculation.py`, `test_rounding.py`, `test_bad_input.py`, `test_extra_checks.py`) that checks the same
behaviour. Sections A to D
are all automated. Section E (screen checks) is manual only, because the assessment has
no screen.

## A. Main calculation

| ID | Title | Pri | Steps | Expected Result | Automated? |
|----|-------|-----|------------|--------------------|-----|
| TC-01 | The assessment example | P1 | Enter the 5 stocks: IBM 20/10 @150, MSFT 20/20 @90, ORCL 20/30 @220, AAPL 20/20 @450, HD 20/20 @70 | IBM **+66** (buy), ORCL **−45** (sell), MSFT, AAPL and HD **0** | `test_assessment_example_gives_66_buy_and_45_sell` |
| TC-02 | Money in equals money out | P1 | Take the TC-01 result and work out the money: shares bought × price, and shares sold × price | 66 × 150 = $9,900 spent on IBM; 45 × 220 = $9,900 received from ORCL; difference $0 | `test_assessment_example_money_in_equals_money_out` |
| TC-03 | Part shares allowed | P2 | Run TC-01 with whole shares turned off | IBM +66.6667, ORCL −45.4545, the rest 0 | `test_assessment_example_with_part_shares` |
| TC-04 | Nothing to change | P1 | Every stock has Current % equal to Target % | Every result is 0 | `test_nothing_to_change_gives_all_zeros` |
| TC-05 | One to buy, one to sell | P1 | A: target 30, current 20, price 150. B: target 70, current 80, price 1 | A +66, B −10,000 | `test_one_to_buy_and_one_to_sell` |
| TC-06 | Buy or sell direction | P1 | Use one stock with Current % lower than Target %, and one with Current % higher | Current lower than Target gives a buy (+), Current higher than Target gives a sell (−) | `test_buy_sell_or_nothing_depending_on_current_vs_target` |
| TC-07 | Only one stock | P3 | One stock, target 100, current 100 | 0 shares | `test_single_stock_gives_zero` |
| TC-08 | Swap everything | P2 | A: target 0, current 100, price 100. B: target 100, current 0, price 50 | A −1000, B +2000 | `test_swap_everything` |
| TC-09 | Target 0% of one stock | P2 | A: target 0, current 25, price 100. B: target 100, current 75, price 100 | A −250 (sell it all), B +250 | `test_target_zero_percent_sells_the_whole_holding` |
| TC-10 | Bigger account | P2 | Run TC-01 with an account worth $1,000,000 | IBM +666, ORCL −454 | `test_bigger_account` |
| TC-11 | Account value with cents | P3 | Account worth $12,345.67. A: target 50, current 40, price 10. B: target 50, current 60, price 10 | A +123, B −123 | `test_account_value_with_cents` |
| TC-12 | Lots of stocks | P3 | 10 stocks, each target 10 and current 10 | All results 0 | `test_ten_stocks_with_nothing_to_change` |
| TC-13 | Total bought and total sold | P1 | (a) Run TC-01 and add up all the plus numbers, then all the minus numbers. (b) Run A 40/30 @100, B 30/20 @50, C 10/25 @200, D 20/25 @100 | (a) 66 bought in total, 45 sold in total. (b) A +100, B +200, C −75, D −50; 300 bought in total, 125 sold in total | `test_assessment_example_total_bought_and_sold`, `test_total_bought_and_sold_with_several_buys_and_sells` |
| TC-14 | Ends on target (part shares) | P1 | Run TC-01 with whole shares turned off, do the trades, then work out each stock's % of the account | Every stock is on its Target % (the difference is under 0.001 percentage points) | `test_part_share_trades_end_on_target` |
| TC-15 | Ends close to target (whole shares) | P1 | Run TC-01, do the trades, then work out how much money each stock is away from its Target % | Every stock is less than the price of one share away (IBM and ORCL are each $100 away) | `test_whole_share_trades_end_less_than_one_share_from_target` |

## B. Rounding

Each case uses two stocks so that the Target % and the Current % each add up to 100.
Stock B is only a filler to make that work; check the result for stock A. The account is $100,000.

| ID | Title | Pri | Steps | Expected Result | Automated? |
|----|-------|-----|------------|--------------------|-----|
| TC-20 | Buying: round down | P1 | A: target 20, current 10, price 150 (needs $10,000 more, which is 66.67 shares). B (filler): target 80, current 90, price 1 | A +66, not 67 | `test_buying_rounds_down` |
| TC-21 | Selling: round down | P1 | A: target 10, current 20, price 150 (needs $10,000 less, which is 66.67 shares). B (filler): target 90, current 80, price 1 | A −66, not −67 | `test_selling_rounds_down_towards_zero` |
| TC-22 | Less than one share | P1 | A: target 20, current 10, price 20,000 (needs $10,000 more, which is 0.5 of a share). B (filler): target 80, current 90, price 1 | A 0 shares | `test_buying_rounds_down` |
| TC-23 | Divides evenly | P2 | A: target 20, current 10, price 100 (needs $10,000 more, which is exactly 100 shares). B (filler): target 80, current 90, price 1 | A +100 | `test_buying_rounds_down` |
| TC-24 | Never trade too much | P1 | Run any example above, or TC-01 | For every stock, the money value of the shares traded (shares × price) is never more than the money value needed | `test_never_trade_more_than_needed` |

## C. Bad input (the app should reject mistakes)

| ID | Title | Pri | Steps | Expected Result | Automated? |
|----|-------|-----|------------|--------------------|-----|
| TC-30 | Target % does not add up | P1 | Target % values add up to 105 | Clear error message, no buy or sell results | `test_target_percent_not_adding_up_to_100` |
| TC-31 | Current % does not add up | P1 | Current % values add up to 105 | Clear error message, no buy or sell results | `test_current_percent_not_adding_up_to_100` |
| TC-32 | Price of 0 | P1 | MSFT price is 0 | Error message, the app does not crash | `test_bad_price` |
| TC-33 | Negative price | P1 | Price is −5 | Error message | `test_bad_price` |
| TC-34 | Price is text | P2 | Price is "abc" | Error message | `test_bad_price` |
| TC-35 | Account value of 0 or less | P1 | Account value 0, then −1 | Error message each time | `test_bad_account_value` |
| TC-36 | Negative percentage | P2 | Target % is −10 | Error message | `test_negative_percentage` |
| TC-37 | Same stock twice | P2 | IBM entered two times | Error message | `test_same_stock_twice` |
| TC-38 | No stocks | P2 | Submit with no stocks entered | Error message | `test_no_stocks` |
| TC-39 | Empty field | P2 | Leave one Target % empty | Error message that says which field is empty | `test_empty_percentage_names_the_field` (also an empty price or account value in `test_bad_price`, `test_bad_account_value`) |

## D. Extra checks

| ID | Title | Pri | Steps | Expected Result | Automated? |
|----|-------|-----|------------|--------------------|-----|
| TC-40 | Order of rows | P2 | Run TC-01, then enter the same stocks in a different order | Each stock gets the same result as before | `test_order_of_rows_does_not_matter` |
| TC-41 | Run it twice | P2 | Do the TC-01 trades, update the Current % to match, then run again | Each stock is at most 1 share away from done | `test_running_again_after_trading_needs_almost_nothing` |
| TC-42 | Huge account | P3 | Account worth $1,000,000,000,000 | Correct results, no strange numbers | `test_huge_account` |
| TC-43 | Tiny percentages | P3 | Percentages with decimals, such as 0.01 | Correct results, no small rounding errors | `test_tiny_percentages_are_exact`, `test_percentages_and_prices_with_decimals` |

## E. Screen checks (only if the app had a screen)

**All manual only.** The assessment has no screen. These checks apply if the app were a web page with a form
for the stocks and a results column called "Number of shares to buy/sell".

| ID | Title | Pri | Steps | Expected Result |
|----|-------|-----|------------|--------------------|
| TC-50 | Results are easy to read | P2 | Run TC-01 on the screen | You can tell buys from sells (a plus or minus sign, or the words Buy and Sell); a result of 0 shows as 0 or "—", not an empty box |
| TC-51 | Numbers look right | P2 | Use an account of $1,000,000 and prices with cents | Large numbers have separators ($1,000,000), prices show 2 decimals, shares show as whole numbers |
| TC-52 | Error shown on the screen | P1 | Enter Target % values that add up to 105 | An error appears next to the problem, the app does not calculate, and the numbers you typed stay in place |
| TC-53 | Required fields | P2 | Leave a price empty and press the button | The empty field is highlighted with a message, and no results are shown |
| TC-54 | Odd typing | P2 | Type "abc", "1e3", "-5" and "1,5" into number fields | Each is accepted or rejected the same way every time, and no crash or "NaN" shows |
| TC-55 | Change and run again | P1 | Run TC-01, change IBM's Current % to 20, then run again | Results update and nothing from the first run is left over |
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
