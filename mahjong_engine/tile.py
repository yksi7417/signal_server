from .constants import (
    SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS,
    SUIT_FLOWERS, SUIT_SEASONS,
    SUITS_NUMERIC, SUITS_BONUS,
    WIND_EAST, WIND_SOUTH, WIND_WEST, WIND_NORTH,
    DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE,
    FLOWER_PLUM, FLOWER_ORCHID, FLOWER_CHRYSANTHEMUM, FLOWER_BAMBOO,
    SEASON_SPRING, SEASON_SUMMER, SEASON_AUTUMN, SEASON_WINTER
)


class Tile:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.unicode = self.__to_string()

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

    def is_bonus(self):
        return self.suit in SUITS_BONUS

    def is_terminal(self):
        return self.is_numeric_suit() and \
            (self.value == '1' or self.value == '9')

    def is_simple(self):
        return self.is_numeric_suit() and not self.is_terminal()

    def __lt__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented

        suit_order = [SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS,
                      SUIT_WINDS, SUIT_DRAGONS, SUIT_FLOWERS, SUIT_SEASONS]
        try:
            self_suit_index = suit_order.index(self.suit)
            other_suit_index = suit_order.index(other.suit)
        except ValueError:
            return NotImplemented

        if self_suit_index != other_suit_index:
            return self_suit_index < other_suit_index

        return self.value < other.value

    def __repr__(self):
        uni = self.__to_string()
        if uni:
            return f"Tile('{self.suit}', '{self.value}', '{uni}')"
        return f"Tile('{self.suit}', '{self.value}')"

    def __to_string(self):
        """
        Return the Unicode string for this tile.
        Returns an empty string if not found.
        """
        unicode_map = {
            (SUIT_CHARACTERS, "1"): "\U0001F007",
            (SUIT_CHARACTERS, "2"): "\U0001F008",
            (SUIT_CHARACTERS, "3"): "\U0001F009",
            (SUIT_CHARACTERS, "4"): "\U0001F00A",
            (SUIT_CHARACTERS, "5"): "\U0001F00B",
            (SUIT_CHARACTERS, "6"): "\U0001F00C",
            (SUIT_CHARACTERS, "7"): "\U0001F00D",
            (SUIT_CHARACTERS, "8"): "\U0001F00E",
            (SUIT_CHARACTERS, "9"): "\U0001F00F",
            (SUIT_BAMBOO, "1"): "\U0001F010",
            (SUIT_BAMBOO, "2"): "\U0001F011",
            (SUIT_BAMBOO, "3"): "\U0001F012",
            (SUIT_BAMBOO, "4"): "\U0001F013",
            (SUIT_BAMBOO, "5"): "\U0001F014",
            (SUIT_BAMBOO, "6"): "\U0001F015",
            (SUIT_BAMBOO, "7"): "\U0001F016",
            (SUIT_BAMBOO, "8"): "\U0001F017",
            (SUIT_BAMBOO, "9"): "\U0001F018",
            (SUIT_DOTS, "1"): "\U0001F019",
            (SUIT_DOTS, "2"): "\U0001F01A",
            (SUIT_DOTS, "3"): "\U0001F01B",
            (SUIT_DOTS, "4"): "\U0001F01C",
            (SUIT_DOTS, "5"): "\U0001F01D",
            (SUIT_DOTS, "6"): "\U0001F01E",
            (SUIT_DOTS, "7"): "\U0001F01F",
            (SUIT_DOTS, "8"): "\U0001F020",
            (SUIT_DOTS, "9"): "\U0001F021",
            (SUIT_WINDS, WIND_EAST): "\U0001F000",
            (SUIT_WINDS, WIND_SOUTH): "\U0001F001",
            (SUIT_WINDS, WIND_WEST): "\U0001F002",
            (SUIT_WINDS, WIND_NORTH): "\U0001F003",
            (SUIT_DRAGONS, DRAGON_RED): "\U0001F004",
            (SUIT_DRAGONS, DRAGON_GREEN): "\U0001F005",
            (SUIT_DRAGONS, DRAGON_WHITE): "\U0001F006",
            (SUIT_FLOWERS, FLOWER_PLUM): "\U0001F022",
            (SUIT_FLOWERS, FLOWER_ORCHID): "\U0001F023",
            (SUIT_FLOWERS, FLOWER_CHRYSANTHEMUM): "\U0001F024",
            (SUIT_FLOWERS, FLOWER_BAMBOO): "\U0001F025",
            (SUIT_SEASONS, SEASON_SPRING): "\U0001F026",
            (SUIT_SEASONS, SEASON_SUMMER): "\U0001F027",
            (SUIT_SEASONS, SEASON_AUTUMN): "\U0001F028",
            (SUIT_SEASONS, SEASON_WINTER): "\U0001F029",
        }
        return unicode_map.get((self.suit, self.value), "")

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))
