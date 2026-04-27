"""
Provides functionality for the stock market, including buying and selling stocks, stock
prices, and a check for ownership.
"""

class Stock:
    """
    A class used for the stock market function of the game.

    Attributes:

    """

    def __init__(self, player_finances, ownership = []):
        """
        Initializes the stock market information for each player

        Args:
            player_finances: a list of lists containing the net worth of each player and the amount of cash they have.
                for n players, player_finances is a list of n lists of 2 elements. player_finances[i][0] stores
                the net worth of player i, and player_finances[i][1] stores the amount of cash player i has.
            ownership: a list of lists representing how much many stocks each player owns of each player
                for n players, ownership is a list of n lists of n elements. ownership[i][j] stores the
                number of stocks player i owns of player j.
        
        Returns: nothing
        """
        self._num_players = len(player_finances)
        self.net_worth = [player_finance[0] for player_finance in player_finances]
        self.cash = [player_finance[1] for player_finance in player_finances]
        self.num_stocks = 50
        if ownership == []:
            self.ownership = [[self.num_stocks if i == j else 0 for j in range(self._num_players)] for i in range(self._num_players)]
        else:
            self.ownership = ownership
    
    def set_prices(self):
        """
        Sets the prices of the stocks of each player's company based on their net worth

        Args: nothing

        Returns:
            prices: a list representing the price of each player's stock
        """

        prices = [player_worth / self.num_stocks for player_worth in self.net_worth]
        return prices
    
    def _execute_transaction(self, buyer, seller, target, amount, price):
        """
        Private helper function to execute a stock purchase of `target`'s stock between `buyer` and `seller`

        Args:
            buyer: an integer representing the player buying the stock
                the integer corresponds to the index of the player in player_finances and ownership
            seller: an integer representing the player who is selling the stock
                the integer corresponds to the index of the player in player_finances and ownership    
            target: an integer representing the player whose company's stock is being bought
                the integer corresponds to the index of the player in player_finances and ownership
            amount: an integer representing the number of stocks being bought
        """

        _cost = price * amount
        self.ownership[buyer][target] += amount
        self.ownership[seller][target] -= amount
        self.cash[buyer] -= _cost
        self.cash[seller] += _cost
        self.net_worth[buyer] -= _cost
        self.net_worth[seller] += _cost
    
    def buy_stock(self, buyer, target, quantity):
        """
        Executes a stock purchase between two players and updates ownership and finances

        Args:
            buyer: an integer representing the player buying the stock
                the integer corresponds to the index of the player in player_finances and ownership
            target: an integer representing the player whose company's stock is being bought
                the integer corresponds to the index of the player in player_finances and ownership
            quantity: an integer representing the number of stocks being bought
        
        Returns: nothing
        """
        prices = self.set_prices()
        price = prices[target]
        total_cost = price * quantity
        if self.cash[buyer] < total_cost:
            raise ValueError("Buyer doesn't have enough cash to complete the purchase")
        
        available_sellers = [player[target] for player in self.ownership]
        available_sellers[buyer] = 0 # buyer can't purchase from themselves
        if sum(available_sellers) < quantity:
            raise ValueError("There aren't enough stocks available for purchase")
        
        while quantity > 0:
            available_sellers = [player[target] for player in self.ownership]
            available_sellers[buyer] = 0
            amount, seller = min((val, idx) for idx, val in enumerate(available_sellers) if val != 0)
            self._execute_transaction(buyer, seller, target, min(quantity, amount), price)
            quantity = quantity - amount
    
    def check_majority_ownership(self, player):
        """
        Checks if `player` has a majority stake in any other player's company. Primarily supposed to be used within
        this class implementation, but can be used outside if desired.

        Args:
            player: an integer representing the player to check for majority ownership
                the integer corresponds to the index of the player in player_finances and ownership
            
        Returns: 
            owned_players:a list of integers representing the players that `player` has a majority stake in
            the integer corresponds to the index of the player in player_finances and ownership
        """
        owned_players = []
        for i in range(self._num_players):
            if self.ownership[player][i] > self.num_stocks / 2 and i != player:
                owned_players.append(i)
        return owned_players
    
    def check_all_majority_ownership(self):
        """
        Checks if any player has a majority stake in any player's company

        Args: nothing

        Returns: 
            all_owned_players:a list of lists containing the companies of players each player has a majority stake of
            for n players, the returned list of lists is a list of n lists. The ith list contains the indices of players whose
            companies are owned a majority 
        """

        all_owned_players = []
        for player in range(self._num_players):
            all_owned_players.append(self.check_majority_ownership(player))
        return all_owned_players
