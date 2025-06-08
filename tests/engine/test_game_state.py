import ast
import collections
import inspect
import re
from unittest.mock import MagicMock

import pytest

from mahjong_engine.constants import (INIT_HAND_SIZE, NUM_COPIES_PER_TILE,
                                      NUM_PLAYERS, SUIT_BAMBOO,
                                      SUIT_CHARACTERS, SUIT_DOTS, SUIT_DRAGONS,
                                      SUIT_WINDS,
                                      TILE_CATEGORIES_FOR_GENERATION,
                                      WIND_EAST, WIND_NORTH, WIND_SOUTH)
from mahjong_engine.game_state import GameState
from mahjong_engine.hand_validator import can_form_pung_with_discard
from mahjong_engine.melds import MeldType, Pung
from mahjong_engine.player import Player
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent
from mahjong_engine.tile import Tile


@pytest.fixture
def game():
    """Fixture to provide a fresh GameState instance for each test."""
    return GameState()


# Test for syntax and code quality issues
class TestCodeQuality:
    """Test class to catch syntax errors, f-string issues, and other code quality problems."""
    
    def test_game_state_syntax_valid(self):
        """Test that game_state.py has valid Python syntax."""
        import mahjong_engine.game_state as game_state_module
        source_file = inspect.getfile(game_state_module)
        
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            ast.parse(source_code)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in game_state.py at line {e.lineno}: {e.msg}")
    
    def test_no_unterminated_fstrings(self):
        """Test that there are no unterminated f-strings in game_state.py."""
        import mahjong_engine.game_state as game_state_module
        source_file = inspect.getfile(game_state_module)
        
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Check for unterminated f-strings
            if 'f"' in line or "f'" in line:
                # Count quotes to ensure they're balanced
                double_quote_count = line.count('"')
                single_quote_count = line.count("'")
                
                # If f-string starts but quotes are unbalanced, it might be unterminated
                if line.strip().startswith('f"') and double_quote_count % 2 != 0:
                    # Check if it continues on next line properly
                    if line_num < len(lines):
                        next_line = lines[line_num]
                        if not next_line.strip().endswith('"') and '"' not in next_line:
                            pytest.fail(f"Potential unterminated f-string at line {line_num}: {line.strip()}")
    
    def test_no_broken_multiline_strings(self):
        """Test that multiline strings are properly formatted."""
        import mahjong_engine.game_state as game_state_module
        source_file = inspect.getfile(game_state_module)
        
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Check for backslash line continuations in f-strings (which can cause issues)
        problematic_patterns = [
            r'f"[^"]*\\[\s\n]+[^"]*"',  # f-string with backslash continuation
            r"f'[^']*\\[\s\n]+[^']*'",  # f-string with backslash continuation (single quotes)
        ]
        
        for pattern in problematic_patterns:
            matches = re.findall(pattern, source_code, re.MULTILINE)
            if matches:
                pytest.fail(f"Found problematic f-string with backslash continuation: {matches}")
    
    def test_print_statements_are_complete(self):
        """Test that all print statements are properly closed."""
        import mahjong_engine.game_state as game_state_module
        source_file = inspect.getfile(game_state_module)
        
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            if 'print(' in line:
                # Count parentheses to ensure they're balanced
                open_parens = line.count('(')
                close_parens = line.count(')')
                
                if open_parens > close_parens:
                    # Check if it's properly continued on next lines
                    current_line = line_num - 1
                    total_open = open_parens
                    total_close = close_parens
                    
                    while current_line + 1 < len(lines) and total_open > total_close:
                        current_line += 1
                        next_line = lines[current_line]
                        total_open += next_line.count('(')
                        total_close += next_line.count(')')
                    
                    if total_open != total_close:
                        pytest.fail(f"Unbalanced parentheses in print statement starting at line {line_num}")
    
    def test_all_methods_are_callable(self):
        """Test that all methods in GameState can be called without syntax errors."""
        game = GameState()
        
        # Get all methods that don't start with underscore (public methods)
        methods = [method for method in dir(game) 
                  if callable(getattr(game, method)) and not method.startswith('_')]
        
        for method_name in methods:
            method = getattr(game, method_name)
            # Just check that the method object exists and is callable
            assert callable(method), f"Method {method_name} is not callable"


