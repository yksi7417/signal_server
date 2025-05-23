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
    # TODO: Implement logic to find all Pungs, Kongs (from hand), Chows
    # This will involve counting tiles, checking sequences.
    # Example: Use collections.Counter for tile counts.
    
    # For now, returns an empty list.
    print("DEV_INFO: find_possible_melds called, but not yet implemented.")
    return []

def _can_form_melds_recursive(tile_counts, num_melds_to_find):
    # tile_counts: collections.Counter of tiles. This will be modified by recursive calls.
    if num_melds_to_find == 0:
        # Base case: if no more melds to find, success if all tiles are used.
        return not any(tile_counts.values())

    # Heuristics to prune branches early
    current_sum_of_tiles = sum(tile_counts.values())
    if current_sum_of_tiles < num_melds_to_find * 3: # Min 3 tiles per meld
        return False
    if current_sum_of_tiles > num_melds_to_find * 4: # Max 4 tiles per meld (Kong)
        return False # Too many tiles for the remaining melds

    # Get an available tile to start forming a meld
    # Iterate over a sorted list of unique tiles present in tile_counts for deterministic behavior
    sorted_unique_tiles = sorted(list(tile_counts.keys()))

    if not sorted_unique_tiles: # No tiles left, but melds still to find
        return False 

    # Pick the first available tile to try forming a meld with.
    # This is a greedy choice; a more exhaustive search might try all possible first melds.
    # However, the outer loop in check_standard_win (trying all pairs) and the recursive nature
    # should explore many combinations.
    for tile in sorted_unique_tiles: 
        if tile_counts[tile] == 0: # Tile already used up by a previous path in the recursion
            continue

        # Try forming a Kong (try Kong first as it uses more tiles)
        if tile_counts[tile] >= 4:
            tile_counts[tile] -= 4
            if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                return True
            tile_counts[tile] += 4 # Backtrack

        # Try forming a Pung
        if tile_counts[tile] >= 3:
            tile_counts[tile] -= 3
            if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                return True
            tile_counts[tile] += 3 # Backtrack
            
        # Try forming a Chow
        if tile.is_numeric_suit() and int(tile.value) <= 7: # Can start a chow (e.g., 123 up to 789)
            t1 = tile
            t2 = Tile(t1.suit, str(int(t1.value) + 1))
            t3 = Tile(t1.suit, str(int(t1.value) + 2))

            if tile_counts[t1] > 0 and tile_counts[t2] > 0 and tile_counts[t3] > 0: # Check t1 again as it might be depleted by Pung/Kong check
                tile_counts[t1] -= 1
                tile_counts[t2] -= 1
                tile_counts[t3] -= 1
                if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                    return True
                tile_counts[t1] += 1 # Backtrack
                tile_counts[t2] += 1 # Backtrack
                tile_counts[t3] += 1 # Backtrack
        
        # If trying this tile as the start of any meld didn't work,
        # it doesn't mean a solution isn't possible with other tiles starting melds.
        # The loop continues. If all tiles are tried and none lead to a solution for the *current*
        # meld being sought, then this recursive call returns False.
    
    return False # No combination of melds found for this path

def check_standard_win(player_hand_tiles, player_revealed_sets):
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

    if num_melds_to_find_in_hand < 0: # More than 4 sets already revealed (e.g. 5 Pungs)
        return False 
    
    # Number of tiles expected in player_hand_tiles for a valid partitioning
    # This is (number of melds to find * 3 tiles/meld) + 2 tiles for the pair.
    # This is a lower bound; Kongs use 4 tiles. The recursive function handles variable meld sizes.
    min_expected_tiles_in_hand = (num_melds_to_find_in_hand * 3) + 2
    max_expected_tiles_in_hand = (num_melds_to_find_in_hand * 4) + 2 # All Kongs

    if len(player_hand_tiles) < min_expected_tiles_in_hand:
        return False
    if len(player_hand_tiles) > max_expected_tiles_in_hand: # Should also be an error or impossible state
        return False
    if len(player_hand_tiles) % 3 == 1 and num_melds_to_find_in_hand > 0: # e.g. 4, 7, 10, 13 tiles for melds + pair
        return False # Cannot form (N*3) tiles from this count. (Unless Kongs are involved)
                     # This check is tricky with Kongs. Let the recursion handle it.

    if num_melds_to_find_in_hand == 0: # All 4 melds are revealed
        # player_hand_tiles must be exactly a pair
        return len(player_hand_tiles) == 2 and player_hand_tiles[0] == player_hand_tiles[1]

    # This case is implicitly handled by len check, but good for clarity
    if not player_hand_tiles and num_melds_to_find_in_hand > 0: 
        return False

    hand_counts = collections.Counter(player_hand_tiles)
    
    # Iterate through all unique tiles in hand to try as a pair
    unique_tiles_in_hand = sorted(list(hand_counts.keys())) # Sort for deterministic behavior

    for tile_for_pair in unique_tiles_in_hand:
        if hand_counts[tile_for_pair] >= 2:
            # Temporarily remove the pair
            hand_counts[tile_for_pair] -= 2
            
            # Check if remaining tiles can form num_melds_to_find_in_hand
            # Pass a copy of tile_counts for recursion, as it will be modified.
            if _can_form_melds_recursive(hand_counts.copy(), num_melds_to_find_in_hand):
                return True # Found a valid win
            
            hand_counts[tile_for_pair] += 2 # Backtrack: put pair back
            
    return False # No winning combination found

def get_hand_score(hand_details, game_context):
    """
    Calculates the score of a winning hand based on its composition and game context.
    This will be based on the Pomax rules (Chinese Classical or Cantonese).
    """
    # TODO: Implement scoring logic.
    print("DEV_INFO: get_hand_score called, but not yet implemented.")
    return 0 # Default score


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
    
    # Count occurrences of the discarded tile's type in hand
    count = 0
    for tile_in_hand in hand:
        if tile_in_hand == discarded_tile: # Tile objects should be comparable by __eq__
            count += 1
    
    return count >= 2 # Needs two matching tiles in hand to form a Pung with the discard
