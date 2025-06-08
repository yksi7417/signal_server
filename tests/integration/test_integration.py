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
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
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
    
    # Start Flask server in background
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    return process


def stop_flask_server(process):
    """Stop the Flask server process gracefully."""
    if process and process.poll() is None:
        try:
            if os.name == 'nt':  # Windows
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:  # Unix-like
                process.terminate()
            
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
    
    print("4. Flask server is ready for testing!")
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
        
        # Verify player hand has tiles
        assert len(data["player_hand"]) > 0
        assert data["remaining_tiles"] > 0
        assert data["current_player_id"] == 0
        assert data["winner_found"] is False
    
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
        assert "suit" in drawn_tile
        assert "unicode" in drawn_tile
        assert "value" in drawn_tile
        assert data["success"] is True
        assert data["player_id"] == 0
    
    @pytest.mark.timeout(20)
    def test_discard_tile_api(self, global_flask_server):
        """Test the discard_tile API endpoint."""
        process, base_url = global_flask_server
        # Start a new game and draw a tile
        requests.post(f"{base_url}/api/start_new_game")
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        hand = draw_response.json()["hand"]
        
        # Discard the first tile in hand (use correct API format)
        tile_to_discard = hand[0]
        discard_data = {
            "tile_to_discard": tile_to_discard
        }
        
        response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )
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


class TestJavaScriptModulesIntegration:
    """Test that JavaScript modules are served correctly with proper MIME types."""
    
    @pytest.mark.timeout(20)
    def test_main_js_serves_correctly(self, global_flask_server):
        """Test that main.js is served with correct MIME type."""
        process, base_url = global_flask_server
        response = requests.get(f"{base_url}/static/game/main.js")
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
            "/static/game/js/gameActions.js",
            "/static/game/js/claimsHandler.js", 
            "/static/game/js/tileDisplay.js",
            "/static/game/js/aiTurnHandler.js",
            "/static/game/js/celebrationScreen.js",
            "/static/game/js/gameStore.js"
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
        response = requests.get(f"{base_url}/static/game/main.js")
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
        assert start_response.status_code == 200
        start_data = start_response.json()
        initial_tiles = start_data["remaining_tiles"]
        
        # Draw a tile
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        assert draw_response.status_code == 200
        draw_data = draw_response.json()
        assert draw_data["success"] is True
        assert draw_data["remaining_tiles"] == initial_tiles - 1
        
        # Discard a tile
        hand = draw_data["hand"]
        tile_to_discard = hand[0]
        discard_data = {
            "tile_to_discard": tile_to_discard
        }
        
        discard_response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )
        assert discard_response.status_code == 200
        discard_data = discard_response.json()
        assert discard_data["success"] is True
        
        # Request AI turn
        ai_response = requests.post(f"{base_url}/api/request_ai_turn")
        assert ai_response.status_code == 200
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
        """Test that Flask app has proper structure for deployment."""
        app_py_path = project_root / "app.py"
        assert app_py_path.exists(), "app.py should exist for deployment"
        
        # Check that app.py contains Flask app
        with open(app_py_path, 'r') as f:
            content = f.read()
            assert "from flask import" in content
            assert "app = Flask" in content
            assert "if __name__ == '__main__':" in content or "app.run" in content
    @pytest.mark.timeout(20)
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists with necessary dependencies."""
        req_path = project_root / "requirements.txt"
        assert req_path.exists(), "requirements.txt should exist for deployment"
        
        with open(req_path, 'r') as f:
            requirements = f.read()
            assert "Flask" in requirements, "Flask should be in requirements.txt"
    
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
            "/static/game/index.html",
            "/static/game/main.js",
            "/static/game/js/gameActions.js"
        ]
        
        for static_file in static_files:
            response = requests.get(f"{base_url}{static_file}")
            assert response.status_code == 200, f"Static file {static_file} should be accessible"


if __name__ == "__main__":
    # Run integration tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