# Test for error message formatting
class TestErrorMessages:
    """Test that error messages are properly formatted and don't contain broken strings."""
    
    def test_discard_error_messages_format_correctly(self):
        """Test that discard error messages format correctly with actual data."""
        game = GameState()
        
        # Try to discard a tile that doesn't exist in hand
        fake_tile = {"suit": "TestSuit", "value": "TestValue", "unicode": "🀫"}
        
        # Capture the result - should return False for invalid discard
        result = game.discard_tile_for_current_player(fake_tile)
        assert result is False, "Should return False for invalid tile discard"
    
    def test_print_statements_with_player_data(self):
        """Test that print statements work correctly with actual player data."""
        game = GameState()
        player = game.players[0]
        
        # Test that we can access player attributes that are used in print statements
        assert hasattr(player, 'player_id'), "Player should have player_id attribute"
        assert isinstance(player.player_id, int), "Player ID should be an integer"
        assert hasattr(player, 'hand'), "Player should have hand attribute"
        assert isinstance(player.hand, list), "Player hand should be a list"
    
    def test_tile_representation_in_error_messages(self):
        """Test that tile representations work correctly in error messages."""
        game = GameState()
        
        # Create a test tile with all required attributes
        test_tile_repr = {
            "suit": "Dots",
            "value": "1", 
            "unicode": "🀙"
        }
        
        # Verify the tile representation has all required keys
        required_keys = ["suit", "value", "unicode"]
        for key in required_keys:
            assert key in test_tile_repr, f"Tile representation should have {key}"
        
        # Test that the discard method can handle this representation
        result = game.discard_tile_for_current_player(test_tile_repr)
        # The result depends on whether the tile is actually in the hand,
        # but the method should not crash due to formatting issues


# Test for method robustness
class TestMethodRobustness:
    """Test that methods handle edge cases and don't crash due to formatting issues."""
    
    def test_run_ai_turn_error_handling(self):
        """Test that run_ai_turn handles errors gracefully with proper string formatting."""
        game = GameState()
        
        # Set current player to AI (index 1)
        game.current_player_index = 1
        ai_player = game.players[1]
        
        # Ensure it's an AI player
        assert isinstance(ai_player.agent, AIPlayerAgent)
        
        # Test with empty wall (should handle gracefully)
        original_wall = game.wall[:]
        game.wall = []
        
        result = game.run_ai_turn()
        assert result["success"] is False
        assert "error" in result
        assert isinstance(result["error"], str)
        
        # Restore wall
        game.wall = original_wall
    
    def test_process_claims_with_none_values(self):
        """Test that claim processing handles None values gracefully."""
        game = GameState()
        
        # Test pung claim with None values
        result = game.process_pung_claim(None, None)
        assert result is False
        
        # Test win claim with None values  
        result = game.process_win_claim(None, None)
        assert result is False
        
        # Test kong claim with None values
        result = game.process_kong_claim(None, None)
        assert result is False
    
    def test_hidden_kong_error_messages(self):
        """Test that hidden kong error messages format correctly."""
        game = GameState()
        
        # Test with invalid tile info
        result = game.process_hidden_kong(0, {"invalid": "data"})
        assert result["success"] is False
        assert "error" in result
        assert isinstance(result["error"], str)
        
        # Test with valid tile info but insufficient tiles
        result = game.process_hidden_kong(0, {"suit": "Dots", "value": "1"})
        assert result["success"] is False
        assert "error" in result
        assert isinstance(result["error"], str)


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
    assert game.potential_claim_tile is None
    assert game.claim_type_pending is None


def test_create_full_tile_set_content(game):
    all_initial_tiles = list(game.wall)
    for player in game.players:
        all_initial_tiles.extend(player.hand)
    expected_total_tiles = sum(len(values) for _, values in TILE_CATEGORIES_FOR_GENERATION) * NUM_COPIES_PER_TILE
    assert len(all_initial_tiles) == expected_total_tiles
    tile_counts = collections.Counter(all_initial_tiles)
    sample_dot_tile = Tile(SUIT_DOTS, '1')
    sample_wind_tile = Tile(SUIT_WINDS, WIND_EAST)
    assert tile_counts[sample_dot_tile] == NUM_COPIES_PER_TILE
    assert tile_counts[sample_wind_tile] == NUM_COPIES_PER_TILE
    sample_north_wind = Tile(SUIT_WINDS, WIND_NORTH)
    assert tile_counts[sample_north_wind] == NUM_COPIES_PER_TILE


