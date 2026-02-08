from .tile import Tile
from .melds import Meld, MeldType, Pung, Kong, Chow, Pair
from .constants import SUITS_NUMERIC, SUIT_WINDS, SUIT_DRAGONS
import collections


def find_possible_melds(hand, last_tile=None):
    """
    Analyzes a hand (list of Tile objects) to find all possible Pungs, Kongs, Chows.
    If last_tile is provided, it's considered part of the hand for this check (e.g. a drawn tile or a claimed discard).
    Returns: A list of Meld objects.
    """

    print("DEV_INFO: find_possible_melds called, but not yet implemented.")
    return []


def _can_form_melds_recursive(tile_counts, num_melds_to_find):
    # NOTE: This function has been moved to mahjong_engine.ruleset.DefaultRuleSet
    # It is kept here temporarily to avoid breaking other potential direct usages,
    # but should be considered deprecated in this file.
    if num_melds_to_find == 0:

        return not any(tile_counts.values())

    current_sum_of_tiles = sum(tile_counts.values())
    if current_sum_of_tiles < num_melds_to_find * 3:
        return False
    if current_sum_of_tiles > num_melds_to_find * 4:
        return False

    sorted_unique_tiles = sorted(list(tile_counts.keys()))

    if not sorted_unique_tiles:
        return False

    for tile in sorted_unique_tiles:
        if tile_counts[tile] == 0:
            continue

        if tile_counts[tile] >= 4:
            tile_counts[tile] -= 4
            if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                return True
            tile_counts[tile] += 4

        if tile_counts[tile] >= 3:
            tile_counts[tile] -= 3
            if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                return True
            tile_counts[tile] += 3

        if tile.is_numeric_suit() and int(tile.value) <= 7:
            t1 = tile
            t2 = Tile(t1.suit, str(int(t1.value) + 1))
            t3 = Tile(t1.suit, str(int(t1.value) + 2))

            if tile_counts[t1] > 0 and tile_counts[t2] > 0 and tile_counts[t3] > 0:
                tile_counts[t1] -= 1
                tile_counts[t2] -= 1
                tile_counts[t3] -= 1
                if _can_form_melds_recursive(
                        tile_counts, num_melds_to_find - 1):
                    return True
                tile_counts[t1] += 1
                tile_counts[t2] += 1
                tile_counts[t3] += 1

    return False


def check_standard_win(player_hand_tiles, player_revealed_sets):
    # NOTE: This function has been moved to mahjong_engine.ruleset.DefaultRuleSet.is_winning_hand
    # It is kept here temporarily to avoid breaking other potential direct usages,
    # but should be considered deprecated in this file for win checking by
    # GameState.
    """
    Checks if a combination of hand tiles and revealed sets forms a standard winning hand (4 melds + 1 pair).
    Args:
        player_hand_tiles: A list of Tile objects representing the tiles to be partitioned
                           into (4 - len(player_revealed_sets)) melds and 1 pair.
                           Example: If 0 revealed sets, this is 14 tiles (13 initial + 1 winning).
                                    If 1 revealed Pung, this is 11 tiles (14 total - 3 in revealed Pung).
        player_revealed_sets: A list of Meld objects already revealed by the player.
    Returns:
        True if it's a winning hand, False otherwise.
    """
    num_melds_to_find_in_hand = 4 - len(player_revealed_sets)

    if num_melds_to_find_in_hand < 0:
        return False

    min_expected_tiles_in_hand = (num_melds_to_find_in_hand * 3) + 2
    max_expected_tiles_in_hand = (num_melds_to_find_in_hand * 4) + 2

    if len(player_hand_tiles) < min_expected_tiles_in_hand:
        return False
    if len(player_hand_tiles) > max_expected_tiles_in_hand:
        return False
    if len(player_hand_tiles) % 3 == 1 and num_melds_to_find_in_hand > 0:
        return False

    if num_melds_to_find_in_hand == 0:

        return len(
            player_hand_tiles) == 2 and player_hand_tiles[0] == player_hand_tiles[1]

    if not player_hand_tiles and num_melds_to_find_in_hand > 0:
        return False

    hand_counts = collections.Counter(player_hand_tiles)

    unique_tiles_in_hand = sorted(list(hand_counts.keys()))

    for tile_for_pair in unique_tiles_in_hand:
        if hand_counts[tile_for_pair] >= 2:

            hand_counts[tile_for_pair] -= 2

            if _can_form_melds_recursive(
                    hand_counts.copy(), num_melds_to_find_in_hand):
                return True

            hand_counts[tile_for_pair] += 2

    return False


def get_hand_score(hand_details, game_context):
    """
    DEPRECATED: Scoring logic has been moved to RuleSet implementations.
    This function should no longer be directly called for new scoring calculations.
    """
    print("DEV_INFO: get_hand_score in hand_validator.py is deprecated. Use RuleSet.calculate_score.")
    return 0  # Return a default value


def can_form_pung_with_discard(hand, discarded_tile):
    """
    Checks if a player's hand can form a Pung with a given discarded tile.
    Args:
        hand: List of Tile objects in the player's hand.
        discarded_tile: The Tile object that was discarded.
    Returns:
        True if a Pung can be formed, False otherwise.
    """
    if not hand or not discarded_tile:
        return False

    count = 0
    for tile_in_hand in hand:
        if tile_in_hand == discarded_tile:
            count += 1

    return count >= 2


