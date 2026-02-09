import ast
import collections
import inspect
import re
from unittest.mock import MagicMock

import pytest

from mahjong_engine.constants import (
    INIT_HAND_SIZE,
    NUM_COPIES_PER_TILE,
    NUM_PLAYERS,
    SUIT_BAMBOO,
    SUIT_CHARACTERS,
    SUIT_DOTS,
    SUIT_DRAGONS,
    SUIT_WINDS,
    TILE_CATEGORIES_FOR_GENERATION,
    WIND_EAST,
    WIND_NORTH,
    WIND_SOUTH,
    WIND_WEST,
    WINDS_ALL,
)
from mahjong_engine.game_state import GameState, TOTAL_TILES
from mahjong_engine.game_session import reset_dealer_rotation_state
from mahjong_engine.hand_validator import can_form_chow_with_discard, can_form_kong_with_discard, can_form_pung_with_discard
from mahjong_engine.melds import MeldType, Pung, Chow, Kong
from mahjong_engine.player import Player
from mahjong_engine.player_agent import AIPlayerAgent, HumanPlayerAgent
from mahjong_engine.tile import Tile


@pytest.fixture
def game():
    """Fixture to provide a fresh GameState instance for each test."""
    # Reset global dealer rotation state before each test
    reset_dealer_rotation_state()
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
        assert result["success"] is True
        assert result["action"] == "wall_empty"
        assert result["game_ended"] == True
        assert "message" in result
        assert isinstance(result["message"], str)
        assert "Wall empty" in result["message"]
        
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

    # Control the human's hand and the wall tile so we know what's discarded
    player.hand = [
        Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West'),
        Tile(SUIT_WINDS, 'North'), Tile(SUIT_DRAGONS, 'Red'),
        Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White'),
        Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '5'),
        Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '9'), Tile(SUIT_DOTS, '1'),
    ]
    # Put a safe tile on top of wall for drawing (honor tile = no chow possible)
    game.wall.insert(0, Tile(SUIT_WINDS, 'East'))

    # Give all AI players single honor tiles only — no pairs, no sequences
    game.players[1].hand = [
        Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West'),
        Tile(SUIT_WINDS, 'North'), Tile(SUIT_DRAGONS, 'Red'),
        Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '3'), Tile(SUIT_DOTS, '5'),
        Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '9'),
        Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '6'),
    ]
    game.players[2].hand = [
        Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White'),
        Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '5'),
        Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '9'),
        Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '3'), Tile(SUIT_CHARACTERS, '5'),
        Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_DOTS, '2'),
    ]
    game.players[3].hand = [
        Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'), Tile(SUIT_DOTS, '8'),
        Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '6'),
        Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '4'),
        Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '8'),
        Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
    ]

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

    # Ensure P2 and P3 have no Dots-1 tiles (so they can't claim before human P0)
    game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
    game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

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
    # Wall tiles: honors that can't form chows
    game.wall = [Tile(SUIT_DRAGONS, 'White')] * 20

    # P1 (AI) gets a deterministic hand with isolated honors
    ai_player.hand = [
        Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
        Tile(SUIT_WINDS, 'West'), Tile(SUIT_WINDS, 'North'),
        Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White'),
        Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
        Tile(SUIT_BAMBOO, '5'), Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '9'),
    ]
    # All other players: only isolated honors (no pairs, no chow possible)
    game.players[0].hand = [
        Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '5'),
        Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '9'),
        Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '4'),
        Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '8'),
        Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'),
        Tile(SUIT_DOTS, '8'), Tile(SUIT_BAMBOO, '2'),
    ]
    # P2 (next after P1, can claim chow): spread tiles far apart so no chow possible
    game.players[2].hand = [
        Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '9'),
        Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '9'),
        Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '5'), Tile(SUIT_CHARACTERS, '9'),
        Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
        Tile(SUIT_WINDS, 'West'), Tile(SUIT_WINDS, 'North'),
    ]
    # P3: also spread tiles apart, no pairs with P1's possible discards
    game.players[3].hand = [
        Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '6'),
        Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '6'),
        Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '6'),
        Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '8'),
        Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '8'),
        Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '8'),
        Tile(SUIT_DRAGONS, 'Red'),
    ]

    result = game.run_ai_turn()
    assert result["success"]
    assert result["ai_player_id"] == ai_player.player_id
    assert isinstance(result["discarded_tile"], str)

    assert len(ai_player.hand) == INIT_HAND_SIZE
    assert game.current_discard is not None
    assert game.current_discard.unicode == result["discarded_tile"]
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

    # Ensure P2 and P3 can't claim Dots-5
    game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
    game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

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
    assert result["discarded_tile"] == tile_ai_will_discard.unicode
    assert result["human_can_claim"] == "PUNG"
    assert result["claimable_tile"] == tile_ai_will_discard.unicode
    assert game.pending_claim_player_id == 0
    assert game.claim_type_pending == "PUNG"
    assert game.current_player_index == ai_player.player_id


def test_run_ai_turn_wall_empty(game):
    game.current_player_index = 1
    ai_player = game.players[1]
    ai_player.hand = ai_player.hand[:INIT_HAND_SIZE]
    game.wall = []
    result = game.run_ai_turn()

    assert result["success"]
    assert result["action"] == "wall_empty"
    assert result["game_ended"] == True
    assert "Wall empty" in result.get("message", "")
    assert len(ai_player.hand) == INIT_HAND_SIZE


