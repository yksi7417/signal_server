from abc import ABC, abstractmethod
import collections
from .tile import Tile
from .melds import Pung, Kong, Chow, Pair, MeldType


class RuleSet(ABC):
    @abstractmethod
    def is_winning_hand(self, hand_tiles, revealed_sets, game_context=None):
        """
        Checks if a combination of hand tiles and revealed sets forms a winning hand
        according to this ruleset.
        Args:
            hand_tiles: A list of Tile objects to be partitioned.
            revealed_sets: A list of Meld objects already revealed by the player.
            game_context: Optional context about the game state (e.g., winds, current turn).
        Returns:
            True if it's a winning hand, False otherwise.
        """
        pass

    @abstractmethod
    def calculate_score(self, hand_tiles, revealed_sets, game_context=None):
        """
        Calculates the score of a winning hand according to this ruleset.
        Args:
            hand_tiles: A list of Tile objects in the hand.
            revealed_sets: A list of Meld objects already revealed.
            game_context: Optional context about the game state.
        Returns:
            An integer score.
        """
        pass


class DefaultRuleSet(RuleSet):
    def _can_form_melds_recursive(self, tile_counts, num_melds_to_find):
        """
        Recursive helper to check if tiles can form a given number of melds (Pungs, Kongs, Chows).
        This function is moved from hand_validator.py.
        """
        if num_melds_to_find == 0:
            # All melds found, check if any tiles are left (should be none for
            # successful partition)
            return not any(tile_counts.values())

        current_sum_of_tiles = sum(tile_counts.values())
        # Basic checks for feasibility
        if current_sum_of_tiles < num_melds_to_find * \
                3:  # Need at least 3 tiles per meld
            return False
        # Max tiles for melds (e.g. kongs). If we have more tiles than can form kongs, something is wrong.
        # This check might be too strict if we consider hands with more than 4 kongs (not standard).
        # For standard hands (4 melds), max is 4*4 = 16, if all are kongs.
        # If current_sum_of_tiles > num_melds_to_find * 4:
        # return False # This check might be overly restrictive depending on
        # interpretation.

        # Get the first available tile to try forming melds
        # Iterating over sorted unique tiles ensures consistent behavior
        sorted_unique_tiles = sorted(list(tile_counts.keys()))

        if not sorted_unique_tiles:  # No tiles left to form melds, but melds_to_find > 0
            return False

        # Try to form melds starting with the smallest tile
        # This is a brute-force search essentially.
        for tile in sorted_unique_tiles:  # Iterate through unique tiles present in the hand
            # Skip if this tile was used up by a previous recursive call
            if tile_counts[tile] == 0:
                continue

            # Try forming a Kong (4 identical tiles)
            if tile_counts[tile] >= 4:
                tile_counts[tile] -= 4
                if self._can_form_melds_recursive(
                        tile_counts, num_melds_to_find - 1):
                    return True
                tile_counts[tile] += 4  # Backtrack

            # Try forming a Pung (3 identical tiles)
            if tile_counts[tile] >= 3:
                tile_counts[tile] -= 3
                if self._can_form_melds_recursive(
                        tile_counts, num_melds_to_find - 1):
                    return True
                tile_counts[tile] += 3  # Backtrack

            # Try forming a Chow (sequence of 3, e.g., 1-2-3 of a suit)
            # Only for numeric suits (Characters, Bamboos, Dots) and if tile
            # value allows a sequence
            if tile.is_numeric_suit() and int(
                    # Max starting tile for a chow is 7 (7-8-9)
                    tile.value) <= 7:
                t1 = tile
                t2 = Tile(t1.suit, str(int(t1.value) + 1))
                t3 = Tile(t1.suit, str(int(t1.value) + 2))

                if tile_counts.get(t1, 0) > 0 and tile_counts.get(
                        t2, 0) > 0 and tile_counts.get(t3, 0) > 0:
                    tile_counts[t1] -= 1
                    tile_counts[t2] -= 1
                    tile_counts[t3] -= 1
                    if self._can_form_melds_recursive(
                            tile_counts, num_melds_to_find - 1):
                        return True
                    # Backtrack
                    tile_counts[t1] += 1
                    tile_counts[t2] += 1
                    tile_counts[t3] += 1

            # If we tried forming melds with 'tile' and failed, and this tile is still in hand,
            # it means this path doesn't work. We must use this tile in some meld.
            # If it couldn't start a Pung, Kong, or Chow, and it's still here, then this path is invalid.
            # However, the outer loop handles trying different tiles first.
            # If a tile cannot start any meld, it will eventually lead to failure when no melds can be formed.
            # The crucial part is that if a tile *can* start a meld, we explore that. If not, we move on.
            # If after trying all tiles, no valid meld sequence is found, this recursive call returns False.
            # Adding a 'break' here if tile_counts[tile] > 0 would be wrong, as
            # other tiles might form melds.

        return False

    def is_winning_hand(self, hand_tiles, revealed_sets, game_context=None):
        """
        Checks if a combination of hand tiles and revealed sets forms a standard winning hand (4 melds + 1 pair).
        This function is moved from hand_validator.py's check_standard_win.
        Args:
            hand_tiles: A list of Tile objects representing the tiles to be partitioned
                               into (4 - len(revealed_sets)) melds and 1 pair.
            revealed_sets: A list of Meld objects already revealed by the player.
            game_context: Optional context (not used in this default implementation).
        Returns:
            True if it's a winning hand, False otherwise.
        """
        num_melds_to_find_in_hand = 4 - len(revealed_sets)

        if num_melds_to_find_in_hand < 0:  # Should not happen with valid revealed_sets
            return False

        # Basic tile count checks for the hand portion
        # A winning hand has 14 tiles (INIT_HAND_SIZE + 1, where INIT_HAND_SIZE is usually 13).
        # Each meld is 3 tiles (Pung, Chow) or 4 tiles (Kong). A pair is 2 tiles.
        # Total tiles = (tiles in revealed_sets) + (tiles in hand_tiles).
        # This method is concerned with partitioning hand_tiles.

        # If 0 melds to find in hand, hand_tiles must be exactly a pair.
        if num_melds_to_find_in_hand == 0:
            return len(hand_tiles) == 2 and hand_tiles[0] == hand_tiles[1]

        # If we need to find melds in hand, hand_tiles cannot be empty.
        if not hand_tiles and num_melds_to_find_in_hand > 0:
            return False

        # The number of tiles in hand must be 2 (for the pair) + 3*N (for N melds)
        # or up to 2 + 4*N if kongs are involved.
        # A simpler check: len(hand_tiles) must be (num_melds_to_find_in_hand * 3) + 2 for the simplest case.
        # It can be more if kongs are present in the hand.
        # Example: 1 meld to find + pair = 5 tiles. 2 melds + pair = 8 tiles.
        # This was the logic from the original check_standard_win:
        min_expected_tiles_in_hand = (num_melds_to_find_in_hand * 3) + 2
        # max_expected_tiles_in_hand = (num_melds_to_find_in_hand * 4) + 2 # Max if all are kongs
        # The original check_standard_win had more complex tile count validation here.
        # For now, let's ensure it's at least the minimum.
        # The recursive function itself will fail if counts don't work out.
        if len(hand_tiles) < min_expected_tiles_in_hand:
            return False
        # A hand to be partitioned into N melds and 1 pair must have 3N+2 tiles.
        # If kongs are allowed in hand, it can be more.
        # The recursive function handles varying meld sizes (3 or 4).
        # The key is that the total number of tiles after pair removal must be divisible by 3 or allow for kongs.
        # The recursive function _can_form_melds_recursive handles the
        # partitioning.

        hand_counts = collections.Counter(hand_tiles)
        unique_tiles_in_hand = sorted(list(hand_counts.keys()))

        # Iterate through each unique tile type in the hand, trying it as the
        # pair
        for tile_for_pair in unique_tiles_in_hand:
            if hand_counts[tile_for_pair] >= 2:
                # Temporarily remove the pair
                hand_counts[tile_for_pair] -= 2

                # Check if the remaining tiles can form the required number of melds
                # Create a copy of hand_counts for the recursive call, as it
                # will be modified.
                if self._can_form_melds_recursive(
                        hand_counts.copy(), num_melds_to_find_in_hand):
                    return True  # Found a valid partition

                # Backtrack: add the pair back if this path failed
                hand_counts[tile_for_pair] += 2

        return False  # No valid pair and meld combination found

    def decompose_winning_hand(self, hand_tiles, revealed_sets):
        """Return all valid ``(melds, pair)`` decompositions of *hand_tiles*.

        Each result is a tuple ``(melds_list, pair_meld)`` where *melds_list*
        contains :class:`Pung`, :class:`Kong`, or :class:`Chow` objects and
        *pair_meld* is a :class:`Pair`.  The caller can iterate over all
        decompositions and pick the highest-scoring one.
        """
        num_melds = 4 - len(revealed_sets)
        results = []

        if num_melds < 0:
            return results

        hand_counts = collections.Counter(hand_tiles)
        unique_tiles = sorted(hand_counts.keys())

        for tile_for_pair in unique_tiles:
            if hand_counts[tile_for_pair] >= 2:
                hand_counts[tile_for_pair] -= 2
                pair_obj = Pair(tile_for_pair)
                melds_acc = []
                self._collect_melds(hand_counts.copy(), num_melds,
                                    melds_acc, results, pair_obj)
                hand_counts[tile_for_pair] += 2

        return results

    def _collect_melds(self, tile_counts, num_melds, current_melds,
                       results, pair_obj):
        """Backtracking helper that collects all decompositions into *results*."""
        if num_melds == 0:
            if not any(tile_counts.values()):
                results.append((list(current_melds), pair_obj))
            return

        if sum(tile_counts.values()) < num_melds * 3:
            return

        sorted_tiles = sorted(t for t in tile_counts if tile_counts[t] > 0)
        if not sorted_tiles:
            return

        for tile in sorted_tiles:
            if tile_counts[tile] == 0:
                continue

            # Kong
            if tile_counts[tile] >= 4:
                tile_counts[tile] -= 4
                current_melds.append(Kong(tile))
                self._collect_melds(tile_counts, num_melds - 1,
                                    current_melds, results, pair_obj)
                current_melds.pop()
                tile_counts[tile] += 4

            # Pung
            if tile_counts[tile] >= 3:
                tile_counts[tile] -= 3
                current_melds.append(Pung(tile))
                self._collect_melds(tile_counts, num_melds - 1,
                                    current_melds, results, pair_obj)
                current_melds.pop()
                tile_counts[tile] += 3

            # Chow
            if tile.is_numeric_suit() and int(tile.value) <= 7:
                t2 = Tile(tile.suit, str(int(tile.value) + 1))
                t3 = Tile(tile.suit, str(int(tile.value) + 2))
                if (tile_counts.get(tile, 0) > 0
                        and tile_counts.get(t2, 0) > 0
                        and tile_counts.get(t3, 0) > 0):
                    tile_counts[tile] -= 1
                    tile_counts[t2] -= 1
                    tile_counts[t3] -= 1
                    current_melds.append(Chow(tile, t2, t3))
                    self._collect_melds(tile_counts, num_melds - 1,
                                        current_melds, results, pair_obj)
                    current_melds.pop()
                    tile_counts[tile] += 1
                    tile_counts[t2] += 1
                    tile_counts[t3] += 1

    def calculate_score(self, hand_tiles, revealed_sets, game_context=None):
        if self.is_winning_hand(hand_tiles, revealed_sets, game_context):
            return 1
        return 0
