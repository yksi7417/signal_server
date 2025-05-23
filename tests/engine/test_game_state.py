import pytest
import collections
from unittest.mock import MagicMock # Added for mocking
from mahjong_engine.game_state import GameState
from mahjong_engine.tile import Tile
from mahjong_engine.player import Player
from mahjong_engine.player_agent import HumanPlayerAgent, AIPlayerAgent
from mahjong_engine.melds import Pung, MeldType
from mahjong_engine.constants import (
    NUM_PLAYERS, INIT_HAND_SIZE, TILE_CATEGORIES_FOR_GENERATION,
    NUM_COPIES_PER_TILE, WIND_EAST, SUIT_DOTS, SUIT_WINDS, WIND_NORTH,
    SUIT_BAMBOO, SUIT_CHARACTERS
)

@pytest.fixture
def game():
    """Yields a fresh GameState() instance for each test."""
    return GameState()

# Test Initialization
def test_game_state_initialization(game):
    assert len(game.players) == NUM_PLAYERS
    
    expected_wall_size = (sum(len(values) for _, values in TILE_CATEGORIES_FOR_GENERATION) * NUM_COPIES_PER_TILE) - (NUM_PLAYERS * INIT_HAND_SIZE)
    assert len(game.wall) == expected_wall_size
    
    for i, player in enumerate(game.players):
        assert isinstance(player, Player)
        assert player.player_id == i
        assert len(player.hand) == INIT_HAND_SIZE
        if i == 0:
            assert isinstance(player.agent, HumanPlayerAgent)
        else:
            assert isinstance(player.agent, AIPlayerAgent)
            
    assert game.current_player_index == 0
    assert game.game_wind == WIND_EAST
    assert game.turn_number == 0
    assert game.current_discard is None
    assert game.pending_claim_player_id is None
    assert game.potential_claim_tile is None # Added from GameState structure
    assert game.claim_type_pending is None   # Added from GameState structure

# Test Tile Set Creation Content
def test_create_full_tile_set_content(game):
    all_initial_tiles = list(game.wall) # Make a mutable copy
    for player in game.players:
        all_initial_tiles.extend(player.hand)
        
    expected_total_tiles = sum(len(values) for _, values in TILE_CATEGORIES_FOR_GENERATION) * NUM_COPIES_PER_TILE
    assert len(all_initial_tiles) == expected_total_tiles
    
    tile_counts = collections.Counter(all_initial_tiles)
    
    # Sample tiles to check counts
    sample_dot_tile = Tile(SUIT_DOTS, '1')
    sample_wind_tile = Tile(SUIT_WINDS, WIND_EAST)
    
    assert tile_counts[sample_dot_tile] == NUM_COPIES_PER_TILE
    assert tile_counts[sample_wind_tile] == NUM_COPIES_PER_TILE
    
    # Check another wind tile for good measure
    sample_north_wind = Tile(SUIT_WINDS, WIND_NORTH)
    assert tile_counts[sample_north_wind] == NUM_COPIES_PER_TILE

# Test Drawing a Tile
def test_draw_tile_for_current_player(game):
    player = game.players[game.current_player_index]
    
    # Ensure player hand is at INIT_HAND_SIZE for a clean test start if needed
    # (though fixture should provide this state)
    if len(player.hand) != INIT_HAND_SIZE:
        # This would indicate a problem with the fixture or previous test interference if not careful
        # For this test, we assume the fixture sets up the initial state correctly.
        player.hand = player.hand[:INIT_HAND_SIZE] # Simplified adjustment
        # Wall might also need adjustment if this were a real recovery
    
    original_wall_size = len(game.wall)
    
    drawn_tile = game.draw_tile_for_current_player()
    assert drawn_tile is not None
    assert len(player.hand) == INIT_HAND_SIZE + 1
    assert len(game.wall) == original_wall_size - 1
    assert drawn_tile in player.hand
    
    # Try to draw again (should fail as hand is full)
    second_drawn_tile = game.draw_tile_for_current_player()
    assert second_drawn_tile is None
    assert len(player.hand) == INIT_HAND_SIZE + 1 # Hand size should not change

# Test Drawing with Empty Wall
def test_draw_tile_empty_wall(game):
    player = game.players[game.current_player_index]
    # Ensure player's hand is at the normal pre-draw size
    player.hand = player.hand[:INIT_HAND_SIZE] 
    
    game.wall = [] # Empty the wall
    
    drawn_tile = game.draw_tile_for_current_player()
    assert drawn_tile is None
    assert len(player.hand) == INIT_HAND_SIZE # Hand size should not change

