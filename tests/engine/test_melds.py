import pytest
from mahjong_engine.tile import Tile
from mahjong_engine.melds import Meld, MeldType, Pung, Kong, Chow, Pair
from mahjong_engine.constants import SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS, TILE_VALUES_NUMERIC
from mahjong_engine.hand_validator import can_form_chow_with_discard

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
        Meld("UNKNOWN_TYPE", [d1, d1])


def test_convenience_pung():
    pung_obj = Pung(d1, revealed=True, claimed_from=2)
    assert pung_obj.meld_type == MeldType.PUNG
    assert pung_obj.raw_tiles == [d1, d1, d1]
    assert pung_obj.key_tile == d1
    assert pung_obj.revealed
    assert pung_obj.claimed_from == 2
    with pytest.raises(ValueError, match="Pung must be initialized with a Tile object."):
        Pung("not-a-tile")


def test_convenience_kong():
    kong_obj = Kong(b1, revealed=False)
    assert kong_obj.meld_type == MeldType.KONG
    assert kong_obj.raw_tiles == [b1, b1, b1, b1]
    assert kong_obj.key_tile == b1
    assert not kong_obj.revealed
    with pytest.raises(ValueError, match="Kong must be initialized with a Tile object."):
        Kong("not-a-tile")


def test_convenience_pair():
    pair_obj = Pair(wE)
    assert pair_obj.meld_type == MeldType.PAIR
    assert pair_obj.raw_tiles == [wE, wE]
    assert pair_obj.key_tile == wE
    assert not pair_obj.revealed
    with pytest.raises(ValueError, match="Pair must be initialized with a Tile object."):
        Pair("not-a-tile")


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
        Chow(d1, d2, "not-a-tile")


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
    chow1 = Chow(d1, d2, d3, revealed=True)
    chow1_unsorted_init = Chow(d3, d1, d2, revealed=True)

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


class TestChowValidation:
    """Tests for can_form_chow_with_discard() function."""

    def test_chow_discard_is_lowest(self):
        """Discarded tile is lowest in sequence (e.g., discard 1, hand has 2,3)."""
        hand = [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'), Tile(SUIT_BAMBOO, '5')]
        discard = Tile(SUIT_DOTS, '1')
        assert can_form_chow_with_discard(hand, discard, discarder_position=3, claimer_position=0) is True

    def test_chow_discard_is_middle(self):
        """Discarded tile is middle of sequence (e.g., discard 5, hand has 4,6)."""
        hand = [Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_DOTS, '1')]
        discard = Tile(SUIT_BAMBOO, '5')
        assert can_form_chow_with_discard(hand, discard, discarder_position=1, claimer_position=2) is True

    def test_chow_discard_is_highest(self):
        """Discarded tile is highest in sequence (e.g., discard 9, hand has 7,8)."""
        hand = [Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_DOTS, '1')]
        discard = Tile(SUIT_CHARACTERS, '9')
        assert can_form_chow_with_discard(hand, discard, discarder_position=2, claimer_position=3) is True

    def test_chow_multiple_patterns_available(self):
        """Hand has tiles for multiple chow patterns with the discard."""
        hand = [Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'), Tile(SUIT_DOTS, '3')]
        discard = Tile(SUIT_DOTS, '5')
        # Can form 3-4-5 or 4-5-6 or 5-6-... wait, 5 is discard, hand has 3,4,6
        # Pattern: discard=5, hand has 3,4 -> 3-4-5 (discard is highest)
        # Pattern: discard=5, hand has 4,6 -> 4-5-6 (discard is middle)
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is True

    def test_chow_invalid_wrong_position(self):
        """Only left neighbor (discarder+1 mod 4) can claim chow."""
        hand = [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3')]
        discard = Tile(SUIT_DOTS, '1')
        # Position 0 discards, claimer is position 2 (not left neighbor)
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=2) is False
        # Position 0 discards, claimer is position 3
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=3) is False

    def test_chow_invalid_honor_tiles(self):
        """Cannot form chow with wind or dragon tiles."""
        hand = [Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West')]
        discard = Tile(SUIT_WINDS, 'East')
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is False

        hand2 = [Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')]
        discard2 = Tile(SUIT_DRAGONS, 'Red')
        assert can_form_chow_with_discard(hand2, discard2, discarder_position=0, claimer_position=1) is False

    def test_chow_invalid_tiles_not_in_hand(self):
        """Hand doesn't contain the needed tiles for any chow pattern."""
        hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '5')]
        discard = Tile(SUIT_DOTS, '3')
        # Need 2,4 or 4,5 or 1,2 — hand has 1,5 so no consecutive pair with 3
        # Actually: need (1,2), (2,4), or (4,5) in hand. Hand has 1,5. None match.
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is False

    def test_chow_invalid_empty_hand(self):
        """Empty hand cannot form chow."""
        assert can_form_chow_with_discard([], Tile(SUIT_DOTS, '5'), discarder_position=0, claimer_position=1) is False

    def test_chow_invalid_none_discard(self):
        """None discard returns False."""
        hand = [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3')]
        assert can_form_chow_with_discard(hand, None, discarder_position=0, claimer_position=1) is False

    def test_chow_invalid_different_suits(self):
        """Tiles must all be the same suit."""
        hand = [Tile(SUIT_DOTS, '2'), Tile(SUIT_BAMBOO, '3')]
        discard = Tile(SUIT_DOTS, '1')
        # Need 2-dots and 3-dots, but hand has 3-bamboo not 3-dots
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is False

    def test_chow_edge_tile_1_cannot_be_highest(self):
        """Tile value 1 cannot be the highest in a sequence (no -1, 0 tiles)."""
        hand = [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3')]
        discard = Tile(SUIT_DOTS, '1')
        # 1 as lowest: need 2,3 in hand -> True
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is True
        # But with only a 9 and 8 in hand, 1 can't form anything
        hand2 = [Tile(SUIT_DOTS, '8'), Tile(SUIT_DOTS, '9')]
        assert can_form_chow_with_discard(hand2, discard, discarder_position=0, claimer_position=1) is False

    def test_chow_edge_tile_9_cannot_be_lowest(self):
        """Tile value 9 cannot be the lowest in a sequence (no 10, 11 tiles)."""
        hand = [Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '8')]
        discard = Tile(SUIT_DOTS, '9')
        # 9 as highest: need 7,8 in hand -> True
        assert can_form_chow_with_discard(hand, discard, discarder_position=0, claimer_position=1) is True

    def test_chow_position_wraps_around(self):
        """Position 3 discards, position 0 is left neighbor (wrap-around)."""
        hand = [Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '5')]
        discard = Tile(SUIT_DOTS, '3')
        assert can_form_chow_with_discard(hand, discard, discarder_position=3, claimer_position=0) is True
