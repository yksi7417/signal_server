import pytest
from mahjong_engine.tile import Tile
from mahjong_engine.melds import Meld, MeldType, Pung, Kong, Chow, Pair
from mahjong_engine.constants import SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS, TILE_VALUES_NUMERIC

# Sample Tiles
d1 = Tile(SUIT_DOTS, '1')
d2 = Tile(SUIT_DOTS, '2')
d3 = Tile(SUIT_DOTS, '3')
d4 = Tile(SUIT_DOTS, '4')
b1 = Tile(SUIT_BAMBOO, '1')
c1 = Tile(SUIT_CHARACTERS, '1')
wE = Tile(SUIT_WINDS, "East")
wS = Tile(SUIT_WINDS, "South")
wW = Tile(SUIT_WINDS, "West")
drR = Tile(SUIT_DRAGONS, "Red")


def test_meld_type_enum():
    assert MeldType.PUNG.value == "Pung"
    assert MeldType.KONG.value == "Kong"
    assert MeldType.CHOW.value == "Chow"
    assert MeldType.PAIR.value == "Pair"

# --- Test Base Meld Class ---
def test_base_meld_creation_success():
   
    pung = Meld(MeldType.PUNG, [d1, d1, d1], revealed=True, claimed_from=1)
    assert pung.meld_type == MeldType.PUNG
    assert pung.raw_tiles == [d1, d1, d1]
    assert pung.key_tile == d1
    assert pung.revealed
    assert pung.claimed_from == 1

   
    kong = Meld(MeldType.KONG, [b1, b1, b1, b1])
    assert kong.meld_type == MeldType.KONG
    assert kong.raw_tiles == [b1, b1, b1, b1]
    assert kong.key_tile == b1
    assert not kong.revealed
    assert kong.claimed_from is None

   
    chow = Meld(MeldType.CHOW, [d1, d2, d3])
    assert chow.meld_type == MeldType.CHOW
    assert chow.raw_tiles == [d1, d2, d3] 
    assert chow.key_tile == d1

   
    chow_unsorted = Meld(MeldType.CHOW, [d3, d1, d2])
    assert chow_unsorted.raw_tiles == [d1, d2, d3]
    assert chow_unsorted.key_tile == d1


   
    pair = Meld(MeldType.PAIR, [wE, wE])
    assert pair.meld_type == MeldType.PAIR
    assert pair.raw_tiles == [wE, wE]
    assert pair.key_tile == wE

def test_base_meld_creation_invalid_tiles():
   
    with pytest.raises(ValueError, match="Meld must be initialized with Tile objects"):
        Meld(MeldType.PUNG, [d1, d1, "not-a-tile"])

   
    with pytest.raises(ValueError, match="Invalid tiles for Pung"):
        Meld(MeldType.PUNG, [d1, d2, d1])
   
    with pytest.raises(ValueError, match="Invalid tiles for Pung"):
        Meld(MeldType.PUNG, [d1, d1])

   
    with pytest.raises(ValueError, match="Invalid tiles for Kong"):
        Meld(MeldType.KONG, [b1, b1, d1, b1])
   
    with pytest.raises(ValueError, match="Invalid tiles for Kong"):
        Meld(MeldType.KONG, [b1, b1, b1])

   
    with pytest.raises(ValueError, match="Invalid tiles for Chow"):
        Meld(MeldType.CHOW, [d1, d2, d4])
   
    with pytest.raises(ValueError, match="Invalid tiles for Chow"):
        Meld(MeldType.CHOW, [d1, d2, Tile(SUIT_BAMBOO, '3')])
   
    with pytest.raises(ValueError, match="Invalid tiles for Chow"):
        Meld(MeldType.CHOW, [wE, wS, wW])
   
    with pytest.raises(ValueError, match="Invalid tiles for Chow"):
        Meld(MeldType.CHOW, [d1, d2])
        
   
    with pytest.raises(ValueError, match="Invalid tiles for Pair"):
        Meld(MeldType.PAIR, [d1, d2])
   
    with pytest.raises(ValueError, match="Invalid tiles for Pair"):
        Meld(MeldType.PAIR, [d1, d1, d1])

   
    with pytest.raises(ValueError, match="Unknown meld type"):
        Meld("UNKNOWN_TYPE", [d1,d1])


