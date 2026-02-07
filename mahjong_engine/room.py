"""Game room data model for multiplayer room management."""

import uuid
from datetime import datetime


class GameRoom:
    """Represents a game room that players can join to play mahjong.

    Attributes:
        room_id: Unique identifier for the room.
        players: List of player identifiers in the room.
        status: Room status ('waiting', 'playing', 'finished').
        max_players: Maximum number of players allowed.
        created_at: ISO 8601 timestamp of room creation.
    """

    def __init__(self, max_players=4):
        self.room_id = str(uuid.uuid4())
        self.players = []
        self.status = "waiting"
        self.max_players = max_players
        self.created_at = datetime.utcnow().isoformat()

    def add_player(self, player_id):
        """Add a player to the room.

        Args:
            player_id: Identifier for the player to add.

        Returns:
            True if player was added, False if room is full or player already in room.
        """
        if player_id in self.players:
            return False
        if len(self.players) >= self.max_players:
            return False
        self.players.append(player_id)
        return True

    def remove_player(self, player_id):
        """Remove a player from the room.

        Args:
            player_id: Identifier for the player to remove.

        Returns:
            True if player was removed, False if player was not in room.
        """
        if player_id not in self.players:
            return False
        self.players.remove(player_id)
        return True

    @property
    def is_full(self):
        """Check if room has reached max_players."""
        return len(self.players) >= self.max_players

    def to_dict(self):
        """Serialize room to dictionary.

        Returns:
            dict: Room data including room_id, players, status, max_players, created_at.
        """
        return {
            "room_id": self.room_id,
            "players": list(self.players),
            "status": self.status,
            "max_players": self.max_players,
            "created_at": self.created_at,
        }
