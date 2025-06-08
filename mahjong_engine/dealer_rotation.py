from .constants import WIND_EAST, WINDS_ALL


class DealerRotationState:
    """Separate class to track dealer rotation and round progression independently from game hands."""
    
    def __init__(self, num_players=4):
        """Initialize dealer rotation state.
        
        Args:
            num_players: Number of players in the game (default 4)
        """
        self.num_players = num_players
        self.dealer_index = 0  # Start with East dealer (player 0)
        self.round_wind = WIND_EAST  # Current round wind
    
    def assign_player_winds(self, players):
        """Assign winds to players based on current dealer position.
        
        Args:
            players: List of player objects to assign winds to
        """
        for i, player in enumerate(players):
            # Calculate wind index relative to dealer
            wind_index = (i - self.dealer_index) % len(WINDS_ALL)
            player.wind = WINDS_ALL[wind_index]
    
    def advance_dealer(self):
        """Advance to next dealer following traditional Mahjong rotation."""
        self.dealer_index = (self.dealer_index + 1) % self.num_players
        
        # When we complete a full dealer rotation (back to player 0 as dealer)
        if self.dealer_index == 0:
            self.advance_round()
    
    def advance_round(self):
        """Advance to next round wind."""
        current_round_index = WINDS_ALL.index(self.round_wind)
        next_round_index = (current_round_index + 1) % len(WINDS_ALL)
        self.round_wind = WINDS_ALL[next_round_index]
    
    def should_dealer_continue(self, winner_id=None, wall_empty=False):
        """Check if dealer should continue based on Mahjong rules.
        
        Args:
            winner_id: ID of the winning player (None if no winner)
            wall_empty: True if the wall is empty (draw situation)
            
        Returns:
            bool: True if dealer should continue, False if dealer should advance
        """
        # Dealer continues if:
        # 1. Current hand wins (winner is current dealer)
        # 2. Wall is empty with no winner (draw situation)
        if winner_id == self.dealer_index or (wall_empty and winner_id is None):
            return True
        return False
    
    def end_hand(self, winner_id=None, wall_empty=False):
        """End current hand and handle dealer rotation.
        
        Args:
            winner_id: ID of the winning player (None if no winner)
            wall_empty: True if the wall is empty (draw situation)
            
        Returns:
            int: The dealer index for the next hand
        """
        if not self.should_dealer_continue(winner_id, wall_empty):
            self.advance_dealer()
        
        # Return the dealer index for the next hand
        return self.dealer_index
    
    def get_state(self):
        """Get current dealer rotation state as a dictionary.
        
        Returns:
            dict: Current state with dealer_index and round_wind
        """
        return {
            "dealer_index": self.dealer_index,
            "round_wind": self.round_wind
        }
    
    def set_state(self, dealer_index, round_wind):
        """Set dealer rotation state to specific values.
        
        Args:
            dealer_index: Index of the dealer (0-3)
            round_wind: Current round wind
        """
        self.dealer_index = dealer_index
        self.round_wind = round_wind
