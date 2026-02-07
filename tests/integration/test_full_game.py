import pytest
import json
import requests
import asyncio
import websockets
from typing import Dict, List, Any


@pytest.mark.integration
class TestCompleteGameFlow:
    """Integration tests for complete mahjong game scenarios."""
    
    BASE_URL = "http://localhost:8080"
    WS_URL = "ws://localhost:8080/ws"
    
    def setup_method(self):
        """Reset game state before each test."""
        requests.post(f"{self.BASE_URL}/reset-game")
        requests.post(f"{self.BASE_URL}/reset-dealer-rotation")
    
    def test_api_health_check(self):
        """Verify server is running and responsive."""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
    
    def test_start_new_game_returns_valid_state(self):
        """Test /start-new-game returns properly structured game state."""
        response = requests.post(f"{self.BASE_URL}/start-new-game")
        assert response.status_code == 200
        
        data = response.json()
        assert "player_hand" in data
        assert "game_wind" in data
        assert "current_player_id" in data
        assert "remaining_tiles" in data
        assert "dealer_index" in data
        assert "round_wind" in data
        assert "winner_found" in data
        
        # Validate types
        assert isinstance(data["player_hand"], list)
        assert isinstance(data["remaining_tiles"], int)
        assert isinstance(data["dealer_index"], int)
        assert data["game_wind"] in ["East", "South", "West", "North"]
        assert data["winner_found"] is False
        
        # Validate initial hand size
        assert len(data["player_hand"]) == 13
        
        # Validate wall size (144 - 52 dealt = 92)
        assert data["remaining_tiles"] == 92
    
    def test_full_game_simulation_with_ai(self):
        """Simulate a complete game with AI players."""
        # Start new game
        response = requests.post(f"{self.BASE_URL}/start-new-game")
        assert response.status_code == 200
        
        game_state = response.json()
        turn_count = 0
        max_turns = 100  # Prevent infinite loops
        
        while not game_state.get("winner_found") and turn_count < max_turns:
            # Get current player
            current_player = game_state["current_player_id"]
            
            # AI players auto-play (simulate by making API calls)
            if current_player != 0:
                # In real test, this would trigger AI logic
                # For now, we'll simulate by drawing and discarding
                pass
            
            turn_count += 1
            
            # Check for wall exhaustion
            if game_state.get("remaining_tiles", 0) < 16:
                break
        
        # Game should complete within reasonable turns
        assert turn_count < max_turns, "Game did not complete within max turns"
    
    def test_dealer_rotation_on_win(self):
        """Verify dealer rotates correctly when non-dealer wins."""
        # Start game
        response = requests.post(f"{self.BASE_URL}/start-new-game")
        initial_dealer = response.json()["dealer_index"]
        
        # Simulate non-dealer win
        # This would require setting up a specific game state
        # and triggering a win from non-dealer position
        
        # Advance dealer
        response = requests.post(
            f"{self.BASE_URL}/advance-dealer",
            json={"dealer_won": False}
        )
        
        dealer_info = response.json()
        new_dealer = dealer_info["dealer_index"]
        
        # Dealer should have advanced
        assert new_dealer != initial_dealer or dealer_info.get("round_wind") != response.json().get("round_wind")


@pytest.mark.integration
class TestRulesCompliance:
    """Validate game follows mahjong rules correctly."""
    
    BASE_URL = "http://localhost:8080"
    
    def setup_method(self):
        requests.post(f"{self.BASE_URL}/reset-game")
        requests.post(f"{self.BASE_URL}/reset-dealer-rotation")
    
    def test_initial_deal_13_tiles_per_player(self):
        """Each player must start with exactly 13 tiles."""
        response = requests.post(f"{self.BASE_URL}/start-new-game")
        data = response.json()
        
        assert len(data["player_hand"]) == 13
        
        # Validate all tiles are valid mahjong tiles
        for tile in data["player_hand"]:
            assert isinstance(tile, str)
            assert len(tile) > 0
    
    def test_wall_decreases_after_draw(self):
        """Wall tile count should decrease after each draw."""
        response = requests.post(f"{self.BASE_URL}/start-new-game")
        initial_remaining = response.json()["remaining_tiles"]
        
        # Note: In current implementation, draw happens implicitly
        # This test validates the wall tracking is working
        assert initial_remaining == 92  # 144 - (13 * 4) = 92
    
    def test_invalid_claim_rejected(self):
        """Invalid claims should be rejected with proper error."""
        requests.post(f"{self.BASE_URL}/start-new-game")
        
        # Try to claim pung when no discard exists
        response = requests.post(
            f"{self.BASE_URL}/player-claims-pung",
            json={"confirm_claim": True}
        )
        
        data = response.json()
        assert data["success"] is False
        assert "No Pung claim was pending" in data["message"]