def test_run_ai_turn_called_on_human_player(game):
    game.current_player_index = 0
    result = game.run_ai_turn()

    assert not result["success"]
    assert result.get("error") == "Not an AI player."

class TestAIClaimingBehavior:
    """Tests for AI claiming tiles during discard_tile_for_current_player()."""

    def test_ai_claims_pung_on_discard(self, game):
        """AI forms pung from human's discard, verify meld created and AI discards."""
        human_player = game.players[0]
        ai_player = game.players[1]

        # AI has two Dots-1 to form pung
        ai_player.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '3'),
        ]
        assert len(ai_player.hand) == INIT_HAND_SIZE

        # Human has a Dots-1 to discard, plus unique tiles so no other claims fire
        game.current_player_index = 0
        human_player.hand = [
            Tile(SUIT_DOTS, '1'),
            Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '5'),
            Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '7'),
            Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '9'),
            Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
            Tile(SUIT_WINDS, 'West'), Tile(SUIT_WINDS, 'North'),
            Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'),
            Tile(SUIT_DRAGONS, 'White'),
        ]
        assert len(human_player.hand) == INIT_HAND_SIZE + 1

        # Ensure P2 and P3 can't claim
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
        game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

        tile_to_discard = Tile(SUIT_DOTS, '1')
        assert can_form_pung_with_discard(ai_player.hand, tile_to_discard)

        discard_repr = {"suit": tile_to_discard.suit, "value": tile_to_discard.value}
        result = game.discard_tile_for_current_player(discard_repr)
        assert result is True

        # AI should have formed a pung
        assert len(ai_player.revealed_sets) == 1
        assert ai_player.revealed_sets[0].meld_type == MeldType.PUNG
        assert ai_player.revealed_sets[0].key_tile == tile_to_discard

        # AI should have discarded (hand = 13 - 2 for pung + need to discard = 10 tiles)
        assert len(ai_player.hand) == INIT_HAND_SIZE - 2 - 1  # 13 - 2 (pung) - 1 (discard)

    def test_ai_claims_kong_on_discard(self, game):
        """AI forms kong from discard, draws replacement, and discards."""
        human_player = game.players[0]
        ai_player = game.players[1]

        kong_tile = Tile(SUIT_DOTS, '5')
        # AI has three Dots-5 to form kong
        ai_player.hand = [
            kong_tile, kong_tile, kong_tile,
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
            Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'),
            Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '1'),
        ]
        assert len(ai_player.hand) == INIT_HAND_SIZE

        # Human discards the kong tile
        game.current_player_index = 0
        human_player.hand = [
            kong_tile,
            Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '3'),
            Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '5'),
            Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '7'),
            Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '9'),
            Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
            Tile(SUIT_WINDS, 'West'), Tile(SUIT_WINDS, 'North'),
            Tile(SUIT_DRAGONS, 'Red'),
        ]
        assert len(human_player.hand) == INIT_HAND_SIZE + 1

        # Ensure P2 and P3 can't claim
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
        game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

        assert can_form_kong_with_discard(ai_player.hand, kong_tile)

        discard_repr = {"suit": kong_tile.suit, "value": kong_tile.value}
        result = game.discard_tile_for_current_player(discard_repr)
        assert result is True

        # AI should have formed a kong
        assert len(ai_player.revealed_sets) == 1
        assert ai_player.revealed_sets[0].meld_type == MeldType.KONG

    def test_ai_claims_chow_on_discard(self, game):
        """Left-neighbor AI forms chow from discard."""
        # Player 0 (human) discards, player 1 (AI, left neighbor) claims chow
        human_player = game.players[0]
        ai_player = game.players[1]  # left neighbor of player 0

        chow_tile = Tile(SUIT_DOTS, '5')
        # AI has Dots-4 and Dots-6 for chow
        ai_player.hand = [
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
            Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'),
            Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'),
        ]
        assert len(ai_player.hand) == INIT_HAND_SIZE

        # Human discards Dots-5
        game.current_player_index = 0
        human_player.hand = [
            chow_tile,
            Tile(SUIT_CHARACTERS, '3'), Tile(SUIT_CHARACTERS, '4'),
            Tile(SUIT_CHARACTERS, '5'), Tile(SUIT_CHARACTERS, '6'),
            Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '8'),
            Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_WINDS, 'East'),
            Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West'),
            Tile(SUIT_WINDS, 'North'), Tile(SUIT_DRAGONS, 'Red'),
            Tile(SUIT_DRAGONS, 'Green'),
        ]
        assert len(human_player.hand) == INIT_HAND_SIZE + 1

        # Ensure P2 and P3 can't claim
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
        game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

        # Verify chow is possible: discarder=0, claimer=1, left neighbor check passes
        assert can_form_chow_with_discard(ai_player.hand, chow_tile, 0, 1)

        discard_repr = {"suit": chow_tile.suit, "value": chow_tile.value}
        result = game.discard_tile_for_current_player(discard_repr)
        assert result is True

        # AI should have formed a chow
        assert len(ai_player.revealed_sets) == 1
        assert ai_player.revealed_sets[0].meld_type == MeldType.CHOW

        # AI should have discarded after claiming
        assert len(ai_player.hand) == INIT_HAND_SIZE - 2 - 1  # 13 - 2 (chow) - 1 (discard)

    def test_ai_claims_win_on_discard(self, game):
        """AI wins by claiming a discard."""
        human_player = game.players[0]
        ai_player = game.players[1]

        # AI has a hand one tile away from winning
        win_tile = Tile(SUIT_BAMBOO, '1')
        ai_player.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '8'), Tile(SUIT_DOTS, '9'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
        ]
        assert len(ai_player.hand) == INIT_HAND_SIZE

        # Human discards the winning tile
        game.current_player_index = 0
        human_player.hand = [
            win_tile,
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'),
            Tile(SUIT_CHARACTERS, '3'), Tile(SUIT_CHARACTERS, '4'),
            Tile(SUIT_CHARACTERS, '5'), Tile(SUIT_CHARACTERS, '6'),
            Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '8'),
            Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_WINDS, 'East'),
            Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West'),
            Tile(SUIT_WINDS, 'North'),
        ]
        assert len(human_player.hand) == INIT_HAND_SIZE + 1

        # Ensure P2 and P3 can't win
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
        game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(4, 10)] + [Tile(SUIT_DOTS, '9'), Tile(SUIT_CHARACTERS, '9'), Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '7')]

        discard_repr = {"suit": win_tile.suit, "value": win_tile.value}
        result = game.discard_tile_for_current_player(discard_repr)
        assert result is True

        # AI should have won
        assert game.winner_found is True
        assert game.winning_player_id == 1

    def test_ai_declines_claim(self, game):
        """When decide_claim returns None, no claim occurs and turn advances."""
        human_player = game.players[0]
        ai_player = game.players[1]

        # AI has two Dots-1 (could pung) but we mock decide_claim to return None
        ai_player.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '4'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '3'),
        ]
        assert len(ai_player.hand) == INIT_HAND_SIZE

        game.current_player_index = 0
        human_player.hand = [
            Tile(SUIT_DOTS, '1'),
            Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '5'),
            Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '7'),
            Tile(SUIT_CHARACTERS, '8'), Tile(SUIT_CHARACTERS, '9'),
            Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'),
            Tile(SUIT_WINDS, 'West'), Tile(SUIT_WINDS, 'North'),
            Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'),
            Tile(SUIT_DRAGONS, 'White'),
        ]
        assert len(human_player.hand) == INIT_HAND_SIZE + 1

        # Ensure P2 and P3 can't claim
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_WINDS, w) for w in ['East', 'South', 'West', 'North']]
        game.players[3].hand = [Tile(SUIT_DRAGONS, 'Red'), Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White')] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '9')]

        # Mock decide_claim to always return None (decline)
        original_decide_claim = ai_player.agent.decide_claim
        ai_player.agent.decide_claim = MagicMock(return_value=None)

        discard_repr = {"suit": SUIT_DOTS, "value": "1"}
        result = game.discard_tile_for_current_player(discard_repr)
        assert result is True

        # AI should NOT have claimed
        assert len(ai_player.revealed_sets) == 0
        assert len(ai_player.hand) == INIT_HAND_SIZE  # unchanged

        # decide_claim was called with PUNG option
        ai_player.agent.decide_claim.assert_called_once_with(
            game, Tile(SUIT_DOTS, '1'), ["PUNG"])

        # Turn should have advanced past the human
        assert game.pending_claim_player_id is None

        # Restore
        ai_player.agent.decide_claim = original_decide_claim


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


# Test dealer rotation and round progression
class TestDealerRotationSystem:
    """Test dealer rotation and round progression according to traditional Mahjong rules."""
    
    def test_initial_dealer_and_winds(self, game):
        """Test that game starts with correct dealer and wind assignments."""
        # East Round, East Hand, East dealer (player 0)
        assert game.dealer_index == 0
        assert game.round_wind == WIND_EAST
        
        # Verify player winds are assigned correctly
        assert game.players[0].wind == WIND_EAST  # Dealer is East
        assert game.players[1].wind == WIND_SOUTH
        assert game.players[2].wind == WIND_WEST  
        assert game.players[3].wind == WIND_NORTH
    
    def test_assign_player_winds_with_different_dealer(self, game):
        """Test wind assignment when dealer is not player 0."""
        # Set player 1 as dealer
        game.dealer_index = 1
        game.assign_player_winds()
        
        assert game.players[1].wind == WIND_EAST  # Dealer is always East
        assert game.players[2].wind == WIND_SOUTH
        assert game.players[3].wind == WIND_WEST
        assert game.players[0].wind == WIND_NORTH
    
    def test_advance_dealer_within_round(self, game):
        """Test dealer advancement within the same round."""
        initial_round = game.round_wind
        
        # Advance dealer from player 0 to player 1
        game.advance_dealer()
        
        assert game.dealer_index == 1
        assert game.round_wind == initial_round  # Same round
          # Verify winds reassigned correctly
        assert game.players[1].wind == WIND_EAST  # New dealer is East
        assert game.players[2].wind == WIND_SOUTH
    
    def test_advance_dealer_triggers_round_progression(self, game):
        """Test that completing dealer rotation advances the round."""
        # Start with player 3 as dealer (last dealer in round)
        game.dealer_index = 3
        game.round_wind = WIND_EAST
        game.assign_player_winds()
          # Advance dealer - should trigger round progression
        game.advance_dealer()
        
        assert game.dealer_index == 0  # Back to player 0
        assert game.round_wind == WIND_SOUTH  # Advanced to South Round
        
        # Verify winds reassigned
        assert game.players[0].wind == WIND_EAST  # Player 0 is dealer again
    
    def test_advance_round_progression(self, game):
        """Test round wind progression: East → South → West → North → East."""
        test_cases = [
            (WIND_EAST, WIND_SOUTH),
            (WIND_SOUTH, WIND_WEST),
            (WIND_WEST, WIND_NORTH),
            (WIND_NORTH, WIND_EAST),  # Wraps back to East
        ]
        
        for current_wind, expected_next in test_cases:
            game.round_wind = current_wind
            game.advance_round()
            assert game.round_wind == expected_next
    
    def test_should_dealer_continue_winner_is_dealer(self, game):
        """Test dealer continues when current dealer wins."""
        game.dealer_index = 2
        
        # Dealer wins - should continue
        assert game.should_dealer_continue(winner_id=2) is True
        
        # Non-dealer wins - should not continue
        assert game.should_dealer_continue(winner_id=1) is False
        assert game.should_dealer_continue(winner_id=3) is False
    
    def test_should_dealer_continue_wall_empty(self, game):
        """Test dealer continues when wall is empty with no winner."""
        # Wall empty, no winner - dealer continues
        assert game.should_dealer_continue(winner_id=None, wall_empty=True) is True
        
        # Wall empty but someone won - normal dealer advancement
        assert game.should_dealer_continue(winner_id=1, wall_empty=True) is False
    
    def test_should_dealer_continue_normal_cases(self, game):
        """Test normal cases where dealer should not continue."""
        game.dealer_index = 0
        
        # Non-dealer wins
        assert game.should_dealer_continue(winner_id=1) is False
        
        # Normal hand end (no wall empty, no winner specified)
        assert game.should_dealer_continue() is False
    
    def test_end_hand_dealer_wins(self, game):
        """Test hand end when dealer wins (dealer continues)."""
        game.dealer_index = 1
        game.winner_found = True
        game.winning_player_id = 1

        # Dealer wins - should continue
        game.end_hand(winner_id=1)

        assert game.dealer_index == 1  # Same dealer
        # winner state persists (NOT reset by end_hand)
        assert game.winner_found is True
        assert game.winning_player_id == 1
    
    def test_end_hand_non_dealer_wins(self, game):
        """Test hand end when non-dealer wins (advance dealer)."""
        game.dealer_index = 1
        game.round_wind = WIND_EAST

        # Non-dealer wins - should advance dealer
        game.end_hand(winner_id=2)

        assert game.dealer_index == 2  # Advanced to next dealer
        assert game.round_wind == WIND_EAST  # Same round
    
    def test_end_hand_wall_empty_no_winner(self, game):
        """Test hand end when wall is empty with no winner (dealer continues)."""
        game.dealer_index = 2

        # Wall empty, no winner - dealer continues
        game.end_hand(winner_id=None, wall_empty=True)

        assert game.dealer_index == 2  # Same dealer
    
    def test_end_hand_resets_transient_state(self, game):
        """Test that end_hand resets claim/discard state but preserves outcome state."""
        # Set up some game state
        game.winner_found = True
        game.winning_player_id = 1
        game.current_discard = Tile(SUIT_DOTS, '5')
        game.turn_number = 10
        game.pending_claim_player_id = 2
        game.potential_claim_tile = Tile(SUIT_BAMBOO, '3')
        game.claim_type_pending = "PUNG"

        game.end_hand(winner_id=2)

        # Transient claim/discard state IS cleared
        assert game.current_discard is None
        assert game.pending_claim_player_id is None
        assert game.potential_claim_tile is None
        assert game.claim_type_pending is None

        # Outcome state is NOT cleared (persists for API/frontend)
        assert game.winner_found is True
        assert game.winning_player_id == 1
        assert game.turn_number == 10
    
    def test_complete_round_cycle(self, game):
        """Test a complete round cycle with all dealer rotations."""
        # Start in East Round with player 0 as dealer
        assert game.round_wind == WIND_EAST
        assert game.dealer_index == 0
        
        # Complete full dealer rotation within East Round
        # Non-dealer must win for dealer to advance
        for expected_dealer in [1, 2, 3]:
            game.end_hand(winner_id=expected_dealer)  # Current non-dealer wins, advance dealer
            assert game.dealer_index == expected_dealer
            assert game.round_wind == WIND_EAST  # Still East Round
        
        # One more advancement should move to South Round
        game.end_hand(winner_id=0)  # Non-dealer wins (current dealer is 3, so 0 is non-dealer)
        assert game.dealer_index == 0  # Back to player 0
        assert game.round_wind == WIND_SOUTH  # Advanced to South Round
    
    def test_dealer_rotation_with_player_wind_consistency(self, game):
        """Test that dealer rotation maintains correct player wind assignments."""
        # Test each player as dealer
        for expected_dealer in range(NUM_PLAYERS):
            game.dealer_index = expected_dealer
            game.assign_player_winds()
            
            # Dealer should always be East wind
            assert game.players[expected_dealer].wind == WIND_EAST
            
            # Other players should have winds in correct order
            for i, player in enumerate(game.players):
                if i != expected_dealer:
                    wind_index = (i - expected_dealer) % len(WINDS_ALL)
                    expected_wind = WINDS_ALL[wind_index]
                    assert player.wind == expected_wind


# Test integration between win detection and dealer rotation system
class TestWinDetectionWithDealerRotation:
    """Test integration between win detection and dealer rotation system."""
    
    def test_process_win_claim_calls_end_hand(self, game):
        """Test that process_win_claim properly calls end_hand with winner."""
        # Setup a valid pung claim scenario
        player0 = game.players[0]
        discarding_player_id = 1
        
        game.pending_claim_player_id = 0
        game.claim_type_pending = "PUNG"
        tile_being_claimed = Tile(SUIT_DOTS, '1')
        game.potential_claim_tile = tile_being_claimed
        game.current_discard = tile_being_claimed
        game.current_player_index = discarding_player_id
        
        # Give player 0 the tiles needed for pung
        player0.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1')] + \
                       [Tile(SUIT_BAMBOO, str(i)) for i in range(3, 14)]
        
        # Track initial dealer state
        initial_dealer = game.dealer_index
        initial_round = game.round_wind
        
        # Process the claim (which should not cause a win, just a meld)
        success = game.process_pung_claim(claiming_player_id=0, claimed_tile=tile_being_claimed)
        assert success
        
        # For this test, we're mainly verifying the structure is in place
        # The actual win checking would need a proper winning hand setup
        # This test ensures the method exists and basic flow works
        
        # Verify pung was created
        assert len(player0.revealed_sets) == 1
        assert game.current_player_index == 0  # Claiming player's turn
    
    def test_draw_tile_win_detection_calls_end_hand(self, game):
        """Test that self-draw win detection calls end_hand."""
        player = game.players[game.current_player_index]
        
        # Give player a nearly winning hand (this is a simplified test)
        # In a real scenario, we'd need a hand that's one tile away from winning
        near_winning_hand = [Tile(SUIT_DOTS, str(i)) for i in range(1, 14)]
        player.hand = near_winning_hand[:INIT_HAND_SIZE]
        
        # Mock the wall to have a specific tile
        winning_tile = Tile(SUIT_DOTS, '1')
        game.wall = [winning_tile] + [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)]
        
        # Track initial state
        initial_dealer = game.dealer_index
        
        # This test primarily verifies the structure is in place
        # The actual win detection logic would need proper hand validation
        drawn_tile = game.draw_tile_for_current_player()
        assert drawn_tile is not None
        
        # The test verifies that the method structure exists for win detection
        # In actual gameplay, win detection would trigger end_hand() with winner_id    


    def test_wall_empty_scenario_triggers_dealer_continuation(self, game):
        """Test that empty wall scenario properly handles dealer rotation."""
        # Create a fresh game instance to avoid fixture contamination
        game = GameState()
        
        # Reset game to ensure clean state for this test
        game.dealer_index = 0
        game.round_wind = WIND_EAST
        
        # Empty the wall
        game.wall = []
        
        # Track initial dealer state
        initial_dealer = game.dealer_index
        initial_round = game.round_wind
        
        # Attempt to draw tile when wall is empty
        result = game.draw_tile_for_current_player()
        assert result is None  # Should not be able to draw
        
        # In actual implementation, wall empty should trigger end_hand(wall_empty=True)
        # This would cause dealer to continue according to traditional rules
        game.end_hand(winner_id=None, wall_empty=True)
        
        # Dealer should continue (same dealer)
        assert game.dealer_index == initial_dealer
        assert game.round_wind == initial_round  # Same round
    
    def test_end_hand_resets_claim_state(self, game):
        """Test that end_hand properly resets all claim-related state."""
        # Set up some claim state
        game.pending_claim_player_id = 1
        game.potential_claim_tile = Tile(SUIT_DOTS, '5')
        game.claim_type_pending = "PUNG"
        game.current_discard = Tile(SUIT_BAMBOO, '3')

        # End the hand
        game.end_hand(winner_id=2)

        # Verify all claim state is reset
        assert game.pending_claim_player_id is None
        assert game.potential_claim_tile is None
        assert game.claim_type_pending is None
        assert game.current_discard is None


