"""Global game session management for persistent dealer rotation across hands."""

from .dealer_rotation import DealerRotationState

# Global dealer rotation state that persists across game resets
_global_dealer_rotation = DealerRotationState()

def get_dealer_rotation_state():
    """Get the global dealer rotation state.
    
    Returns:
        DealerRotationState: The global dealer rotation state instance
    """
    return _global_dealer_rotation

def reset_dealer_rotation_state():
    """Reset the global dealer rotation state to initial values.
    
    This should only be called when starting a completely new game session,
    not when just starting a new hand.
    """
    global _global_dealer_rotation
    _global_dealer_rotation = DealerRotationState()

def advance_dealer_rotation(winner_id=None, wall_empty=False):
    """Advance the global dealer rotation based on hand outcome.
    
    Args:
        winner_id: ID of the winning player (None if no winner)
        wall_empty: True if the wall is empty (draw situation)
        
    Returns:
        int: The dealer index for the next hand
    """
    return _global_dealer_rotation.end_hand(winner_id, wall_empty)

def get_current_dealer_info():
    """Get current dealer information.
    
    Returns:
        dict: Dictionary with dealer_index and round_wind
    """
    return _global_dealer_rotation.get_state()

def assign_player_winds_globally(players):
    """Assign winds to players based on global dealer rotation state.
    
    Args:
        players: List of player objects to assign winds to
    """
    _global_dealer_rotation.assign_player_winds(players)

def set_dealer_rotation_state(dealer_index, round_wind):
    """Set the global dealer rotation state to specific values.
    
    This function is primarily for testing purposes to allow setting 
    specific dealer and round states.
    
    Args:
        dealer_index: Index of the dealer (0-3)
        round_wind: Current round wind
    """
    _global_dealer_rotation.set_state(dealer_index, round_wind)
