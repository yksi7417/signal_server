import pytest
from mahjong_engine.tile import Tile
from mahjong_engine.constants import (
    SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS,
    SUIT_FLOWERS, SUIT_SEASONS,
    WIND_EAST, WIND_SOUTH, WIND_WEST, WIND_NORTH,
    DRAGON_RED, DRAGON_GREEN, DRAGON_WHITE,
    FLOWER_PLUM, FLOWER_ORCHID, FLOWER_CHRYSANTHEMUM, FLOWER_BAMBOO,
    SEASON_SPRING, SEASON_SUMMER, SEASON_AUTUMN, SEASON_WINTER,
    TILE_VALUES_NUMERIC
)

# Test Initialization and Representation
def test_tile_creation():
    tile = Tile(SUIT_DOTS, '1')
    assert tile.suit == SUIT_DOTS
    assert tile.value == '1'
    assert repr(tile) == "Tile('Dots', '1', '🀙')"

    wind_tile = Tile(SUIT_WINDS, WIND_EAST)
    assert wind_tile.suit == SUIT_WINDS
    assert wind_tile.value == WIND_EAST
    assert repr(wind_tile) == "Tile('Winds', 'East', '🀀')"

    flower_tile = Tile(SUIT_FLOWERS, FLOWER_PLUM)
    assert flower_tile.suit == SUIT_FLOWERS
    assert flower_tile.value == FLOWER_PLUM
    assert repr(flower_tile) == "Tile('Flowers', 'Plum', '🀢')"

# Test Equality and Hashing
def test_tile_equality_and_hash():
    tile1a = Tile(SUIT_DOTS, '1')
    tile1b = Tile(SUIT_DOTS, '1')
    tile2 = Tile(SUIT_BAMBOO, '2')
    tile3 = Tile(SUIT_DOTS, '2') # Same suit, different value
    tile4 = Tile(SUIT_WINDS, WIND_EAST)
    tile5 = Tile(SUIT_WINDS, WIND_EAST)

    assert tile1a == tile1b
    assert tile1a != tile2
    assert tile1a != tile3
    assert tile4 == tile5
    assert tile1a != tile4
    
    assert tile1a != None
    assert tile1a != "Not a tile"
    
    # Test hashing and set usage
    tile_set = {tile1a, tile1b, tile2, tile3, tile4, tile5}
    # Expected: tile1a (same as tile1b), tile2, tile3, tile4 (same as tile5)
    assert len(tile_set) == 4 
    assert tile1a in tile_set
    assert tile2 in tile_set
    assert tile3 in tile_set
    assert tile4 in tile_set

    # Test dictionary key usage
    tile_dict = {tile1a: "one_dots", tile2: "two_bamboo", tile4: "east_wind"}
    assert tile_dict[tile1b] == "one_dots" # tile1b is same as tile1a
    assert tile_dict[tile5] == "east_wind"  # tile5 is same as tile4
    assert len(tile_dict) == 3


# Test Properties
def test_tile_properties():
    dot1 = Tile(SUIT_DOTS, '1')
    dot5 = Tile(SUIT_DOTS, '5')
    char9 = Tile(SUIT_CHARACTERS, '9')
    bamboo2 = Tile(SUIT_BAMBOO, '2')
    east_wind = Tile(SUIT_WINDS, WIND_EAST)
    red_dragon = Tile(SUIT_DRAGONS, DRAGON_RED)
    flower = Tile(SUIT_FLOWERS, "Plum")
    season = Tile(SUIT_SEASONS, "Spring")

    # is_numeric_suit
    assert dot1.is_numeric_suit()
    assert char9.is_numeric_suit()
    assert bamboo2.is_numeric_suit()
    assert not east_wind.is_numeric_suit()
    assert not red_dragon.is_numeric_suit()
    assert not flower.is_numeric_suit()
    assert not season.is_numeric_suit()

    # is_honor
    assert not dot1.is_honor()
    assert east_wind.is_honor()
    assert red_dragon.is_honor()
    assert not flower.is_honor()
    assert not season.is_honor()

    # is_wind / is_dragon
    assert east_wind.is_wind()
    assert not dot1.is_wind()
    assert not red_dragon.is_wind()
    assert red_dragon.is_dragon()
    assert not east_wind.is_dragon()
    assert not dot5.is_dragon()

    # is_bonus
    assert flower.is_bonus()
    assert season.is_bonus()
    assert not dot1.is_bonus()
    assert not east_wind.is_bonus()
    assert not red_dragon.is_bonus()

    # is_terminal
    assert dot1.is_terminal()
    assert not dot5.is_terminal()
    assert char9.is_terminal()
    assert not bamboo2.is_terminal()
    assert not east_wind.is_terminal() # Honors are not terminals by this definition
    assert not red_dragon.is_terminal()
    assert not flower.is_terminal()

    # is_simple
    assert not dot1.is_simple() # Terminal
    assert dot5.is_simple()
    assert bamboo2.is_simple()
    assert not char9.is_simple() # Terminal
    assert not east_wind.is_simple() # Honor
    assert not red_dragon.is_simple() # Honor
    assert not flower.is_simple() # Bonus
    
    # is_suit
    assert dot1.is_suit(SUIT_DOTS)
    assert not dot1.is_suit(SUIT_BAMBOO)
    assert east_wind.is_suit(SUIT_WINDS)
    assert not east_wind.is_suit(SUIT_DRAGONS)
    assert flower.is_suit(SUIT_FLOWERS)
    assert not flower.is_suit(SUIT_SEASONS)


