import random
from .player import Player
from .tile import Tile
from .constants import TILE_CATEGORIES_FOR_GENERATION, NUM_COPIES_PER_TILE, NUM_PLAYERS, INIT_HAND_SIZE, WIND_EAST
from .player_agent import HumanPlayerAgent, AIPlayerAgent
from .hand_validator import can_form_pung_with_discard # Added import
from .melds import Pung # Added import

class GameState:
    def _create_full_tile_set(self):
        tiles = []
        for suit, values in TILE_CATEGORIES_FOR_GENERATION:
            for value in values:
                tiles.extend([Tile(suit, value)] * NUM_COPIES_PER_TILE)
        # print(f"Generated {len(tiles)} tiles.") # For debugging
        return tiles

    def __init__(self, num_players=NUM_PLAYERS): # Use constant
        self.players = []
        for i in range(num_players): 
            if i == 0: # Player 0 is Human
                agent = HumanPlayerAgent(player_id=i)
            else: # Other players are AI
                agent = AIPlayerAgent(player_id=i)
            self.players.append(Player(player_id=i, agent=agent))
            
        self.wall = self._create_full_tile_set()
        random.shuffle(self.wall)
        
        self.deal_tiles()

        self.current_player_index = 0 # East player starts
        self.game_wind = WIND_EAST # Default game wind
        self.current_discard = None
        self.turn_number = 0
        
        self.pending_claim_player_id = None # Player who might claim
        self.potential_claim_tile = None # The tile that can be claimed
        self.claim_type_pending = None # E.g., "PUNG"
        # print(f"Initial wall size: {len(self.wall)}") # For debugging
        # for p in self.players: # For debugging
        #    print(f"Player {p.player_id} hand size: {len(p.hand)}")

    def deal_tiles(self):
        for player in self.players:
            player.hand = [] # Clear previous hand
            for _ in range(INIT_HAND_SIZE):
                if self.wall: # Check if wall is not empty
                    player.hand.append(self.wall.pop(0)) # Deal from the 'front' of the wall
                else:
                    # This case should ideally not happen in a standard game start
                    print("Warning: Wall is empty during initial deal!") 
                    break 

    def __repr__(self):
        return f"GameState(players={len(self.players)}, wall_size={len(self.wall)}, turn={self.turn_number})"

    def draw_tile_for_current_player(self):
        if not self.wall:
            print("Wall is empty. Cannot draw.")
            return None # Or raise an exception

        player = self.players[self.current_player_index]
        
        # Typically, a player should have 13 tiles before drawing, unless it's for a Kong replacement.
        # For a basic turn, they draw to get 14, then discard to 13.
        # Let's assume hand size is 13 for now before drawing.
        if len(player.hand) >= INIT_HAND_SIZE + 1: # INIT_HAND_SIZE is 13
             print(f"Player {player.player_id} already has {len(player.hand)} tiles. Cannot draw again before discarding.")
             return None


        drawn_tile = self.wall.pop(0) # Take from the "front" of the wall
        player.hand.append(drawn_tile)
        # print(f"Player {player.player_id} drew {drawn_tile}. Hand size: {len(player.hand)}")
        return drawn_tile

    def discard_tile_for_current_player(self, tile_to_discard_repr): # tile_to_discard_repr could be {'suit': 'Dots', 'value': '5'}
        player = self.players[self.current_player_index]

        # Player should have 14 tiles before discarding in a normal turn.
        if len(player.hand) != INIT_HAND_SIZE + 1:
            print(f"Player {player.player_id} has {len(player.hand)} tiles. Should have {INIT_HAND_SIZE + 1} before discarding.")
            return False

        tile_object_to_discard = None
        # Find the tile in hand. For simplicity, we assume tile_to_discard_repr is sufficient to identify it.
        # A more robust way would be to pass an index or a unique tile ID if tiles had them.
        # For now, let's find the first match.
        found_tile = False
        for tile_in_hand in player.hand:
            if tile_in_hand.suit == tile_to_discard_repr['suit'] and tile_in_hand.value == tile_to_discard_repr['value']:
                tile_object_to_discard = tile_in_hand
                player.hand.remove(tile_object_to_discard)
                found_tile = True
                break
        
        if not found_tile:
            print(f"Tile {tile_to_discard_repr} not found in player {player.player_id}'s hand.")
            # It's important to add the tile back if it was removed optimistically or handle state carefully.
            # In this code, remove only happens if found, so this is fine.
            return False

        self.current_discard = tile_object_to_discard # Track the last discarded tile
        player.discards.append(tile_object_to_discard) # Keep a history of player's discards
        
        # print(f"Player {player.player_id} discarded {tile_object_to_discard}. Hand size: {len(player.hand)}")

        # --- START NEW CLAIM CHECK LOGIC ---
        self.potential_claim_tile = self.current_discard
        self.pending_claim_player_id = None # Reset before checking
        self.claim_type_pending = None

        # Check other players for Pung claim
        # Iterate starting from the player after the current one, wrapping around.
        # This ensures a more standard priority if multiple players can claim (though only Pung for now).
        start_check_idx = (self.current_player_index + 1) % len(self.players)
        for i in range(len(self.players) -1): # Check all other players
            check_player_idx = (start_check_idx + i) % len(self.players)
            if check_player_idx == self.current_player_index: # Should not happen with this loop structure
                continue 
            
            other_player = self.players[check_player_idx]
            if can_form_pung_with_discard(other_player.hand, self.potential_claim_tile):
                # For now, first player who can Pung gets priority (simplification)
                # More complex logic would handle multiple claims (e.g., win > Pung/Kong > Chow)
                
                # Ask agent if they want to claim
                if isinstance(other_player.agent, HumanPlayerAgent):
                    self.pending_claim_player_id = other_player.player_id
                    self.claim_type_pending = "PUNG" # Store MeldType.PUNG or a string
                    print(f"Player {other_player.player_id} (Human) can Pung {self.potential_claim_tile}. Waiting for UI.")
                    # This state will be picked up by app.py to notify client.
                    # The turn does NOT advance yet if a human claim is pending.
                    return True # Discard was successful, claim pending

                elif isinstance(other_player.agent, AIPlayerAgent):
                    # AI makes its decision immediately
                    # claim_decision = other_player.agent.decide_claim(self, self.potential_claim_tile, ["PUNG"]) 
                    # For this step, AIPlayerAgent.decide_claim always returns None, so AI won't claim.
                    # If AI could claim, we'd call process_pung_claim here and it would return True.
                    # If AI claims, the turn advances to them, and they discard.
                    # For now, AI does nothing. If an AI *could* claim, it would do so here.
                    # If AI claims, it should be processed immediately.
                    # For this subtask, AI will not claim.
                    pass # AI does nothing for now regarding Pung.
        
        # --- END NEW CLAIM CHECK LOGIC ---

        # If no claim is pending (e.g. no one could Pung, or AI declined)
        if self.pending_claim_player_id is None:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.turn_number += 1
            # print(f"Turn {self.turn_number}. Next player is {self.players[self.current_player_index].player_id}")
        
        return True # Discard was successful

    def process_pung_claim(self, claiming_player_id, claimed_tile):
        """
        Processes a Pung claim for the specified player with the given tile.
        Assumes validation (can_form_pung_with_discard) and decision were already made.
        """
        if claimed_tile is None or claiming_player_id is None:
            print("Error: Claimed tile or player ID is None.")
            return False

        claiming_player = None
        discarding_player_original_index = self.current_player_index # Player who discarded the tile

        for p in self.players:
            if p.player_id == claiming_player_id:
                claiming_player = p
                break
        
        if not claiming_player:
            print(f"Error: Claiming player {claiming_player_id} not found.")
            return False

        # Remove 2 matching tiles from player's hand
        removed_count = 0
        temp_hand = list(claiming_player.hand) # Iterate over a copy
        for tile_in_hand in temp_hand:
            # Need to compare Tile objects; ensure claimed_tile is a Tile object
            # self.potential_claim_tile should be a Tile object
            if tile_in_hand == claimed_tile and removed_count < 2:
                claiming_player.hand.remove(tile_in_hand)
                removed_count += 1
        
        if removed_count != 2:
            # This should not happen if can_form_pung_with_discard was true
            print(f"Error: Could not remove 2 matching tiles for Pung from player {claiming_player_id}'s hand. Found {removed_count}.")
            # Attempt to restore hand if possible (complex, for now just error out)
            # This indicates a state inconsistency or bug in can_form_pung_with_discard or hand state.
            return False

        # Add the Pung to revealed_sets
        new_pung = Pung(tile=claimed_tile, revealed=True, claimed_from=discarding_player_original_index)
        claiming_player.add_revealed_set(new_pung)

        print(f"Player {claiming_player_id} formed Pung: {new_pung} from player {discarding_player_original_index}'s discard.")

        # Update game state
        self.current_player_index = claiming_player_id # Turn goes to the claiming player
        
        self.current_discard = None # The claimed tile is no longer the "current discard" in the same way
        self.potential_claim_tile = None 
        self.pending_claim_player_id = None
        self.claim_type_pending = None
        # self.turn_number does not advance here, it advances when the claiming player discards.
        # Or, if you consider a claim part of the "turn cycle", it could advance.
        # For now, let's say the discard from the claiming player is part of their new turn.
        
        print(f"Player {claiming_player.player_id}'s turn. Hand size: {len(claiming_player.hand)}. Must discard.")
        # The claiming player now has 11 tiles in hand (13 + 1 drawn - 3 for Pung + 1 claimed = 12, then -1 for Pung? No.)
        # Hand was size 13 (INIT_HAND_SIZE). They did not draw.
        # They use 2 from hand + 1 claimed tile for Pung. Hand size becomes 13 - 2 = 11.
        # They now have 11 tiles + revealed Pung. They must discard one of these 11 tiles.
        # So their hand size should be 11. The rules of Mahjong mean after claim, you discard.
        # The hand size for discard check (INIT_HAND_SIZE + 1) is for *after drawing a tile*.
        # After claiming a Pung, a player has 13 (original) - 2 (used for Pung) = 11 tiles in hand + the Pung.
        # They then discard from these 11, resulting in 10 tiles in hand + Pung.
        # This is different from draw-discard.
        # The check `if len(player.hand) != INIT_HAND_SIZE + 1:` in `discard_tile_for_current_player` will fail.
        # This needs a state or flag to indicate "post-claim discard".
        # For now, the subtask does not require modifying the discard logic for post-claim.
        # We will assume the next action for the human player is to call `eel_discard_tile`
        # and the current `discard_tile_for_current_player` logic will need adjustment in a future step.
        return True # Pung processed, player needs to discard

    def run_ai_turn(self): # Assumes self.current_player_index points to an AI
        ai_player = self.players[self.current_player_index]
        if not isinstance(ai_player.agent, AIPlayerAgent):
            print(f"Error: run_ai_turn called for non-AI player {ai_player.player_id}")
            return {"success": False, "error": "Not an AI player."}

        # 1. AI Draws a tile
        drawn_tile = self.draw_tile_for_current_player()
        if drawn_tile is None:
            # print(f"AI Player {ai_player.player_id} could not draw (wall empty?).")
            # This might indicate end of game (draw/exhaustion)
            # TODO: Handle wall empty scenario (game ends in a draw if no one wins)
            return {"success": False, "error": "Wall empty, AI cannot draw."} # Or a specific "game_over_draw" status

        # print(f"AI Player {ai_player.player_id} drew {drawn_tile}. Hand size: {len(ai_player.hand)}")

        # 2. AI Chooses a tile to discard
        # The hand passed to choose_discard is ai_player.hand, which now has 14 tiles.
        tile_to_discard_by_ai = ai_player.agent.choose_discard(self, ai_player.hand, drawn_tile)
        
        if tile_to_discard_by_ai is None:
            print(f"Error: AI Player {ai_player.player_id} failed to choose a discard.")
            # This is an internal AI error, try to recover by discarding randomly.
            if ai_player.hand: # Check hand is not empty
                 tile_to_discard_by_ai = random.choice(ai_player.hand)
            else: # Should not happen if draw was successful
                 return {"success": False, "error": "AI hand empty after draw, cannot discard."}


        # print(f"AI Player {ai_player.player_id} chose to discard {tile_to_discard_by_ai}")

        # 3. AI Discards the chosen tile
        # We need to pass a representation of the tile if discard_tile_for_current_player expects it
        discard_repr = {"suit": tile_to_discard_by_ai.suit, "value": tile_to_discard_by_ai.value}
        discard_success = self.discard_tile_for_current_player(discard_repr)
        
        if not discard_success:
            # This would be unusual if the AI chose a tile from its own hand.
            print(f"Error: AI Player {ai_player.player_id} failed to discard {tile_to_discard_by_ai} properly.")
            return {"success": False, "error": "AI failed to execute discard."}

        # discard_tile_for_current_player already handles:
        # - Setting self.current_discard
        # - Checking for claims by other players (which might set pending_claim_player_id)
        # - Advancing turn if no claims are pending.
        
        # print(f"AI Player {ai_player.player_id} turn finished. Discarded: {self.current_discard}")
        return {
            "success": True,
            "ai_player_id": ai_player.player_id,
            "discarded_tile": {"suit": self.current_discard.suit, "value": self.current_discard.value},
            "next_player_id": self.players[self.current_player_index].player_id, # Who's turn is it now conceptually
            "human_can_claim_pung": (self.pending_claim_player_id == 0 and self.claim_type_pending == "PUNG"),
            "claimable_tile": {"suit": self.potential_claim_tile.suit, "value": self.potential_claim_tile.value} if self.potential_claim_tile and self.pending_claim_player_id == 0 else None
        }
