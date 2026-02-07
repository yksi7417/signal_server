import pytest

from mahjong_engine.room import GameRoom


class TestGameRoom:
    """Tests for GameRoom data model."""

    def test_room_creation(self):
        """Room is created with default values."""
        room = GameRoom()
        assert room.room_id is not None
        assert len(room.room_id) == 36  # UUID
        assert room.status == "waiting"
        assert room.max_players == 4
        assert room.players == []
        assert room.created_at is not None

    def test_rooms_have_unique_ids(self):
        """Each room gets a unique ID."""
        r1 = GameRoom()
        r2 = GameRoom()
        assert r1.room_id != r2.room_id

    def test_add_player(self):
        """Adding a player to a room."""
        room = GameRoom()
        room.add_player("player_1")
        assert "player_1" in room.players
        assert len(room.players) == 1

    def test_add_player_full_room(self):
        """Cannot add more players than max_players."""
        room = GameRoom(max_players=2)
        room.add_player("p1")
        room.add_player("p2")
        assert room.add_player("p3") is False
        assert len(room.players) == 2

    def test_add_duplicate_player(self):
        """Cannot add the same player twice."""
        room = GameRoom()
        room.add_player("p1")
        assert room.add_player("p1") is False
        assert len(room.players) == 1

    def test_remove_player(self):
        """Removing a player from a room."""
        room = GameRoom()
        room.add_player("p1")
        room.add_player("p2")
        room.remove_player("p1")
        assert "p1" not in room.players
        assert len(room.players) == 1

    def test_remove_nonexistent_player(self):
        """Removing a player not in the room returns False."""
        room = GameRoom()
        assert room.remove_player("p1") is False

    def test_status_transitions(self):
        """Room status can be changed."""
        room = GameRoom()
        assert room.status == "waiting"
        room.status = "playing"
        assert room.status == "playing"
        room.status = "finished"
        assert room.status == "finished"

    def test_is_full(self):
        """is_full returns True when room reaches max_players."""
        room = GameRoom(max_players=2)
        assert room.is_full is False
        room.add_player("p1")
        assert room.is_full is False
        room.add_player("p2")
        assert room.is_full is True

    def test_to_dict(self):
        """Room serializes to dictionary."""
        room = GameRoom()
        room.add_player("p1")
        data = room.to_dict()
        assert data["room_id"] == room.room_id
        assert data["status"] == "waiting"
        assert data["players"] == ["p1"]
        assert data["max_players"] == 4
        assert "created_at" in data

    def test_custom_max_players(self):
        """Room can be created with custom max_players."""
        room = GameRoom(max_players=2)
        assert room.max_players == 2