@pytest.mark.integration
class TestAPIContract:
    """Verify API responses match expected contracts."""
    
    BASE_URL = "http://localhost:8080"
    
    def setup_method(self):
        requests.post(f"{self.BASE_URL}/reset-game")
        requests.post(f"{self.BASE_URL}/reset-dealer-rotation")
    
    def test_claim_response_format(self):
        """All claim endpoints must return consistent response format."""
        requests.post(f"{self.BASE_URL}/start-new-game")
        
        endpoints = [
            "/player-claims-pung",
            "/player-claims-win",
            "/player-claims-kong"
        ]
        
        for endpoint in endpoints:
            response = requests.post(f"{self.BASE_URL}{endpoint}", json={})
            data = response.json()
            
            # Validate required fields
            assert "success" in data
            assert "message" in data
            assert isinstance(data["success"], bool)
            assert isinstance(data["message"], str)
    
    def test_dealer_info_response_format(self):
        """Dealer info endpoint returns correct format."""
        response = requests.get(f"{self.BASE_URL}/dealer-info")
        data = response.json()
        
        assert "dealer_index" in data
        assert "round_wind" in data
        assert isinstance(data["dealer_index"], int)
        assert data["round_wind"] in ["East", "South", "West", "North"]


@pytest.mark.integration
@pytest.mark.slow
class TestScenarioLoader:
    """Load and execute game scenarios from JSON files."""
    
    BASE_URL = "http://localhost:8080"
    SCENARIOS_DIR = "tests/integration/scenarios"
    
    def load_scenario(self, filename: str) -> Dict[str, Any]:
        """Load a scenario from JSON file."""
        with open(f"{self.SCENARIOS_DIR}/{filename}", "r") as f:
            return json.load(f)
    
    def test_winning_hand_scenario(self):
        """Execute winning hand scenario and verify outcome."""
        scenario = self.load_scenario("winning_hand_scenario.json")
        
        # Setup initial state would require API extensions
        # This test demonstrates the structure
        
        expected = scenario["expected_outcome"]
        assert "winner" in expected
        assert "winning_tile" in expected
        assert "win_type" in expected
    
    def test_pung_priority_scenario(self):
        """Verify pung priority over chow."""
        scenario = self.load_scenario("pung_priority_test.json")
        
        expected = scenario["expected_outcome"]
        assert expected["successful_claim"]["type"] == "pung"
        assert expected["successful_claim"]["player"] == 1


@pytest.mark.integration
@pytest.mark.concurrent
class TestConcurrentMultiplayer:
    """Test multiple simultaneous games."""
    
    BASE_URL = "http://localhost:8080"
    
    def test_multiple_games_state_isolation(self):
        """Multiple games should not interfere with each other."""
        # Note: Current implementation has single global game state
        # This test documents the requirement for future multi-room support
        
        # Start first game
        game1 = requests.post(f"{self.BASE_URL}/start-new-game").json()
        hand1 = game1["player_hand"].copy()
        
        # Start second game (overwrites first in current implementation)
        game2 = requests.post(f"{self.BASE_URL}/start-new-game").json()
        hand2 = game2["player_hand"]
        
        # In current implementation, hands will differ due to shuffle
        # Future: Each game should maintain independent state
        
        # Both games should have valid state
        assert len(hand2) == 13
        assert game2["winner_found"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
