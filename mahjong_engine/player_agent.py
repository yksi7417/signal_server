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
        scores = [(self._score_tile(t, hand, game_state), random.random(), t) for t in hand]
        scores.sort(key=lambda x: (x[0], x[1]))  # Lowest score first, random tiebreak
        return scores[0][2]

    def _count_available(self, tile, hand, game_state):
        """Count how many copies of tile remain unseen (not in hand, discards, or melds)."""
        if game_state is None:
            return 2  # Conservative default when no game state
        total = 4
        total -= sum(1 for t in hand if t == tile)
        for p in game_state.players:
            total -= sum(1 for t in p.discards if t == tile)
            for meld in p.revealed_sets:
                total -= sum(1 for t in meld.raw_tiles if t == tile)
        return max(0, total)

    def _score_tile(self, tile, hand, game_state):
        count = sum(1 for t in hand if t == tile)
        avail = self._count_available(tile, hand, game_state)

        if count >= 3:
            return 100 if avail > 0 else 90
        if count == 2:
            return 90 if avail > 0 else 50

        # Single tile
        if tile.is_honor():
            if avail == 0:
                return 0
            if tile.is_dragon():
                return 45
            if tile.is_wind():
                if game_state is not None:
                    player = game_state.players[self.player_id]
                    if tile.value == player.wind or tile.value == game_state.game_wind:
                        return 45
                    return 40  # Non-scoring wind
                return 40
            return 0

        if tile.is_numeric_suit():
            return self._score_numeric_single(tile, hand, avail)

        return 0

    def _score_numeric_single(self, tile, hand, avail):
        val = int(tile.value)
        suit_values = [int(t.value) for t in hand if t.suit == tile.suit and t != tile]
        best = 0

        # Check 3 chow windows that include this tile
        for start in range(max(1, val - 2), min(8, val) + 1):
            needed = [start, start + 1, start + 2]
            needed.remove(val)
            has_both = all(v in suit_values for v in needed)
            has_one = any(v in suit_values for v in needed)

            if has_both:
                best = max(best, 90)  # Complete chow
            elif has_one:
                held = [v for v in needed if v in suit_values][0]
                # Check if tile and held neighbor are adjacent or gapped
                if abs(val - held) == 1:
                    best = max(best, 80)  # Connected (adjacent)
                else:
                    best = max(best, 70)  # Gapped

        if best > 0:
            return best

        # Fallback: distance to nearest same-suit tile
        if suit_values:
            min_dist = min(abs(val - sv) for sv in suit_values)
            return max(0, 8 - min_dist)

        return 0  # Completely isolated

    def decide_claim(self, game_state, discarded_tile, claim_options):
        # Priority: WIN > KONG > PUNG > CHOW
        for claim in ["WIN", "KONG", "PUNG", "CHOW"]:
            if claim in claim_options:
                return claim
        return None
