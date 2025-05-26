import eel
from mahjong_engine.game_state import GameState
from mahjong_engine.player_agent import AIPlayerAgent

# 1. point Eel at your web/ folder
eel.init('static/game')
current_game_state = GameState()


@eel.expose
def reset_game():
    global current_game_state
    current_game_state = GameState()
    return True


@eel.expose
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
    }

    return game_info


@eel.expose
def eel_player_claims_pung(confirm_claim):
    global current_game_state
    response = {"success": False, "message": "Claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "PUNG"
    ):
        response["message"] = "No Pung claim was pending or tile info missing."
        return response

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return response

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

    return response


@eel.expose
def eel_draw_tile():
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
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in current_player_hand
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
                        {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in meld.raw_tiles
                    ],
                }
                for meld in current_game_state.players[player_id].revealed_sets
            ]
            return {
                "success": True,
                "action": "win",
                "winner_found": True,
                "winning_player_id": player_id,
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "drawn_tile": drawn_tile_serializable,
            }


        return {
            "success": True,
            "drawn_tile": drawn_tile_serializable,
            "hand": hand_serializable,
            "player_id": player_id,
            "winner_found": False,
        }
    else:

        current_player_hand = current_game_state.players[
            current_game_state.current_player_index
        ].hand
        hand_serializable = [
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in current_player_hand
        ]
        return {
            "success": False,
            "error": "Failed to draw tile (wall empty or hand full?)",
            "hand": hand_serializable,
            "player_id": player_id,
            "winner_found": current_game_state.winner_found,
        }


@eel.expose
def eel_discard_tile(tile_to_discard_data):
    global current_game_state
    print("Discarding tile:", tile_to_discard_data)

    discarding_player_id = current_game_state.players[
        current_game_state.current_player_index
    ].player_id
    print("Current player ID:", discarding_player_id)

    if (
        not isinstance(tile_to_discard_data, dict)
        or "suit" not in tile_to_discard_data
        or "value" not in tile_to_discard_data
    ):
        return {"success": False, "error": "Invalid tile data for discard."}

    success = current_game_state.discard_tile_for_current_player(tile_to_discard_data)

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

        response = {
            "success": True,
            "discarded_by_player_id": discarding_player_id,
            "updated_hand": hand_serializable,
            "next_player_id": next_player_id,
            "discarded_tile": {
                "unicode": current_game_state.current_discard.unicode,
                "suit": current_game_state.current_discard.suit,
                "value": current_game_state.current_discard.value,
            },
            "winner_found": current_game_state.winner_found,
        }


        if (
            current_game_state.pending_claim_player_id == 0
            and current_game_state.potential_claim_tile
            and current_game_state.claim_type_pending == "PUNG"
        ):
            response["human_can_claim_pung"] = True
            response["claimable_tile"] = {
                "unicode": current_game_state.potential_claim_tile.unicode,
                "suit": current_game_state.potential_claim_tile.suit,
                "value": current_game_state.potential_claim_tile.value,
            }
        else:
            response["human_can_claim_pung"] = False
        return response
    else:

        current_player_obj = current_game_state.players[discarding_player_id]
        hand_serializable = [
            {"unicode": t.unicode, "suit": t.suit, "value": t.value} for t in current_player_obj.hand
        ]
        return {
            "success": False,
            "error": "Failed to discard tile (tile not in hand, or wrong hand size?)",
            "hand": hand_serializable,
            "player_id": discarding_player_id,
            "winner_found": current_game_state.winner_found,
        }


@eel.expose
def eel_request_ai_turn():
    global current_game_state
    if current_game_state.pending_claim_player_id is not None:
        return {
            "success": False,
            "error": "Human claim pending. AI turn cannot run yet.",
        }

    current_player_id = current_game_state.players[
        current_game_state.current_player_index
    ].player_id

    current_player_agent_type = type(
        current_game_state.players[current_game_state.current_player_index].agent
    )
    if current_player_agent_type == AIPlayerAgent:
        result = current_game_state.run_ai_turn()

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
                }
                for meld in player0.revealed_sets
            ]
        result["player0_revealed_sets"] = player0_revealed_sets_serializable
        print(f"AI {current_player_id} turn result:", result)
        return result


if __name__ == "__main__":
    eel.start("index.html", size=(1200, 1500))
