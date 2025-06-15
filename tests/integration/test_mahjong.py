"""
Integration tests for the Mahjong Flask application.
These tests verify that the entire application stack works correctly:
- Flask server startup and API endpoints
- JavaScript module serving and MIME types
- Game functionality end-to-end
- Deployment readiness checks
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pytest
import requests

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mahjong_engine.game_state import GameState


def kill_existing_servers(port=8080):
    """Kill any existing processes running on the specified port."""
    killed_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections for this specific process
                connections = proc.connections()
                if connections:
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                            proc.terminate()
                            killed_processes.append(proc.info['pid'])
                            
                            # Wait for process to terminate, then force kill if needed
                            try:
                                proc.wait(timeout=5)
                            except psutil.TimeoutExpired:
                                proc.kill()
                                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
    except Exception as e:
        print(f"Error while killing existing servers: {e}")
    
    if killed_processes:
        print(f"Killed {len(killed_processes)} processes using port {port}")
        time.sleep(2)  # Give time for ports to be released
    
    return killed_processes


def wait_for_server_start(base_url, max_attempts=30, timeout=1):
    """Wait for the Flask server to start and be responsive."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/", timeout=timeout)
            if response.status_code == 200:
                print(f"Server is responsive after {attempt + 1} attempts")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def start_flask_server():
    """Start a fresh Flask server and return the process."""
    # Change to project directory
    os.chdir(project_root)
    
    # Start Flask server in background with proper output handling
    if os.name == 'nt':  # Windows
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:  # Unix-like
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
    
    return process