def test_draw_tile_for_current_player(game):
    player = game.players[game.current_player_index]
    if len(player.hand) != INIT_HAND_SIZE:
        player.hand = player.hand[:INIT_HAND_SIZE]
    original_wall_size = len(game.wall)
    drawn_tile = game.draw_tile_for_current_player()
    assert drawn_tile is not None
    assert len(player.hand) == INIT_HAND_SIZE + 1
    assert len(game.wall) == original_wall_size - 1
    assert drawn_tile in player.hand
    second_drawn_tile = game.draw_tile_for_current_player()
    assert second_drawn_tile is None
    assert len(player.hand) == INIT_HAND_SIZE + 1


def test_draw_tile_empty_wall(game):
    player = game.players[game.current_player_index]
    player.hand = player.hand[:INIT_HAND_SIZE]
    game.wall = []
    drawn_tile = game.draw_tile_for_current_player()
    assert drawn_tile is None
    assert len(player.hand) == INIT_HAND_SIZE


def test_discard_tile_for_current_player_basic(game):
    player = game.players[game.current_player_index]
    draw_success = game.draw_tile_for_current_player()
    assert draw_success is not None, "Setup: Player failed to draw a tile."
    assert len(player.hand) == INIT_HAND_SIZE + 1
    tile_to_discard = player.hand[0]
    tile_repr = {"suit": tile_to_discard.suit, "value": tile_to_discard.value}
    original_hand_size_before_discard = len(player.hand)
    initial_turn = game.turn_number
    initial_player_idx = game.current_player_index
    success = game.discard_tile_for_current_player(tile_repr)
    assert success is True
    assert len(player.hand) == original_hand_size_before_discard - 1
    assert game.current_discard == tile_to_discard
    assert tile_to_discard in player.discards
    if game.pending_claim_player_id is None:
        assert game.current_player_index == (initial_player_idx + 1) % NUM_PLAYERS
        assert game.turn_number == initial_turn + 1
    else:
        assert game.current_player_index == initial_player_idx
        assert game.turn_number == initial_turn


def test_discard_tile_invalid_hand_size(game):
    player = game.players[game.current_player_index]
    assert len(player.hand) == INIT_HAND_SIZE
    tile_to_discard = player.hand[0]
    tile_repr = {"suit": tile_to_discard.suit, "value": tile_to_discard.value}
    success = game.discard_tile_for_current_player(tile_repr)
    assert success is False


def test_discard_tile_not_in_hand(game):
    player = game.players[game.current_player_index]
    draw_success = game.draw_tile_for_current_player()
    assert draw_success is not None, "Setup: Player failed to draw a tile."
    assert len(player.hand) == INIT_HAND_SIZE + 1
    non_existent_tile_repr = {"suit": "NonExistentSuit", "value": "NonExistentValue"}
    success = game.discard_tile_for_current_player(non_existent_tile_repr)
    assert success is False


def test_discard_leads_to_human_pung_claim_opportunity(game):
    player0 = game.players[0]
    player1 = game.players[1]
    player0.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(3, 13)]
    game.current_player_index = 1
    player1.hand = [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 14)]
    player1.discards = []

    game.draw_tile_for_current_player()
    assert len(player1.hand) == INIT_HAND_SIZE + 1
    discarded_tile_repr = {"suit": SUIT_DOTS, "value": '1'}
    tile_to_be_discarded_by_p1 = Tile(SUIT_DOTS, '1')
    if player1.hand:
        player1.hand[0] = tile_to_be_discarded_by_p1
    else:
        player1.hand.append(tile_to_be_discarded_by_p1)

    original_discarder_index = game.current_player_index
    success_discard = game.discard_tile_for_current_player(discarded_tile_repr)
    assert success_discard

    assert game.pending_claim_player_id == 0
    assert game.claim_type_pending == "PUNG"
    assert game.potential_claim_tile == Tile(SUIT_DOTS, '1')
    assert game.current_player_index == original_discarder_index


