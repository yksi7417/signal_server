import random

from .constants import INIT_HAND_SIZE, NUM_COPIES_PER_TILE, NUM_PLAYERS, TILE_CATEGORIES_FOR_GENERATION, WIND_EAST, WINDS_ALL
from .hand_validator import (
    can_form_kong_with_discard,
    can_form_pung_with_discard,
    can_form_self_kong,
    check_standard_win,
)
from .melds import Kong, Pung
from .player import Player
from .player_agent import AIPlayerAgent, HumanPlayerAgent
from .ruleset import DefaultRuleSet  # Added import for DefaultRuleSet
from .tile import Tile


class GameState:
    def _create_full_tile_set(self):
        tiles = []
        for suit, values in TILE_CATEGORIES_FOR_GENERATION:
            for value in values:
                tiles.extend([Tile(suit, value)] * NUM_COPIES_PER_TILE)
        return tiles

    def __init__(self, num_players=NUM_PLAYERS):
        self.players = []
        for i in range(num_players):
            if i == 0:
                agent = HumanPlayerAgent(player_id=i)
            else:
                agent = AIPlayerAgent(player_id=i)
            self.players.append(Player(player_id=i, agent=agent))

        self.wall = self._create_full_tile_set()
        random.shuffle(self.wall)

        self.deal_tiles()
        self.rules = DefaultRuleSet()  # Instantiated DefaultRuleSet        
        self.current_player_index = 0
        self.game_wind = WIND_EAST
        self.current_discard = None
        self.turn_number = 0
        self.pending_claim_player_id = None
        self.potential_claim_tile = None
        self.claim_type_pending = None        # Dealer rotation and round tracking
        self.dealer_index = 0  # Start with East dealer (player 0)
        self.round_wind = WIND_EAST  # Current round wind

        self.winner_found = False
        self.winning_player_id = None        # Assign initial player winds based on dealer position
        self.assign_player_winds()

    def deal_tiles(self):
        for player in self.players:
            player.hand = []
            for _ in range(INIT_HAND_SIZE):
                if self.wall:
                    player.hand.append(self.wall.pop(0))
                else:
                    print("Warning: Wall is empty during initial deal!")
                    break

    def __repr__(self):
        return f"GameState(players={len(self.players)}, wall_size={len(self.wall)}, turn={self.turn_number})"

    def draw_tile_for_current_player(self):
        """Draw a tile for current player with modulo-3 hand validation."""
        if not self.wall:
            print("Wall is empty. Cannot draw.")
            # Handle wall empty case - dealer continues if no winner
            self.end_hand(wall_empty=True)
            return None

        player = self.players[self.current_player_index]
        hand_size = len(player.hand)

        if hand_size % 3 != 1:
            msg = (f"Player {player.player_id} cannot draw with {hand_size} tiles in hand.")
            print(msg)
            return None

        # Draw and add tile
        drawn_tile = self.wall.pop(0)
        player.hand.append(drawn_tile)        # Check for win if hand size % 3 == 2
        if len(player.hand) % 3 == 2:
            is_win = self.rules.is_winning_hand(
                player.hand, player.revealed_sets)
            if is_win:
                self.winner_found = True
                self.winning_player_id = player.player_id
                msg = f"Player {player.player_id} won by self-draw!"
                print(msg)
                
                # Handle dealer rotation based on self-draw win
                self.end_hand(winner_id=player.player_id)

        return drawn_tile

    def discard_tile_for_current_player(self, tile_to_discard_repr):
        player = self.players[self.current_player_index]
        if len(player.hand) % 3 != 2:
            print(
                f"Player {player.player_id} has tiles:{len(player.hand)} % 3 != 1 before discarding.")
            return False

        tile_object_to_discard = None
        found_tile = False
        for tile_in_hand in player.hand:
            if tile_in_hand.suit == tile_to_discard_repr[
                    'suit'] and tile_in_hand.value == tile_to_discard_repr['value']:
                tile_object_to_discard = tile_in_hand
                player.hand.remove(tile_object_to_discard)
                found_tile = True
                break

        if not found_tile:
            print(f"Tile {tile_to_discard_repr} not found in player {player.player_id}'s hand.")
            return False

        self.current_discard = tile_object_to_discard
        player.discards.append(tile_object_to_discard)

        self.potential_claim_tile = self.current_discard
        # Reset pending claims before checks
        self.pending_claim_player_id = None
        self.claim_type_pending = None

        # 1. Check for WIN claim from other players
        start_check_idx = (self.current_player_index + 1) % len(self.players)
        for i in range(len(self.players) - 1):  # Iterate through other players
            check_player_idx = (start_check_idx + i) % len(self.players)
            # current_player_index is implicitly skipped by the loop structure
            # starting from current_player_index + 1

            other_player = self.players[check_player_idx]
            potential_win_hand = other_player.hand + [self.current_discard]

            if self.rules.is_winning_hand(
                    potential_win_hand,
                    other_player.revealed_sets):  # Changed to self.rules
                if isinstance(other_player.agent, HumanPlayerAgent):
                    self.pending_claim_player_id = other_player.player_id
                    self.claim_type_pending = "WIN"
                    # self.potential_claim_tile is already self.current_discard
                    print(
                        f"Player {other_player.player_id} (Human) can WIN with {self.current_discard}. Waiting for UI.")
                    return True  # Human win claim takes priority
                # Optional: Logic for AI win claim can be added here if needed in future.
                # For now, if an AI can win, it doesn't immediately halt flow for UI.
                # It might be recorded or handled by AI's own turn logic.

        # 2. If no WIN claim by a Human, check for PUNG/KONG claims
        if self.pending_claim_player_id is None:  # Only proceed if no Human WIN claim took precedence
            # Iterate through other players again for Pung/Kong.
            # Note: Could combine with the WIN check loop if careful about claim priorities.
            # For clarity and strict adherence to "WIN first for Human",
            # separate loops are fine.
            for i in range(len(self.players) - 1):
                check_player_idx = (start_check_idx + i) % len(self.players)
                other_player = self.players[check_player_idx]

                # Check for Kong first (higher priority)
                if can_form_kong_with_discard(
                        other_player.hand, self.potential_claim_tile):
                    if isinstance(other_player.agent, HumanPlayerAgent):
                        self.pending_claim_player_id = other_player.player_id
                        self.claim_type_pending = "KONG"
                        print(
                            f"Player {other_player.player_id} can Kong {self.potential_claim_tile}")
                        return True
                    elif isinstance(other_player.agent, AIPlayerAgent):
                        # TODO: Implement AI Kong decision
                        pass

                # Then check for Pung
                elif can_form_pung_with_discard(other_player.hand, self.potential_claim_tile):
                    if isinstance(other_player.agent, HumanPlayerAgent):
                        # Check if this Pung is part of a win already identified for an AI (less likely to be an issue here)
                        # Or if this player could also have won (win check has priority)
                        # This simplified logic assumes WIN check above handles
                        # Human WIN priority.
                        self.pending_claim_player_id = other_player.player_id
                        self.claim_type_pending = "PUNG"
                        print(
                            f"Player {other_player.player_id} (Human) can Pung {self.potential_claim_tile}. Waiting for UI.")
                        return True
                    # elif isinstance(other_player.agent, AIPlayerAgent): pass
                        # AI Pung claim logic could be triggered here if AI should pre-emptively claim.
                        # Current game flow usually has AI decide on its turn.

        # 3. If no claims by a human player that require UI interaction,
        # advance turn
        if self.pending_claim_player_id is None:
            self.current_player_index = (
                self.current_player_index + 1) % len(self.players)
            self.turn_number += 1

        return True  # Discard was successful, regardless of claims

    def process_pung_claim(self, claiming_player_id, claimed_tile):
        """
        Processes a Pung claim for the specified player with the given tile.
        Assumes validation (can_form_pung_with_discard) and decision were already made.
        """
        if claimed_tile is None or claiming_player_id is None:
            print("Error: Claimed tile or player ID is None.")
            return False

        claiming_player = None
        discarding_player_original_index = self.current_player_index

        for p in self.players:
            if p.player_id == claiming_player_id:
                claiming_player = p
                break

        if not claiming_player:
            print(f"Error: Claiming player {claiming_player_id} not found.")
            return False
        tiles_to_remove_for_pung = []
        temp_hand_for_search = list(claiming_player.hand)

        for tile_in_hand in temp_hand_for_search:
            if tile_in_hand == claimed_tile and len(
                    tiles_to_remove_for_pung) < 2:
                tiles_to_remove_for_pung.append(tile_in_hand)

        if len(tiles_to_remove_for_pung) != 2:
            print(
                f"Error: Could not identify 2 matching tiles for Pung from player {claiming_player_id}'s hand. Found {len(tiles_to_remove_for_pung)}.")
            return False

        for tile_to_remove in tiles_to_remove_for_pung:
            claiming_player.hand.remove(tile_to_remove)

        new_pung = Pung(
            tile=claimed_tile,
            revealed=True,
            claimed_from=discarding_player_original_index)
        claiming_player.add_revealed_set(new_pung)

        print(
            f"Player {claiming_player_id} formed Pung: {new_pung} from player {discarding_player_original_index}'s discard.")

        self.current_player_index = claiming_player_id

        self.current_discard = None
        self.potential_claim_tile = None
        self.pending_claim_player_id = None
        self.claim_type_pending = None

        print(f"Player {claiming_player.player_id}'s turn. Hand size: {len(claiming_player.hand)}. Must discard.")
        return True

    def process_win_claim(self, claiming_player_id, claimed_tile):
        """
        Processes a Win claim for the specified player with the given tile.
        Assumes validation (is_winning_hand) and decision were already made.
        """
        claiming_player = None
        for p in self.players:
            if p.player_id == claiming_player_id:
                claiming_player = p
                break

        if not claiming_player:
            print(
                f"Error: Claiming player {claiming_player_id} not found for WIN.")
            return False

        # Add the claimed tile to the player's hand for completeness,
        # even though validation happened with it conceptually.
        # This ensures the hand reflects the winning state.
        claiming_player.hand.append(claimed_tile)

        self.winner_found = True
        self.winning_player_id = claiming_player_id

        print(
            f"Player {claiming_player_id} has claimed WIN with tile {claimed_tile}!")        # Clear pending claim and discard information
        self.pending_claim_player_id = None
        self.claim_type_pending = None
        self.potential_claim_tile = None
        self.current_discard = None  # Tile is claimed for win

        # Set current player context to the winner
        self.current_player_index = claiming_player_id

        # Handle dealer rotation based on win
        self.end_hand(winner_id=claiming_player_id)

        # No further actions like drawing/discarding are needed after a win.
        return True

    def process_hidden_kong(self, player_id, tile_info):
        """
        Processes a Hidden Kong declaration for the specified player with the given tile_info.
        """
        player = self.players[player_id]

        if self.current_player_index != player_id:
            return {"success": False,
                    "error": "Not your turn to declare a Hidden Kong."}

        # Hand size check: Expected INIT_HAND_SIZE + 1 (14 tiles) after drawing, before discard.
        # Or INIT_HAND_SIZE (13 tiles) if declaring from existing hand before drawing (less common for hidden kong)
        # For this implementation, we'll assume it's possible after drawing, so hand size is 14.
        # Or, if it's from a hand of 13 tiles, it implies they haven't drawn yet this turn.
        # Let's be flexible: player must have 4 of the tiles.
        # A more strict check would be: len(player.hand) == INIT_HAND_SIZE + 1

        try:
            kong_tile_obj = Tile(tile_info['suit'], tile_info['value'])
        except Exception as e:
            return {"success": False,
                    "error": f"Invalid tile data for Hidden Kong: {e}"}

        tile_count_in_hand = sum(1 for t in player.hand if t == kong_tile_obj)

        if tile_count_in_hand < 4:
            return {
                "success": False,
                "error": f"Not enough {kong_tile_obj} tiles in hand for Hidden Kong. Found {tile_count_in_hand}."}

        # Process the Kong
        removed_count = 0
        # Create a copy to modify while iterating
        temp_hand = list(player.hand)
        for _ in range(4):
            for tile_in_hand in temp_hand:
                if tile_in_hand == kong_tile_obj:
                    # Remove from original hand
                    player.hand.remove(tile_in_hand)
                    # Remove from temp hand to avoid recounting
                    temp_hand.remove(tile_in_hand)
                    removed_count += 1
                    break

        if removed_count != 4:  # Should not happen if tile_count_in_hand was >= 4
            # Restore hand if removal failed partway (though very unlikely)
            # This is not a perfect restore, but a fallback.
            player.hand = temp_hand
            return {"success": False,
                    "error": "Error removing tiles for Hidden Kong."}

        # Create the Kong meld - revealed=False is crucial for hidden kong
        new_kong = Kong(
            tile=kong_tile_obj,
            revealed=False,
            claimed_from=player_id)
        player.add_revealed_set(new_kong)

        # Draw Replacement Tile
        # This appends to hand and checks for win
        replacement_tile = self.draw_tile_for_current_player()

        drawn_tile_serializable = None
        if replacement_tile:
            drawn_tile_serializable = {
                "unicode": replacement_tile.unicode,
                "suit": replacement_tile.suit,
                "value": replacement_tile.value
            }

        message = f"Hidden Kong with {kong_tile_obj} declared. Replacement tile drawn: {replacement_tile.unicode if replacement_tile else 'None'}. Your turn to discard."

        if self.winner_found and self.winning_player_id == player_id:
            # This condition would be true if draw_tile_for_current_player()
            # resulted in a win
            message = f"Hidden Kong with {kong_tile_obj}. Drew {replacement_tile.unicode if replacement_tile else 'None'}. Player {player_id} WINS by self-draw after Kong!"
        elif replacement_tile is None:
            # This is a problem case - wall empty before discard turn after Kong.
            # Game might end in a draw or other specific rule.
            # For now, allow the successful Kong declaration but flag the
            # issue.
            message = f"Hidden Kong with {kong_tile_obj} declared. Wall empty, no replacement tile drawn. Special game condition."
            # Potentially, this should be success:False if no replacement means invalid move.
            # However, forming the Kong itself is valid.
            # Let's return success, but the frontend/game rules might need to
            # handle this state.

        return {
            "success": True,
            "message": message,
            "drawn_tile": drawn_tile_serializable
        }

    def process_kong_claim(self, claiming_player_id, claimed_tile):
        """
        Processes a Kong claim for the specified player with the given tile.
        """
        if claimed_tile is None or claiming_player_id is None:
            print("Error: Claimed tile or player ID is None.")
            return False

        claiming_player = None
        discarding_player_original_index = self.current_player_index

        for p in self.players:
            if p.player_id == claiming_player_id:
                claiming_player = p
                break

        if not claiming_player:
            print(f"Error: Claiming player {claiming_player_id} not found.")
            return False

        # Find the three matching tiles in hand
        tiles_to_remove_for_kong = []
        temp_hand_for_search = list(claiming_player.hand)

        for tile_in_hand in temp_hand_for_search:
            if tile_in_hand == claimed_tile:
                tiles_to_remove_for_kong.append(tile_in_hand)

        if len(tiles_to_remove_for_kong) != 3:
            print(f"Error: Could not identify 3 matching tiles for Kong.")
            return False

        # Remove the tiles from hand
        for tile_to_remove in tiles_to_remove_for_kong:
            claiming_player.hand.remove(tile_to_remove)

        # Create and add the Kong meld
        new_kong = Kong(
            tile=claimed_tile,
            revealed=True,
            claimed_from=discarding_player_original_index)
        claiming_player.add_revealed_set(new_kong)

        print(
            f"Player {claiming_player_id} formed Kong from player {discarding_player_original_index}'s discard.")

        self.current_player_index = claiming_player_id
        self.current_discard = None
        self.potential_claim_tile = None
        self.pending_claim_player_id = None
        self.claim_type_pending = None

        # Draw a replacement tile after Kong
        self.draw_tile_for_current_player()

        return True

    def check_and_handle_self_kong(self, player):
        """Check if player can form Kong with their own tiles and handle it."""
        possible_kongs = can_form_self_kong(player.hand)

        if possible_kongs and isinstance(player.agent, HumanPlayerAgent):
            # For human players, we'll need UI interaction
            self.potential_self_kong_tiles = possible_kongs
            return True

        return False

    def run_ai_turn(self):
        ai_player = self.players[self.current_player_index]
        if not isinstance(ai_player.agent, AIPlayerAgent):
            print(
                f"Error: run_ai_turn called for non-AI player {ai_player.player_id}")
            return {"success": False, "error": "Not an AI player."}
        drawn_tile = self.draw_tile_for_current_player()
        if drawn_tile is None:
            return {"success": False, "error": "Wall empty, AI cannot draw."}
        if self.winner_found and self.winning_player_id == ai_player.player_id:
            print(
                f"AI Player {ai_player.player_id} has won by self-draw after drawing {drawn_tile}!")
            return {
                "success": True,
                "ai_player_id": ai_player.player_id,
                "action": "win",
                "winner_found": True,
                "winning_player_id": self.winning_player_id,
                "drawn_tile_for_win": {
                    "suit": drawn_tile.suit,
                    "value": drawn_tile.value,
                    "unicode": drawn_tile.unicode},
                "discarded_tile": None,
                "next_player_id": self.winning_player_id,
                "human_can_claim": None,
                "claimable_tile": None
            }

        tile_to_discard_by_ai = ai_player.agent.choose_discard(
            self, ai_player.hand, drawn_tile)
        if tile_to_discard_by_ai is None:
            print(f"Error: AI Player {ai_player.player_id} failed to choose a discard.")
            if ai_player.hand:
                tile_to_discard_by_ai = random.choice(ai_player.hand)
            else:
                return {"success": False,
                        "error": "AI hand empty after draw, cannot discard."}
        discard_repr = {"suit": tile_to_discard_by_ai.suit,
                        "value": tile_to_discard_by_ai.value,
                        "unicode": tile_to_discard_by_ai.unicode}
        discard_success = self.discard_tile_for_current_player(discard_repr)
        if not discard_success:
            print(
                f"Error: AI Player {ai_player.player_id} failed to discard {tile_to_discard_by_ai} properly.")
            return {"success": False, "error": "AI failed to execute discard."}

        return {"success": True,
                "ai_player_id": ai_player.player_id,
                "discarded_tile": {"suit": self.current_discard.suit,
                                   "value": self.current_discard.value,
                                   "unicode": self.current_discard.unicode} if self.current_discard else None,
                "next_player_id": self.players[self.current_player_index].player_id,                "human_can_claim": self.claim_type_pending if self.pending_claim_player_id == 0 else None,
                "claimable_tile": {"suit": self.potential_claim_tile.suit,
                                   "value": self.potential_claim_tile.value} if self.potential_claim_tile and self.pending_claim_player_id == 0 else None}

    def assign_player_winds(self):
        """Assign winds to players based on current dealer position."""
        for i, player in enumerate(self.players):
            # Calculate wind index relative to dealer
            wind_index = (i - self.dealer_index) % len(WINDS_ALL)
            player.wind = WINDS_ALL[wind_index]


    def advance_dealer(self):
        """Advance to next dealer following traditional Mahjong rotation."""
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        
        # When we complete a full dealer rotation (back to player 0 as dealer)
        if self.dealer_index == 0:
            self.advance_round()
            
        self.assign_player_winds()


    def advance_round(self):
        """Advance to next round wind."""
        current_round_index = WINDS_ALL.index(self.round_wind)
        next_round_index = (current_round_index + 1) % len(WINDS_ALL)
        self.round_wind = WINDS_ALL[next_round_index]


    def should_dealer_continue(self, winner_id=None, wall_empty=False):
        """Check if dealer should continue based on Mahjong rules."""
        # Dealer continues if:
        # 1. Current hand wins (winner is current dealer)
        # 2. Wall is empty with no winner (draw situation)
        if winner_id == self.dealer_index or (wall_empty and winner_id is None):
            return True
        return False


    def end_hand(self, winner_id=None, wall_empty=False):
        """End current hand and handle dealer rotation."""
        if not self.should_dealer_continue(winner_id, wall_empty):
            self.advance_dealer()
            
        # Reset game state for next hand
        self.current_player_index = self.dealer_index  # Next hand starts with dealer
        self.winner_found = False
        self.winning_player_id = None
        self.current_discard = None
        self.turn_number = 0
        self.pending_claim_player_id = None
        self.potential_claim_tile = None
        self.claim_type_pending = None