# --- Test Convenience Classes ---
def test_convenience_pung():
    pung_obj = Pung(d1, revealed=True, claimed_from=2)
    assert pung_obj.meld_type == MeldType.PUNG
    assert pung_obj.raw_tiles == [d1, d1, d1]
    assert pung_obj.key_tile == d1
    assert pung_obj.revealed
    assert pung_obj.claimed_from == 2
    with pytest.raises(ValueError, match="Pung must be initialized with a Tile object."):
        Pung("not-a-tile") #type: ignore

def test_convenience_kong():
    kong_obj = Kong(b1, revealed=False)
    assert kong_obj.meld_type == MeldType.KONG
    assert kong_obj.raw_tiles == [b1, b1, b1, b1]
    assert kong_obj.key_tile == b1
    assert not kong_obj.revealed
    with pytest.raises(ValueError, match="Kong must be initialized with a Tile object."):
        Kong("not-a-tile") #type: ignore


def test_convenience_pair():
    pair_obj = Pair(wE)
    assert pair_obj.meld_type == MeldType.PAIR
    assert pair_obj.raw_tiles == [wE, wE]
    assert pair_obj.key_tile == wE
    assert not pair_obj.revealed
    with pytest.raises(ValueError, match="Pair must be initialized with a Tile object."):
        Pair("not-a-tile") #type: ignore


def test_convenience_chow():
   
    chow1 = Chow(d1, d2, d3, revealed=True)
    assert chow1.meld_type == MeldType.CHOW
    assert chow1.raw_tiles == [d1, d2, d3] 
    assert chow1.key_tile == d1
    assert chow1.revealed

   
    chow2 = Chow(d3, d1, d2)
    assert chow2.raw_tiles == [d1, d2, d3]
    assert chow2.key_tile == d1
    
    with pytest.raises(ValueError, match="Chow must be initialized with three Tile objects."):
        Chow(d1, d2, "not-a-tile") #type: ignore


# --- Test Representation, Equality, Hashing ---
def test_meld_repr():
    pung = Pung(drR, revealed=True)
   
    expected_pung_repr = f"Pung([{drR!r}, {drR!r}, {drR!r}], revealed=True)"
    assert repr(pung) == expected_pung_repr
    
    pair = Pair(wE)
    expected_pair_repr = f"Pair([{wE!r}, {wE!r}], revealed=False)"
    assert repr(pair) == expected_pair_repr

    chow = Chow(d2, d1, d3)
   
    expected_chow_repr = f"Chow([{d1!r}, {d2!r}, {d3!r}], revealed=False)"
    assert repr(chow) == expected_chow_repr


def test_meld_equality_and_hash():
    p1a = Pung(d1, revealed=True)
    p1b = Pung(d1, revealed=True)
    p1_concealed = Pung(d1, revealed=False)
    p2_tiles = [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '2')]
    p2 = Meld(MeldType.PUNG, p2_tiles, revealed=True)
    
    pair1 = Pair(d1)
    
    chow1 = Chow(d1,d2,d3, revealed=True)
    chow1_unsorted_init = Chow(d3,d1,d2, revealed=True)

    assert p1a == p1b
    assert p1a != p1_concealed 
    assert p1a != p2           
    assert p1a != pair1        
    assert p1a != "not-a-meld"
    assert chow1 == chow1_unsorted_init

    meld_set = {p1a, p1b, p1_concealed, p2, pair1, chow1, chow1_unsorted_init}
   
    assert len(meld_set) == 5 
    assert p1a in meld_set
    assert p1_concealed in meld_set
    assert p2 in meld_set
    assert pair1 in meld_set
    assert chow1 in meld_set

   
    meld_dict = {p1a: "Pung D1 Revealed", p1_concealed: "Pung D1 Concealed", chow1: "Chow D123 Revealed"}
    assert meld_dict[p1b] == "Pung D1 Revealed"
    assert meld_dict[chow1_unsorted_init] == "Chow D123 Revealed"
    assert len(meld_dict) == 3
