from .tile import Tile
from .melds import Meld, MeldType, Pung, Kong, Chow, Pair # Assuming Pung, Kong etc. are defined in melds.py
from .constants import SUITS_NUMERIC, SUIT_WINDS, SUIT_DRAGONS # Add other constants as needed
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

def check_standard_win(hand, revealed_sets, last_tile=None, game_context=None):
    """
    Checks if a combination of hand tiles and revealed sets forms a standard winning hand (4 melds + 1 pair).
    Args:
        hand: List of Tile objects in the concealed part of the hand.
        revealed_sets: List of Meld objects already declared.
        last_tile: The tile that completes the hand (either drawn or claimed for win).
        game_context: Optional, for context like prevailing wind, self-draw, etc. for scoring.
    Returns:
        True if it's a winning hand, False otherwise.
        (Later, could return details of the win/score).
    """
    # TODO: Implement logic. This is complex.
    # 1. Combine last_tile with hand.
    # 2. Try to form 4 melds and 1 pair from the (hand + revealed_sets).
    #    This usually involves recursive partitioning of the hand.
    # 3. Consider special hands (e.g., Thirteen Orphans) separately.

    # For now, returns False.
    print("DEV_INFO: check_standard_win called, but not yet implemented.")
    if last_tile:
        current_hand = sorted(hand + [last_tile])
    else:
        current_hand = sorted(hand)
    
    # Basic check: total tiles (concealed + revealed) must be 14 for a standard win
    # (3*num_melds + 2*num_pairs)
    # For 4 melds and 1 pair: 4*3 + 2 = 14. (Kong is 4 tiles, but often counts as a 3-tile meld for this check)
    # The actual tiles in revealed_sets: sum(len(m.raw_tiles) for m in revealed_sets)
    # Number of tiles in hand: len(current_hand)
    # Total tiles = sum(len(m.raw_tiles) for m in revealed_sets) + len(current_hand)
    # This needs to be handled carefully based on how Kongs are treated.
    # A simpler count is number of sets: len(revealed_sets) + (number of melds in hand) should be 4, plus one pair.

    print(f"DEV_INFO: Checking win with {len(current_hand)} concealed tiles and {len(revealed_sets)} revealed sets.")
    return False

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
