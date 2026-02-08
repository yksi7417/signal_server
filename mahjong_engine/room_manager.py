"""Room manager for managing multiple game rooms."""

import threading
from datetime import datetime, timedelta

from .room import GameRoom


class RoomManager:
    """Manages multiple game rooms with thread-safe operations.

    Provides CRUD operations for game rooms and stale room cleanup.
    """

    def __init__(self):
        self._rooms = {}
        self._lock = threading.Lock()

    def create_room(self, max_players=4):
        """Create a new game room.

        Args:
            max_players: Maximum players allowed in the room.

        Returns:
            GameRoom: The newly created room.
        """
        room = GameRoom(max_players=max_players)
        with self._lock:
            self._rooms[room.room_id] = room
        return room

    def get_room(self, room_id):
        """Get a room by its ID.

        Args:
            room_id: UUID string of the room.

        Returns:
            GameRoom or None if not found.
        """
        with self._lock:
            return self._rooms.get(room_id)

    def delete_room(self, room_id):
        """Delete a room by its ID.

        Args:
            room_id: UUID string of the room to delete.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            if room_id in self._rooms:
                del self._rooms[room_id]
                return True
            return False

    def list_rooms(self):
        """List all active rooms.

        Returns:
            dict: Mapping of room_id to GameRoom.
        """
        with self._lock:
            return dict(self._rooms)

    @property
    def room_count(self):
        """Number of active rooms."""
        with self._lock:
            return len(self._rooms)

    def cleanup_stale(self, max_age_hours=24):
        """Remove rooms older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours before a room is considered stale.

        Returns:
            int: Number of rooms removed.
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed = 0
        with self._lock:
            stale_ids = []
            for room_id, room in self._rooms.items():
                try:
                    created = datetime.fromisoformat(room.created_at)
                    if created < cutoff:
                        stale_ids.append(room_id)
                except (ValueError, TypeError):
                    stale_ids.append(room_id)
            for room_id in stale_ids:
                del self._rooms[room_id]
                removed += 1
        return removed