# Test Basic Discard Operation
def test_discard_tile_for_current_player_basic(game):
    player = game.players[game.current_player_index]
    
    # Player draws first
    draw_success = game.draw_tile_for_current_player()
    assert draw_success is not None, "Setup: Player failed to draw a tile."
    assert len(player.hand) == INIT_HAND_SIZE + 1
    
    tile_to_discard = player.hand[0] # Choose first tile to discard
    tile_repr = {"suit": tile_to_discard.suit, "value": tile_to_discard.value}
    
    original_hand_size_before_discard = len(player.hand)
    initial_turn = game.turn_number
    initial_player_idx = game.current_player_index
    
    success = game.discard_tile_for_current_player(tile_repr)
    assert success is True
    
    assert len(player.hand) == original_hand_size_before_discard - 1
    assert game.current_discard == tile_to_discard
    assert tile_to_discard in player.discards
    
    # Conditional assertion for turn advancement (depends on claim checks)
    if game.pending_claim_player_id is None:
        assert game.current_player_index == (initial_player_idx + 1) % NUM_PLAYERS
        assert game.turn_number == initial_turn + 1
    else:
        # If a claim is pending (e.g. HumanPlayerAgent can Pung), turn does not advance yet.
        assert game.current_player_index == initial_player_idx
        # turn_number also should not advance until claim resolved or AI plays through
        # The provided GameState.discard_tile_for_current_player advances turn if no claim,
        # so this 'else' branch might only be hit if AI claims are implemented and an AI claims.
        # For Human Pung claim, discard_tile returns True, but turn advancement is paused.
        # The logic in discard_tile_for_current_player:
        # - if Human can claim, it returns True, current_player_index is NOT advanced yet.
        # - if AI can claim (but doesn't for now), it passes.
        # - if no claim is pending, then current_player_index is advanced.
        # So, if pending_claim_player_id is set (to player 0 for human), index hasn't changed.
        assert game.turn_number == initial_turn # Turn number doesn't advance if human claim is pending

# Test Discard with Invalid Hand Size
def test_discard_tile_invalid_hand_size(game):
    player = game.players[game.current_player_index]
    assert len(player.hand) == INIT_HAND_SIZE # Should have 13 tiles, not 14
    
    tile_to_discard = player.hand[0]
    tile_repr = {"suit": tile_to_discard.suit, "value": tile_to_discard.value}
    
    success = game.discard_tile_for_current_player(tile_repr)
    assert success is False

# Test Discarding a Tile Not in Hand
def test_discard_tile_not_in_hand(game):
    player = game.players[game.current_player_index]
    
    draw_success = game.draw_tile_for_current_player()
    assert draw_success is not None, "Setup: Player failed to draw a tile."
    assert len(player.hand) == INIT_HAND_SIZE + 1
    
    # Create a tile representation that is guaranteed not to be in the hand
    # (assuming "NonExistentSuit" and "NonExistentValue" are not valid constants)
    non_existent_tile_repr = {"suit": "NonExistentSuit", "value": "NonExistentValue"}
    
    success = game.discard_tile_for_current_player(non_existent_tile_repr)
    assert success is False

def test_discard_leads_to_human_pung_claim_opportunity(game):
    # Player 0: Human, Player 1: AI
    player0 = game.players[0]
    player1 = game.players[1]
    
    # Setup Player 0's hand to have two Dots '1'
    player0.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(3, 13)] # 13 tiles
    
    # Set current player to Player 1
    game.current_player_index = 1
    
    # Player 1 draws a tile (needs 14 to discard)
    # Ensure player1's hand is reasonable for drawing one tile
    player1.hand = [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 14)] # 13 tiles
    # Clear player1's discards for this test to avoid confusion
    player1.discards = [] 

    game.draw_tile_for_current_player() # Player 1 draws
    assert len(player1.hand) == INIT_HAND_SIZE + 1
    
    # Player 1 discards Dots '1'
    discarded_tile_repr = {"suit": SUIT_DOTS, "value": '1'}
    # Find the actual Dots '1' in player1's hand to make discard valid, or add it.
    # Replace one of player1's tiles with a Dots '1'
    tile_to_be_discarded_by_p1 = Tile(SUIT_DOTS, '1')
    
    # Ensure the tile to be discarded is actually in P1's hand by replacing one
    # This setup is crucial for discard_tile_for_current_player to find and remove the tile.
    if player1.hand: 
        player1.hand[0] = tile_to_be_discarded_by_p1 
    else: # Should not happen with above setup if draw was successful
        player1.hand.append(tile_to_be_discarded_by_p1)


    original_discarder_index = game.current_player_index # Should be 1
    
    success_discard = game.discard_tile_for_current_player(discarded_tile_repr)
    assert success_discard

    # Assert that Player 0 (Human) has a pending Pung claim
    assert game.pending_claim_player_id == 0
    assert game.claim_type_pending == "PUNG"
    assert game.potential_claim_tile == Tile(SUIT_DOTS, '1')
    # Crucially, turn should NOT have advanced past player 1 yet because human claim is pending
    assert game.current_player_index == original_discarder_index 