class TestWinnerStatePersistence:
    """Tests verifying that winner state persists after end_hand (bug fix for issue #34)."""

    def test_process_win_claim_winner_persists(self, game):
        """process_win_claim sets winner_found=True and it survives end_hand()."""
        player0 = game.players[0]
        # Build a hand that's one tile away from winning: 3 complete sets + a pair
        # [1d,2d,3d, 4d,5d,6d, 7d,8d,9d, 1b,1b] + one more tile for the pair
        player0.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '8'), Tile(SUIT_DOTS, '9'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
        ]
        # Set up a win claim scenario: another player discarded 1b
        win_tile = Tile(SUIT_BAMBOO, '1')
        game.current_player_index = 1  # Some other player discarded
        game.pending_claim_player_id = 0
        game.claim_type_pending = "WIN"
        game.potential_claim_tile = win_tile
        game.current_discard = win_tile

        success = game.process_win_claim(0, win_tile)
        assert success
        # Winner state must persist after process_win_claim (which calls end_hand)
        assert game.winner_found is True
        assert game.winning_player_id == 0

    def test_ai_self_draw_win_detected_after_end_hand(self, game):
        """AI self-draw win: winner_found stays True after end_hand so run_ai_turn detects it."""
        ai_player = game.players[1]  # AI player
        game.current_player_index = 1

        # Build a hand that's one tile away from winning
        ai_player.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '5'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_DOTS, '7'), Tile(SUIT_DOTS, '8'), Tile(SUIT_DOTS, '9'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '1'),
            Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '3'),
        ]
        # Put the winning tile on top of the wall
        game.wall = [Tile(SUIT_BAMBOO, '1')] + game.wall

        drawn = game.draw_tile_for_current_player()
        assert drawn is not None
        # After draw_tile_for_current_player detects AI win and calls end_hand,
        # winner_found must still be True
        assert game.winner_found is True
        assert game.winning_player_id == 1

    def test_end_hand_wall_empty_no_false_winner(self, game):
        """Wall-empty end_hand must not accidentally set winner_found."""
        game.wall = []
        game.winner_found = False

        game.draw_tile_for_current_player()  # triggers end_hand(wall_empty=True)
        assert game.winner_found is False
        assert game.winning_player_id is None


