from flask import Flask, jsonify, render_template, request

from mahjong_engine.game_state import GameState
from mahjong_engine.player_agent import AIPlayerAgent

# Initialize Flask app
app = Flask(__name__, static_folder='static/game', template_folder='static/game')
current_game_state = GameState()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game')
def game():
    return render_template('index.html')


@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    global current_game_state
    current_game_state = GameState()
    return jsonify(True)


@app.route('/api/start_new_game', methods=['POST'])
def start_new_game():
    global current_game_state
    current_game_state = GameState()

    player0_hand_serializable = []
    if current_game_state.players:
        player0 = current_game_state.players[0]
        player0_hand_serializable = [
            {"unicode": tile.unicode, "suit": tile.suit, "value": tile.value} for tile in player0.hand
        ]

    game_info = {
        "player_hand": player0_hand_serializable,
        "game_wind": current_game_state.game_wind,
        "current_player_id": current_game_state.players[
            current_game_state.current_player_index
        ].player_id,
        "winner_found": False,
        "remaining_tiles": len(current_game_state.wall)
    }

    return jsonify(game_info)


@app.route('/api/player_claims_pung', methods=['POST'])
def player_claims_pung():
    global current_game_state
    data = request.get_json()
    confirm_claim = data.get('confirm_claim', False)
    
    response = {"success": False, "message": "Claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "PUNG"
    ):
        response["message"] = "No Pung claim was pending or tile info missing."
        return jsonify(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return jsonify(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_pung_claim(
            claiming_player_id, claimed_tile
        )
        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [
                {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in player.hand
            ]
            revealed_sets_serializable = [
                {
                    "type": meld.meld_type.value,
                    "tiles": [
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in meld.raw_tiles
                    ],
                }
                for meld in player.revealed_sets
            ]
            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Pung. Your turn to discard.",
                "player_hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "current_player_id": current_game_state.current_player_index,
                "action": "discard_after_pung",
                "winner_found": current_game_state.winner_found,
            }
        else:
            response["message"] = "Backend failed to process Pung claim."
            response["winner_found"] = current_game_state.winner_found
    else:
        discarder_player_id = current_game_state.current_player_index

        current_game_state.potential_claim_tile = None
        current_game_state.pending_claim_player_id = None
        current_game_state.claim_type_pending = None

        current_game_state.current_player_index = (
            discarder_player_id + 1
        ) % len(current_game_state.players)
        current_game_state.turn_number += 1

        response = {
            "success": True,
            "message": "Pung claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.players[
                current_game_state.current_player_index
            ].player_id,
            "discarded_tile": {
                "unicode": current_game_state.current_discard.unicode,
                "suit": current_game_state.current_discard.suit,
                "value": current_game_state.current_discard.value,
            }
            if current_game_state.current_discard
            else None,
            "winner_found": current_game_state.winner_found,
        }

    return jsonify(response)


@app.route('/api/player_claims_win', methods=['POST'])
def player_claims_win():
    global current_game_state
    data = request.get_json()
    confirm_claim = data.get('confirm_claim', False)
    
    response = {"success": False, "message": "Win claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "WIN"
    ):
        response["message"] = "No Win claim was pending or tile info missing."
        return jsonify(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:  # Assuming 0 is the human player
        response["message"] = "Pending win claim is not for the human player."
        return jsonify(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_win_claim(
            claiming_player_id, claimed_tile)

        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [
                {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                for t in player.hand
            ]
            revealed_sets_serializable = [
                {
                    "type": meld.meld_type.value,
                    "tiles": [
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                        for t in meld.raw_tiles
                    ],
                }
                for meld in player.revealed_sets
            ]
            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Win!",
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "winner_found": current_game_state.winner_found,
                "winning_player_id": current_game_state.winning_player_id,
                "action": "win_claimed"
            }
        else:
            response["message"] = "Backend failed to process Win claim."
            response["winner_found"] = current_game_state.winner_found
    else:
        # Win claim declined
        discarder_player_id = current_game_state.current_player_index

        current_game_state.potential_claim_tile = None
        current_game_state.pending_claim_player_id = None
        current_game_state.claim_type_pending = None

        current_game_state.current_player_index = (
            discarder_player_id + 1) % len(current_game_state.players)
        current_game_state.turn_number += 1

        discarded_tile_serializable = None
        if current_game_state.current_discard:
            discarded_tile_serializable = {
                "unicode": current_game_state.current_discard.unicode,
                "suit": current_game_state.current_discard.suit,
                "value": current_game_state.current_discard.value,
            }

        response = {
            "success": True,
            "message": "Win claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.players[current_game_state.current_player_index].player_id,
            "discarded_tile": discarded_tile_serializable,
            "winner_found": current_game_state.winner_found
        }

    return jsonify(response)


@app.route('/api/player_claims_kong', methods=['POST'])
def player_claims_kong():
    global current_game_state
    data = request.get_json()
    confirm_claim = data.get('confirm_claim', False)
    
    response = {"success": False, "message": "Kong claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "KONG"
    ):
        response["message"] = "No Kong claim was pending or tile info missing."
        return jsonify(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return jsonify(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_kong_claim(
            claiming_player_id, claimed_tile)

        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [
                {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                for t in player.hand
            ]
            revealed_sets_serializable = [
                {
                    "type": meld.meld_type.value,
                    "tiles": [
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                        for t in meld.raw_tiles
                    ],
                }
                for meld in player.revealed_sets
            ]

            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Kong. Your turn to discard.",
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "winner_found": current_game_state.winner_found,
                "winning_player_id": current_game_state.winning_player_id if current_game_state.winner_found else None
            }
        else:
            response["message"] = "Backend failed to process Kong claim."
    else:
        # Kong claim declined
        discarder_player_id = current_game_state.current_player_index
        current_game_state.potential_claim_tile = None
        current_game_state.pending_claim_player_id = None
        current_game_state.claim_type_pending = None
        current_game_state.current_player_index = (
            discarder_player_id + 1) % len(current_game_state.players)

        response = {
            "success": True,
            "message": "Kong claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.current_player_index,
            "winner_found": current_game_state.winner_found,
            "winning_player_id": current_game_state.winning_player_id if current_game_state.winner_found else None
        }

    return jsonify(response)


@app.route('/api/player_declares_hidden_kong', methods=['POST'])
def player_declares_hidden_kong():
    global current_game_state
    data = request.get_json()
    tile_info = data.get('tile_info', {})
    
    response = {
        "success": False,
        "error": "Failed to declare hidden kong by default."}

    if not current_game_state.players:
        response["error"] = "Game not initialized or no players found."
        return jsonify(response)

    # Ensure it's the human player's turn (player_id == 0)
    if current_game_state.current_player_index != 0:
        response["error"] = "Not your turn to declare hidden kong."
        return jsonify(response)

    player_id = current_game_state.players[current_game_state.current_player_index].player_id
    if player_id != 0:  # Double check
        response["error"] = "Not your turn (player ID mismatch)."
        return jsonify(response)

    if not tile_info or 'suit' not in tile_info or 'value' not in tile_info:
        response["error"] = "Invalid tile_info provided for Hidden Kong."
        return jsonify(response)

    # Call the GameState method to process the hidden kong
    result_dict = current_game_state.process_hidden_kong(player_id, tile_info)

    if result_dict.get("success"):
        player = current_game_state.players[player_id]
        hand_serializable = [
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in player.hand
        ]
        revealed_sets_serializable = [
            {
                "type": meld.meld_type.value,
                "tiles": [
                    {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in meld.raw_tiles
                ],
                "revealed": meld.revealed
            }
            for meld in player.revealed_sets
        ]

        response = {
            "success": True,
            "message": result_dict.get("message", "Hidden Kong declared successfully."),
            "hand": hand_serializable,
            "revealed_sets": revealed_sets_serializable,
            "drawn_tile": result_dict.get("drawn_tile"),
            "winner_found": current_game_state.winner_found,
            "winning_player_id": current_game_state.winning_player_id
        }
    else:
        response["error"] = result_dict.get(
            "error", "Unknown error declaring Hidden Kong.")

    return jsonify(response)


@app.route('/api/draw_tile', methods=['POST'])
def draw_tile():
    global current_game_state

    player_id = current_game_state.players[
        current_game_state.current_player_index
    ].player_id

    drawn_tile_obj = current_game_state.draw_tile_for_current_player()

    if drawn_tile_obj:
        drawn_tile_serializable = {
            "unicode": drawn_tile_obj.unicode,
            "suit": drawn_tile_obj.suit,
            "value": drawn_tile_obj.value,
        }

        current_player_hand = current_game_state.players[
            current_game_state.current_player_index
        ].hand
        hand_serializable = [
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} 
            for t in current_player_hand
        ]

        if (
            current_game_state.winner_found
            and current_game_state.winning_player_id == player_id
        ):
            hand_serializable = [
                {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                for t in current_game_state.players[player_id].hand
            ]
            revealed_sets_serializable = [
                {
                    "type": meld.meld_type.value,
                    "tiles": [
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value} 
                        for t in meld.raw_tiles
                    ],
                }
                for meld in current_game_state.players[player_id].revealed_sets
            ]
            return jsonify({
                "success": True,
                "action": "win",
                "winner_found": True,
                "winning_player_id": player_id,
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "drawn_tile": drawn_tile_serializable,
                "remaining_tiles": len(current_game_state.wall)
            })

        return jsonify({
            "success": True,
            "drawn_tile": drawn_tile_serializable,
            "hand": hand_serializable,
            "player_id": player_id,
            "winner_found": False,
            "remaining_tiles": len(current_game_state.wall)
        })
    else:
        current_player_hand = current_game_state.players[
            current_game_state.current_player_index
        ].hand
        hand_serializable = [
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} 
            for t in current_player_hand
        ]
        return jsonify({
            "success": False,
            "error": "Failed to draw tile (wall empty or hand full?)",
            "hand": hand_serializable,
            "player_id": player_id,
            "winner_found": current_game_state.winner_found,
            "remaining_tiles": len(current_game_state.wall)
        })


@app.route('/api/discard_tile', methods=['POST'])
def discard_tile():
    try:
        global current_game_state
        data = request.get_json()
        tile_to_discard_data = data.get('tile_to_discard', {})
          # Debug output - avoid Unicode console errors on Windows
        try:
            print("Discarding tile:", tile_to_discard_data)
        except UnicodeEncodeError:
            print("Discarding tile: [Unicode tile data]")

        discarding_player_id = current_game_state.players[
            current_game_state.current_player_index
        ].player_id
        print("Current player ID:", discarding_player_id)

        if (not isinstance(tile_to_discard_data, dict)
            or "suit" not in tile_to_discard_data
            or "value" not in tile_to_discard_data):
            return jsonify({"success": False, "error": "Invalid tile data for discard."})

        success = current_game_state.discard_tile_for_current_player(
            tile_to_discard_data)

        if success:
            next_player_id = current_game_state.players[
                current_game_state.current_player_index
            ].player_id

            discarding_player_object = None
            for p in current_game_state.players:
                if p.player_id == discarding_player_id:
                    discarding_player_object = p
                    break

            hand_serializable = []

            if discarding_player_object:
                hand_serializable = [
                    {"unicode": t.unicode, "suit": t.suit, "value": t.value}
                    for t in discarding_player_object.hand
                ]
            
            # Handle potential None current_discard
            discarded_tile_info = None
            if current_game_state.current_discard:
                discarded_tile_info = {
                    "unicode": current_game_state.current_discard.unicode,
                    "suit": current_game_state.current_discard.suit,
                    "value": current_game_state.current_discard.value,
                }

            response = {
                "success": True,
                "discarded_by_player_id": discarding_player_id,
                "updated_hand": hand_serializable,
                "next_player_id": next_player_id,
                "discarded_tile": discarded_tile_info,
                "winner_found": current_game_state.winner_found,
                "remaining_tiles": len(current_game_state.wall)
            }

            if (
                current_game_state.pending_claim_player_id == 0
                and current_game_state.potential_claim_tile
                and current_game_state.claim_type_pending
            ):
                response["human_can_claim"] = current_game_state.claim_type_pending
                response["claimable_tile"] = {
                    "unicode": current_game_state.potential_claim_tile.unicode,
                    "suit": current_game_state.potential_claim_tile.suit,
                    "value": current_game_state.potential_claim_tile.value,
                }
            else:
                response["human_can_claim"] = None
            return jsonify(response)
        else:
            current_player_obj = current_game_state.players[discarding_player_id]
            hand_serializable = [{"unicode": t.unicode,
                                  "suit": t.suit,
                                  "value": t.value} for t in current_player_obj.hand]
            return jsonify({
                "success": False,
                "error": "Failed to discard tile (tile not in hand, or wrong hand size?)",
                "hand": hand_serializable,
                "player_id": discarding_player_id,
                "winner_found": current_game_state.winner_found,
            })
    except Exception as e:
        import traceback
        print(f"Error in discard_tile: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/request_ai_turn', methods=['POST'])
def request_ai_turn():
    global current_game_state
    if current_game_state.pending_claim_player_id is not None:
        return jsonify({
            "success": False,
            "error": "Human claim pending. AI turn cannot run yet.",
        })

    current_player_id = current_game_state.players[
        current_game_state.current_player_index
    ].player_id
    current_player_agent_type = type(
        current_game_state.players[current_game_state.current_player_index].agent
    )    
    if current_player_agent_type == AIPlayerAgent:
        result = current_game_state.run_ai_turn()        # Add winner_found to the result
        result["winner_found"] = current_game_state.winner_found
        # Add remaining tiles count
        result["remaining_tiles"] = len(current_game_state.wall)

        player0_hand_serializable = []
        if current_game_state.players:
            player0 = current_game_state.players[0]
            player0_hand_serializable = [
                {"unicode": tile.unicode, "suit": tile.suit, "value": tile.value} for tile in player0.hand
            ]
        result["player0_hand"] = player0_hand_serializable
        
        player0_revealed_sets_serializable = []
        if current_game_state.players:
            player0 = current_game_state.players[0]
            player0_revealed_sets_serializable = [
                {
                    "type": meld.meld_type.value,
                    "tiles": [
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in meld.raw_tiles
                    ],
                }                for meld in player0.revealed_sets
            ]
        result["player0_revealed_sets"] = player0_revealed_sets_serializable
        # Debug output - avoid Unicode console errors on Windows
        try:
            print(f"AI {current_player_id} turn result:", result)
        except UnicodeEncodeError:
            print(f"AI {current_player_id} turn result: [Unicode result data]")
        return jsonify(result)
    else:
        return jsonify({
            "success": False,
            "error": f"Player {current_player_id} is not an AI player.",
        })


# Add proper headers for static files and security
@app.after_request
def after_request(response):
    # Set proper MIME types for JavaScript files
    if request.path.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'
    
    # Add CORS headers if needed
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Add security headers but allow local storage
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    return response


if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
