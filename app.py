import os
import json
import logging
import aiohttp_cors
from aiohttp import web, WSMsgType

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not installed. GitHub issue creation will be disabled.")

from mahjong_engine.bug_report import BugReport
from mahjong_engine.game_state import GameState
from mahjong_engine.player_agent import AIPlayerAgent
from mahjong_engine.room_manager import RoomManager
from mahjong_engine.ws_room_tracker import WebSocketRoomTracker
from mahjong_engine.chat_protocol import handle_chat_message, handle_chat_history, handle_chat_typing
from mahjong_engine.game_session import (
    GameSession,
    reset_dealer_rotation_state,
    advance_dealer_rotation,
    get_current_dealer_info,
)
from mahjong_engine.livekit_service import LiveKitService


BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static", "game")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WS_ENDPOINTS = {
    "dev": "ws://localhost:8080/ws",
    "uat": "wss://oracle-free-instance-20230330-1941.tail356fe.ts.net/ws",
    "prod": "wss://signal-server-eo-7uq.fly.dev/ws",
}

current_game_state = GameState()

# Session management for multi-game support
game_sessions = {}

# Room management for multiplayer lobbies
room_manager = RoomManager()

# WebSocket room-based peer tracking
ws_room_tracker = WebSocketRoomTracker()

# LiveKit video chat service
livekit_service = LiveKitService()

clients = {}


def _players_info():
    return current_game_state.get_players_public_info()


def _current_pid():
    return current_game_state.players[current_game_state.current_player_index].player_id


def _winning_hand_info():
    """Return winning player's hand and melds for verification display."""
    if not current_game_state.winner_found:
        return {}
    for p in current_game_state.players:
        if p.player_id == current_game_state.winning_player_id:
            return {
                "winning_hand": [t.unicode for t in p.hand],
                "winning_revealed_sets": [
                    {"type": m.meld_type.value, "tiles": [t.unicode for t in m.raw_tiles]}
                    for m in p.revealed_sets
                ],
                "faan": current_game_state.winning_faan,
                "faan_breakdown": current_game_state.winning_faan_breakdown,
            }
    return {}


async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def game(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(STATIC_DIR, "index.html"))


async def env_js_handler(request: web.Request) -> web.Response:
    env = os.getenv("APP_ENV", "prod").lower().strip()
    ws_url = WS_ENDPOINTS.get(env, WS_ENDPOINTS["prod"])

    js_code = (
        "window.APP_CONFIG = {\n"
        f"  env: '{env}',\n"
        f"  wsUrl: '{ws_url}'\n"
        "};"
    )
    return web.Response(text=js_code, content_type="application/javascript")


async def voice_handler(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(BASE_DIR, "voice.html"))


