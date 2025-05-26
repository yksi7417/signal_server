from .player_agent import PlayerAgent
from .tile import Tile
from .melds import Meld
from typing import Optional


class Player:
    def __init__(self, player_id: int, agent: Optional[PlayerAgent] = None):
        self.player_id = player_id
        self.hand: list[Tile] = []
        self.revealed_sets: list[Meld] = []
        self.discards: list[Tile] = []
        self.score = 0
        self.agent = agent
        self.wind: Optional[str] = None

    def __repr__(self):
        if self.agent:
            agent_class_name = self.agent.__class__.__name__
        else:
            agent_class_name = 'None'
        return f"Player(player_id={self.player_id}, agent={agent_class_name}, wind={self.wind}, revealed_sets={len(self.revealed_sets)})"

    def set_agent(self, agent):
        self.agent = agent

    def add_revealed_set(self, meld_obj):
        if not isinstance(meld_obj, Meld):
            raise ValueError("Can only add Meld objects to revealed_sets")
        self.revealed_sets.append(meld_obj)
