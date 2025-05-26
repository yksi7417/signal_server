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
                if _can_form_melds_recursive(tile_counts, num_melds_to_find - 1):
                    return True
                tile_counts[t1] += 1
                tile_counts[t2] += 1
                tile_counts[t3] += 1
        
       
       
       
       
    
    return False

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
       
        return len(player_hand_tiles) == 2 and player_hand_tiles[0] == player_hand_tiles[1]

   
    if not player_hand_tiles and num_melds_to_find_in_hand > 0: 
        return False

    hand_counts = collections.Counter(player_hand_tiles)
    
   
    unique_tiles_in_hand = sorted(list(hand_counts.keys()))

    for tile_for_pair in unique_tiles_in_hand:
        if hand_counts[tile_for_pair] >= 2:
           
            hand_counts[tile_for_pair] -= 2
            
           
           
            if _can_form_melds_recursive(hand_counts.copy(), num_melds_to_find_in_hand):
                return True
            
            hand_counts[tile_for_pair] += 2
            
    return False

def get_hand_score(hand_details, game_context):
    """
    Calculates the score of a winning hand based on its composition and game context.
    This will be based on the Pomax rules (Chinese Classical or Cantonese).
    """
   
    print("DEV_INFO: get_hand_score called, but not yet implemented.")
    return 0


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
