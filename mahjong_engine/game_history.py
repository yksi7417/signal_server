import json
import threading
from datetime import datetime


class GameHistory:
    """Records game actions with timestamps for replay and analysis.

    Thread-safe implementation using a lock for concurrent access.
    """

    def __init__(self):
        self._actions = []
        self._lock = threading.Lock()

    def record_action(self, action_type, player_id=None, tile=None):
        """Record a game action.

        Args:
            action_type: Type of action (e.g., 'draw', 'discard', 'pung', 'chow', 'kong', 'win').
            player_id: ID of the player performing the action (None for system events).
            tile: Unicode representation of the tile involved (None if not applicable).
        """
        entry = {
            "action": action_type,
            "player_id": player_id,
            "tile": tile,
            "timestamp": datetime.utcnow().isoformat(),
        }
        with self._lock:
            self._actions.append(entry)

    def get_history(self):
        """Return a copy of the action history list.

        Returns:
            List of action dictionaries.
        """
        with self._lock:
            return list(self._actions)

    def to_json(self):
        """Serialize history to a JSON string.

        Returns:
            JSON string representation of the action history.
        """
        with self._lock:
            return json.dumps(self._actions)

    def clear(self):
        """Remove all recorded actions."""
        with self._lock:
            self._actions.clear()

    @property
    def action_count(self):
        """Return the number of recorded actions."""
        with self._lock:
            return len(self._actions)