def test_process_pung_claim_successful(game):
    player0 = game.players[0]
    discarding_player_id = 1 # Assume player 1 discarded

    # Setup game state for a pending Pung claim by Player 0
    game.pending_claim_player_id = 0
    game.claim_type_pending = "PUNG"
    tile_being_claimed = Tile(SUIT_DOTS, '1')
    game.potential_claim_tile = tile_being_claimed
    game.current_discard = tile_being_claimed # This would have been set by discarder
    game.current_player_index = discarding_player_id # It was player 1's turn when they discarded

    # Setup Player 0's hand
    player0.hand = [
        Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'), # The two tiles for Pung
        Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'), Tile(SUIT_DOTS, '4'),
        Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
        Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_CHARACTERS, '9'),
        Tile(SUIT_WINDS, WIND_EAST), Tile(SUIT_WINDS, WIND_EAST) # 13 tiles
    ]
    original_hand_count_for_pung_tile = player0.hand.count(tile_being_claimed) # Should be 2
    
    success = game.process_pung_claim(claiming_player_id=0, claimed_tile=tile_being_claimed)
    assert success

    assert player0.hand.count(tile_being_claimed) == original_hand_count_for_pung_tile - 2
    assert len(player0.revealed_sets) == 1
    revealed_pung = player0.revealed_sets[0]
    assert isinstance(revealed_pung, Pung) # Check it's a Pung object
    assert revealed_pung.meld_type == MeldType.PUNG
    assert revealed_pung.key_tile == tile_being_claimed 
    assert revealed_pung.revealed 
    assert revealed_pung.claimed_from == discarding_player_id 

    assert game.current_player_index == 0 # Player 0's turn now
    assert game.pending_claim_player_id is None
    assert game.claim_type_pending is None
    assert game.potential_claim_tile is None
    assert len(player0.hand) == INIT_HAND_SIZE - 2 


def test_process_pung_claim_invalid_inputs(game):
    assert not game.process_pung_claim(claiming_player_id=None, claimed_tile=Tile(SUIT_DOTS, '1'))
    assert not game.process_pung_claim(claiming_player_id=0, claimed_tile=None)
    # Test with a player_id that is out of bounds
    assert not game.process_pung_claim(claiming_player_id=NUM_PLAYERS + 1, claimed_tile=Tile(SUIT_DOTS, '1')) 

def test_process_pung_claim_player_lacks_tiles(game):
    player0 = game.players[0]
    discarding_player_id = 1

    game.pending_claim_player_id = 0
    game.claim_type_pending = "PUNG"
    tile_being_claimed = Tile(SUIT_DOTS, '1')
    game.potential_claim_tile = tile_being_claimed
    game.current_discard = tile_being_claimed
    game.current_player_index = discarding_player_id

    # Player 0 only has one Dots '1' (or none)
    player0.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(3, 14)] # Only one '1'
    original_hand = list(player0.hand)
    original_revealed_sets_count = len(player0.revealed_sets)

    success = game.process_pung_claim(claiming_player_id=0, claimed_tile=tile_being_claimed)
    assert not success # Should fail because player doesn't have two matching tiles
    
    # Ensure state was not changed significantly
    assert player0.hand == original_hand # Hand should be unchanged
    assert len(player0.revealed_sets) == original_revealed_sets_count # No new meld
    assert game.current_player_index == discarding_player_id # Turn should not have changed to player0
    # The claim state should ideally remain if processing failed mid-way before resetting,
    # or be reset if the failure is determined early.
    # For this test, the crucial part is that the claim didn't succeed and player state is consistent.
    # Depending on GameState.process_pung_claim's exact error handling,
    # these might still be set if failure is late:
    # assert game.pending_claim_player_id == 0
    # assert game.claim_type_pending == "PUNG"

# --- Tests for run_ai_turn ---