async def voice_command_handler(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(BASE_DIR, "voice_command.html"))


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info("Websocket from: %s", request.remote)
    logger.debug("Headers: %s", dict(request.headers))

    client_id = None
    room_id = None

    msg = await ws.receive()
    if msg.type == WSMsgType.TEXT:
        try:
            client_info = json.loads(msg.data)
            client_id = client_info["id"]
            room_id = client_info.get("room_id", "lobby")
        except Exception as e:
            logger.error("Invalid JSON message: %s", e)
            await ws.close()
            return ws
    else:
        await ws.close()
        return ws

    clients[client_id] = ws
    ws_room_tracker.register(client_id, room_id)

    # Notify only peers in the same room
    room_peers = ws_room_tracker.get_room_peers(client_id)
    for peer_id in room_peers:
        if peer_id in clients:
            await clients[peer_id].send_str(
                json.dumps({"type": "new-peer", "id": client_id, "room_id": room_id})
            )

    # Send peer list (only peers in the same room)
    await ws.send_str(
        json.dumps({"type": "peer-list", "peers": room_peers, "room_id": room_id})
    )

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get("type", "")
                to_id = data.get("to")

                if msg_type in ("chat:message", "chat:history", "chat:typing"):
                    room = room_manager.get_room(room_id)
                    if msg_type == "chat:message":
                        result = handle_chat_message(data, room)
                    elif msg_type == "chat:history":
                        result = handle_chat_history(data, room)
                    else:
                        result = handle_chat_typing(data, room)

                    result_json = json.dumps(result)
                    if result.get("success") and msg_type in ("chat:message", "chat:typing"):
                        # Broadcast to all peers in room (including sender)
                        await ws.send_str(result_json)
                        for peer_id in ws_room_tracker.get_room_peers(client_id):
                            if peer_id in clients:
                                await clients[peer_id].send_str(result_json)
                    else:
                        # Send response only to requester
                        await ws.send_str(result_json)
                elif to_id and to_id in clients:
                    await clients[to_id].send_str(msg.data)
                elif msg_type == "room-broadcast":
                    # Broadcast to all peers in the same room
                    for peer_id in ws_room_tracker.get_room_peers(client_id):
                        if peer_id in clients:
                            await clients[peer_id].send_str(msg.data)
    finally:
        ws_room_tracker.unregister(client_id)
        if client_id in clients:
            del clients[client_id]
            # Notify only room peers of disconnect
            for peer_id in ws_room_tracker.clients_in_room(room_id):
                if peer_id in clients:
                    await clients[peer_id].send_str(
                        json.dumps({"type": "peer-disconnect", "id": client_id, "room_id": room_id})
                    )

    return ws


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
        "players_info": _players_info(),
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
                "players_info": _players_info(),
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
            "players_info": _players_info(),
            "current_player_id": _current_pid(),
        }

    return web.json_response(response)


async def player_claims_chow(request: web.Request) -> web.Response:
    global current_game_state
    data = await request.json()
    confirm_claim = data.get("confirm_claim", False)

    response = {"success": False, "message": "Claim processing failed."}

    if (
        current_game_state.pending_claim_player_id is None
        or current_game_state.potential_claim_tile is None
        or current_game_state.claim_type_pending != "CHOW"
    ):
        response["message"] = "No Chow claim was pending or tile info missing."
        return web.json_response(response)

    claiming_player_id = current_game_state.pending_claim_player_id

    if claiming_player_id != 0:
        response["message"] = "Pending claim is not for the human player."
        return web.json_response(response)

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_chow_claim(claiming_player_id, claimed_tile)
        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [t.unicode for t in player.hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles]}
                for meld in player.revealed_sets
            ]
            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Chow. Your turn to discard.",
                "player_hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "current_player_id": current_game_state.current_player_index,
                "action": "discard_after_chow",
                "winner_found": current_game_state.winner_found,
                "players_info": _players_info(),
            }
        else:
            response["message"] = "Backend failed to process Chow claim."
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
            "message": "Chow claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.players[
                current_game_state.current_player_index
            ].player_id,
            "discarded_tile": current_game_state.current_discard.unicode
            if current_game_state.current_discard
            else None,
            "winner_found": current_game_state.winner_found,
            "players_info": _players_info(),
            "current_player_id": _current_pid(),
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
                "winning_hand": hand_serializable,
                "winning_revealed_sets": revealed_sets_serializable,
                "winner_found": current_game_state.winner_found,
                "winning_player_id": current_game_state.winning_player_id,
                "action": "win_claimed",
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
                "faan": current_game_state.winning_faan,
                "faan_breakdown": current_game_state.winning_faan_breakdown,
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
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
            "players_info": _players_info(),
            "current_player_id": _current_pid(),
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
            "players_info": _players_info(),
            "current_player_id": _current_pid(),
        }
    else:
        response["error"] = result_dict.get("error", "Unknown error declaring Hidden Kong.")

    return web.json_response(response)


