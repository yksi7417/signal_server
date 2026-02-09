import pytest
import collections
from unittest.mock import MagicMock
from mahjong_engine.tile import Tile
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent
from mahjong_engine.player import Player
from mahjong_engine.melds import Pung, Kong, Chow
from mahjong_engine.constants import (
    SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS, SUIT_DRAGONS,
    WIND_EAST, WIND_SOUTH,
)

# Sample Tiles
d1 = Tile(SUIT_DOTS, '1')
d2 = Tile(SUIT_DOTS, '2')
d3 = Tile(SUIT_DOTS, '3')
d4 = Tile(SUIT_DOTS, '4')
d5 = Tile(SUIT_DOTS, '5')
d6 = Tile(SUIT_DOTS, '6')
d7 = Tile(SUIT_DOTS, '7')
d8 = Tile(SUIT_DOTS, '8')
d9 = Tile(SUIT_DOTS, '9')
b1 = Tile(SUIT_BAMBOO, '1')
b2 = Tile(SUIT_BAMBOO, '2')
b3 = Tile(SUIT_BAMBOO, '3')
b5 = Tile(SUIT_BAMBOO, '5')
b7 = Tile(SUIT_BAMBOO, '7')
b9 = Tile(SUIT_BAMBOO, '9')
c1 = Tile(SUIT_CHARACTERS, '1')
c5 = Tile(SUIT_CHARACTERS, '5')
c9 = Tile(SUIT_CHARACTERS, '9')
wE = Tile(SUIT_WINDS, "East")
wS = Tile(SUIT_WINDS, "South")
wW = Tile(SUIT_WINDS, "West")
wN = Tile(SUIT_WINDS, "North")
dR = Tile(SUIT_DRAGONS, "Red")
dG = Tile(SUIT_DRAGONS, "Green")
dW = Tile(SUIT_DRAGONS, "White")


def _make_game_state(player_id=1, discards=None, revealed_sets=None,
                     game_wind=WIND_EAST, player_wind=WIND_SOUTH):
    """Create a minimal mock game state for AI discard tests."""
    gs = MagicMock()
    gs.game_wind = game_wind
    gs.players = []
    for pid in range(4):
        p = MagicMock()
        p.player_id = pid
        p.discards = []
        p.revealed_sets = []
        if pid == player_id:
            p.wind = player_wind
        else:
            p.wind = None
        gs.players.append(p)
    if discards:
        for pid, tiles in discards.items():
            gs.players[pid].discards = tiles
    if revealed_sets:
        for pid, melds in revealed_sets.items():
            gs.players[pid].revealed_sets = melds
    return gs


@pytest.fixture
def ai_agent():
    return AIPlayerAgent(player_id=1)


# === Basic Strategy Tests ===

def test_ai_discards_isolated_tile_over_pair(ai_agent):
    """AI should discard an isolated tile rather than break a pair."""
    # b9 is isolated (no nearby bamboo), d1 pair scores 90
    hand = [d1, d1, b9]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=b9)
    assert chosen == b9


def test_ai_discards_isolated_over_connected(ai_agent):
    """AI should discard an isolated tile over tiles that form sequences."""
    # d1,d2,d3 form a complete chow (score 90 each), c9 is isolated (score 0)
    hand = [d1, d2, d3, c9]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_keeps_pairs_over_singles(ai_agent):
    """AI should discard a single tile rather than break a pair."""
    # d5,d5 pair (score 90), b7 isolated single (score 0)
    hand = [d5, d5, b7]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=b7)
    assert chosen == b7


def test_ai_keeps_triplet_over_single(ai_agent):
    """AI should discard a single rather than break a triplet."""
    hand = [d3, d3, d3, c9]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_keeps_chow_over_isolated(ai_agent):
    """AI should keep a formed chow and discard an isolated tile."""
    # b1,b2,b3 form a chow (score 90), c9 is isolated (score 0)
    hand = [b1, b2, b3, c9]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_discards_dead_honor(ai_agent):
    """Honor tile with 0 remaining copies should be discarded first."""
    # All 4 copies of wN are visible (3 discarded by others + 1 in hand)
    # Wait — _count_available subtracts hand copies too. 4 - 1(hand) - 3(discards) = 0
    gs = _make_game_state(discards={0: [wN, wN, wN]})
    hand = [d5, d5, wN]
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=wN)
    assert chosen == wN


