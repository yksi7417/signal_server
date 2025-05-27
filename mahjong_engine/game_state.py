import random
from .player import Player
from .tile import Tile
from .constants import TILE_CATEGORIES_FOR_GENERATION, NUM_COPIES_PER_TILE, NUM_PLAYERS, INIT_HAND_SIZE, WIND_EAST
from .player_agent import HumanPlayerAgent, AIPlayerAgent
from .hand_validator import (can_form_pung_with_discard, check_standard_win,
                           can_form_kong_with_discard, can_form_self_kong)
from .melds import Pung, Kong


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

        self.current_player_index = 0
        self.game_wind = WIND_EAST
        self.current_discard = None
        self.turn_number = 0
        self.pending_claim_player_id = None
        self.potential_claim_tile = None
        self.claim_type_pending = None

        self.winner_found = False
        self.winning_player_id = None





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
        if not self.wall:
            print("Wall is empty. Cannot draw.")
            return None

        player = self.players[self.current_player_index]
        if len(player.hand) >= INIT_HAND_SIZE + 1:
            print(f"Player {player.player_id} already has {len(player.hand)} tiles.\
                  Cannot draw again before discarding.")
            return None

        drawn_tile = self.wall.pop(0)
        player.hand.append(drawn_tile)
        is_win = check_standard_win(player.hand, player.revealed_sets)
        if is_win:
            self.winner_found = True
            self.winning_player_id = player.player_id
            print(f"Player {player.player_id} has won!")
        return drawn_tile

    def discard_tile_for_current_player(self, tile_to_discard_repr):
        player = self.players[self.current_player_index]
        print(f"Player {player.revealed_sets}")
        revealed_count = sum(len(meld.raw_tiles) for meld in player.revealed_sets)

        if len(player.hand) + revealed_count != INIT_HAND_SIZE + 1:
            print(f"Player {player.player_id} has {len(player.hand)} tiles. Should have {INIT_HAND_SIZE + 1} before discarding.")
            return False

        tile_object_to_discard = None
        found_tile = False
        for tile_in_hand in player.hand:
            if tile_in_hand.suit == tile_to_discard_repr['suit'] and tile_in_hand.value == tile_to_discard_repr['value']:
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
        self.pending_claim_player_id = None
        self.claim_type_pending = None

        start_check_idx = (self.current_player_index + 1) % len(self.players)
        for i in range(len(self.players) - 1):
            check_player_idx = (start_check_idx + i) % len(self.players)
            if check_player_idx == self.current_player_index:
                continue
            other_player = self.players[check_player_idx]
            
            # Check for Kong first (higher priority)
            if can_form_kong_with_discard(other_player.hand, self.potential_claim_tile):
                if isinstance(other_player.agent, HumanPlayerAgent):
                    self.pending_claim_player_id = other_player.player_id
                    self.claim_type_pending = "KONG"
                    print(f"Player {other_player.player_id} can Kong {self.potential_claim_tile}")
                    return True
                elif isinstance(other_player.agent, AIPlayerAgent):
                    # TODO: Implement AI Kong decision
                    pass
            
            # Then check for Pung
            elif can_form_pung_with_discard(other_player.hand, self.potential_claim_tile):
                if isinstance(other_player.agent, HumanPlayerAgent):
                    self.pending_claim_player_id = other_player.player_id
                    self.claim_type_pending = "PUNG"
                    print(f"Player {other_player.player_id} can Pung {self.potential_claim_tile}")
                    return True
                elif isinstance(other_player.agent, AIPlayerAgent):
                    # TODO: Implement AI Pung decision
                    pass
        if self.pending_claim_player_id is None:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.turn_number += 1
        return True

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
            if tile_in_hand == claimed_tile and len(tiles_to_remove_for_pung) < 2:
                tiles_to_remove_for_pung.append(tile_in_hand)

        if len(tiles_to_remove_for_pung) != 2:






            print(f"Error: Could not identify 2 matching tiles for Pung from player {claiming_player_id}'s hand. Found {len(tiles_to_remove_for_pung)}.")
            return False


        for tile_to_remove in tiles_to_remove_for_pung:
            claiming_player.hand.remove(tile_to_remove)


        new_pung = Pung(tile=claimed_tile, revealed=True, claimed_from=discarding_player_original_index)
        claiming_player.add_revealed_set(new_pung)

        print(f"Player {claiming_player_id} formed Pung: {new_pung} from player {discarding_player_original_index}'s discard.")


        self.current_player_index = claiming_player_id

        self.current_discard = None
        self.potential_claim_tile = None
        self.pending_claim_player_id = None
        self.claim_type_pending = None




        print(f"Player {claiming_player.player_id}'s turn. Hand size: {len(claiming_player.hand)}. Must discard.")
        return True

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
        new_kong = Kong(tile=claimed_tile, revealed=True, claimed_from=discarding_player_original_index)
        claiming_player.add_revealed_set(new_kong)

        print(f"Player {claiming_player_id} formed Kong from player {discarding_player_original_index}'s discard.")

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
            print(f"Error: run_ai_turn called for non-AI player {ai_player.player_id}")
            return {"success": False, "error": "Not an AI player."}
        drawn_tile = self.draw_tile_for_current_player()
        if drawn_tile is None:
            return {"success": False, "error": "Wall empty, AI cannot draw."}
        if self.winner_found and self.winning_player_id == ai_player.player_id:
            print(f"AI Player {ai_player.player_id} has won by self-draw after drawing {drawn_tile}!")
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

        tile_to_discard_by_ai = ai_player.agent.choose_discard(self, ai_player.hand, drawn_tile)
        if tile_to_discard_by_ai is None:
            print(f"Error: AI Player {ai_player.player_id} failed to choose a discard.")
            if ai_player.hand:
                 tile_to_discard_by_ai = random.choice(ai_player.hand)
            else:
                 return {"success": False, "error": "AI hand empty after draw, cannot discard."}
        discard_repr = {"suit": tile_to_discard_by_ai.suit,
                        "value": tile_to_discard_by_ai.value,
                        "unicode": tile_to_discard_by_ai.unicode}
        discard_success = self.discard_tile_for_current_player(discard_repr)

        if not discard_success:
            print(f"Error: AI Player {ai_player.player_id} failed to discard {tile_to_discard_by_ai} properly.")
            return {"success": False, "error": "AI failed to execute discard."}

        return {
            "success": True,
            "ai_player_id": ai_player.player_id,
            "discarded_tile": {
                "suit": self.current_discard.suit,
                "value": self.current_discard.value,
                "unicode": self.current_discard.unicode
            },
            "next_player_id": self.players[self.current_player_index].player_id,
            "human_can_claim": self.claim_type_pending if self.pending_claim_player_id == 0 else None,
            "claimable_tile": {"suit": self.potential_claim_tile.suit, "value": self.potential_claim_tile.value} if self.potential_claim_tile and self.pending_claim_player_id == 0 else None
        }
