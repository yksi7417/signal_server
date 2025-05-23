from abc import ABC, abstractmethod
import random # For AIPlayerAgent later
import collections # Added import

class PlayerAgent(ABC):
    def __init__(self, player_id):
        self.player_id = player_id

    @abstractmethod
    def choose_discard(self, game_state, hand):
        """
        Decide which tile to discard from the hand.
        Args:
            game_state: The current GameState object.
            hand: A list of Tile objects representing the player's hand (typically 14 tiles).
        Returns:
            A Tile object from the hand to be discarded.
        """
        pass

    @abstractmethod
    def decide_claim(self, game_state, discarded_tile, claim_options):
        """
        Decide whether to claim a discarded tile.
        Args:
            game_state: The current GameState object.
            discarded_tile: The Tile object that was just discarded.
            claim_options: A list of possible claims (e.g., Pung, Kong, Chow, Win).
        Returns:
            A claim action object/identifier, or None if no claim.
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(player_id={self.player_id})"


class HumanPlayerAgent(PlayerAgent):
    def choose_discard(self, game_state, hand):
        # For a human player, this decision comes from the UI via an Eel call.
        # This method might not be directly called by the game loop if it's a human.
        # If called, it indicates an issue or a fallback is needed.
        print(f"Warning: HumanPlayerAgent.choose_discard called for player {self.player_id}. This should be UI driven.")
        # Fallback: return the last tile if hand is not empty (a simple, predictable behavior)
        if hand:
            return hand[-1] 
        return None # Should not happen with a valid hand

    def decide_claim(self, game_state, discarded_tile, claim_options):
        # Decision comes from UI.
        print(f"Warning: HumanPlayerAgent.decide_claim called for player {self.player_id}. This should be UI driven.")
        return None # Default to no claim


class AIPlayerAgent(PlayerAgent):
    def choose_discard(self, game_state, hand, drawn_tile): # Added drawn_tile parameter
        if not hand:
            return None 

        # Basic strategy:
        # 1. If the drawn_tile forms no immediate pair with existing tiles, discard it.
        #    (More advanced: check if it helps form sequences, etc.)
        # 2. Otherwise, discard another "isolated" tile.
        # 3. For now, let's keep it simple: if drawn_tile is in hand, try to discard it.
        #    If not (which would be odd), or for a slightly better basic strategy,
        #    discard a random tile that isn't part of a pair.

        if drawn_tile in hand:
            # Check if the drawn_tile makes a pair with anything else in the hand (excluding itself for the count)
            count_of_drawn_tile_in_hand = 0
            for tile in hand:
                if tile == drawn_tile:
                    count_of_drawn_tile_in_hand +=1
            
            if count_of_drawn_tile_in_hand == 1: # Only the drawn tile itself, no pre-existing match
                # print(f"AI Player {self.player_id} choosing to discard newly drawn tile: {drawn_tile}")
                return drawn_tile

        # Fallback: If drawn tile made a pair or wasn't found (edge case), discard a random tile.
        # A slightly better fallback: try to discard a non-pair tile.
        
        # Count all tiles in hand
        tile_counts = collections.Counter(hand)
        
        # Try to find a tile that is not part of a pair (count == 1)
        single_tiles = [tile for tile, count in tile_counts.items() if count == 1]
        
        if single_tiles:
            # Prefer discarding the drawn_tile if it's among the single_tiles
            if drawn_tile in single_tiles:
                # print(f"AI Player {self.player_id} choosing to discard drawn_tile (as a single): {drawn_tile}")
                return drawn_tile
            # Else, discard a random single tile
            chosen = random.choice(single_tiles)
            # print(f"AI Player {self.player_id} choosing to discard random single tile: {chosen}")
            return chosen
        else:
            # All tiles are part of pairs or more (e.g., two pairs, a Pung). Just discard randomly.
            chosen = random.choice(hand)
            # print(f"AI Player {self.player_id} choosing to discard random tile (all are parts of sets): {chosen}")
            return chosen

    def decide_claim(self, game_state, discarded_tile, claim_options):
        # Simplest AI: never claim.
        return None
