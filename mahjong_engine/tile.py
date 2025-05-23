from .constants import (
    SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS,
    SUIT_FLOWERS, SUIT_SEASONS,
    SUITS_NUMERIC, SUITS_BONUS,
    WIND_EAST, WIND_SOUTH, WIND_WEST, WIND_NORTH,
    DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE,
    TILE_VALUES_NUMERIC
)

class Tile:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def is_suit(self, suit_type):
        return self.suit == suit_type

    def is_numeric_suit(self):
        return self.suit in SUITS_NUMERIC

    def is_honor(self):
        return self.suit == SUIT_WINDS or self.suit == SUIT_DRAGONS

    def is_wind(self):
        return self.suit == SUIT_WINDS

    def is_dragon(self):
        return self.suit == SUIT_DRAGONS
    
    def is_bonus(self): # Flowers or Seasons
        return self.suit in SUITS_BONUS

    def is_terminal(self):
        return self.is_numeric_suit() and (self.value == '1' or self.value == '9')

    def is_simple(self): # Numeric but not terminal
        return self.is_numeric_suit() and not self.is_terminal()

    # Add __lt__ for sorting, primarily by suit then value
    # This is a simplified sort order. True Mahjong sorting can be complex.
    def __lt__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        
        suit_order = [SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS, SUIT_FLOWERS, SUIT_SEASONS]
        try:
            self_suit_index = suit_order.index(self.suit)
            other_suit_index = suit_order.index(other.suit)
        except ValueError: # Should not happen if suits are valid
            return NotImplemented

        if self_suit_index != other_suit_index:
            return self_suit_index < other_suit_index
        
        # Value comparison (simple lexicographical for now, might need adjustment for numeric vs named values)
        return self.value < other.value

    def __repr__(self):
        return f"Tile('{self.suit}', '{self.value}')"

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))