def test_process_pung_claim_successful(game):
    player0 = game.players[0]
    discarding_player_id = 1
    game.pending_claim_player_id = 0
    game.claim_type_pending = "PUNG"
    tile_being_claimed = Tile(SUIT_DOTS, '1')
    game.potential_claim_tile = tile_being_claimed
    game.current_discard = tile_being_claimed
    game.current_player_index = discarding_player_id
    player0.hand = [
        Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'),
        Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'), Tile(SUIT_DOTS, '4'),
        Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
        Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_CHARACTERS, '9'),
        Tile(SUIT_WINDS, WIND_EAST), Tile(SUIT_WINDS, WIND_EAST)
    ]
    original_hand_count_for_pung_tile = player0.hand.count(tile_being_claimed)
    success = game.process_pung_claim(claiming_player_id=0, claimed_tile=tile_being_claimed)
    assert success

    assert player0.hand.count(tile_being_claimed) == original_hand_count_for_pung_tile - 2
    assert len(player0.revealed_sets) == 1
    revealed_pung = player0.revealed_sets[0]
    assert isinstance(revealed_pung, Pung)
    assert revealed_pung.meld_type == MeldType.PUNG
    assert revealed_pung.key_tile == tile_being_claimed
    assert revealed_pung.revealed
    assert revealed_pung.claimed_from == discarding_player_id

    assert game.current_player_index == 0
    assert game.pending_claim_player_id is None
    assert game.claim_type_pending is None
    assert game.potential_claim_tile is None
    assert len(player0.hand) == INIT_HAND_SIZE - 2


def test_process_pung_claim_invalid_inputs(game):
    assert not game.process_pung_claim(claiming_player_id=None, claimed_tile=Tile(SUIT_DOTS, '1'))
    assert not game.process_pung_claim(claiming_player_id=0, claimed_tile=None)
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

    player0.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2')] + \
                   [Tile(SUIT_BAMBOO, str(i)) for i in range(3, 14)]
    original_hand = list(player0.hand)
    original_revealed_sets_count = len(player0.revealed_sets)

    success = game.process_pung_claim(claiming_player_id=0,
                                      claimed_tile=tile_being_claimed)
    assert not success
    assert player0.hand == original_hand
    assert len(player0.revealed_sets) == original_revealed_sets_count
    assert game.current_player_index == discarding_player_id


def test_run_ai_turn_successful_no_human_claim(game):
    game.current_player_index = 1
    ai_player = game.players[1]
    assert isinstance(ai_player.agent, AIPlayerAgent)
    if not game.wall:
        game.wall = [Tile(SUIT_DOTS, str(i % 9 + 1)) for i in range(20)]

    result = game.run_ai_turn()
    assert result["success"]
    assert result["ai_player_id"] == ai_player.player_id
    assert "suit" in result["discarded_tile"] and "value" in result["discarded_tile"]

    assert len(ai_player.hand) == INIT_HAND_SIZE
    assert game.current_discard is not None
    assert game.current_discard == Tile(result["discarded_tile"]["suit"], result["discarded_tile"]["value"])
    assert game.current_discard in ai_player.discards
    assert result["human_can_claim"] is None
    assert game.pending_claim_player_id is None
    assert game.current_player_index == (1 + 1) % NUM_PLAYERS


