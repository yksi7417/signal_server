import random
import eel
from mahjong_engine.game_state import GameState
from mahjong_engine.player_agent import AIPlayerAgent # Added import
# from mahjong_engine.constants import SUIT_DOTS, WIND_EAST # Example constants (optional for now)

# 1. point Eel at your web/ folder
eel.init('static/game')
current_game_state = GameState()


# 2. simple game‐state stored in Python
# TILES = ["🀇", "🀈", "🀉", "🀊", "🀋", "🀌"] # Commented out
# history = [] # Commented out


@eel.expose
def draw_tile():
    print("Old draw_tile function called. This functionality will be replaced.")
    # Consider what JS expects: perhaps an empty string or a specific format
    return "" 

@eel.expose
def reset_game():
    print("Old reset_game function called. This functionality will be replaced.")
    global current_game_state
    current_game_state = GameState() # Re-initialize our new game state for now
    if eel: # Check if eel is available (it should be)
         eel.update_history([]) # Send empty history as main.js expects it
    return True # main.js expects a return

@eel.expose
def start_new_game():
    global current_game_state
    current_game_state = GameState() # This will call __init__ and set up a new game
    
    # Prepare data for the client (Player 0's perspective)
    player0_hand_serializable = []
    if current_game_state.players: # Check if players exist
        player0 = current_game_state.players[0]
        player0_hand_serializable = [{"suit": tile.suit, "value": tile.value} for tile in player0.hand]
    
    game_info = {
        "player_hand": player0_hand_serializable,
        "game_wind": current_game_state.game_wind,
        "current_player_id": current_game_state.players[current_game_state.current_player_index].player_id,
        "winner_found": False # Added
    }
    # print(f"Starting new game. Player 0 hand: {player0_hand_serializable}") # For debugging
    return game_info

@eel.expose
def eel_player_claims_pung(confirm_claim): # confirm_claim is boolean
    global current_game_state
    response = {"success": False, "message": "Claim processing failed."}

    if current_game_state.pending_claim_player_id is None or \
       current_game_state.potential_claim_tile is None or \
       current_game_state.claim_type_pending != "PUNG":
        response["message"] = "No Pung claim was pending or tile info missing."
        return response

    claiming_player_id = current_game_state.pending_claim_player_id
    # For now, we assume player 0 is the only human and only one who can be pending
    if claiming_player_id != 0: # Or check if player is HumanAgent
         response["message"] = "Pending claim is not for the human player."
         return response

    if confirm_claim:
        claimed_tile = current_game_state.potential_claim_tile
        success = current_game_state.process_pung_claim(claiming_player_id, claimed_tile)
        if success:
            player = current_game_state.players[claiming_player_id]
            hand_serializable = [{"suit": t.suit, "value": t.value} for t in player.hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [{"suit": t.suit, "value": t.value} for t in meld.raw_tiles]}
                for meld in player.revealed_sets
            ]
            response = {
                "success": True,
                "message": f"Player {claiming_player_id} claimed Pung. Your turn to discard.",
                "player_hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "current_player_id": current_game_state.current_player_index,
                "action": "discard_after_pung", # Signal to UI
                "winner_found": current_game_state.winner_found # Added (likely False here)
            }
        else:
            response["message"] = "Backend failed to process Pung claim."
            response["winner_found"] = current_game_state.winner_found
    else: # Player declined the Pung
        # The current_player_index in GameState is still the player who discarded.
        # We need to advance the turn from that player.
        discarder_player_id = current_game_state.current_player_index
        
        # Reset claim state in GameState
        current_game_state.potential_claim_tile = None
        current_game_state.pending_claim_player_id = None
        current_game_state.claim_type_pending = None
        
        # Advance turn
        current_game_state.current_player_index = (discarder_player_id + 1) % len(current_game_state.players)
        current_game_state.turn_number += 1
        
        response = {
            "success": True, # Claim declined successfully
            "message": "Pung claim declined. Game continues.",
            "action": "claim_declined",
            "next_player_id": current_game_state.players[current_game_state.current_player_index].player_id,
            "last_discarded_tile": {"suit": current_game_state.current_discard.suit, "value": current_game_state.current_discard.value} if current_game_state.current_discard else None,
            "winner_found": current_game_state.winner_found # Added (likely False here)
        }

    return response

