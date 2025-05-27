import unittest
from mahjong_engine.ruleset import DefaultRuleSet
from mahjong_engine.tile import Tile
from mahjong_engine.melds import Pung # Pung is a type of Meld
from mahjong_engine.constants import SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_DOTS


class TestDefaultRuleSet(unittest.TestCase):

    def setUp(self):
        self.rules = DefaultRuleSet()

    def test_standard_win_4_revealed_melds_1_pair(self):
        """Test win with 4 revealed Pungs and a pair in hand."""
        revealed_sets = [
            Pung(Tile(SUIT_BAMBOO, '3')),
            Pung(Tile(SUIT_BAMBOO, '7')),
            Pung(Tile(SUIT_BAMBOO, '6')),
            Pung(Tile(SUIT_CHARACTERS, '3'))
        ]
        # Hand tiles should form the pair for the win
        hand_tiles = [Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '2')]
        self.assertTrue(self.rules.is_winning_hand(hand_tiles, revealed_sets))

    def test_standard_win_all_tiles_in_hand(self):
        """Test standard win with all 14 tiles in hand (4 melds + 1 pair)."""
        # Example: 111 (Pung), 234 (Chow), 567 (Chow), 888 (Pung), 99 (Pair) - all Bamboo
        hand_tiles = [
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '8'),
            Tile(SUIT_BAMBOO, '9'), Tile(SUIT_BAMBOO, '9')
        ]
        revealed_sets = []
        self.assertTrue(self.rules.is_winning_hand(hand_tiles, revealed_sets))

    def test_standard_win_all_tiles_in_hand_mixed_melds(self):
        """Test standard win with 14 tiles in hand, mixed Pungs and Chows."""
        # Hand: 111 (Pung C), 22 (Pair C), 345 (Chow B), 678 (Chow D), 999 (Pung D)
        hand_tiles = [
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '1'),
            Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '5'),
            Tile(SUIT_DOTS, '6'), Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '8'),
            Tile(SUIT_DOTS, '9'), Tile(SUIT_DOTS, '9'), Tile(SUIT_DOTS, '9'),
            Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '2') # Pair
        ]
        revealed_sets = []
        self.assertTrue(self.rules.is_winning_hand(hand_tiles, revealed_sets))


    def test_non_winning_hand_all_tiles_in_hand(self):
        """Test a non-winning hand with 14 tiles."""
        # Example: 111, 234, 567, 88, 9999 (Pung, Chow, Chow, Pair, Kong -> 5 melds effectively, not 4+pair)
        # Or simply a jumbled hand:
        hand_tiles = [
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '8'), # One pair
            Tile(SUIT_BAMBOO, '9'), Tile(SUIT_BAMBOO, '9'), Tile(SUIT_BAMBOO, '5') # Another pair and a loose tile
        ]
        revealed_sets = []
        self.assertFalse(self.rules.is_winning_hand(hand_tiles, revealed_sets))

    def test_calculate_score_placeholder_winning_hand(self):
        """Test calculate_score placeholder for a winning hand."""
        revealed_sets = [
            Pung(Tile(SUIT_BAMBOO, '3')),
            Pung(Tile(SUIT_BAMBOO, '7')),
            Pung(Tile(SUIT_BAMBOO, '6')),
            Pung(Tile(SUIT_CHARACTERS, '3'))
        ]
        hand_tiles = [Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '2')]
        score = self.rules.calculate_score(hand_tiles, revealed_sets)
        self.assertEqual(score, 1)

    def test_calculate_score_placeholder_winning_hand_2(self):
        revealed_sets = []
        hand_tiles = [
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '3'),
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7')
        ]
        score = self.rules.calculate_score(hand_tiles, revealed_sets)
        self.assertEqual(score, 1)


    def test_calculate_score_placeholder_non_winning_hand(self):
        revealed_sets = []
        hand_tiles = [
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7')
        ]
        score = self.rules.calculate_score(hand_tiles, revealed_sets)
        self.assertEqual(score, 0)