async def player_declares_add_kong(request: web.Request) -> web.Response:
    global current_game_state
    from mahjong_engine.tile import TileFactory

    data = await request.json()
    tile_info_raw = data.get("tile_info", {})

    if isinstance(tile_info_raw, str):
        tile_obj = TileFactory.from_unicode(tile_info_raw)
        if not tile_obj:
            return web.json_response({"success": False, "error": "Invalid tile_info for add Kong."})
        tile_info = {"suit": tile_obj.suit, "value": tile_obj.value}
    else:
        tile_info = tile_info_raw

    if not current_game_state.players:
        return web.json_response({"success": False, "error": "Game not initialized."})

    if current_game_state.current_player_index != 0:
        return web.json_response({"success": False, "error": "Not your turn."})

    player_id = current_game_state.players[0].player_id

    result_dict = current_game_state.process_add_kong(player_id, tile_info)

    if result_dict.get("success"):
        player = current_game_state.players[player_id]
        hand_serializable = [t.unicode for t in player.hand]
        revealed_sets_serializable = [
            {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles], "revealed": meld.revealed}
            for meld in player.revealed_sets
        ]
        return web.json_response({
            "success": True,
            "message": result_dict.get("message"),
            "hand": hand_serializable,
            "revealed_sets": revealed_sets_serializable,
            "drawn_tile": result_dict.get("drawn_tile"),
            "winner_found": current_game_state.winner_found,
            "winning_player_id": current_game_state.winning_player_id,
            "players_info": _players_info(),
            "current_player_id": _current_pid(),
        })
    else:
        return web.json_response({"success": False, "error": result_dict.get("error")})


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
            resp = {
                "success": True,
                "action": "win",
                "winner_found": True,
                "winning_player_id": player_id,
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "winning_hand": hand_serializable,
                "winning_revealed_sets": revealed_sets_serializable,
                "drawn_tile": drawn_tile_serializable,
                "remaining_tiles": len(current_game_state.wall),
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
                "faan": current_game_state.winning_faan,
                "faan_breakdown": current_game_state.winning_faan_breakdown,
            }
            return web.json_response(resp)

        # Check for add-kong candidates (tile in hand matching exposed pung)
        from mahjong_engine.hand_validator import can_add_to_exposed_kong
        player = current_game_state.players[player_id]
        add_kong_candidates = can_add_to_exposed_kong(player.hand, player.revealed_sets)
        add_kong_tiles = [t.unicode for t in add_kong_candidates]

        revealed_sets_serializable = [
            {"type": meld.meld_type.value, "tiles": [t.unicode for t in meld.raw_tiles], "revealed": meld.revealed}
            for meld in player.revealed_sets
        ]

        return web.json_response(
            {
                "success": True,
                "drawn_tile": drawn_tile_serializable,
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "player_id": player_id,
                "winner_found": False,
                "remaining_tiles": len(current_game_state.wall),
                "human_can_claim": current_game_state.claim_type_pending
                if current_game_state.pending_claim_player_id == player_id
                else None,
                "claimable_tile": drawn_tile_serializable
                if current_game_state.claim_type_pending == "SELF_DRAW_WIN"
                else None,
                "add_kong_tiles": add_kong_tiles,
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
                "players_info": _players_info(),
                "current_player_id": _current_pid(),
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
    try:
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
            result["players_info"] = _players_info()
            result["current_player_id"] = _current_pid()
            if current_game_state.winner_found:
                result.update(_winning_hand_info())
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
    except Exception as e:
        import traceback
        print(f"Error in request_ai_turn: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return web.json_response(
            {"success": False, "error": f"AI turn error: {str(e)}"},
            status=200  # Return 200 so frontend can parse JSON
        )


async def create_room(request: web.Request) -> web.Response:
    """Create a new game room."""
    room = room_manager.create_room()
    return web.json_response({"success": True, "room": room.to_dict()})


async def get_room(request: web.Request) -> web.Response:
    """Get room details by ID."""
    room_id = request.match_info["room_id"]
    room = room_manager.get_room(room_id)
    if not room:
        return web.json_response({"success": False, "message": "Room not found."}, status=404)
    return web.json_response({"success": True, "room": room.to_dict()})


async def list_rooms(request: web.Request) -> web.Response:
    """List all active rooms."""
    rooms = room_manager.list_rooms()
    rooms_list = [r.to_dict() for r in rooms.values()]
    return web.json_response({"success": True, "rooms": rooms_list, "count": len(rooms_list)})


async def join_room(request: web.Request) -> web.Response:
    """Join a game room."""
    room_id = request.match_info["room_id"]
    data = await request.json()
    player_id = data.get("player_id")

    if not player_id:
        return web.json_response({"success": False, "message": "player_id required."})

    room = room_manager.get_room(room_id)
    if not room:
        return web.json_response({"success": False, "message": "Room not found."}, status=404)

    if room.add_player(player_id):
        return web.json_response({"success": True, "message": f"Player {player_id} joined room.", "room": room.to_dict()})
    return web.json_response({"success": False, "message": "Cannot join room (full or already joined)."})


async def leave_room(request: web.Request) -> web.Response:
    """Leave a game room."""
    room_id = request.match_info["room_id"]
    data = await request.json()
    player_id = data.get("player_id")

    if not player_id:
        return web.json_response({"success": False, "message": "player_id required."})

    room = room_manager.get_room(room_id)
    if not room:
        return web.json_response({"success": False, "message": "Room not found."}, status=404)

    if room.remove_player(player_id):
        return web.json_response({"success": True, "message": f"Player {player_id} left room.", "room": room.to_dict()})
    return web.json_response({"success": False, "message": "Player not in room."})


async def create_session(request: web.Request) -> web.Response:
    """Create a new game session."""
    session = GameSession()
    game_sessions[session.session_id] = session
    return web.json_response({
        "success": True,
        "session_id": session.session_id,
        "created_at": session.created_at,
    })


async def get_session(request: web.Request) -> web.Response:
    """Get session state by ID."""
    session_id = request.match_info["session_id"]
    session = game_sessions.get(session_id)
    if not session:
        return web.json_response({"success": False, "message": "Session not found."}, status=404)
    session.update_activity()
    data = session.to_dict()
    data["success"] = True
    data["player_count"] = len(session.game_state.players)
    return web.json_response(data)


async def list_sessions(request: web.Request) -> web.Response:
    """List all active sessions."""
    sessions_list = [
        {"session_id": s.session_id, "created_at": s.created_at, "last_activity": s.last_activity}
        for s in game_sessions.values()
    ]
    return web.json_response({"success": True, "sessions": sessions_list, "count": len(sessions_list)})


async def livekit_token(request: web.Request) -> web.Response:
    """Generate a LiveKit token for a participant to join a video room."""
    data = await request.json()
    room_id = data.get("room_id")
    participant_name = data.get("participant_name")

    if not room_id or not participant_name:
        return web.json_response(
            {"success": False, "error": "room_id and participant_name are required."}, status=400
        )

    info = livekit_service.get_connection_info(room_id, participant_name)
    return web.json_response({"success": True, **info})


async def livekit_config(request: web.Request) -> web.Response:
    """Return LiveKit connection URL (for frontend to know where to connect)."""
    return web.json_response({
        "success": True,
        "url": livekit_service.livekit_url,
    })


async def game_history(request: web.Request) -> web.Response:
    global current_game_state
    history = current_game_state.get_history()
    return web.json_response({"success": True, "history": history, "count": len(history)})


async def action_log(request: web.Request) -> web.Response:
    """Return decoded action log for the current game."""
    global current_game_state
    player_filter = request.rel_url.query.get("player_id")
    if player_filter is not None:
        try:
            player_filter = int(player_filter)
        except ValueError:
            return web.json_response(
                {"success": False, "error": "player_id must be an integer."})

    decoded = current_game_state.action_log.decode(player_filter=player_filter)
    return web.json_response(
        {"success": True, "actions": decoded, "count": len(decoded)},
        content_type="application/json",
    )


async def report_bug(request: web.Request) -> web.Response:
    """Create a bug report capturing action log and game state.

    Request body: {"description": "What went wrong..."}

    Environment variables:
        GITHUB_TOKEN: Personal access token for automatic issue creation (optional)
        GITHUB_REPO: Repository in format "owner/repo" (default: "yksi7417/signal_server")
    """
    global current_game_state

    data = await request.json()
    description = data.get("description", "").strip()

    if not description:
        return web.json_response(
            {"success": False, "error": "description is required."})

    snapshot = current_game_state.get_state_snapshot()
    report = BugReport(
        description=description,
        action_log=current_game_state.action_log,
        game_state_snapshot=snapshot,
    )

    report_dir = report.save()
    markdown = report.to_github_markdown()

    # Try to automatically create GitHub issue
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO", "yksi7417/signal_server")
    issue_url = None
    issue_number = None
    auto_created = False

    if GITHUB_AVAILABLE and github_token:
        try:
            # Create GitHub issue automatically
            gh = Github(github_token)
            repo = gh.get_repo(github_repo)

            # Upload parquet file as a Gist
            gist_url = None
            parquet_path = os.path.join(report_dir, "actions.parquet")

            # Check if parquet file exists before trying to upload
            if not os.path.exists(parquet_path):
                logger.warning(f"Parquet file not found at {parquet_path}, skipping gist creation")
            elif report.action_log.count == 0:
                logger.warning(f"Action log is empty (0 actions), skipping gist creation")
            else:
                try:
                    logger.info(f"Reading parquet file from {parquet_path} ({os.path.getsize(parquet_path)} bytes)")
                    with open(parquet_path, "rb") as f:
                        parquet_content = f.read()

                    # Convert to base64 for text-based gist storage
                    import base64
                    parquet_b64 = base64.b64encode(parquet_content).decode('ascii')
                    logger.info(f"Encoded parquet to base64 ({len(parquet_b64)} chars)")

                    # Create gist with both the parquet (as base64) and a README
                    gist_files = {
                        "actions.parquet.b64": {
                            "content": parquet_b64
                        },
                        "README.md": {
                            "content": f"# Bug Report Action Log\n\n"
                                       f"Bug ID: `{report.bug_id}`\n\n"
                                       f"This gist contains the action log for bug report {report.bug_id}.\n\n"
                                       f"## Files\n"
                                       f"- `actions.parquet.b64`: Base64-encoded parquet file with {report.action_log.count} actions\n\n"
                                       f"## How to Use\n"
                                       f"Download `actions.parquet.b64` and decode:\n"
                                       f"```bash\n"
                                       f"# On Linux/Mac:\n"
                                       f"base64 -d actions.parquet.b64 > actions.parquet\n\n"
                                       f"# On Windows PowerShell:\n"
                                       f"[System.Convert]::FromBase64String((Get-Content actions.parquet.b64)) | Set-Content actions.parquet -Encoding Byte\n\n"
                                       f"# Then view the actions:\n"
                                       f"python -m mahjong_engine.action_log actions.parquet\n"
                                       f"```"
                        }
                    }

                    logger.info(f"Creating private gist for bug {report.bug_id}")
                    user = gh.get_user()
                    gist = user.create_gist(
                        public=False,
                        files=gist_files,
                        description=f"Action log for bug {report.bug_id}"
                    )
                    gist_url = gist.html_url
                    logger.info(f"Successfully created gist with action log: {gist_url}")

                    # Append gist link to markdown
                    markdown += f"\n\n---\n\n### 📎 Action Log File\n\n"
                    markdown += f"The complete action log ({report.action_log.count} actions) is available as a parquet file:\n"
                    markdown += f"**[Download from Gist]({gist_url})**\n\n"
                    markdown += f"Use `python -m mahjong_engine.action_log <file.parquet>` to view the decoded actions."

                except FileNotFoundError as e:
                    logger.error(f"Parquet file not found: {e}")
                except PermissionError as e:
                    logger.error(f"Permission denied reading parquet file: {e}")
                except Exception as gist_error:
                    logger.warning(f"Gist creation failed ({gist_error}), embedding parquet in issue body")
                    # Fallback: embed base64 parquet directly in the issue body
                    try:
                        markdown += f"\n\n---\n\n### Action Log File\n\n"
                        markdown += f"Action log ({report.action_log.count} actions) as base64-encoded parquet.\n"
                        markdown += f"Save the block below to `actions.parquet.b64` then run: "
                        markdown += f"`base64 -d actions.parquet.b64 > actions.parquet`\n\n"
                        markdown += f"<details>\n<summary>Base64 parquet data</summary>\n\n"
                        markdown += f"```\n{parquet_b64}\n```\n\n</details>"
                    except Exception:
                        logger.error("Failed to embed parquet fallback", exc_info=True)

            # Create issue with bug report
            issue = repo.create_issue(
                title=f"Bug Report: {description[:80]}{'...' if len(description) > 80 else ''}",
                body=markdown,
                labels=["bug", "auto-reported"]
            )

            issue_url = issue.html_url
            issue_number = issue.number
            auto_created = True

            logger.info(f"Auto-created GitHub issue #{issue_number}: {issue_url}")
        except Exception as e:
            logger.error(f"Failed to auto-create GitHub issue: {e}")
            # Fall back to manual URL
            issue_url = f"https://github.com/{github_repo}/issues/new"
    else:
        # No token or PyGithub not available - provide manual URL
        issue_url = f"https://github.com/{github_repo}/issues/new"

    response = {
        "success": True,
        "bug_id": report.bug_id,
        "report_dir": report_dir,
        "markdown": markdown,
        "issue_url": issue_url,
        "auto_created": auto_created,
    }

    if issue_number is not None:
        response["issue_number"] = issue_number

    # Include gist_url if it was created
    if 'gist_url' in locals() and gist_url:
        response["gist_url"] = gist_url

    return web.json_response(response)


@web.middleware
async def security_headers(request: web.Request, handler):
    response = await handler(request)
    response.headers.setdefault("Cache-Control", "no-cache")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")
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
app.router.add_post("/api/player_claims_chow", player_claims_chow)
app.router.add_post("/api/player_claims_win", player_claims_win)
app.router.add_post("/api/player_claims_kong", player_claims_kong)
app.router.add_post("/api/player_declares_hidden_kong", player_declares_hidden_kong)
app.router.add_post("/api/player_declares_add_kong", player_declares_add_kong)
app.router.add_post("/api/draw_tile", draw_tile)
app.router.add_post("/api/discard_tile", discard_tile)
app.router.add_post("/api/request_ai_turn", request_ai_turn)
app.router.add_get("/api/game_history", game_history)
app.router.add_get("/api/action_log", action_log)
app.router.add_post("/api/report_bug", report_bug)
app.router.add_post("/api/rooms/create", create_room)
app.router.add_get("/api/rooms", list_rooms)
app.router.add_get("/api/rooms/{room_id}", get_room)
app.router.add_post("/api/rooms/{room_id}/join", join_room)
app.router.add_post("/api/rooms/{room_id}/leave", leave_room)
app.router.add_post("/api/sessions/create", create_session)
app.router.add_get("/api/sessions", list_sessions)
app.router.add_get("/api/sessions/{session_id}", get_session)
app.router.add_post("/api/livekit/token", livekit_token)
app.router.add_get("/api/livekit/config", livekit_config)
app.router.add_get("/voice.html", voice_handler)
app.router.add_get("/voice_command.html", voice_command_handler)
app.router.add_get("/ws", websocket_handler)
app.router.add_get("/env.js", env_js_handler)
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
