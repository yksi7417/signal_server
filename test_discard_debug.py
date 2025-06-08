#!/usr/bin/env python3
"""
Debug script to test the discard_tile API endpoint
"""
import json

import requests


def test_discard_tile():
    base_url = "http://localhost:8080"
    
    print("1. Starting new game...")
    start_response = requests.post(f"{base_url}/api/start_new_game")
    print(f"Start game status: {start_response.status_code}")
    if start_response.status_code != 200:
        print(f"Start game failed: {start_response.text}")
        return
    
    print("2. Drawing a tile...")
    draw_response = requests.post(f"{base_url}/api/draw_tile")
    print(f"Draw tile status: {draw_response.status_code}")
    if draw_response.status_code != 200:
        print(f"Draw tile failed: {draw_response.text}")
        return
    
    draw_data = draw_response.json()
    hand = draw_data["hand"]
    print(f"Current hand has {len(hand)} tiles")
    
    # Get the first tile to discard
    tile_to_discard = hand[0]
    print(f"3. Discarding tile: {tile_to_discard}")
    
    discard_data = {
        "tile_to_discard": tile_to_discard
    }
    
    print(f"Request data: {json.dumps(discard_data, indent=2)}")
    
    discard_response = requests.post(
        f"{base_url}/api/discard_tile",
        json=discard_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"4. Discard tile status: {discard_response.status_code}")
    print(f"Response headers: {dict(discard_response.headers)}")
    print(f"Response text: {discard_response.text}")
    
    if discard_response.status_code == 200:
        print("✅ Discard tile API works correctly!")
        response_data = discard_response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
    else:
        print("❌ Discard tile API failed!")

if __name__ == "__main__":
    test_discard_tile()