def test_run_ai_turn_successful_no_human_claim(game):
    # Set current player to Player 1 (AI)
    game.current_player_index = 1
    ai_player = game.players[1]
    assert isinstance(ai_player.agent, AIPlayerAgent)

    # Ensure wall has enough tiles
    if not game.wall: # Should not be empty from fixture, but good check
        game.wall = [Tile(SUIT_DOTS, str(i % 9 + 1)) for i in range(20)] 

    original_wall_size = len(game.wall)
    # original_ai_hand_size = len(ai_player.hand) # Should be 13 from fixture

    result = game.run_ai_turn()
    # print("AI turn result (no claim):", result) # For debugging

    assert result["success"]
    assert result["ai_player_id"] == ai_player.player_id
    assert "suit" in result["discarded_tile"] and "value" in result["discarded_tile"]
    
    assert len(ai_player.hand) == INIT_HAND_SIZE # Drew 1, discarded 1
    assert game.current_discard is not None
    assert game.current_discard == Tile(result["discarded_tile"]["suit"], result["discarded_tile"]["value"])
    assert game.current_discard in ai_player.discards
    
    # Assuming Player 0 (human) cannot claim this discard based on default hand setup
    assert not result["human_can_claim_pung"] 
    assert game.pending_claim_player_id is None # No pending claim
    assert game.current_player_index == (1 + 1) % NUM_PLAYERS # Advanced to next player


def test_run_ai_turn_leads_to_human_pung_claim(game):
    game.current_player_index = 1 # AI Player 1's turn
    ai_player = game.players[1]
    human_player = game.players[0]

    # AI will discard Dots '5'. Setup human hand for Pung.
    tile_ai_will_discard = Tile(SUIT_DOTS, '5')
    human_player.hand = [Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '5'), Tile(SUIT_BAMBOO, '1')] + [Tile(SUIT_DOTS, str(i)) for i in range(1,11) if str(i) != '5'] # Make it 13
    human_player.hand = human_player.hand[:INIT_HAND_SIZE]


    # Modify AI's hand so it's likely to discard Dots '5'
    # Easiest: ensure Dots '5' is the only "single" tile after AI draws, or mock choose_discard.
    
    # Mock the AI's choose_discard method for this test.
    original_ai_choose_discard = ai_player.agent.choose_discard
    def mock_choose_discard(game_state, hand, drawn_tile):
        # To ensure the test is robust, make sure tile_ai_will_discard is in hand.
        # The AI's actual hand after drawing will be passed here.
        # We need to ensure tile_ai_will_discard is part of that hand and is chosen.
        # For this mock, we assume the test setup will ensure tile_ai_will_discard is in `hand`.
        if tile_ai_will_discard in hand:
            return tile_ai_will_discard
        return hand[0] # Fallback, but test setup should prevent this.
    
    ai_player.agent.choose_discard = mock_choose_discard
    
    # Setup AI's hand so it *contains* the tile_ai_will_discard before drawing its 14th tile.
    # The mock will then ensure it's chosen.
    # Remove one tile and add the one we want to discard.
    ai_player.hand.pop() 
    ai_player.hand.append(tile_ai_will_discard)
    assert len(ai_player.hand) == INIT_HAND_SIZE


    result = game.run_ai_turn()
    # print("AI turn result (human can claim):", result) # For debugging

    ai_player.agent.choose_discard = original_ai_choose_discard # Restore original method

    assert result["success"]
    assert result["ai_player_id"] == ai_player.player_id
    assert Tile(result["discarded_tile"]["suit"], result["discarded_tile"]["value"]) == tile_ai_will_discard
    
    assert result["human_can_claim_pung"]
    assert Tile(result["claimable_tile"]["suit"], result["claimable_tile"]["value"]) == tile_ai_will_discard
    assert game.pending_claim_player_id == 0
    assert game.claim_type_pending == "PUNG"
    assert game.current_player_index == ai_player.player_id # Turn paused at AI

def test_run_ai_turn_wall_empty(game):
    game.current_player_index = 1 # AI Player
    ai_player = game.players[1]
    # Ensure AI player has a normal hand before trying to draw
    # This is already handled by the fixture, but an explicit slice ensures it if tests run out of order or modify hand.
    ai_player.hand = ai_player.hand[:INIT_HAND_SIZE]

    game.wall = []
    result = game.run_ai_turn()
    
    assert not result["success"]
    assert "Wall empty" in result.get("error", "")
    assert len(ai_player.hand) == INIT_HAND_SIZE # Hand size unchanged