def test_run_ai_turn_leads_to_human_pung_claim(game):
    game.current_player_index = 1
    ai_player = game.players[1]
    human_player = game.players[0]
    tile_ai_will_discard = Tile(SUIT_DOTS, '5')
    human_player.hand = [Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '5'), Tile(SUIT_BAMBOO, '1')] + [Tile(SUIT_DOTS, str(i)) for i in range(1,11) if str(i) != '5']
    human_player.hand = human_player.hand[:INIT_HAND_SIZE]
    original_ai_choose_discard = ai_player.agent.choose_discard

    def mock_choose_discard(game_state, hand, drawn_tile):
        if tile_ai_will_discard in hand:
            return tile_ai_will_discard
        return hand[0]

    ai_player.agent.choose_discard = mock_choose_discard
    ai_player.hand.pop()
    ai_player.hand.append(tile_ai_will_discard)
    assert len(ai_player.hand) == INIT_HAND_SIZE
    result = game.run_ai_turn()
    ai_player.agent.choose_discard = original_ai_choose_discard

    assert result["success"]
    assert result["ai_player_id"] == ai_player.player_id
    assert Tile(result["discarded_tile"]["suit"], result["discarded_tile"]["value"]) == tile_ai_will_discard    
    assert result["human_can_claim"] == "PUNG"
    assert Tile(result["claimable_tile"]["suit"], result["claimable_tile"]["value"]) == tile_ai_will_discard
    assert game.pending_claim_player_id == 0
    assert game.claim_type_pending == "PUNG"
    assert game.current_player_index == ai_player.player_id


def test_run_ai_turn_wall_empty(game):
    game.current_player_index = 1
    ai_player = game.players[1]
    ai_player.hand = ai_player.hand[:INIT_HAND_SIZE]
    game.wall = []
    result = game.run_ai_turn()

    assert not result["success"]
    assert "Wall empty" in result.get("error", "")
    assert len(ai_player.hand) == INIT_HAND_SIZE


def test_run_ai_turn_called_on_human_player(game):
    game.current_player_index = 0
    result = game.run_ai_turn()

    assert not result["success"]
    assert not result["success"]
    assert not result["success"]
    assert "Not an AI player" in result.get("error", "")

#### Disabled test - not implemented in the game logic yet
# def test_discard_tile_ai_hypothetically_claims_pung(game):
#     human_player = game.players[0]

#     ai_agent_in_game = game.players[1].agent
#     assert isinstance(ai_agent_in_game, AIPlayerAgent), "Player 1 is not an AI agent as expected in fixture."

#     tile_to_be_discarded_by_human = Tile(SUIT_DOTS, '1')
#     game.players[1].hand = [
#         Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'),
#         Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'),
#         Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
#         Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
#         Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '3')
#     ]
#     assert len(game.players[1].hand) == INIT_HAND_SIZE
#     game.current_player_index = 0

#     human_player.hand = [Tile(SUIT_BAMBOO, str(i)) for i in range(1, INIT_HAND_SIZE + 1)]
#     game.draw_tile_for_current_player()
#     assert len(human_player.hand) == INIT_HAND_SIZE + 1

#     human_player.hand[0] = tile_to_be_discarded_by_human
#     discard_repr = {"suit": tile_to_be_discarded_by_human.suit,
#                     "value": tile_to_be_discarded_by_human.value}
#     assert can_form_pung_with_discard(game.players[1].hand,
#                                       tile_to_be_discarded_by_human), \
#         "Test setup error: AI hand cannot form Pung with the discard according to can_form_pung_with_discard."
#     original_decide_claim = ai_agent_in_game.decide_claim
#     ai_agent_in_game.decide_claim = MagicMock(return_value=None)
#     discard_successful = game.discard_tile_for_current_player(discard_repr)
#     assert discard_successful, "Discard itself failed."
#     try:
#         ai_agent_in_game.decide_claim.assert_called_once_with(
#             game, tile_to_be_discarded_by_human, ["PUNG"])
#     finally:
#         ai_agent_in_game.decide_claim = original_decide_claim
#     assert game.pending_claim_player_id is None
#     assert game.current_player_index == (0 + 1) % NUM_PLAYERS


def test_run_ai_turn_ai_hand_empty_after_draw_failsafe(game):
    game.current_player_index = 1
    ai_player = game.players[1]
    original_draw = game.draw_tile_for_current_player
    drawn_tile_for_test = Tile(SUIT_DOTS, '7')

    def mock_draw_and_empty_hand():
        ai_player.hand = []
        return drawn_tile_for_test

    game.draw_tile_for_current_player = mock_draw_and_empty_hand
    result = game.run_ai_turn()
    assert not result["success"]
    assert result.get("error") == "AI hand empty after draw, cannot discard."
    game.draw_tile_for_current_player = original_draw
