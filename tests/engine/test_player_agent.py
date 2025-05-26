import pytest
import random
import collections
from mahjong_engine.tile import Tile
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent
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
   
    hand = [d1, d2, d3, d4]
    drawn_tile = d4
   
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4

def test_ai_discard_newly_drawn_single_tile_mixed_hand(ai_agent):
   
    hand = [d1, d1, d2, d3, d4]
    drawn_tile = d4
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4
    
def test_ai_discard_priority_drawn_tile_if_single_among_other_singles(ai_agent):
   
   
   
    hand = [d1, d2, d3, d4]
    drawn_tile = d4
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d4

# 2. Drawn Tile Forms a Pair
def test_ai_drawn_tile_forms_pair_does_not_discard_drawn(ai_agent):
   
   
   
    hand_content = [d1, d2, d3, d1]
    drawn_tile = d1
    
   
    assert collections.Counter(hand_content)[d1] == 2
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand_content), drawn_tile=drawn_tile)
   
   
    assert chosen_discard in [d2, d3]
    assert chosen_discard != d1


# 3. Discarding Other Single Tiles
def test_ai_drawn_tile_forms_pair_discards_other_single(ai_agent):
   
   
    hand_before_draw = [d1, d2, d3, d4]
    drawn_tile = d1
    current_hand = hand_before_draw + [drawn_tile]
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
    
   
   
    assert chosen_discard in [d2, d3, d4]
    assert chosen_discard != d1

def test_ai_drawn_tile_forms_third_of_a_kind_discards_single(ai_agent):
   
   
    hand_before_draw = [d1, d1, d2, d3]
    drawn_tile = d1
    current_hand = hand_before_draw + [drawn_tile]
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
   
   
    assert chosen_discard in [d2, d3]

# This test might be redundant if the above covers the logic sufficiently.
# It tests when drawn_tile is a single, but other tiles form pairs.
def test_ai_drawn_tile_is_single_others_are_pairs(ai_agent):
   
    hand = [d1,d1,d2,d2,d3]
    drawn_tile = d3
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile)
    assert chosen_discard == d3


# 4. All Tiles in Pairs/Sets
def test_ai_all_tiles_in_pairs_after_draw(ai_agent):
   
   
   
    full_hand_7pairs_before_draw = [
        d1,d1, d2,d2, d3,d3, d4,d4, d5,d5, 
        b1,b1, b2
    ]
    drawn_tile_for_7pairs = b2
    current_hand_7pairs = full_hand_7pairs_before_draw + [drawn_tile_for_7pairs]
   

   
   
   
   
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand_7pairs), drawn_tile=drawn_tile_for_7pairs)
    assert chosen_discard in current_hand_7pairs

   
   
    counts = collections.Counter(current_hand_7pairs)
    assert counts[chosen_discard] >= 2


# 5. Edge Cases
def test_ai_empty_hand(ai_agent):
   
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=[], drawn_tile=d1)
    assert chosen_discard is None

def test_ai_drawn_tile_not_in_hand_edge_case(ai_agent):
   
   
    hand = [d1, d1, d2, d3]
    drawn_tile_not_actually_in_hand = d4
    
   
   
   
   
   
   
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(hand), drawn_tile=drawn_tile_not_actually_in_hand)
    assert chosen_discard in [d2, d3]

# Placeholder for HumanPlayerAgent tests (not part of this subtask)
# from mahjong_engine.player_agent import HumanPlayerAgent
# def test_human_player_agent_placeholder():
#    human_agent = HumanPlayerAgent(player_id=0)
#   
#   
#    pass

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

def test_ai_drawn_forms_pair_and_other_singles_exist_specific(ai_agent):
   
   
   
    hand_before_draw = [d1, d2, d3, d4]
    drawn_tile = d1
    
    current_hand = list(hand_before_draw)
    current_hand.append(drawn_tile)
    
   
    counts = collections.Counter(current_hand)
    assert counts[d1] == 2
    assert counts[d2] == 1
    assert counts[d3] == 1
    assert counts[d4] == 1
    
    chosen_discard = ai_agent.choose_discard(game_state=None, hand=list(current_hand), drawn_tile=drawn_tile)
    
   
   
   
   
   
   
   
   
    assert chosen_discard in [d2, d3, d4]
    assert chosen_discard != d1
