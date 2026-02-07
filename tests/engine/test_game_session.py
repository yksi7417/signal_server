import time

import pytest

from mahjong_engine.game_session import GameSession, reset_dealer_rotation_state


@pytest.fixture
def session():
    """Fixture to provide a fresh GameSession instance."""
    reset_dealer_rotation_state()
    return GameSession()


class TestGameSession:
    """Tests for GameSession class."""

    def test_session_has_unique_id(self, session):
        """Each session gets a unique UUID."""
        assert session.session_id is not None
        assert len(session.session_id) == 36  # UUID format

    def test_sessions_have_different_ids(self):
        """Two sessions have different IDs."""
        reset_dealer_rotation_state()
        s1 = GameSession()
        reset_dealer_rotation_state()
        s2 = GameSession()
        assert s1.session_id != s2.session_id

    def test_session_has_timestamps(self, session):
        """Session tracks created_at and last_activity."""
        assert session.created_at is not None
        assert session.last_activity is not None
        assert session.created_at <= session.last_activity

    def test_session_has_game_state(self, session):
        """Session wraps a GameState instance."""
        assert session.game_state is not None
        assert len(session.game_state.players) == 4

    def test_update_activity(self, session):
        """update_activity() refreshes the last_activity timestamp."""
        original = session.last_activity
        time.sleep(0.01)
        session.update_activity()
        assert session.last_activity > original

    def test_to_dict(self, session):
        """to_dict() serializes session to dictionary."""
        data = session.to_dict()
        assert "session_id" in data
        assert "created_at" in data
        assert "last_activity" in data
        assert data["session_id"] == session.session_id

    def test_to_dict_roundtrip(self, session):
        """from_dict() can reconstruct a session from to_dict() output."""
        data = session.to_dict()
        restored = GameSession.from_dict(data)
        assert restored.session_id == session.session_id
        assert restored.created_at == session.created_at
