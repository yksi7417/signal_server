import pytest

from mahjong_engine.room_manager import RoomManager


@pytest.fixture
def manager():
    """Fresh RoomManager for each test."""
    return RoomManager()


class TestRoomManager:
    """Tests for RoomManager class."""

    def test_create_room(self, manager):
        """Creating a room returns a GameRoom."""
        room = manager.create_room()
        assert room is not None
        assert room.room_id in manager.list_rooms()

    def test_get_room(self, manager):
        """get_room returns the room by ID."""
        room = manager.create_room()
        fetched = manager.get_room(room.room_id)
        assert fetched is room

    def test_get_room_nonexistent(self, manager):
        """get_room returns None for unknown IDs."""
        assert manager.get_room("nonexistent") is None

    def test_delete_room(self, manager):
        """delete_room removes the room."""
        room = manager.create_room()
        assert manager.delete_room(room.room_id) is True
        assert manager.get_room(room.room_id) is None

    def test_delete_nonexistent_room(self, manager):
        """delete_room returns False for unknown IDs."""
        assert manager.delete_room("nonexistent") is False

    def test_list_rooms(self, manager):
        """list_rooms returns dict of all rooms."""
        r1 = manager.create_room()
        r2 = manager.create_room()
        rooms = manager.list_rooms()
        assert r1.room_id in rooms
        assert r2.room_id in rooms
        assert len(rooms) == 2

    def test_list_rooms_empty(self, manager):
        """list_rooms returns empty dict when no rooms exist."""
        assert manager.list_rooms() == {}

    def test_room_count(self, manager):
        """room_count tracks number of active rooms."""
        assert manager.room_count == 0
        manager.create_room()
        assert manager.room_count == 1
        room2 = manager.create_room()
        assert manager.room_count == 2
        manager.delete_room(room2.room_id)
        assert manager.room_count == 1

    def test_cleanup_stale(self, manager):
        """cleanup_stale removes rooms older than max_age_hours."""
        room = manager.create_room()
        # Artificially age the room
        room.created_at = "2020-01-01T00:00:00"
        removed = manager.cleanup_stale(max_age_hours=1)
        assert removed == 1
        assert manager.room_count == 0

    def test_cleanup_stale_keeps_recent(self, manager):
        """cleanup_stale keeps recently created rooms."""
        manager.create_room()
        removed = manager.cleanup_stale(max_age_hours=24)
        assert removed == 0
        assert manager.room_count == 1