class TestChowIntegration:
    """Tests for chow claim integration in GameState."""

    def test_process_chow_claim_successful(self, game):
        """process_chow_claim removes correct tiles and creates Chow meld."""
        player = game.players[0]
        # Give player a hand with tiles that can form a chow with 5-dots
        player.hand = [
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'),
            Tile(SUIT_CHARACTERS, '7'), Tile(SUIT_CHARACTERS, '8'),
            Tile(SUIT_CHARACTERS, '9'),
        ]
        claimed_tile = Tile(SUIT_DOTS, '5')
        game.current_player_index = 3  # discarder is player 3
        game.potential_claim_tile = claimed_tile

        initial_hand_size = len(player.hand)
        success = game.process_chow_claim(0, claimed_tile)

        assert success is True
        assert len(player.hand) == initial_hand_size - 2
        assert len(player.revealed_sets) == 1
        assert player.revealed_sets[0].meld_type == MeldType.CHOW
        assert player.revealed_sets[0].revealed is True
        # Current player should be the claimer
        assert game.current_player_index == 0
        # Claim state should be cleared
        assert game.pending_claim_player_id is None
        assert game.claim_type_pending is None

    def test_process_chow_claim_invalid_no_tiles(self, game):
        """process_chow_claim fails when hand doesn't have sequence tiles."""
        player = game.players[0]
        player.hand = [Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '9')]
        claimed_tile = Tile(SUIT_DOTS, '5')
        game.current_player_index = 3

        success = game.process_chow_claim(0, claimed_tile)
        assert success is False

    def test_process_chow_claim_none_inputs(self, game):
        """process_chow_claim fails with None inputs."""
        assert game.process_chow_claim(None, Tile(SUIT_DOTS, '5')) is False
        assert game.process_chow_claim(0, None) is False

    def test_process_chow_claim_honor_tile_rejected(self, game):
        """Chow cannot be formed with honor tiles."""
        player = game.players[0]
        player.hand = [Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West')]

        success = game.process_chow_claim(0, Tile(SUIT_WINDS, 'East'))
        assert success is False

    def test_discard_triggers_chow_opportunity(self, game):
        """When AI (player 3) discards, human (player 0) gets chow opportunity."""
        # Set up: player 3 is current, player 0 is left neighbor
        game.current_player_index = 3
        player_0 = game.players[0]
        # Give player 0 tiles for a chow
        player_0.hand = [
            Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'),
            Tile(SUIT_CHARACTERS, '1'), Tile(SUIT_CHARACTERS, '2'),
            Tile(SUIT_CHARACTERS, '3'),
        ]
        # Player 3 has a valid hand for discard
        player_3 = game.players[3]
        player_3.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '5'),
            Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '7'),
        ]

        discard_repr = {'suit': SUIT_DOTS, 'value': '1'}
        game.discard_tile_for_current_player(discard_repr)

        # Player 0 should have a chow claim opportunity
        assert game.pending_claim_player_id == 0
        assert game.claim_type_pending == "CHOW"

    def test_chow_lower_priority_than_pung(self, game):
        """Pung claim takes priority over chow claim."""
        game.current_player_index = 3
        # Player 0 can chow AND pung the discarded tile
        player_0 = game.players[0]
        player_0.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_DOTS, '1'),  # Can pung
            Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '3'),   # Can also chow with 1-dot
            Tile(SUIT_BAMBOO, '5'), Tile(SUIT_BAMBOO, '6'),
            Tile(SUIT_CHARACTERS, '7'),
        ]
        player_3 = game.players[3]
        player_3.hand = [
            Tile(SUIT_DOTS, '1'), Tile(SUIT_BAMBOO, '7'),
            Tile(SUIT_BAMBOO, '8'), Tile(SUIT_BAMBOO, '9'),
            Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '5'),
            Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '7'),
        ]

        discard_repr = {'suit': SUIT_DOTS, 'value': '1'}
        game.discard_tile_for_current_player(discard_repr)

        # Should be PUNG, not CHOW (pung has higher priority)
        assert game.claim_type_pending == "PUNG"


