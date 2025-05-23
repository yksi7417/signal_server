from .player_agent import PlayerAgent # Already there
from .tile import Tile # Should be imported if used for type hints in hand etc.
from .melds import Meld # Add this import

class Player:
    def __init__(self, player_id, agent=None):
        self.player_id = player_id
        self.hand = []  # List of Tile objects
        self.revealed_sets = [] # List of Meld objects
        self.discards = [] # List of Tile objects
        self.score = 0
        self.agent = agent
        self.wind = None # Player's seat wind (East, South, etc.) - to be set at round start
        # print(f"Player {self.player_id} initialized with agent {self.agent}, wind {self.wind}")


    def __repr__(self):
        agent_class_name = self.agent.__class__.__name__ if self.agent else 'None'
        return f"Player(player_id={self.player_id}, agent={agent_class_name}, wind={self.wind}, revealed_sets={len(self.revealed_sets)})"

    def set_agent(self, agent): # Keep this method for flexibility
        self.agent = agent

    def add_revealed_set(self, meld_obj):
        if not isinstance(meld_obj, Meld): # Assuming Meld is the base class
           raise ValueError("Can only add Meld objects to revealed_sets")
        self.revealed_sets.append(meld_obj)