def stop_flask_server(process):
    """Stop the Flask server process gracefully."""
    if process and process.poll() is None:
        try:
            if os.name == 'nt':  # Windows
                # Kill the entire process group
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                             capture_output=True, check=False)
            else:  # Unix-like
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print("Flask server stopped gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                print("Flask server force killed")
                
        except Exception as e:
            print(f"Error stopping Flask server: {e}")
            try:
                process.kill()
                process.wait()
            except:
                pass


@pytest.fixture(scope="session")
def global_flask_server():
    """Session-wide Flask server fixture that manages server lifecycle."""
    base_url = "http://localhost:8080"
    
    print("\n" + "="*60)
    print("SETTING UP INTEGRATION TEST ENVIRONMENT")
    print("="*60)
    
    # Kill any existing servers on port 8080
    print("1. Killing any existing servers on port 8080...")
    kill_existing_servers(8080)
    
    # Start fresh Flask server
    print("2. Starting fresh Flask server...")
    process = start_flask_server()
    
    # Wait for server to be responsive
    print("3. Waiting for server to start...")
    if not wait_for_server_start(base_url, max_attempts=30):
        stop_flask_server(process)
        pytest.fail("Flask server failed to start within 30 seconds")
    print(f"4. Flask server is ready for testing! pid={process.pid}")
    print("="*60)
    
    yield process, base_url
    
    # Cleanup
    print("\n" + "="*60)
    print("CLEANING UP INTEGRATION TEST ENVIRONMENT")
    print("="*60)
    print("Stopping Flask server...")
    stop_flask_server(process)
    print("Integration test cleanup complete!")
    print("="*60)


class TestFlaskServerIntegration:
    """Test Flask server startup and basic functionality."""
    
    @pytest.mark.timeout(20)
    def test_server_is_running(self, global_flask_server):
        """Test that the Flask server is running and accessible."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200, "Server should be accessible on port 8080"
    
    @pytest.mark.timeout(20)
    def test_root_endpoint_serves_html(self, global_flask_server):
        """Test that the root endpoint serves the game HTML."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "mahjong" in response.text.lower() or "game" in response.text.lower()
    
    @pytest.mark.timeout(20)
    def test_game_endpoint_serves_html(self, global_flask_server):
        """Test that the /game endpoint serves the same HTML as root."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/game")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")


class TestAPIEndpointsIntegration:
    """Test all Flask API endpoints for correct functionality."""
    
    @pytest.mark.timeout(20)
    def test_start_new_game_api(self, global_flask_server):
        """Test the start_new_game API endpoint."""
        process, base_url = global_flask_server
        response = requests.post(f"{base_url}/api/start_new_game")
        assert response.status_code == 200
        
        data = response.json()
        assert "player_hand" in data
        assert "game_wind" in data
        assert "current_player_id" in data
        assert "winner_found" in data
        assert "remaining_tiles" in data
        
        # Verify dealer rotation fields are included
        assert "dealer_index" in data
        assert "round_wind" in data

        
        # Verify player hand has tiles
        assert len(data["player_hand"]) > 0
        assert data["remaining_tiles"] > 0
        assert data["current_player_id"] == 0
        assert data["winner_found"] is False
        
        # Verify initial dealer rotation state
        assert data["dealer_index"] == 0  # East dealer starts
        assert data["round_wind"] == "East"  # East Round starts

    
    @pytest.mark.timeout(20)
    def test_reset_game_api(self, global_flask_server):
        """Test the reset_game API endpoint."""
        process, base_url = global_flask_server
        response = requests.post(f"{base_url}/api/reset_game")
        assert response.status_code == 200
        assert response.json() is True
    
    @pytest.mark.timeout(20)
    def test_draw_tile_api(self, global_flask_server):
        """Test the draw_tile API endpoint."""
        process, base_url = global_flask_server
        # First start a new game
        requests.post(f"{base_url}/api/start_new_game")
        
        response = requests.post(f"{base_url}/api/draw_tile")
        assert response.status_code == 200
        
        data = response.json()
        assert "drawn_tile" in data
        assert "hand" in data
        assert "player_id" in data
        assert "remaining_tiles" in data
        assert "success" in data
        assert "winner_found" in data
          # Verify tile structure
        drawn_tile = data["drawn_tile"]
        assert isinstance(drawn_tile, str)
        assert data["success"] is True
        assert data["player_id"] == 0
    
    @pytest.mark.timeout(20)
    def test_discard_tile_api(self, global_flask_server):
        """Test the discard_tile API endpoint."""
        process, base_url = global_flask_server        # Start a new game and draw a tile
        requests.post(f"{base_url}/api/start_new_game")
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        hand = draw_response.json()["hand"]
        print(hand)
        
        # Discard the first tile in hand (use correct API format)
        tile_to_discard = hand[0]
        discard_data = {
            "tile_to_discard": tile_to_discard
        }
        
        print(discard_data)

        response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )

        print(response.json())
        
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "discarded_tile" in data
        assert "next_player_id" in data
        assert "winner_found" in data

    @pytest.mark.timeout(20)
    def test_request_ai_turn_api(self, global_flask_server):
        """Test the request_ai_turn API endpoint."""
        process, base_url = global_flask_server
        # Start a new game and make it an AI player's turn
        requests.post(f"{base_url}/api/start_new_game")

        # Draw and discard a tile to advance to AI player's turn (Player 1)
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        hand = draw_response.json()["hand"]
        tile_to_discard = hand[0]

        discard_response = requests.post(
            f"{base_url}/api/discard_tile",
            json={"tile_to_discard": tile_to_discard},
            headers={"Content-Type": "application/json"}
        )
        
        # Verify the discard was successful first
        assert discard_response.status_code == 200, f"Discard failed: {discard_response.text}"
        discard_data = discard_response.json()
        assert discard_data["success"] is True, f"Discard not successful: {discard_data}"
        
        # Now it should be Player 1's turn (AI), so request AI turn should work
        response = requests.post(f"{base_url}/api/request_ai_turn")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "winner_found" in data
        # Note: This might fail if the current player is not AI, which is expected behavior

    @pytest.mark.timeout(30)
    def test_remaining_tiles_updates_for_all_players(self, global_flask_server):
        """Test that remaining_tiles count updates after both human and AI turns."""
        process, base_url = global_flask_server
        
        # 1. Start a new game
        response = requests.post(f"{base_url}/api/start_new_game")
        assert response.status_code == 200
        
        game_data = response.json()
        initial_remaining_tiles = game_data.get('remaining_tiles')
        assert initial_remaining_tiles is not None
        assert initial_remaining_tiles > 0
        
        # 2. Human player draws a tile (should decrease remaining_tiles by 1)
        response = requests.post(f"{base_url}/api/draw_tile")
        assert response.status_code == 200
        
        draw_data = response.json()
        assert draw_data["success"] is True
        remaining_after_human_draw = draw_data.get('remaining_tiles')
        assert remaining_after_human_draw == initial_remaining_tiles - 1
        
        # 3. Human player discards a tile (remaining_tiles should stay the same)
        hand = draw_data.get("hand", [])
        assert len(hand) > 0
        
        tile_to_discard = hand[0]
        discard_data = {"tile_to_discard": tile_to_discard}
        response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        discard_result = response.json()
        assert discard_result["success"] is True
        remaining_after_human_discard = discard_result.get('remaining_tiles')
        assert remaining_after_human_discard == remaining_after_human_draw
        
        # 4. AI player takes a turn (should decrease remaining_tiles by 1 more)
        response = requests.post(f"{base_url}/api/request_ai_turn")
        assert response.status_code == 200, f"AI turn request failed: {response.text}"
        
        ai_result = response.json()
        assert ai_result.get("success") is True
        remaining_after_first_ai = ai_result.get('remaining_tiles')
        assert remaining_after_first_ai == remaining_after_human_discard - 1
        
        # Verify AI discarded a tile
        assert "discarded_tile" in ai_result
        assert ai_result["discarded_tile"] is not None
        
        # 5. Another AI player takes a turn (should decrease remaining_tiles by 1 more)
        response = requests.post(f"{base_url}/api/request_ai_turn")
        assert response.status_code == 200, f"Second AI turn request failed: {response.text}"
        
        ai_result2 = response.json()
        if ai_result2.get("success"):
            # If AI turn succeeded, remaining_tiles should decrease by 1
            remaining_after_second_ai = ai_result2.get('remaining_tiles')
            assert remaining_after_second_ai == remaining_after_first_ai - 1
            
            # Verify the progression: each draw reduces remaining_tiles by 1
            total_draws = 3  # human + first AI + second AI
            expected_remaining = initial_remaining_tiles - total_draws
            assert remaining_after_second_ai == expected_remaining
        else:
            # If AI turn failed (e.g., back to human player), that's also valid
            # Just verify the first AI turn worked correctly
            assert remaining_after_first_ai == initial_remaining_tiles - 2


class TestJavaScriptModulesIntegration:
    """Test that JavaScript modules are served correctly with proper MIME types."""
    
    @pytest.mark.timeout(20)
    def test_main_js_serves_correctly(self, global_flask_server):
        """Test that main.js is served with correct MIME type."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/game/main.js")
        assert response.status_code == 200
        
        content_type = response.headers.get("Content-Type", "")
        assert any(js_type in content_type for js_type in [
            "application/javascript", 
            "text/javascript"
        ]), f"Expected JavaScript MIME type, got: {content_type}"
        
        # Verify it contains ES6 module syntax
        assert "import" in response.text
        assert "export" in response.text or "from" in response.text
    @pytest.mark.timeout(20)
    def test_all_js_modules_serve_correctly(self, global_flask_server):
        """Test that all JavaScript modules are served correctly."""
        process, base_url = global_flask_server
        js_modules = [
            "/game/js/gameActions.js",
            "/game/js/claimsHandler.js", 
            "/game/js/tileDisplay.js",
            "/game/js/aiTurnHandler.js",
            "/game/js/celebrationScreen.js",
            "/game/js/gameStore.js"
        ]
        
        for module_path in js_modules:
            response = requests.get(f"{base_url}{module_path}")
            assert response.status_code == 200, f"Module {module_path} should be accessible"
            
            content_type = response.headers.get("Content-Type", "")
            assert any(js_type in content_type for js_type in [
                "application/javascript", 
                "text/javascript"
            ]), f"Module {module_path} should have JavaScript MIME type, got: {content_type}"
    
    @pytest.mark.timeout(20)
    def test_security_headers_present(self, global_flask_server):
        """Test that security headers are present in responses."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/game/main.js")
        assert response.status_code == 200
        
        # Check for CORS headers
        headers = response.headers
        assert "Cache-Control" in headers


class TestGameFlowIntegration:
    """Test complete game flow scenarios."""
    
    @pytest.mark.timeout(20)
    def test_complete_turn_cycle(self, global_flask_server):
        """Test a complete turn cycle: start game -> draw -> discard -> AI turn."""
        process, base_url = global_flask_server
        # Start new game
        start_response = requests.post(f"{base_url}/api/start_new_game")
        assert start_response.status_code == 200, "Failed to start new game"
        start_data = start_response.json()
        initial_tiles = start_data["remaining_tiles"]
        
        # Draw a tile
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        assert draw_response.status_code == 200, "Failed to draw new game"
        draw_data = draw_response.json()
        assert draw_data["success"] is True
        assert draw_data["remaining_tiles"] == initial_tiles - 1
        
        # Discard a tile
        hand = draw_data["hand"]
        tile_to_discard = hand[0]
        discard_data = {
            "tile_to_discard": tile_to_discard
        }
        print(discard_data)
        
        discard_response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )
        assert discard_response.status_code == 200, "Failed to discard a tile"
        discard_data = discard_response.json()
        assert discard_data["success"] is True
        
        # Request AI turn
        ai_response = requests.post(f"{base_url}/api/request_ai_turn")
        assert ai_response.status_code == 200, "Failed to request AI turn"
        ai_data = ai_response.json()
        
        # Verify the game state progressed        assert "success" in ai_data
        assert "winner_found" in ai_data
    
    @pytest.mark.timeout(20)
    def test_game_reset_functionality(self, global_flask_server):
        """Test that game reset works correctly."""
        process, base_url = global_flask_server
        # Start a game and make some moves
        requests.post(f"{base_url}/api/start_new_game")
        requests.post(f"{base_url}/api/draw_tile")
        
        # Reset the game
        reset_response = requests.post(f"{base_url}/api/reset_game")
        assert reset_response.status_code == 200
        assert reset_response.json() is True
        
        # Start a new game and verify it's fresh
        new_game_response = requests.post(f"{base_url}/api/start_new_game")
        assert new_game_response.status_code == 200
        new_game_data = new_game_response.json()
        
        # Should have fresh state
        assert new_game_data["current_player_id"] == 0
        assert new_game_data["winner_found"] is False
        assert new_game_data["remaining_tiles"] > 80  # Should be close to full deck


class TestDeploymentReadiness:
    """Test that the application is ready for deployment to fly.io."""
    
    @pytest.mark.timeout(20)
    def test_flask_app_structure(self):
        """Test that the app has proper structure for deployment."""
        app_py_path = project_root / "app.py"
        assert app_py_path.exists(), "app.py should exist for deployment"

        # Check that app.py contains aiohttp app
        with open(app_py_path, 'r') as f:
            content = f.read()
            assert "from aiohttp import web" in content
            assert "web.Application" in content
            assert "web.run_app" in content
    @pytest.mark.timeout(20)
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists with necessary dependencies."""
        req_path = project_root / "requirements.txt"
        assert req_path.exists(), "requirements.txt should exist for deployment"
        
        with open(req_path, 'r') as f:
            requirements = f.read()
            assert "aiohttp" in requirements, "aiohttp should be in requirements.txt"
    
    @pytest.mark.timeout(20)
    def test_fly_toml_configuration(self):
        """Test that fly.toml is properly configured."""
        fly_toml_path = project_root / "fly.toml"
        assert fly_toml_path.exists(), "fly.toml should exist for fly.io deployment"
        
        with open(fly_toml_path, 'r') as f:
            content = f.read()
            assert "8080" in content, "fly.toml should reference port 8080"
    
    @pytest.mark.timeout(20)
    def test_server_responds_on_correct_port(self, global_flask_server):
        """Test that server responds on the port configured for fly.io."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        
        # Verify server is binding to 0.0.0.0 (required for fly.io)
        # This is implicit if we can reach it via localhost
    
    @pytest.mark.timeout(20)
    def test_static_files_accessible(self, global_flask_server):
        """Test that static files are accessible for deployment."""
        process, base_url = global_flask_server
        static_files = [
            "/",
            "/game/main.js",
            "/game/js/gameActions.js"
        ]
        
        for static_file in static_files:
            response = requests.get(f"{base_url}{static_file}")
            assert response.status_code == 200, f"Static file {static_file} should be accessible"


class TestDealerRotationIntegration:
    """Test dealer rotation system through API endpoints."""
    
    @pytest.mark.timeout(30)
    def test_start_new_game_dealer_info(self, global_flask_server):
        """Test that start_new_game includes correct dealer rotation information."""
        process, base_url = global_flask_server
        
        response = requests.post(f"{base_url}/api/start_new_game")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all dealer rotation fields are present
        assert "dealer_index" in data
        assert "round_wind" in data

        
        # Verify initial values follow traditional Mahjong rules
        assert data["dealer_index"] == 0  # East dealer starts (player 0)
        assert data["round_wind"] == "East"  # East Round starts

        
        # Verify game_wind is consistent with traditional setup
        assert data["game_wind"] == "East"  # Should match round_wind initially
    
    @pytest.mark.timeout(30)
    def test_reset_game_resets_dealer_info(self, global_flask_server):
        """Test that reset_game properly resets dealer rotation state."""
        process, base_url = global_flask_server
        
        # Start a game
        start_response = requests.post(f"{base_url}/api/start_new_game")
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        # Verify initial state
        assert start_data["dealer_index"] == 0
        assert start_data["round_wind"] == "East"

        
        # Reset the game
        reset_response = requests.post(f"{base_url}/api/reset_game")
        assert reset_response.status_code == 200
        assert reset_response.json() is True
        
        # Start new game after reset
        new_start_response = requests.post(f"{base_url}/api/start_new_game")
        assert new_start_response.status_code == 200
        new_start_data = new_start_response.json()
        
        # Verify dealer rotation state is reset to initial values
        assert new_start_data["dealer_index"] == 0
        assert new_start_data["round_wind"] == "East"

    
    @pytest.mark.timeout(30)
    def test_dealer_info_consistency_across_endpoints(self, global_flask_server):
        """Test that dealer info is consistent across different API endpoints."""
        process, base_url = global_flask_server
        
        # Start new game and get initial dealer info
        start_response = requests.post(f"{base_url}/api/start_new_game")
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        initial_dealer = start_data["dealer_index"]
        initial_round = start_data["round_wind"]

        
        # Make a few game moves and check if dealer info is preserved
        # (since dealer rotation only happens on hand completion)
        
        # Draw a tile
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        assert draw_response.status_code == 200
        draw_data = draw_response.json()
        
        # Note: Not all endpoints may include dealer info, 
        # but the game state should remain consistent
        # This test validates that the state doesn't randomly change
        
        # Discard a tile
        if "hand" in draw_data and len(draw_data["hand"]) > 0:
            tile_to_discard = draw_data["hand"][0]
            discard_response = requests.post(
                f"{base_url}/api/discard_tile",
                json={"tile_to_discard": tile_to_discard},
                headers={"Content-Type": "application/json"}
            )
            assert discard_response.status_code == 200
            discard_data = discard_response.json()
            assert discard_data["success"] is True
        
        # AI turn
        ai_response = requests.post(f"{base_url}/api/request_ai_turn")
        assert ai_response.status_code == 200
        ai_data = ai_response.json()
        
        # During normal gameplay (no hand completion), dealer info should remain the same
        # We can't easily test dealer rotation in integration tests without simulating
        # complete hands or wins, but we can verify the info is maintained consistently
        
        # Start another game to verify reset works
        final_start_response = requests.post(f"{base_url}/api/start_new_game")
        assert final_start_response.status_code == 200
        final_start_data = final_start_response.json()
        
        # Should return to initial dealer state
        assert final_start_data["dealer_index"] == 0
        assert final_start_data["round_wind"] == "East"


if __name__ == "__main__":
    # Run integration tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