def can_form_kong_with_discard(hand, discarded_tile):
    """
    Checks if a player's hand can form a Kong with a given discarded tile.
    Args:
        hand: List of Tile objects in the player's hand.
        discarded_tile: The Tile object that was discarded.
    Returns:
        True if a Kong can be formed, False otherwise.
    """
    if not hand or not discarded_tile:
        return False

    count = 0
    for tile_in_hand in hand:
        if tile_in_hand == discarded_tile:
            count += 1

    return count >= 3


def can_form_chow_with_discard(hand, discarded_tile, discarder_position, claimer_position):
    """
    Checks if a player's hand can form a Chow with a given discarded tile.

    Args:
        hand: List of Tile objects in the player's hand.
        discarded_tile: The Tile object that was discarded.
        discarder_position: Position (0-3) of the player who discarded.
        claimer_position: Position (0-3) of the player attempting to claim.

    Returns:
        True if a Chow can be formed, False otherwise.

    Rules:
        - Only the left neighbor can claim chow: (discarder_position + 1) % 4 == claimer_position
        - Only numeric suits (Dots, Bamboo, Characters) can form chows
        - Must form a sequence of 3 consecutive values
    """
    if not hand or not discarded_tile:
        return False

    # Position check: Only left neighbor can claim
    if (discarder_position + 1) % 4 != claimer_position:
        return False

    # Suit check: Only numeric suits (no winds/dragons)
    if not discarded_tile.is_numeric_suit():
        return False

    # Check for three possible chow patterns
    discarded_value = int(discarded_tile.value)

    # Pattern A: discarded is highest (e.g., discard 7, need 5-6 in hand)
    # Pattern B: discarded is middle (e.g., discard 6, need 5-7 in hand)
    # Pattern C: discarded is lowest (e.g., discard 5, need 6-7 in hand)

    patterns = [
        # Pattern A: [N-2, N-1, N(discarded)]
        ([discarded_value - 2, discarded_value - 1], discarded_value >= 3),
        # Pattern B: [N-1, N(discarded), N+1]
        ([discarded_value - 1, discarded_value + 1], 2 <= discarded_value <= 8),
        # Pattern C: [N(discarded), N+1, N+2]
        ([discarded_value + 1, discarded_value + 2], discarded_value <= 7),
    ]

    for needed_values, valid_range in patterns:
        if not valid_range:
            continue

        # Check if hand has tiles of same suit with needed values
        found_tiles = []
        for needed_val in needed_values:
            for tile in hand:
                if (tile.suit == discarded_tile.suit and
                    tile.is_numeric_suit() and
                    int(tile.value) == needed_val and
                    tile not in found_tiles):
                    found_tiles.append(tile)
                    break

        if len(found_tiles) == 2:
            return True

    return False


def can_form_self_kong(hand):
    """
    Checks if a player's hand contains any Kong (4 identical tiles).
    Returns a list of tiles that could form Kongs.
    """
    if not hand:
        return []

    tile_counts = collections.Counter(hand)
    return [tile for tile, count in tile_counts.items() if count >= 4]


def can_form_chow_with_discard(hand, discarded_tile, discarder_position, claimer_position):
    """
    Checks if a player's hand can form a Chow (sequence of 3 consecutive tiles
    in the same numeric suit) with a given discarded tile.

    Chow rules:
    - Only the left neighbor of the discarder can claim a chow.
    - Only numeric suits (Dots, Bamboo, Characters) can form chows.
    - The sequence must be 3 consecutive values in the same suit.

    Args:
        hand: List of Tile objects in the player's hand.
        discarded_tile: The Tile object that was discarded.
        discarder_position: Seat position (0-3) of the player who discarded.
        claimer_position: Seat position (0-3) of the player claiming the chow.

    Returns:
        True if a Chow can be formed, False otherwise.
    """
    if not hand or not discarded_tile:
        return False

    # Only left neighbor can claim chow
    if (discarder_position + 1) % 4 != claimer_position:
        return False

    # Only numeric suits can form chows
    if not discarded_tile.is_numeric_suit():
        return False

    val = int(discarded_tile.value)
    suit = discarded_tile.suit

    # Check three possible patterns where discarded_tile completes a sequence
    # Pattern A: discard is lowest (val, val+1, val+2) — need val+1 and val+2 in hand
    # Pattern B: discard is middle (val-1, val, val+1) — need val-1 and val+1 in hand
    # Pattern C: discard is highest (val-2, val-1, val) — need val-2 and val-1 in hand

    hand_tiles = set((t.suit, int(t.value)) for t in hand if t.is_numeric_suit())

    # Pattern A: discard is lowest
    if val <= 7 and (suit, val + 1) in hand_tiles and (suit, val + 2) in hand_tiles:
        return True

    # Pattern B: discard is middle
    if val >= 2 and val <= 8 and (suit, val - 1) in hand_tiles and (suit, val + 1) in hand_tiles:
        return True

    # Pattern C: discard is highest
    if val >= 3 and (suit, val - 2) in hand_tiles and (suit, val - 1) in hand_tiles:
        return True

    return False
