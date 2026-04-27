from pathlib import Path
import sys

# Allow running this test file directly from inside the tests directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.stock_market import Stock

# Test 1: Test a simple stock purchase with no purchase from multiple players
player_finances = [[10920000, 10000000], [678, 320], [4909, 1051], [404, 21]]
ownership = [[45, 4, 1, 0], [1, 46, 9, 23], [3, 0, 33, 3], [1, 0, 7, 24]]
market = Stock(player_finances, ownership)
market.buy_stock(0, 3, 2)
assert market.ownership == [[45, 4, 1, 2], [1, 46, 9, 23], [3, 0, 33, 1], [1, 0, 7, 24]]

# Test 2: Test a simple stock purchase that goes through multiple players
player_finances = [[10920000, 10000000], [678, 320], [4909, 1051], [404, 21]]
ownership = [[45, 4, 1, 0], [1, 46, 9, 23], [3, 0, 33, 3], [1, 0, 7, 24]]
market = Stock(player_finances, ownership)
market.buy_stock(0, 3, 13)
assert market.ownership == [[45, 4, 1, 13], [1, 46, 9, 13], [3, 0, 33, 0], [1, 0, 7, 24]]

# Test 3: Test a simple stock purchase with no ownership information provided
player_finances = [[10000, 1000], [10000, 1000], [10000, 1000], [10000, 1000]]
market = Stock(player_finances)
market.buy_stock(0, 1, 1)
assert market.ownership == [[50, 1, 0, 0], [0, 49, 0, 0], [0, 0, 50, 0], [0, 0, 0, 50]]

# Test 4: Test a simple stock purchase that purchases all stocks of the game
player_finances = [[10000000000, 10000000000], [10000, 1000], [10000, 1000], [10000, 1000]]
market = Stock(player_finances)
market.buy_stock(0, 1, 50)
market.buy_stock(0, 2, 50)
market.buy_stock(0, 3, 50)
assert market.ownership == [[50, 50, 50, 50], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

# Test 5: Test two simple stock purchases that both go through multiple players
player_finances = [[999999, 99999], [999999, 99999], [9999999, 999999], [999999, 99999], [9999999, 999999]]
ownership = [[34, 4, 10, 2, 9], [10, 36, 9, 12, 9], [5, 8, 20, 2, 9], [1, 2, 11, 34, 9], [0, 0, 0, 0, 14]]
market = Stock(player_finances, ownership)
market.buy_stock(4, 0, 7)
market.buy_stock(2, 3, 10)
assert market.ownership == [[34, 4, 10, 0, 9], [9, 36, 9, 4, 9], [0, 8, 20, 12, 9], [0, 2, 11, 34, 9], [7, 0, 0, 0, 14]]

# Test 6: Test a simple stock purchase where a player buys the stock of their own company
player_finances = [[43214, 2314], [23144, 1221], [124323, 23411], [123420, 21411]]
ownership = [[39, 5, 1, 6], [2, 35, 8, 9], [4, 2, 40, 1], [5, 8, 1, 34]]
market = Stock(player_finances, ownership)
market.buy_stock(1, 1, 2)
assert market.ownership == [[39, 5, 1, 6], [2, 37, 8, 9], [4, 0, 40, 1], [5, 8, 1, 34]]

# Test 7: Test that cash is properly updated after a simple stock purchase
player_finances = [[10000, 1000], [10000, 1000], [10000, 1000]]
ownership = [[45, 4, 1], [1, 46, 9], [4, 0, 40]]
market = Stock(player_finances, ownership)
market.buy_stock(2, 0, 1)
assert market.cash == [1000, 1200, 800]

# Test 8: Test that cash is properly updated after multiple stock purchases
player_finances = [[10000, 1000], [10000, 1000], [10000, 1000], [10000, 1000]]
ownership = [[26, 5, 3, 1], [6, 45, 11, 5], [11, 0, 29, 0], [13, 0, 7, 44]]
market = Stock(player_finances, ownership)
market.buy_stock(3, 0, 2)
market.buy_stock(1, 3, 2)
assert market.cash == [1192, 1016, 1000, 792] # unintuitive values due to changing net worths, see next unit test

# Test 9: Test that net worth is properly updated after a simple stock purchase
player_finances = [[10000, 1000], [10000, 1000], [10000, 1000]]
ownership = [[40, 5, 2], [7, 46, 9], [3, 1, 39]]
market = Stock(player_finances, ownership)
market.buy_stock(1, 0, 1)
assert market.net_worth == [10000, 9800, 10200]

# Test 10: Test that net worth is properly updated after multiple stock purchases
player_finances = [[10000, 1000], [10000, 1000], [10000, 1000], [10000, 1000]]
ownership = [[26, 5, 3, 1], [6, 45, 11, 5], [11, 0, 29, 0], [13, 0, 7, 44]]
market = Stock(player_finances, ownership)
market.buy_stock(3, 0, 2)
market.buy_stock(1, 3, 2)
assert market.net_worth == [10192, 10016, 10000, 9792]

# Test 11: Test a scenario where all players hold a majority of their own company, and therefore
# no player controls any other player's company
player_finances = [[10920000, 10000000], [678, 320], [4909, 1051], [404, 21]]
ownership = [[45, 4, 1, 0], [1, 46, 9, 23], [3, 0, 33, 3], [1, 0, 7, 24]]
market = Stock(player_finances, ownership)
assert market.check_all_majority_ownership() == [[], [], [], []]

# Test 12: Test a scenario where one player holds a majority of another player's company
player_finances = [[10920000, 10000000], [678, 320], [4909, 1051], [404, 21]]
ownership = [[45, 4, 1, 0], [1, 20, 9, 23], [3, 0, 33, 3], [1, 26, 7, 24]]
market = Stock(player_finances, ownership)
assert market.check_all_majority_ownership() == [[], [], [], [1]]

# Test 13: Test a scenario where one player gains control of another player's company after a stock purchase
player_finances = [[434211, 23140], [5233, 1221], [3721, 90], [4212, 990]]
ownership = [[45, 13, 24, 1], [1, 36, 9, 0], [3, 1, 10, 3], [1, 0, 7, 46]]
market = Stock(player_finances, ownership)
assert market.check_all_majority_ownership() == [[], [], [], []]
market.buy_stock(0, 2, 2)
assert market.check_all_majority_ownership() == [[2], [], [], []]

# Test 14: Test a scenario where no player holds a majority of one player's company
player_finances = [[434211, 23140], [5233, 1221], [3721, 90], [4212, 990]]
ownership = [[40, 14, 10, 1], [3, 35, 10, 1], [5, 0, 10, 4], [2, 1, 10, 44]]
market = Stock(player_finances, ownership)
assert market.check_all_majority_ownership() == [[], [], [], []]