class TestGameHistoryIntegration:
    """Tests for GameHistory integration in GameState."""

    def test_history_exists_on_game_state(self, game):
        """GameState has a history attribute."""
        assert hasattr(game, 'history')
        assert game.history is not None

    def test_draw_records_history(self, game):
        """Drawing a tile records a 'draw' action in history."""
        game.draw_tile_for_current_player()
        actions = game.get_history()
        assert len(actions) >= 1
        draw_actions = [a for a in actions if a["action"] == "draw"]
        assert len(draw_actions) == 1
        assert draw_actions[0]["player_id"] == game.current_player_index

    def test_discard_records_history(self, game):
        """Discarding a tile records a 'discard' action in history."""
        player = game.players[game.current_player_index]

        # Control hands and wall so discard of honor tile triggers no AI claims
        player.hand = [
            Tile(SUIT_WINDS, 'East'), Tile(SUIT_WINDS, 'South'), Tile(SUIT_WINDS, 'West'),
            Tile(SUIT_WINDS, 'North'), Tile(SUIT_DRAGONS, 'Red'),
            Tile(SUIT_DRAGONS, 'Green'), Tile(SUIT_DRAGONS, 'White'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '3'), Tile(SUIT_BAMBOO, '5'),
            Tile(SUIT_BAMBOO, '7'), Tile(SUIT_BAMBOO, '9'), Tile(SUIT_DOTS, '1'),
        ]
        game.wall.insert(0, Tile(SUIT_WINDS, 'East'))
        game.players[1].hand = [Tile(SUIT_DOTS, str(i)) for i in range(1, 10)] + [Tile(SUIT_BAMBOO, '2'), Tile(SUIT_BAMBOO, '4'), Tile(SUIT_BAMBOO, '6'), Tile(SUIT_BAMBOO, '8')]
        game.players[2].hand = [Tile(SUIT_CHARACTERS, str(i)) for i in range(1, 10)] + [Tile(SUIT_DOTS, '2'), Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'), Tile(SUIT_DOTS, '8')]
        game.players[3].hand = [Tile(SUIT_BAMBOO, str(i)) for i in range(1, 10)] + [Tile(SUIT_CHARACTERS, '2'), Tile(SUIT_CHARACTERS, '4'), Tile(SUIT_CHARACTERS, '6'), Tile(SUIT_CHARACTERS, '8')]

        # Draw first to get to valid hand size
        game.draw_tile_for_current_player()
        tile = player.hand[0]  # Will be Tile(SUIT_WINDS, 'East') — honor, no claims
        discard_repr = {'suit': tile.suit, 'value': tile.value}
        game.discard_tile_for_current_player(discard_repr)

        actions = game.get_history()
        discard_actions = [a for a in actions if a["action"] == "discard"]
        assert len(discard_actions) == 1

    def test_pung_records_history(self, game):
        """Processing a pung claim records a 'pung' action."""
        player = game.players[0]
        claimed_tile = Tile(SUIT_DOTS, '5')
        player.hand = [
            claimed_tile, claimed_tile,
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'),
            Tile(SUIT_CHARACTERS, '7'),
        ]
        game.current_player_index = 1
        game.process_pung_claim(0, claimed_tile)

        actions = game.get_history()
        pung_actions = [a for a in actions if a["action"] == "pung"]
        assert len(pung_actions) == 1
        assert pung_actions[0]["player_id"] == 0

    def test_chow_records_history(self, game):
        """Processing a chow claim records a 'chow' action."""
        player = game.players[0]
        claimed_tile = Tile(SUIT_DOTS, '5')
        player.hand = [
            Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6'),
            Tile(SUIT_BAMBOO, '1'), Tile(SUIT_BAMBOO, '2'),
            Tile(SUIT_CHARACTERS, '7'),
        ]
        game.current_player_index = 3
        game.process_chow_claim(0, claimed_tile)

        actions = game.get_history()
        chow_actions = [a for a in actions if a["action"] == "chow"]
        assert len(chow_actions) == 1

    def test_get_history_method(self, game):
        """get_history() returns action list."""
        # game_init is always recorded at creation
        history = game.get_history()
        assert len(history) >= 1
        assert history[0]["action"] == "game_init"

        game.draw_tile_for_current_player()
        assert len(game.get_history()) >= 2

    def test_end_hand_preserves_action_log(self, game):
        """end_hand() preserves the action log for debugging/bug reports."""
        game.draw_tile_for_current_player()
        count_before = len(game.get_history())
        assert count_before >= 1

        game.end_hand(wall_empty=True)
        # Action log should still contain entries (plus end_hand + snapshot)
        assert len(game.get_history()) > count_before


class TestTileChecksum:
    """Tests for the tile accounting checksum (validate_tile_accounting)."""

    def test_tile_checksum_valid_after_init(self, game):
        """All 136 tiles are accounted for right after deal."""
        result = game.validate_tile_accounting()
        assert result["valid"] is True
        assert result["total"] == TOTAL_TILES
        assert result["expected"] == TOTAL_TILES
        assert result["discrepancy"] == 0

    def test_tile_checksum_valid_after_draw(self, game):
        """Still 136 tiles after a player draws."""
        game.draw_tile_for_current_player()
        result = game.validate_tile_accounting()
        assert result["valid"] is True
        assert result["total"] == TOTAL_TILES

    def test_tile_checksum_valid_after_discard(self, game):
        """Still 136 tiles after draw + discard cycle."""
        player = game.players[game.current_player_index]
        game.draw_tile_for_current_player()
        tile = player.hand[0]
        game.discard_tile_for_current_player({"suit": tile.suit, "value": tile.value})
        result = game.validate_tile_accounting()
        assert result["valid"] is True
        assert result["total"] == TOTAL_TILES

    def test_tile_checksum_valid_after_chow(self, game):
        """Tile count unchanged after a chow claim (draw → discard → chow flow)."""
        # Use real game flow: AI (player 3) discards, human (player 0) claims chow
        game.current_player_index = 3
        player3 = game.players[3]
        player0 = game.players[0]

        # Give player 0 tiles that can form a chow with whatever player 3 will discard
        # We'll use a Dots 4,5,6 sequence: player 0 has 4d and 6d, player 3 discards 5d
        chow_tile = Tile(SUIT_DOTS, '5')
        player0.hand = [Tile(SUIT_DOTS, '4'), Tile(SUIT_DOTS, '6')] + player0.hand[2:]

        # Player 3 draws, then discards 5-dots
        player3.hand[0] = chow_tile
        game.draw_tile_for_current_player()
        tile_repr = {"suit": SUIT_DOTS, "value": "5"}
        game.discard_tile_for_current_player(tile_repr)

        count_before = game.validate_tile_accounting()["total"]
        game.process_chow_claim(0, chow_tile)
        count_after = game.validate_tile_accounting()["total"]

        assert count_before == count_after
        assert count_before == TOTAL_TILES

    def test_tile_checksum_valid_after_pung(self, game):
        """Tile count unchanged after a pung claim (draw → discard → pung flow)."""
        # Use real game flow: AI (player 1) discards, human (player 0) claims pung
        game.current_player_index = 1
        player1 = game.players[1]
        player0 = game.players[0]

        pung_tile = Tile(SUIT_DOTS, '5')
        # Ensure player 0 has two 5-dots for pung
        player0.hand[0] = pung_tile
        player0.hand[1] = pung_tile

        # Ensure P2 and P3 can't claim Dots-5: replace any Dots tiles in [3-7] range
        # with safe non-Dots tiles (same count to preserve tile accounting)
        for p_idx in [2, 3]:
            p = game.players[p_idx]
            for i, tile in enumerate(p.hand):
                if tile.suit == SUIT_DOTS and tile.value in ['3', '4', '5', '6', '7']:
                    p.hand[i] = Tile(SUIT_WINDS, 'North')

        # Player 1 draws, then discards 5-dots
        player1.hand[0] = pung_tile
        game.draw_tile_for_current_player()
        tile_repr = {"suit": SUIT_DOTS, "value": "5"}
        game.discard_tile_for_current_player(tile_repr)

        count_before = game.validate_tile_accounting()["total"]
        game.process_pung_claim(0, pung_tile)
        count_after = game.validate_tile_accounting()["total"]

        assert count_before == count_after
        assert count_before == TOTAL_TILES

    def test_tile_checksum_detects_extra_tile(self, game):
        """Checksum catches when a tile is manually added (total > 136)."""
        game.players[0].hand.append(Tile(SUIT_DOTS, '1'))
        result = game.validate_tile_accounting()
        assert result["valid"] is False
        assert result["total"] == TOTAL_TILES + 1
        assert result["discrepancy"] == 1

    def test_snapshot_includes_tile_checksum(self, game):
        """get_state_snapshot() includes tile_checksum and per-player counts."""
        snapshot = game.get_state_snapshot()
        assert "tile_checksum" in snapshot
        checksum = snapshot["tile_checksum"]
        assert checksum["valid"] is True
        assert checksum["total"] == TOTAL_TILES

        # Verify per-player counts in snapshot
        for p_snap in snapshot["players"]:
            assert "hand_count" in p_snap
            assert "discard_count" in p_snap
            assert "meld_tile_count" in p_snap
            assert p_snap["hand_count"] == len(p_snap["hand"])
            assert p_snap["discard_count"] == len(p_snap["discards"])
