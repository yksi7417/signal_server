"""WebSocket room-based peer tracking for room-scoped messaging."""

import threading


class WebSocketRoomTracker:
    """Tracks which WebSocket clients are in which rooms.

    Provides room-scoped peer lookup for broadcasting messages
    only to clients in the same room.
    """

    def __init__(self):
        self._client_rooms = {}  # client_id -> room_id
        self._lock = threading.Lock()

    def register(self, client_id, room_id="lobby"):
        """Register a client in a room.

        Args:
            client_id: Unique identifier for the client.
            room_id: Room to assign the client to. Defaults to 'lobby'.
        """
        with self._lock:
            self._client_rooms[client_id] = room_id

    def unregister(self, client_id):
        """Remove a client from tracking.

        Args:
            client_id: Client to remove.
        """
        with self._lock:
            self._client_rooms.pop(client_id, None)

    def get_room(self, client_id):
        """Get the room a client is in.

        Args:
            client_id: Client to look up.

        Returns:
            Room ID string, or None if client is not registered.
        """
        with self._lock:
            return self._client_rooms.get(client_id)

    def get_room_peers(self, client_id):
        """Get other clients in the same room as client_id.

        Args:
            client_id: Client whose room peers to find.

        Returns:
            List of client_ids in the same room (excluding the given client).
        """
        with self._lock:
            room_id = self._client_rooms.get(client_id)
            if room_id is None:
                return []
            return [
                cid for cid, rid in self._client_rooms.items()
                if rid == room_id and cid != client_id
            ]

    def clients_in_room(self, room_id):
        """Get all clients in a specific room.

        Args:
            room_id: Room to query.

        Returns:
            List of client_ids in the room.
        """
        with self._lock:
            return [cid for cid, rid in self._client_rooms.items() if rid == room_id]

    @property
    def client_count(self):
        """Total number of tracked clients."""
        with self._lock:
            return len(self._client_rooms)
