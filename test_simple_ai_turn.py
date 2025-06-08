#!/usr/bin/env python3
"""
Simple standalone test to debug the AI turn timeout issue.
"""

import time

import requests

BASE_URL = "http://localhost:8080"

def test_ai_turn_with_timeouts():
    """Test AI turn with explicit timeouts to identify where it hangs."""
    print("Testing AI turn with timeouts...")
    
    try:
        # Start new game
        print("1. Starting new game...")
        response = requests.post(f"{BASE_URL}/api/start_new_game", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Failed to start game: {response.text}")
            return
        game_data = response.json()
        print(f"   Current player: {game_data.get('current_player_id')}")
        
        # Draw tile
        print("2. Drawing tile...")
        response = requests.post(f"{BASE_URL}/api/draw_tile", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Failed to draw tile: {response.text}")
            return
        draw_data = response.json()
        print(f"   Success: {draw_data.get('success')}")
        print(f"   Player ID: {draw_data.get('player_id')}")
        
        # Discard tile
        print("3. Discarding tile...")
        hand = draw_data.get("hand", [])
        if not hand:
            print("   No tiles in hand to discard!")
            return
            
        tile_to_discard = hand[0]
        print(f"   Discarding: {tile_to_discard}")
        
        discard_data = {"tile_to_discard": tile_to_discard}
        response = requests.post(
            f"{BASE_URL}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Failed to discard tile: {response.text}")
            return
        discard_result = response.json()
        print(f"   Success: {discard_result.get('success')}")
        print(f"   Next player: {discard_result.get('next_player_id')}")
        
        # Request AI turn with short timeout
        print("4. Requesting AI turn...")
        start_time = time.time()
        try:
            response = requests.post(f"{BASE_URL}/api/request_ai_turn", timeout=10)
            elapsed = time.time() - start_time
            print(f"   Status: {response.status_code} (took {elapsed:.2f}s)")
            
            if response.status_code == 200:
                ai_data = response.json()
                print(f"   Success: {ai_data.get('success')}")
                print(f"   AI Player ID: {ai_data.get('ai_player_id')}")
                if not ai_data.get('success'):
                    print(f"   Error: {ai_data.get('error')}")
            else:
                print(f"   HTTP Error: {response.text}")
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"   TIMEOUT after {elapsed:.2f}s - This is the issue!")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   Exception after {elapsed:.2f}s: {e}")
            
    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == "__main__":
    test_ai_turn_with_timeouts()