# Test Sorting (__lt__)
def test_tile_sorting():
    tiles_to_sort = [
        Tile(SUIT_WINDS, WIND_EAST),
        Tile(SUIT_DOTS, '2'),
        Tile(SUIT_DRAGONS, DRAGON_RED),
        Tile(SUIT_DOTS, '1'),
        Tile(SUIT_BAMBOO, '5'),
        Tile(SUIT_CHARACTERS, '9'),
        Tile(SUIT_FLOWERS, "Orchid"),
        Tile(SUIT_WINDS, WIND_SOUTH),
        Tile(SUIT_SEASONS, "Winter"),
        Tile(SUIT_DRAGONS, DRAGON_GREEN),
    ]
    
    expected_order = [
        Tile(SUIT_DOTS, '1'),
        Tile(SUIT_DOTS, '2'),
        Tile(SUIT_BAMBOO, '5'),
        Tile(SUIT_CHARACTERS, '9'),
        Tile(SUIT_WINDS, WIND_EAST), # Assuming 'East' < 'South' lexicographically
        Tile(SUIT_WINDS, WIND_SOUTH),
        Tile(SUIT_DRAGONS, DRAGON_GREEN), # Assuming 'Green' < 'Red' lexicographically
        Tile(SUIT_DRAGONS, DRAGON_RED),
        Tile(SUIT_FLOWERS, "Orchid"),
        Tile(SUIT_SEASONS, "Winter"),
    ]
    
    sorted_tiles = sorted(tiles_to_sort)
    assert sorted_tiles == expected_order

    # Test specific comparisons based on defined suit order and then value
    assert Tile(SUIT_DOTS, '1') < Tile(SUIT_DOTS, '2')
    assert Tile(SUIT_DOTS, '9') < Tile(SUIT_BAMBOO, '1')
    assert Tile(SUIT_BAMBOO, '9') < Tile(SUIT_CHARACTERS, '1')
    assert Tile(SUIT_CHARACTERS, '9') < Tile(SUIT_WINDS, WIND_EAST)
    assert Tile(SUIT_WINDS, WIND_NORTH) < Tile(SUIT_DRAGONS, DRAGON_RED) # North vs Red Dragon
    assert Tile(SUIT_WINDS, WIND_EAST) < Tile(SUIT_WINDS, WIND_NORTH) # East vs North Wind
    assert Tile(SUIT_DRAGONS, DRAGON_GREEN) < Tile(SUIT_DRAGONS, DRAGON_RED) # Green vs Red Dragon
    assert Tile(SUIT_DRAGONS, DRAGON_WHITE) < Tile(SUIT_FLOWERS, "Orchid") # Dragon vs Flower
    assert Tile(SUIT_FLOWERS, "Chrysanthemum") < Tile(SUIT_FLOWERS, "Orchid") # Flower vs Flower (lexicographical)
    assert Tile(SUIT_FLOWERS, "Plum") < Tile(SUIT_SEASONS, "Autumn") # Flower vs Season
    assert Tile(SUIT_SEASONS, "Autumn") < Tile(SUIT_SEASONS, "Spring") # Season vs Season (lexicographical)

    # Test with non-Tile type
    with pytest.raises(TypeError):
        Tile(SUIT_DOTS, '1') < "Not a tile"

def test_tile_lt_suit_not_in_order_edge_case():
    tile1 = Tile(SUIT_DOTS, '1')
    # Create a tile with a suit that is not in Tile.__lt__.suit_order
    # Assuming Tile.__init__ allows any string as suit for this test.
    tile2_invalid_suit = Tile("AN_INVALID_SUIT_NOT_IN_ORDER_LIST", '1')

    # When __lt__ returns NotImplemented for one or both due to ValueError,
    # Python's comparison mechanism should raise a TypeError.
    with pytest.raises(TypeError):
        _ = tile1 < tile2_invalid_suit
    with pytest.raises(TypeError):
        _ = tile2_invalid_suit < tile1

    # Re-confirming existing same-suit value comparison logic,
    # which covers `return self.value < other.value`
    assert (Tile(SUIT_DOTS, '1') < Tile(SUIT_DOTS, '9')) is True
    assert (Tile(SUIT_WINDS, WIND_EAST) < Tile(SUIT_WINDS, WIND_NORTH)) is True # "East" < "North"
