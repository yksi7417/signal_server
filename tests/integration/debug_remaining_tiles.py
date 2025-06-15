#!/usr/bin/env python3
"""
Debug script to test remaining tiles count updates for both human and AI turns
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_remaining_tiles_updates():
    """Test that remaining tiles count updates after both human and AI turns"""
    
    print("=== Testing Remaining Tiles Count Updates ===")
    
    # Start a new game
    print("\n1. Starting new game...")
    response = requests.post(f"{BASE_URL}/api/start_new_game")
    if response.status_code != 200:
        print(f"Failed to start game: {response.status_code}")
        return
    
    game_data = response.json()
    print(f"   Initial remaining tiles: {game_data.get('remaining_tiles')}")
    
    # Human draws a tile
    print("\n2. Human player draws a tile...")
    response = requests.post(f"{BASE_URL}/api/draw_tile")
    if response.status_code != 200:
        print(f"Failed to draw tile: {response.status_code}")
        return
    
    draw_data = response.json()
    print(f"   After human draw, remaining tiles: {draw_data.get('remaining_tiles')}")
    
    # Human discards a tile
    print("\n3. Human player discards a tile...")
    hand = draw_data.get("hand", [])
    if not hand:
        print("   No tiles in hand!")
        return
    
    tile_to_discard = hand[0]
    print(f"   Discarding: {tile_to_discard.get('unicode', '?')} ({tile_to_discard.get('suit')} {tile_to_discard.get('value')})")
    
    discard_data = {"tile_to_discard": tile_to_discard}
    response = requests.post(f"{BASE_URL}/api/discard_tile", json=discard_data)
    if response.status_code != 200:
        print(f"Failed to discard tile: {response.status_code}")
        return
    
    discard_result = response.json()
    print(f"   After human discard, remaining tiles: {discard_result.get('remaining_tiles')}")
    
    # AI takes a turn
    print("\n4. AI player takes a turn...")
    response = requests.post(f"{BASE_URL}/api/request_ai_turn")
    if response.status_code != 200:
        print(f"Failed to request AI turn: {response.status_code}")
        return
    
    ai_result = response.json()
    if ai_result.get("success"):
        print(f"   AI discarded: {ai_result.get('discarded_tile', {}).get('unicode', '?')}")
        print(f"   After AI turn, remaining tiles: {ai_result.get('remaining_tiles')}")
    else:
        print(f"   AI turn failed: {ai_result.get('error')}")
    
    # Another AI turn if possible
    print("\n5. Another AI player takes a turn...")
    response = requests.post(f"{BASE_URL}/api/request_ai_turn")
    if response.status_code != 200:
        print(f"Failed to request second AI turn: {response.status_code}")
        return
    
    ai_result2 = response.json()
    if ai_result2.get("success"):
        print(f"   AI discarded: {ai_result2.get('discarded_tile', {}).get('unicode', '?')}")
        print(f"   After second AI turn, remaining tiles: {ai_result2.get('remaining_tiles')}")
    else:
        print(f"   Second AI turn failed: {ai_result2.get('error')}")
    
    print("\n=== Test Complete ===")
    print("Expected behavior: remaining_tiles should decrease by 1 after each draw (human and AI)")

if __name__ == "__main__":
    try:
        test_remaining_tiles_updates()
    except requests.RequestException as e:
        print(f"Connection error: {e}")
        print("Make sure the server is running on localhost:8080")
    except Exception as e:
        print(f"Error: {e}")
