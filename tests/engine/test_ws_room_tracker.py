import pytest

from mahjong_engine.ws_room_tracker import WebSocketRoomTracker


@pytest.fixture
def tracker():
    return WebSocketRoomTracker()


class TestWebSocketRoomTracker:
    """Tests for WebSocket room-based peer tracking."""

    def test_register_client(self, tracker):
        """Registering a client associates them with a room."""
        tracker.register("client_1", "room_A")
        assert tracker.get_room("client_1") == "room_A"

    def test_register_client_no_room(self, tracker):
        """Clients without a room get assigned to the lobby."""
        tracker.register("client_1")
        assert tracker.get_room("client_1") == "lobby"

    def test_unregister_client(self, tracker):
        """Unregistering removes the client."""
        tracker.register("client_1", "room_A")
        tracker.unregister("client_1")
        assert tracker.get_room("client_1") is None

    def test_get_room_peers(self, tracker):
        """get_room_peers returns only clients in the same room."""
        tracker.register("c1", "room_A")
        tracker.register("c2", "room_A")
        tracker.register("c3", "room_B")

        peers = tracker.get_room_peers("c1")
        assert "c2" in peers
        assert "c1" not in peers  # Excludes self
        assert "c3" not in peers  # Different room

    def test_get_room_peers_empty(self, tracker):
        """get_room_peers returns empty list when alone in room."""
        tracker.register("c1", "room_A")
        assert tracker.get_room_peers("c1") == []

    def test_get_room_peers_unknown_client(self, tracker):
        """get_room_peers returns empty list for unknown clients."""
        assert tracker.get_room_peers("unknown") == []

    def test_clients_in_room(self, tracker):
        """clients_in_room returns all clients in a given room."""
        tracker.register("c1", "room_A")
        tracker.register("c2", "room_A")
        tracker.register("c3", "room_B")

        room_a_clients = tracker.clients_in_room("room_A")
        assert set(room_a_clients) == {"c1", "c2"}

    def test_switch_room(self, tracker):
        """Client can switch rooms."""
        tracker.register("c1", "room_A")
        tracker.register("c1", "room_B")
        assert tracker.get_room("c1") == "room_B"

    def test_client_count(self, tracker):
        """client_count returns total connected clients."""
        assert tracker.client_count == 0
        tracker.register("c1", "room_A")
        tracker.register("c2", "room_B")
        assert tracker.client_count == 2
        tracker.unregister("c1")
        assert tracker.client_count == 1
