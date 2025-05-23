import pytest
import random
import collections
from mahjong_engine.tile import Tile
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent # Added HumanPlayerAgent
from mahjong_engine.constants import SUIT_DOTS, SUIT_BAMBOO, SUIT_CHARACTERS, SUIT_WINDS

# Sample Tiles
d1 = Tile(SUIT_DOTS, '1')
d2 = Tile(SUIT_DOTS, '2')
d3 = Tile(SUIT_DOTS, '3')
d4 = Tile(SUIT_DOTS, '4')
d5 = Tile(SUIT_DOTS, '5')
b1 = Tile(SUIT_BAMBOO, '1')
b2 = Tile(SUIT_BAMBOO, '2')
c1 = Tile(SUIT_CHARACTERS, '1')
wE = Tile(SUIT_WINDS, "East")

@pytest.fixture
def ai_agent():
    return AIPlayerAgent(player_id=1)

# 1. Basic Discard of Drawn Tile
def test_ai_discard_newly_drawn_single_tile(ai_agent):
    # Hand: d1, d2, d3. Drawn: d4. Expected discard: d4
    hand = [d1, d2, d3, d4] # Hand includes the drawn tile
    drawn_tile = d4
    # Make a copy for the function call, as it might be modified by some implementations
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4

def test_ai_discard_newly_drawn_single_tile_mixed_hand(ai_agent):
    # Hand: d1, d1, d2, d3. Drawn: d4. Expected discard: d4
    hand = [d1, d1, d2, d3, d4]
    drawn_tile = d4
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4
    
def test_ai_discard_priority_drawn_tile_if_single_among_other_singles(ai_agent):
    # Hand: d1, d2, d3. Drawn: d4. All are singles. Drawn tile (d4) should be preferred.
    # This tests the `if drawn_tile in single_tiles:` part of AI logic,
    # but also the initial check `if count_of_drawn_tile_in_hand == 1`.
    hand = [d1, d2, d3, d4]
    drawn_tile = d4
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4

# 2. Drawn Tile Forms a Pair
def test_ai_drawn_tile_forms_pair_does_not_discard_drawn(ai_agent):
    # Hand: d1(existing), d2, d3. Drawn: d1 (new).
    # Drawn d1 forms a pair. AI should not discard d1.
    # Expected discard: d2 or d3
    hand_content = [d1, d2, d3, d1] # Simulating hand after draw: one d1 was old, one is new
    drawn_tile = d1 # The specific instance of d1 that was "drawn"
    
    # Ensure there are two d1s in hand_content for the test setup
    assert collections.Counter(hand_content)[d1] == 2
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand_content), drawn_tile=drawn_tile)
    # The logic is: if drawn_tile_count > 1, it proceeds to discard other singles.
    # Here d2 and d3 are singles.
    assert chosen_discard in [d2, d3]
    assert chosen_discard != d1


# 3. Discarding Other Single Tiles
def test_ai_drawn_tile_forms_pair_discards_other_single(ai_agent):
    # Hand: d1, d2, d3, d4. Drawn: d1 (forms pair with existing d1).
    # Expected discard: d2, d3, or d4 (any of the singles)
    hand_before_draw = [d1, d2, d3, d4] # One d1 already present
    drawn_tile = d1 # This is a new d1, making a pair d1,d1
    current_hand = hand_before_draw + [drawn_tile] # Effectively [d1, d2, d3, d4, d1]
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
    
    # d1s are now a pair (count = 2). d2, d3, d4 are singles.
    # AI should discard one of d2, d3, d4.
    assert chosen_discard in [d2, d3, d4]
    assert chosen_discard != d1

def test_ai_drawn_tile_forms_third_of_a_kind_discards_single(ai_agent):
    # Hand: d1, d1, d2, d3. Drawn: d1 (forms Pung of d1).
    # Expected discard: d2 or d3 (a single)
    hand_before_draw = [d1, d1, d2, d3]
    drawn_tile = d1 # This is a new d1, making three d1s
    current_hand = hand_before_draw + [drawn_tile] # [d1, d1, d2, d3, d1]
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
    # d1s are now a triplet (count = 3). d2, d3 are singles.
    # AI should discard one of d2, d3.
    assert chosen_discard in [d2, d3]

# This test might be redundant if the above covers the logic sufficiently.
# It tests when drawn_tile is a single, but other tiles form pairs.
def test_ai_drawn_tile_is_single_others_are_pairs(ai_agent):
    # Hand: d1,d1, d2,d2. Drawn: d3. Expected: d3
    hand = [d1,d1,d2,d2,d3]
    drawn_tile = d3
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d3


# 4. All Tiles in Pairs/Sets
def test_ai_all_tiles_in_pairs_after_draw(ai_agent):
    # Hand: d1,d1, d2,d2, d3. Drawn: d3 (forms pair d3,d3). All tiles are now paired.
    # Expected: any tile can be discarded (current logic: random choice from hand)
    # Using a more realistic 14-tile hand of 7 pairs.
    full_hand_7pairs_before_draw = [
        d1,d1, d2,d2, d3,d3, d4,d4, d5,d5, 
        b1,b1, b2 # 13 tiles, b2 is single
    ]
    drawn_tile_for_7pairs = b2 # Makes 7th pair (b2,b2)
    current_hand_7pairs = full_hand_7pairs_before_draw + [drawn_tile_for_7pairs]
    # Hand is now: [d1,d1, d2,d2, d3,d3, d4,d4, d5,d5, b1,b1, b2,b2]

    # Seed random for predictability if we wanted to assert a *specific* random choice
    # However, the current AI logic for this case is `random.choice(hand)`
    # so we just check it's one of the hand tiles.
    # random.seed(0) 
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand_7pairs), drawn_tile=drawn_tile_for_7pairs)
    assert chosen_discard in current_hand_7pairs # It must discard one of them

    # Verify that the chosen discard is indeed one of the tiles that has a count of 2 (or more)
    # For this specific hand, all counts are 2.
    counts = collections.Counter(current_hand_7pairs)
    assert counts[chosen_discard] >= 2


