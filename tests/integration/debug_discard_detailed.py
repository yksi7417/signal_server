#!/usr/bin/env python3
"""
Debug script to test the discard_tile API endpoint with detailed error handling
"""
import json
import requests


def test_discard_tile_detailed():
    base_url = "http://localhost:8080"
    
    try:
        print("1. Starting new game...")
        start_response = requests.post(f"{base_url}/api/start_new_game")
        print(f"Start game status: {start_response.status_code}")
        if start_response.status_code != 200:
            print(f"Start game failed: {start_response.text}")
            return
        
        start_data = start_response.json()
        print(f"Initial hand size: {len(start_data.get('player_hand', []))}")
        
        print("\n2. Drawing a tile...")
        draw_response = requests.post(f"{base_url}/api/draw_tile")
        print(f"Draw tile status: {draw_response.status_code}")
        if draw_response.status_code != 200:
            print(f"Draw tile failed: {draw_response.text}")
            return
        
        draw_data = draw_response.json()
        hand = draw_data["hand"]
        print(f"Hand after draw has {len(hand)} tiles")
        print(f"Hand contents: {json.dumps(hand, indent=2)}")
        
        # Get the first tile to discard
        tile_to_discard = hand[0]
        print(f"\n3. Discarding tile: {tile_to_discard}")
        
        discard_data = {
            "tile_to_discard": tile_to_discard
        }
        
        print(f"Request data: {json.dumps(discard_data, indent=2)}")
        
        discard_response = requests.post(
            f"{base_url}/api/discard_tile",
            json=discard_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n4. Discard tile status: {discard_response.status_code}")
        print(f"Response headers: {dict(discard_response.headers)}")
        
        if discard_response.status_code == 200:
            print("✅ Discard tile API works correctly!")
            response_data = discard_response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
        else:
            print("❌ Discard tile API failed!")
            print(f"Response text: {discard_response.text}")
            
            # Try to parse as JSON to see if there's a structured error
            try:
                error_data = discard_response.json()
                print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("Response is not valid JSON")
                
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_discard_tile_detailed()