@eel.expose
def eel_draw_tile():
    global current_game_state
    # player_id is the one whose turn it is *before* drawing.
    player_id = current_game_state.players[current_game_state.current_player_index].player_id
    
    drawn_tile_obj = current_game_state.draw_tile_for_current_player()
    
    if drawn_tile_obj:
        drawn_tile_serializable = {"suit": drawn_tile_obj.suit, "value": drawn_tile_obj.value}
        # The hand returned is of the current player who just drew
        current_player_hand = current_game_state.players[current_game_state.current_player_index].hand
        hand_serializable = [{"suit": t.suit, "value": t.value} for t in current_player_hand]
        
        # Check for win after draw
        if current_game_state.winner_found and current_game_state.winning_player_id == player_id:
            # Player 0 (human) just drew and won
            # Hand already includes drawn_tile_obj due to how draw_tile_for_current_player works
            hand_serializable = [{"suit": t.suit, "value": t.value} for t in current_game_state.players[player_id].hand]
            revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [{"suit": t.suit, "value": t.value} for t in meld.raw_tiles]}
                for meld in current_game_state.players[player_id].revealed_sets
            ]
            return {
                "success": True, # Draw was successful, and it resulted in a win
                "action": "win",
                "winner_found": True,
                "winning_player_id": player_id,
                "hand": hand_serializable,
                "revealed_sets": revealed_sets_serializable,
                "drawn_tile": drawn_tile_serializable 
            }
        
        # If not a win, but draw was successful
        return {
            "success": True,
            "drawn_tile": drawn_tile_serializable,
            "hand": hand_serializable, # Hand after drawing
            "player_id": player_id,
            "winner_found": False # Explicitly false if no win on this draw
        }
    else:
        # If draw failed, return current player's hand for client to potentially re-sync
        current_player_hand = current_game_state.players[current_game_state.current_player_index].hand
        hand_serializable = [{"suit": t.suit, "value": t.value} for t in current_player_hand]
        return {
            "success": False, 
            "error": "Failed to draw tile (wall empty or hand full?).",
            "hand": hand_serializable,
            "player_id": player_id,
            "winner_found": current_game_state.winner_found # Could be true if another player won previously
        }

@eel.expose
def eel_discard_tile(tile_to_discard_data): # tile_to_discard_data is {'suit': 'Dots', 'value': '5'}
    global current_game_state
    # Player ID of the player whose turn it is to discard
    discarding_player_id = current_game_state.players[current_game_state.current_player_index].player_id

    if not isinstance(tile_to_discard_data, dict) or 'suit' not in tile_to_discard_data or 'value' not in tile_to_discard_data:
        return {"success": False, "error": "Invalid tile data for discard."}

    success = current_game_state.discard_tile_for_current_player(tile_to_discard_data)
    
    if success:
        # After successful discard, current_player_index has moved to the next player.
        next_player_id = current_game_state.players[current_game_state.current_player_index].player_id
        
        # The hand of the player who just discarded (use discarding_player_id)
        discarding_player_object = None
        for p in current_game_state.players:
            if p.player_id == discarding_player_id:
                discarding_player_object = p
                break
        
        hand_serializable = []
        if discarding_player_object:
             hand_serializable = [{"suit": t.suit, "value": t.value} for t in discarding_player_object.hand]

        response = { # Changed to response variable
            "success": True,
            "discarded_by_player_id": discarding_player_id,
            "updated_hand": hand_serializable, # Their hand after discard
            "next_player_id": next_player_id,
            "last_discarded_tile": {"suit": current_game_state.current_discard.suit, "value": current_game_state.current_discard.value},
            "winner_found": current_game_state.winner_found # Pass current win status
        }

        # CHECK FOR PENDING HUMAN CLAIM AFTER DISCARD
        if current_game_state.pending_claim_player_id == 0 and \
           current_game_state.potential_claim_tile and \
           current_game_state.claim_type_pending == "PUNG":
            
            response["human_can_claim_pung"] = True
            response["claimable_tile"] = {
                "suit": current_game_state.potential_claim_tile.suit,
                "value": current_game_state.potential_claim_tile.value
            }
        else:
            response["human_can_claim_pung"] = False
        
        return response # Return the modified response
    else:
        # Hand state might be inconsistent if tile not found, or wrong number of tiles.
        current_player_obj = current_game_state.players[discarding_player_id]
        hand_serializable = [{"suit": t.suit, "value": t.value} for t in current_player_obj.hand]
        return {
            "success": False, 
            "error": "Failed to discard tile (tile not in hand, or wrong hand size?).",
            "hand": hand_serializable, # Return current hand for resync
            "player_id": discarding_player_id,
            "winner_found": current_game_state.winner_found # Pass current win status
        }

