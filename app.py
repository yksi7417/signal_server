import os
import aiohttp_cors
from aiohttp import web, WSMsgType

from mahjong_engine.game_state import GameState
from mahjong_engine.player_agent import AIPlayerAgent
from mahjong_engine.game_session import (
    reset_dealer_rotation_state,
    advance_dealer_rotation,
    get_current_dealer_info,
)


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static", "game")

current_game_state = GameState()


async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def game(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def reset_game(request: web.Request) -> web.Response:
    global current_game_state
    current_game_state = GameState()
    return web.json_response(True)


async def start_new_game(request: web.Request) -> web.Response:
    global current_game_state
    current_game_state = GameState()

    player0_hand_serializable = []
    if current_game_state.players:
        player0 = current_game_state.players[0]
        player0_hand_serializable = [tile.unicode for tile in player0.hand]

    dealer_info = get_current_dealer_info()

    game_info = {
        "player_hand": player0_hand_serializable,
        "game_wind": current_game_state.game_wind,
        "current_player_id": current_game_state.players[
            current_game_state.current_player_index
        ].player_id,
        "winner_found": False,
        "remaining_tiles": len(current_game_state.wall),
        "dealer_index": dealer_info["dealer_index"],
        "round_wind": dealer_info["round_wind"],
    }

    return web.json_response(game_info)


async def reset_dealer_rotation(request: web.Request) -> web.Response:
    reset_dealer_rotation_state()
    dealer_info = get_current_dealer_info()
    return web.json_response(
        {
            "success": True,
            "message": "Dealer rotation reset to initial state",
            "dealer_index": dealer_info["dealer_index"],
            "round_wind": dealer_info["round_wind"],
        }
    )


async def advance_dealer(request: web.Request) -> web.Response:
    data = await request.json()
    dealer_won = data.get("dealer_won", False)

    advance_dealer_rotation(dealer_won)
    dealer_info = get_current_dealer_info()

    return web.json_response(
        {
            "success": True,
            "message": f"Advanced to next {'hand' if dealer_won else 'dealer/round'}",
            "dealer_index": dealer_info["dealer_index"],
            "round_wind": dealer_info["round_wind"],
            "dealer_won": dealer_won,
        }
    )


async def get_dealer_info(request: web.Request) -> web.Response:
    dealer_info = get_current_dealer_info()
    return web.json_response(
        {"dealer_index": dealer_info["dealer_index"], "round_wind": dealer_info["round_wind"]}
    )


async def player_claims_pung(request: web.Request) -> web.Response:
    global current_game_state
    data = await request.json()
    confirm_claim = data.get("confirm_claim", False)

    response = {"success": False, "message": "Claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "PUNG"
    ):
        response["message"] = "No Pung claim was pending or tile info missing."
        return web.json_response(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return web.json_response(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_pung_claim(claiming_player_id, claimed_tile)
        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [t.unicode for t in player.hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
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
            "discarded_tile": current_game_state.current_discard.unicode
            if current_game_state.current_discard
            else None,
            "winner_found": current_game_state.winner_found,
        }

    return web.json_response(response)


async def player_claims_win(request: web.Request) -> web.Response:
    global current_game_state
    data = await request.json()
    confirm_claim = data.get("confirm_claim", False)

    response = {"success": False, "message": "Win claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "WIN"
    ):
        response["message"] = "No Win claim was pending or tile info missing."
        return web.json_response(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending win claim is not for the human player."
        return web.json_response(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_win_claim(claiming_player_id, claimed_tile)

        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [t.unicode for t in player.hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
                for meld in player.revealed_sets
            ]
            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Win!",
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "winner_found": current_game_state.winner_found,
                "winning_player_id": current_game_state.winning_player_id,
                "action": "win_claimed",
            }
        else:
            response["message"] = "Backend failed to process Win claim."
            response["winner_found"] = current_game_state.winner_found
    else:
        claim_type = current_game_state.claim_type_pending

        if claim_type == "SELF_DRAW_WIN":
            current_game_state.potential_claim_tile = None
            current_game_state.pending_claim_player_id = None
            current_game_state.claim_type_pending = None

            response = {
                "success": True,
                "message": "Self-draw win declined. You may now discard.",
                "action": "self_draw_win_declined",
                "winner_found": False,
                "next_player_id": current_game_state.current_player_index,
            }
        else:
            discarder_player_id = current_game_state.current_player_index

            current_game_state.potential_claim_tile = None
            current_game_state.pending_claim_player_id = None
            current_game_state.claim_type_pending = None

            current_game_state.current_player_index = (
                discarder_player_id + 1
            ) % len(current_game_state.players)
            current_game_state.turn_number += 1

            discarded_tile_serializable = None
            if current_game_state.current_discard:
                discarded_tile_serializable = current_game_state.current_discard.unicode

            response = {
                "success": True,
                "message": "Win claim declined. Game continues.",
                "action": "claim_declined",
                "next_player_id": current_game_state.players[
                    current_game_state.current_player_index
                ].player_id,
                "discarded_tile": discarded_tile_serializable,
                "winner_found": current_game_state.winner_found,
            }

    return web.json_response(response)


async def player_claims_kong(request: web.Request) -> web.Response:
    global current_game_state
    data = await request.json()
    confirm_claim = data.get("confirm_claim", False)

    response = {"success": False, "message": "Kong claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "KONG"
    ):
        response["message"] = "No Kong claim was pending or tile info missing."
        return web.json_response(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return web.json_response(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_kong_claim(claiming_player_id, claimed_tile)

        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [t.unicode for t in player.hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
                for meld in player.revealed_sets
            ]

            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Kong. Your turn to discard.",
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "winner_found": current_game_state.winner_found,
                "winning_player_id": current_game_state.winning_player_id
                if current_game_state.winner_found
                else None,
            }
        else:
            response["message"] = "Backend failed to process Kong claim."
    else:
        discarder_player_id = current_game_state.current_player_index
        current_game_state.potential_claim_tile = None
        current_game_state.pending_claim_player_id = None
        current_game_state.claim_type_pending = None
        current_game_state.current_player_index = (
            discarder_player_id + 1
        ) % len(current_game_state.players)

        response = {
            "success": True,
            "message": "Kong claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.current_player_index,
            "winner_found": current_game_state.winner_found,
            "winning_player_id": current_game_state.winning_player_id
            if current_game_state.winner_found
            else None,
        }

    return web.json_response(response)


async def player_declares_hidden_kong(request: web.Request) -> web.Response:
    global current_game_state
    from mahjong_engine.tile import TileFactory

    data = await request.json()
    tile_info_raw = data.get("tile_info", {})

    if isinstance(tile_info_raw, str):
        tile_obj = TileFactory.from_unicode(tile_info_raw)
        if not tile_obj:
            return web.json_response({"success": False, "error": "Invalid tile_info provided for Hidden Kong."})
        tile_info = {"suit": tile_obj.suit, "value": tile_obj.value}
    else:
        tile_info = tile_info_raw

    response = {"success": False, "error": "Failed to declare hidden kong by default."}

    if not current_game_state.players:
        response["error"] = "Game not initialized or no players found."
        return web.json_response(response)

    if current_game_state.current_player_index != 0:
        response["error"] = "Not your turn to declare hidden kong."
        return web.json_response(response)

    player_id = current_game_state.players[current_game_state.current_player_index].player_id
    if player_id != 0:
        response["error"] = "Not your turn (player ID mismatch)."
        return web.json_response(response)

    if not tile_info or "suit" not in tile_info or "value" not in tile_info:
        response["error"] = "Invalid tile_info provided for Hidden Kong."
        return web.json_response(response)

    result_dict = current_game_state.process_hidden_kong(player_id, tile_info)

    if result_dict.get("success"):
        player = current_game_state.players[player_id]
        hand_serializable = [t.unicode for t in player.hand]
        revealed_sets_serializable = [
            {
                "type": meld.meld_type.value,
                "tiles": [t.unicode for t in meld.raw_tiles],
                "revealed": meld.revealed,
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
            "winning_player_id": current_game_state.winning_player_id,
        }
    else:
        response["error"] = result_dict.get("error", "Unknown error declaring Hidden Kong.")

    return web.json_response(response)


async def draw_tile(request: web.Request) -> web.Response:
    global current_game_state

    player_id = current_game_state.players[current_game_state.current_player_index].player_id

    drawn_tile_obj = current_game_state.draw_tile_for_current_player()

    if drawn_tile_obj:
        drawn_tile_serializable = drawn_tile_obj.unicode

        current_player_hand = current_game_state.players[current_game_state.current_player_index].hand
        hand_serializable = [t.unicode for t in current_player_hand]

        if current_game_state.winner_found and current_game_state.winning_player_id == player_id:
            hand_serializable = [t.unicode for t in current_game_state.players[player_id].hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
                for meld in current_game_state.players[player_id].revealed_sets
            ]
            return web.json_response(
                {
                    "success": True,
                    "action": "win",
                    "winner_found": True,
                    "winning_player_id": player_id,
                    "hand": hand_serializable,
                    "revealed_sets": revealed_sets_serializable,
                    "drawn_tile": drawn_tile_serializable,
                    "remaining_tiles": len(current_game_state.wall),
                }
            )

        return web.json_response(
            {
                "success": True,
                "drawn_tile": drawn_tile_serializable,
                "hand": hand_serializable,
                "player_id": player_id,
                "winner_found": False,
                "remaining_tiles": len(current_game_state.wall),
                "human_can_claim": current_game_state.claim_type_pending
                if current_game_state.pending_claim_player_id == player_id
                else None,
                "claimable_tile": drawn_tile_serializable
                if current_game_state.claim_type_pending == "SELF_DRAW_WIN"
                else None,
            }
        )
    else:
        current_player_hand = current_game_state.players[current_game_state.current_player_index].hand
        hand_serializable = [t.unicode for t in current_player_hand]
        return web.json_response(
            {
                "success": True,
                "action": "wall_empty",
                "winner_found": False,
                "game_ended": True,
                "message": "Wall empty - game ends in a draw",
                "hand": hand_serializable,
                "player_id": player_id,
                "remaining_tiles": len(current_game_state.wall),
            }
        )


async def discard_tile(request: web.Request) -> web.Response:
    try:
        global current_game_state
        from mahjong_engine.tile import TileFactory

        data = await request.json()
        tile_raw = data.get("tile_to_discard", {})
        if isinstance(tile_raw, str):
            tile_obj = TileFactory.from_unicode(tile_raw)
            if not tile_obj:
                return web.json_response({"success": False, "error": "Invalid tile data for discard."})
            tile_to_discard_data = {"suit": tile_obj.suit, "value": tile_obj.value}
        else:
            tile_to_discard_data = tile_raw
        try:
            print("Discarding tile:", tile_to_discard_data)
        except UnicodeEncodeError:
            print("Discarding tile: [Unicode tile data]")

        discarding_player_id = current_game_state.players[current_game_state.current_player_index].player_id
        print("Current player ID:", discarding_player_id)

        if not isinstance(tile_to_discard_data, dict) or "suit" not in tile_to_discard_data or "value" not in tile_to_discard_data:
            return web.json_response({"success": False, "error": "Invalid tile data for discard."})

        success = current_game_state.discard_tile_for_current_player(tile_to_discard_data)

        if success:
            next_player_id = current_game_state.players[current_game_state.current_player_index].player_id

            discarding_player_object = None
            for p in current_game_state.players:
                if p.player_id == discarding_player_id:
                    discarding_player_object = p
                    break

            hand_serializable = []

            if discarding_player_object:
                hand_serializable = [t.unicode for t in discarding_player_object.hand]

            discarded_tile_info = None
            if current_game_state.current_discard:
                discarded_tile_info = current_game_state.current_discard.unicode

            response = {
                "success": True,
                "discarded_by_player_id": discarding_player_id,
                "updated_hand": hand_serializable,
                "next_player_id": next_player_id,
                "discarded_tile": discarded_tile_info,
                "winner_found": current_game_state.winner_found,
                "remaining_tiles": len(current_game_state.wall),
            }

            if (
                current_game_state.pending_claim_player_id == 0
                and current_game_state.potential_claim_tile
                and current_game_state.claim_type_pending
            ):
                response["human_can_claim"] = current_game_state.claim_type_pending
                response["claimable_tile"] = current_game_state.potential_claim_tile.unicode
            else:
                response["human_can_claim"] = None
            return web.json_response(response)
        else:
            current_player_obj = current_game_state.players[discarding_player_id]
            hand_serializable = [t.unicode for t in current_player_obj.hand]
            return web.json_response(
                {
                    "success": False,
                    "error": "Failed to discard tile (tile not in hand, or wrong hand size?)",
                    "hand": hand_serializable,
                    "player_id": discarding_player_id,
                    "winner_found": current_game_state.winner_found,
                }
            )
    except Exception as e:
        import traceback

        print(f"Error in discard_tile: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return web.json_response({"success": False, "error": f"Internal server error: {str(e)}"}, status=500)


async def request_ai_turn(request: web.Request) -> web.Response:
    global current_game_state
    if current_game_state.pending_claim_player_id is not None:
        return web.json_response(
            {
                "success": False,
                "error": "Human claim pending. AI turn cannot run yet.",
            }
        )

    current_player_id = current_game_state.players[current_game_state.current_player_index].player_id

    current_player_agent_type = type(current_game_state.players[current_game_state.current_player_index].agent)

    if current_player_agent_type == AIPlayerAgent:
        result = current_game_state.run_ai_turn()

        result["winner_found"] = current_game_state.winner_found
        result["remaining_tiles"] = len(current_game_state.wall)

        player0_hand_serializable = []
        if current_game_state.players:
            player0 = current_game_state.players[0]
            player0_hand_serializable = [tile.unicode for tile in player0.hand]
        result["player0_hand"] = player0_hand_serializable

        player0_revealed_sets_serializable = []
        if current_game_state.players:
            player0 = current_game_state.players[0]
            player0_revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
                for meld in player0.revealed_sets
            ]
        result["player0_revealed_sets"] = player0_revealed_sets_serializable
        try:
            print(f"AI {current_player_id} turn result:", result)
        except UnicodeEncodeError:
            print(f"AI {current_player_id} turn result: [Unicode result data]")
        return web.json_response(result)
    else:
        return web.json_response(
            {
                "success": False,
                "error": f"Player {current_player_id} is not an AI player.",
            }
        )


@web.middleware
async def security_headers(request: web.Request, handler):
    response = await handler(request)
    response.headers.setdefault("Cache-Control", "no-cache")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return response


app = web.Application(middlewares=[security_headers])

app.router.add_get("/", index)
app.router.add_get("/game", game)
app.router.add_post("/api/reset_game", reset_game)
app.router.add_post("/api/start_new_game", start_new_game)
app.router.add_post("/api/reset_dealer_rotation", reset_dealer_rotation)
app.router.add_post("/api/advance_dealer", advance_dealer)
app.router.add_get("/api/get_dealer_info", get_dealer_info)
app.router.add_post("/api/player_claims_pung", player_claims_pung)
app.router.add_post("/api/player_claims_win", player_claims_win)
app.router.add_post("/api/player_claims_kong", player_claims_kong)
app.router.add_post("/api/player_declares_hidden_kong", player_declares_hidden_kong)
app.router.add_post("/api/draw_tile", draw_tile)
app.router.add_post("/api/discard_tile", discard_tile)
app.router.add_post("/api/request_ai_turn", request_ai_turn)
app.router.add_static('/static/', path='./static', name='static')

cors = aiohttp_cors.setup(
    app,
    defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    },
)

for route in list(app.router.routes()):
    cors.add(route)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
