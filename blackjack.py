import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def value(self):
        if self.rank in ['Jack', 'Queen', 'King']:
            return 10
        elif self.rank == 'Ace':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    def calculate_value(self):
        value = sum(card.value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'Ace')
        
        while value > 21 and aces:
            value -= 10
            aces -= 1
        
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.calculate_value() == 21
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

class Player:
    def __init__(self, chips=1000):
        self.chips = chips
    
    def place_bet(self):
        while True:
            try:
                bet = int(input(f"\nYou have {self.chips} chips. How much do you want to bet? "))
                if bet <= 0:
                    print("Bet must be positive!")
                elif bet > self.chips:
                    print(f"You only have {self.chips} chips!")
                else:
                    return bet
            except ValueError:
                print("Please enter a valid number!")
    
    def win(self, amount):
        self.chips += amount
    
    def lose(self, amount):
        self.chips -= amount

def play_blackjack(player):
    print("\n" + "=" * 40)
    print(f"Current chips: {player.chips}")
    
    if player.chips <= 0:
        print("You're out of chips! Game over!")
        return False
    
    bet = player.place_bet()
    
    deck = Deck()
    deck.shuffle()
    
    player_hand = Hand()
    dealer_hand = Hand()
    
    # Initial deal
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    dealer_hand.add_card(deck.deal())
    
    # Show initial hands
    print(f"\nDealer's hand: {dealer_hand.cards[0]}, [Hidden]")
    print(f"Player's hand: {player_hand} (Value: {player_hand.calculate_value()})")
    
    # Check for player blackjack
    if player_hand.is_blackjack():
        print("\nBlackjack!")
        if dealer_hand.is_blackjack():
            print(f"Dealer also has Blackjack: {dealer_hand}")
            print("Push! Bet returned.")
            return True
        else:
            print(f"Dealer's hand: {dealer_hand} (Value: {dealer_hand.calculate_value()})")
            winnings = int(bet * 1.5)
            player.win(winnings)
            print(f"You win {winnings} chips! (Blackjack pays 3:2)")
            return True
    
    # Player's turn
    while True:
        choice = input("\nDo you want to (h)it or (s)tand? ").lower()
        
        if choice == 'h':
            player_hand.add_card(deck.deal())
            print(f"Player's hand: {player_hand} (Value: {player_hand.calculate_value()})")
            
            if player_hand.calculate_value() > 21:
                print("\nBust! You lose!")
                player.lose(bet)
                print(f"Lost {bet} chips. Remaining: {player.chips}")
                return True
        elif choice == 's':
            break
        else:
            print("Invalid input. Please enter 'h' or 's'.")
    
    # Reveal dealer's hand
    print(f"\nDealer's hand: {dealer_hand} (Value: {dealer_hand.calculate_value()})")
    
    # Check for dealer blackjack
    if dealer_hand.is_blackjack():
        print("Dealer has Blackjack!")
        player.lose(bet)
        print(f"Lost {bet} chips. Remaining: {player.chips}")
        return True
    
    # Dealer's turn
    while dealer_hand.calculate_value() < 17:
        print("Dealer hits...")
        dealer_hand.add_card(deck.deal())
        print(f"Dealer's hand: {dealer_hand} (Value: {dealer_hand.calculate_value()})")
    
    # Determine winner
    player_value = player_hand.calculate_value()
    dealer_value = dealer_hand.calculate_value()
    
    print("\n" + "-" * 40)
    if dealer_value > 21:
        print("Dealer busts! You win!")
        player.win(bet)
        print(f"Won {bet} chips! Total: {player.chips}")
    elif player_value > dealer_value:
        print(f"You win! ({player_value} vs {dealer_value})")
        player.win(bet)
        print(f"Won {bet} chips! Total: {player.chips}")
    elif player_value < dealer_value:
        print(f"Dealer wins! ({dealer_value} vs {player_value})")
        player.lose(bet)
        print(f"Lost {bet} chips. Remaining: {player.chips}")
    else:
        print(f"Push! It's a tie! ({player_value})")
        print(f"Bet returned. Total: {player.chips}")
    
    return True

if __name__ == "__main__":
    print("Welcome to Blackjack!")
    print("-" * 40)
    
    player = Player(chips=1000)
    
    while True:
        if not play_blackjack(player):
            break
        
        if player.chips <= 0:
            print("\nYou're out of chips! Thanks for playing!")
            break
        
        play_again = input("\nPlay again? (y/n): ").lower()
        if play_again != 'y':
            print(f"\nYou're leaving with {player.chips} chips. Thanks for playing!")
            break
input()