if __name__ == '__main__':
    # 3. start a Chromium window at web/index.html
    eel.start('index.html', size=(400, 500))


@eel.expose
def eel_request_ai_turn():
    global current_game_state
    
    if current_game_state.pending_claim_player_id is not None:
        # This shouldn't be called if a human claim is actively pending resolution by the UI
        return {"success": False, "error": "Human claim pending. AI turn cannot run yet."}

    current_player_id = current_game_state.players[current_game_state.current_player_index].player_id
    current_player_agent_type = type(current_game_state.players[current_game_state.current_player_index].agent)
    
    # print(f"eel_request_ai_turn: Current player {current_player_id} is {current_player_agent_type}")

    if current_player_agent_type == AIPlayerAgent:
        result = current_game_state.run_ai_turn() # This handles draw, discard, and post-discard claim checks
        
        # The result from run_ai_turn already contains:
        # success, ai_player_id, discarded_tile, next_player_id, human_can_claim_pung, claimable_tile
        # We might want to add the current hand of player 0 if it's their turn next or if they can claim
        
        player0_hand_serializable = []
        if current_game_state.players:
             player0 = current_game_state.players[0]
             player0_hand_serializable = [{"suit": tile.suit, "value": tile.value} for tile in player0.hand]
        
        result["player0_hand"] = player0_hand_serializable # Add player 0's hand to the response

        # Also send revealed sets for player 0
        player0_revealed_sets_serializable = []
        if current_game_state.players:
            player0 = current_game_state.players[0]
            player0_revealed_sets_serializable = [
                {"type": meld.meld_type.value, "tiles": [{"suit": t.suit, "value": t.value} for t in meld.raw_tiles]}
                for meld in player0.revealed_sets
            ]
        result["player0_revealed_sets"] = player0_revealed_sets_serializable
        
        return result
    else:
        # print(f"eel_request_ai_turn: Current player {current_player_id} is Human. No AI turn to run.")
        # It's human's turn, client should already know or enable human actions
        player0_hand_serializable = []
        if current_game_state.players:
             player0 = current_game_state.players[0]
             player0_hand_serializable = [{"suit": tile.suit, "value": tile.value} for tile in player0.hand]
        
        return {
            "success": False, 
            "error": "Not AI's turn.",
            "next_player_id": current_player_id, # It's still this player's turn (human)
            "player0_hand": player0_hand_serializable, # Send current hand for player 0
            "human_can_claim_pung": (current_game_state.pending_claim_player_id == 0 and current_game_state.claim_type_pending == "PUNG"), # Re-send claim status
            "claimable_tile": {"suit": current_game_state.potential_claim_tile.suit, "value": current_game_state.potential_claim_tile.value} if current_game_state.potential_claim_tile and current_game_state.pending_claim_player_id == 0 else None,
            "player0_revealed_sets": [
                {"type": meld.meld_type.value, "tiles": [{"suit": t.suit, "value": t.value} for t in meld.raw_tiles]}
                for meld in current_game_state.players[0].revealed_sets
            ] if current_game_state.players else []
        }