# 5. Edge Cases
def test_ai_empty_hand(ai_agent):
    # Test with an empty hand
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=[], drawn_tile=d1)
    assert chosen_discard is None

def test_ai_drawn_tile_not_in_hand_edge_case(ai_agent):
    # This scenario implies an issue with how the hand/drawn_tile is passed to choose_discard
    # The AI logic should still try to make a valid choice from the 'hand' it's given.
    hand = [d1, d1, d2, d3] # d1 is a pair, d2, d3 are singles
    drawn_tile_not_actually_in_hand = d4 # This tile isn't in the hand list
    
    # Current AI logic:
    # 1. `if drawn_tile in hand:` (d4 is not in hand) -> this check is effectively skipped.
    # 2. It then counts tiles in `hand`: d1 (2), d2 (1), d3 (1).
    # 3. `single_tiles` becomes `[d2, d3]`.
    # 4. `if drawn_tile in single_tiles:` (d4 is not in [d2,d3]) -> skipped.
    # 5. `return random.choice(single_tiles)` -> random choice from [d2, d3].
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile_not_actually_in_hand)
    assert chosen_discard in [d2, d3]

# Placeholder for HumanPlayerAgent tests (not part of this subtask)
# from mahjong_engine.player_agent import HumanPlayerAgent
# def test_human_player_agent_placeholder():
#    human_agent = HumanPlayerAgent(player_id=0)
#    # Example: Test current fallback for choose_discard
#    # assert human_agent.choose_discard(None, [d1,d2], d2) == d2
#    pass

def test_ai_all_tiles_in_pairs_or_triplets_forces_random_discard(ai_agent):
    # Hand where every tile is part of a pair or triplet, making no "single" tiles.
    # Let's use a 14-tile hand of 7 pairs
    hand_of_7_pairs = [
        d1, d1, d2, d2, d3, d3, d4, d4, d5, d5,
        b1, b1, b2, b2 # 14 tiles
    ]
    # The drawn_tile is one of these, completing the final pair or triplet
    drawn_tile = b2 # This tile completes the pair of b2s

    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand_of_7_pairs), drawn_tile=drawn_tile)
    assert chosen_discard in hand_of_7_pairs
    
    # Ensure that the list of single_tiles would be empty in this scenario.
    tile_counts = collections.Counter(hand_of_7_pairs)
    single_tiles = [tile for tile, count in tile_counts.items() if count == 1]
    assert not single_tiles

def test_human_player_agent_fallbacks():
    human_agent = HumanPlayerAgent(player_id=0)
    # Test choose_discard fallback
    sample_hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')]
    # Expect it to print a warning and return the last tile
    assert human_agent.choose_discard(None, sample_hand) == sample_hand[1] # Removed extra argument
    assert human_agent.choose_discard(None, []) is None # Empty hand case, also removed extra argument

    # Test decide_claim fallback
    # Expect it to print a warning and return None
    assert human_agent.decide_claim(None, Tile(SUIT_DOTS, '3'), ["PUNG"]) is None

def test_ai_drawn_forms_pair_and_other_singles_exist_specific(ai_agent):
    # Hand: d1 (existing), d2, d3, d4 (all singles before draw). Drawn: d1 (makes d1 a pair).
    # Expected: d2, d3, or d4.
    # This explicitly tests the path where drawn_tile forms a pair, and the AI must choose from other single tiles.
    hand_before_draw = [d1, d2, d3, d4]
    drawn_tile = d1 # This is the "newly drawn" tile, identical to one already in hand
    
    current_hand = list(hand_before_draw) # Make a copy
    current_hand.append(drawn_tile) # Simulate adding the drawn tile, resulting in [d1, d2, d3, d4, d1]
    
    # Ensure setup is correct: d1 is a pair, d2, d3, d4 are singles
    counts = collections.Counter(current_hand)
    assert counts[d1] == 2
    assert counts[d2] == 1
    assert counts[d3] == 1
    assert counts[d4] == 1
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
    
    # AI's logic:
    # 1. count_of_drawn_tile_in_hand for d1 will be 2.
    # 2. This skips the first `if count_of_drawn_tile_in_hand == 1:` block.
    # 3. It proceeds to the fallback: `tile_counts = collections.Counter(hand)` -> counts is {d1:2, d2:1, d3:1, d4:1}
    # 4. `single_tiles` will be `[d2, d3, d4]` (order might vary).
    # 5. `if single_tiles:` is true.
    # 6. `if drawn_tile in single_tiles:` (d1 is not in [d2,d3,d4]) -> this is false.
    # 7. `return random.choice(single_tiles)` -> should pick one of d2, d3, d4.
    assert chosen_discard in [d2, d3, d4]
    assert chosen_discard != d1 # Should not discard the tile that formed a pair