def test_run_ai_turn_called_on_human_player(game):
    game.current_player_index = 0 # Human Player
    result = game.run_ai_turn()
    
    assert not result["success"]
    assert "Not an AI player" in result.get("error", "")

def test_discard_tile_ai_hypothetically_claims_pung(game):
    # Player 0 (Human) discards, Player 1 (AI) can claim Pung.
    # We'll mock Player 1's AI to decide to claim.
    human_player = game.players[0]
    ai_player = game.players[1]
    
    # Ensure AIPlayerAgent is assigned to player 1
    if not isinstance(ai_player.agent, AIPlayerAgent): # Should be true from fixture
        ai_player.agent = AIPlayerAgent(player_id=1) 

    # Setup AI player's hand to have two Dots '1'
    ai_player.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'), Tile(SUIT_BAMBOO, '2')] + [Tile(SUIT_DOTS, str(i)) for i in range(3, 14)]
    ai_player.hand = ai_player.hand[:INIT_HAND_SIZE]


    # Player 0 (Human) is current player
    game.current_player_index = 0
    # Human draws
    # Ensure human has a tile to draw
    if not game.wall: game.wall = [Tile(SUIT_BAMBOO, '5')]
    game.draw_tile_for_current_player()
    assert len(human_player.hand) == INIT_HAND_SIZE + 1
    
    # Human discards Dots '1'
    tile_human_discards = Tile(SUIT_DOTS, '1')
    # Ensure human has this tile to discard
    human_player.hand[0] = tile_human_discards 
    discard_repr = {"suit": tile_human_discards.suit, "value": tile_human_discards.value}

    # Mock AI's decide_claim to return "PUNG"
    original_decide_claim = ai_player.agent.decide_claim
    # The actual return value of decide_claim is not used by GameState for AI claims yet.
    # GameState's discard_tile_for_current_player calls can_form_pung_with_discard.
    # The current AIPlayerAgent.decide_claim returns None and GameState has a 'pass'
    # for AI claims. This test primarily verifies the decide_claim method is called.
    ai_player.agent.decide_claim = MagicMock(return_value="PUNG") 
                                                                
    game.discard_tile_for_current_player(discard_repr)
    
    # Assert that the AI's decide_claim method was called
    # The can_form_pung_with_discard check happens first. If true, then decide_claim is called.
    # Note: The current logic in discard_tile_for_current_player for AIPlayerAgent is:
    #   claim_decision = other_player.agent.decide_claim(self, self.potential_claim_tile, ["PUNG"])
    #   pass # AI does nothing for now.
    # So, decide_claim IS called. The 'pass' means no claim processing occurs for AI.
    ai_player.agent.decide_claim.assert_called_once_with(game, tile_human_discards, ["PUNG"])

    # Since current AI doesn't act on claim (due to 'pass'), game should proceed as if no AI claim.
    # If Player 0 discarded, and Player 1 (AI) was checked (and decided_claim called but ignored),
    # then Player 2 and Player 3 (AIs) would also be checked. If they don't claim, turn advances.
    # Assuming Player 2 and 3 don't have tiles for Pung for this discard.
    assert game.pending_claim_player_id is None # No human claim, AI claim ignored.
    assert game.current_player_index == (0 + 1) % NUM_PLAYERS # Turn should advance past Player 0.
    
    ai_player.agent.decide_claim = original_decide_claim # Restore


# Test for run_ai_turn: AI hand empty after draw (very edge case)
def test_run_ai_turn_ai_hand_empty_after_draw_failsafe(game):
    game.current_player_index = 1 # AI Player
    ai_player = game.players[1]
    
    # Mock draw_tile_for_current_player to return a tile but also empty the hand
    # This is to test the specific 'else: return {"success": False, "error": "AI hand empty..."}'
    original_draw = game.draw_tile_for_current_player
    drawn_tile_for_test = Tile(SUIT_DOTS, '7') # A tile to be "drawn"
    
    def mock_draw_and_empty_hand():
        # Simulate that a tile was drawn (for choose_discard to receive it)
        # but then the hand becomes empty before choose_discard can operate on a populated hand.
        # This is a very specific edge case for the 'if ai_player.hand:' check in run_ai_turn's fallback.
        ai_player.hand = [] 
        return drawn_tile_for_test # Return the tile that was "drawn"
    
    game.draw_tile_for_current_player = mock_draw_and_empty_hand

    result = game.run_ai_turn()
    assert not result["success"]
    assert result.get("error") == "AI hand empty after draw, cannot discard."

    game.draw_tile_for_current_player = original_draw # Restore