def test_ai_keeps_dragon_over_isolated_numeric(ai_agent):
    """Dragon with copies available scores 45, higher than isolated numeric (0)."""
    hand = [dR, c9]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_keeps_scoring_wind_over_non_scoring(ai_agent):
    """Seat/round wind (45) should be kept over non-scoring wind (40)."""
    # Player 1 wind is South, game wind is East.
    # wE = seat/round wind score 45, wW = non-scoring wind score 40
    hand = [wE, wW]
    gs = _make_game_state(player_wind=WIND_SOUTH, game_wind=WIND_EAST)
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=wW)
    assert chosen == wW


def test_ai_connected_pair_over_gapped(ai_agent):
    """Connected pair (80) should be kept over gapped pair (70)."""
    # d4,d5 are connected (need 3 or 6 for chow → score 80 each)
    # b1,b3 are gapped (need 2 for chow → score 70 each)
    hand = [d4, d5, b1, b3]
    gs = _make_game_state()
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=b1)
    assert chosen in [b1, b3]  # Both gapped, score 70


def test_ai_pair_no_copies_scores_50(ai_agent):
    """Pair with no more copies available scores 50 (stuck pair)."""
    # All 4 d1 accounted for: 2 in hand + 2 discarded → avail=0 → score 50
    # c9 isolated → score 0
    gs = _make_game_state(discards={0: [d1, d1]})
    hand = [d1, d1, c9]
    chosen = ai_agent.choose_discard(gs, list(hand), drawn_tile=c9)
    assert chosen == c9


# === Backward Compatibility Tests ===

def test_ai_empty_hand(ai_agent):
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=[], drawn_tile=d1)
    assert chosen_discard is None


def test_ai_triplet_kept_over_single(ai_agent):
    """Three-of-a-kind (score 90+) is kept over a singleton."""
    hand = [d1, d1, d1, c9]
    chosen = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_pair_kept_over_isolated_single(ai_agent):
    """Pair (score 90 with avail>0) is kept over isolated single (score 0)."""
    hand = [d5, d5, c9]
    chosen = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=c9)
    assert chosen == c9


def test_ai_all_tiles_in_pairs_after_draw(ai_agent):
    full_hand_7pairs_before_draw = [
        d1, d1, d2, d1, d2, d2, d2, d3, d3, d4, d4, d5, d5,
        b1, b1, b2
    ]
    drawn_tile_for_7pairs = b2
    current_hand_7pairs = full_hand_7pairs_before_draw + [drawn_tile_for_7pairs]
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand_7pairs), drawn_tile=drawn_tile_for_7pairs)
    assert chosen_discard in current_hand_7pairs
    counts = collections.Counter(current_hand_7pairs)
    assert counts[chosen_discard] >= 2


def test_ai_all_tiles_in_pairs_or_triplets_forces_random_discard(ai_agent):
    hand_of_7_pairs = [
        d1, d1, d2, d2, d3, d3, d4, d4, d5, d5,
        b1, b1, b2, b2
    ]
    drawn_tile = b2
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand_of_7_pairs), drawn_tile=drawn_tile)
    assert chosen_discard in hand_of_7_pairs
    tile_counts = collections.Counter(hand_of_7_pairs)
    single_tiles = [tile for tile, count in tile_counts.items() if count == 1]
    assert not single_tiles


def test_human_player_agent_fallbacks():
    human_agent = HumanPlayerAgent(player_id=0)
    sample_hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')]
    assert human_agent.choose_discard(None, sample_hand) == sample_hand[1]
    assert human_agent.choose_discard(None, []) is None
    assert human_agent.decide_claim(None, Tile(SUIT_DOTS, '3'), ["PUNG"]) is None


