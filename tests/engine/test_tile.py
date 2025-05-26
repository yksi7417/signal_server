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

    season_tile = Tile(SUIT_SEASONS, SEASON_AUTUMN)
    assert season_tile.suit == SUIT_SEASONS
    assert season_tile.value == SEASON_AUTUMN
    assert repr(season_tile) == "Tile('Seasons', 'Autumn', '🀨')"


def test_tile_equality_and_hash():
    tile1a = Tile(SUIT_DOTS, '1')
    tile1b = Tile(SUIT_DOTS, '1')
    tile2 = Tile(SUIT_BAMBOO, '2')
    tile3 = Tile(SUIT_DOTS, '2')
    tile4 = Tile(SUIT_WINDS, WIND_EAST)
    tile5 = Tile(SUIT_WINDS, WIND_EAST)

    assert tile1a == tile1b
    assert tile1a != tile2
    assert tile1a != tile3
    assert tile4 == tile5
    assert tile1a != tile4
    assert tile1a != "Not a tile"

    tile_set = {tile1a, tile1b, tile2, tile3, tile4, tile5}

    assert len(tile_set) == 4
    assert tile1a in tile_set
    assert tile2 in tile_set
    assert tile3 in tile_set
    assert tile4 in tile_set


    tile_dict = {tile1a: "one_dots", tile2: "two_bamboo", tile4: "east_wind"}
    assert tile_dict[tile1b] == "one_dots"
    assert tile_dict[tile5] == "east_wind"
    assert len(tile_dict) == 3


# Test Properties
def test_tile_properties():
    dot1 = Tile(SUIT_DOTS, '1')
    dot5 = Tile(SUIT_DOTS, '5')
    char9 = Tile(SUIT_CHARACTERS, '9')
    bamboo2 = Tile(SUIT_BAMBOO, '2')
    east_wind = Tile(SUIT_WINDS, WIND_EAST)
    red_dragon = Tile(SUIT_DRAGONS, DRAGON_RED)
    flower = Tile(SUIT_FLOWERS, FLOWER_PLUM)
    season = Tile(SUIT_SEASONS, SEASON_SPRING)


    assert dot1.is_numeric_suit()
    assert char9.is_numeric_suit()
    assert bamboo2.is_numeric_suit()
    assert not east_wind.is_numeric_suit()
    assert not red_dragon.is_numeric_suit()
    assert not flower.is_numeric_suit()
    assert not season.is_numeric_suit()


    assert not dot1.is_honor()
    assert east_wind.is_honor()
    assert red_dragon.is_honor()
    assert not flower.is_honor()
    assert not season.is_honor()


    assert east_wind.is_wind()
    assert not dot1.is_wind()
    assert not red_dragon.is_wind()
    assert red_dragon.is_dragon()
    assert not east_wind.is_dragon()
    assert not dot5.is_dragon()


    assert flower.is_bonus()
    assert season.is_bonus()
    assert not dot1.is_bonus()
    assert not east_wind.is_bonus()
    assert not red_dragon.is_bonus()


    assert dot1.is_terminal()
    assert not dot5.is_terminal()
    assert char9.is_terminal()
    assert not bamboo2.is_terminal()
    assert not east_wind.is_terminal()
    assert not red_dragon.is_terminal()
    assert not flower.is_terminal()


    assert not dot1.is_simple()
    assert dot5.is_simple()
    assert bamboo2.is_simple()
    assert not char9.is_simple()
    assert not east_wind.is_simple()
    assert not red_dragon.is_simple()
    assert not flower.is_simple()


    assert dot1.is_suit(SUIT_DOTS)
    assert not dot1.is_suit(SUIT_BAMBOO)
    assert east_wind.is_suit(SUIT_WINDS)
    assert not east_wind.is_suit(SUIT_DRAGONS)
    assert flower.is_suit(SUIT_FLOWERS)
    assert not flower.is_suit(SUIT_SEASONS)


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
        Tile(SUIT_WINDS, WIND_EAST),
        Tile(SUIT_WINDS, WIND_SOUTH),
        Tile(SUIT_DRAGONS, DRAGON_GREEN),
        Tile(SUIT_DRAGONS, DRAGON_RED),
        Tile(SUIT_FLOWERS, "Orchid"),
        Tile(SUIT_SEASONS, "Winter"),
    ]

    sorted_tiles = sorted(tiles_to_sort)
    assert sorted_tiles == expected_order


    assert Tile(SUIT_DOTS, '1') < Tile(SUIT_DOTS, '2')
    assert Tile(SUIT_DOTS, '9') < Tile(SUIT_BAMBOO, '1')
    assert Tile(SUIT_BAMBOO, '9') < Tile(SUIT_CHARACTERS, '1')
    assert Tile(SUIT_CHARACTERS, '9') < Tile(SUIT_WINDS, WIND_EAST)
    assert Tile(SUIT_WINDS, WIND_NORTH) < Tile(SUIT_DRAGONS, DRAGON_RED)
    assert Tile(SUIT_WINDS, WIND_EAST) < Tile(SUIT_WINDS, WIND_NORTH)
    assert Tile(SUIT_DRAGONS, DRAGON_GREEN) < Tile(SUIT_DRAGONS, DRAGON_RED)
    assert Tile(SUIT_DRAGONS, DRAGON_WHITE) < Tile(SUIT_FLOWERS, FLOWER_ORCHID)
    assert Tile(SUIT_FLOWERS, FLOWER_CHRYSANTHEMUM) < Tile(SUIT_FLOWERS, FLOWER_ORCHID)
    assert Tile(SUIT_FLOWERS, FLOWER_PLUM) < Tile(SUIT_SEASONS, SEASON_AUTUMN)
    assert Tile(SUIT_SEASONS, SEASON_AUTUMN) < Tile(SUIT_SEASONS, SEASON_SPRING)


    with pytest.raises(TypeError):
        Tile(SUIT_DOTS, '1') < "Not a tile"


def test_tile_lt_suit_not_in_order_edge_case():
    tile1 = Tile(SUIT_DOTS, '1')
    tile2_invalid_suit = Tile("AN_INVALID_SUIT_NOT_IN_ORDER_LIST", '1')

    with pytest.raises(TypeError):
        _ = tile1 < tile2_invalid_suit
    with pytest.raises(TypeError):
        _ = tile2_invalid_suit < tile1

    assert (Tile(SUIT_DOTS, '1') < Tile(SUIT_DOTS, '9')) is True
    assert (Tile(SUIT_WINDS, WIND_EAST) < Tile(SUIT_WINDS, WIND_NORTH)) is True
