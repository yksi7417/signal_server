import collections
import random
from abc import ABC, abstractmethod


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
        print(
            f"Warning: HumanPlayerAgent.choose_discard called for player {self.player_id}. This should be UI driven.")
        if hand:
            return hand[-1]
        return None

    def decide_claim(self, game_state, discarded_tile, claim_options):
        print(
            f"Warning: HumanPlayerAgent.decide_claim called for player {self.player_id}. This should be UI driven.")
        return None


class AIPlayerAgent(PlayerAgent):
    def choose_discard(self, game_state, hand, drawn_tile):
        if not hand:
            return None
        if drawn_tile in hand:
            count_of_drawn_tile_in_hand = 0
            for tile in hand:
                if tile == drawn_tile:
                    count_of_drawn_tile_in_hand += 1
            if count_of_drawn_tile_in_hand == 1:
                return drawn_tile
        tile_counts = collections.Counter(hand)
        single_tiles = [
            tile for tile,
            count in tile_counts.items() if count == 1]
        if single_tiles:
            if drawn_tile in single_tiles:
                return drawn_tile
            chosen = random.choice(single_tiles)
            return chosen
        else:
            chosen = random.choice(hand)
            return chosen

    def decide_claim(self, game_state, discarded_tile, claim_options):
        return None