# === Scoring Method Unit Tests ===

class TestAIScoring:
    """Test internal scoring methods directly."""

    def test_score_triplet_with_copies(self, ai_agent):
        hand = [d1, d1, d1, c5]
        gs = _make_game_state()
        assert ai_agent._score_tile(d1, hand, gs) == 100  # 4th copy available

    def test_score_triplet_no_copies(self, ai_agent):
        # 3 in hand + 1 discarded = all 4 accounted for
        hand = [d1, d1, d1, c5]
        gs = _make_game_state(discards={0: [d1]})
        assert ai_agent._score_tile(d1, hand, gs) == 90

    def test_score_pair_with_copies(self, ai_agent):
        hand = [d1, d1, c5]
        gs = _make_game_state()
        assert ai_agent._score_tile(d1, hand, gs) == 90

    def test_score_pair_no_copies(self, ai_agent):
        hand = [d1, d1, c5]
        gs = _make_game_state(discards={0: [d1, d1]})
        assert ai_agent._score_tile(d1, hand, gs) == 50

    def test_score_complete_chow(self, ai_agent):
        hand = [d1, d2, d3]
        gs = _make_game_state()
        # d2 is part of chow 1-2-3 → score 90
        assert ai_agent._score_tile(d2, hand, gs) == 90

    def test_score_connected_pair(self, ai_agent):
        hand = [d4, d5, c9]
        gs = _make_game_state()
        # d4 and d5 are connected → score 80
        assert ai_agent._score_tile(d4, hand, gs) == 80

    def test_score_gapped_pair(self, ai_agent):
        hand = [d4, d6, c9]
        gs = _make_game_state()
        # d4 and d6 are gapped (need d5) → score 70
        assert ai_agent._score_tile(d4, hand, gs) == 70

    def test_score_isolated_numeric(self, ai_agent):
        hand = [c9, d1, d2, d3]
        gs = _make_game_state()
        # c9 has no same-suit neighbors → score 0
        assert ai_agent._score_tile(c9, hand, gs) == 0

    def test_score_dragon_with_copies(self, ai_agent):
        hand = [dR, c9]
        gs = _make_game_state()
        assert ai_agent._score_tile(dR, hand, gs) == 45

    def test_score_dragon_no_copies(self, ai_agent):
        hand = [dR, c9]
        gs = _make_game_state(discards={0: [dR, dR, dR]})
        assert ai_agent._score_tile(dR, hand, gs) == 0

    def test_score_seat_wind(self, ai_agent):
        hand = [wS, c9]
        gs = _make_game_state(player_wind=WIND_SOUTH)
        # Seat wind → 45
        assert ai_agent._score_tile(wS, hand, gs) == 45

    def test_score_round_wind(self, ai_agent):
        hand = [wE, c9]
        gs = _make_game_state(game_wind=WIND_EAST)
        # Round wind → 45
        assert ai_agent._score_tile(wE, hand, gs) == 45

    def test_score_non_scoring_wind(self, ai_agent):
        hand = [wW, c9]
        gs = _make_game_state(player_wind=WIND_SOUTH, game_wind=WIND_EAST)
        # West wind, not seat or round → 40
        assert ai_agent._score_tile(wW, hand, gs) == 40

    def test_count_available_with_melds(self, ai_agent):
        hand = [d1]
        gs = _make_game_state(
            revealed_sets={2: [Pung(d1, revealed=True, claimed_from=0)]}
        )
        # 4 total - 1 hand - 3 meld = 0
        assert ai_agent._count_available(d1, hand, gs) == 0

    def test_count_available_no_game_state(self, ai_agent):
        """When game_state is None, return conservative default of 2."""
        assert ai_agent._count_available(d1, [d1], None) == 2

    def test_score_distance_fallback(self, ai_agent):
        """Single numeric tile near same-suit tiles uses 8-distance scoring."""
        hand = [d1, d5, c9]
        gs = _make_game_state()
        # d1 is 4 away from d5 → score = 8 - 4 = 4
        assert ai_agent._score_tile(d1, hand, gs) == 4
