import json
import threading

import pytest

from mahjong_engine.game_history import GameHistory


class TestGameHistory:
    """Tests for GameHistory class."""

    def test_record_action(self):
        """Recording an action adds it to history."""
        history = GameHistory()
        history.record_action("draw", player_id=0, tile="🀇")

        actions = history.get_history()
        assert len(actions) == 1
        assert actions[0]["action"] == "draw"
        assert actions[0]["player_id"] == 0
        assert actions[0]["tile"] == "🀇"
        assert "timestamp" in actions[0]

    def test_record_multiple_actions(self):
        """Multiple actions are recorded in order."""
        history = GameHistory()
        history.record_action("draw", player_id=0, tile="🀇")
        history.record_action("discard", player_id=0, tile="🀈")
        history.record_action("pung", player_id=1, tile="🀈")

        actions = history.get_history()
        assert len(actions) == 3
        assert actions[0]["action"] == "draw"
        assert actions[1]["action"] == "discard"
        assert actions[2]["action"] == "pung"

    def test_record_action_without_tile(self):
        """Actions can be recorded without a tile (e.g., system events)."""
        history = GameHistory()
        history.record_action("game_start", player_id=None)

        actions = history.get_history()
        assert len(actions) == 1
        assert actions[0]["tile"] is None

    def test_to_json(self):
        """History serializes to valid JSON string."""
        history = GameHistory()
        history.record_action("draw", player_id=0, tile="🀇")
        history.record_action("discard", player_id=0, tile="🀈")

        json_str = history.to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["action"] == "draw"

    def test_to_json_empty(self):
        """Empty history serializes to empty JSON array."""
        history = GameHistory()
        json_str = history.to_json()
        assert json.loads(json_str) == []

    def test_clear(self):
        """Clear removes all recorded actions."""
        history = GameHistory()
        history.record_action("draw", player_id=0, tile="🀇")
        history.record_action("discard", player_id=0, tile="🀈")

        history.clear()
        assert history.get_history() == []

    def test_get_history_returns_copy(self):
        """get_history returns a copy, not a reference to internal list."""
        history = GameHistory()
        history.record_action("draw", player_id=0, tile="🀇")

        actions = history.get_history()
        actions.clear()  # Modify returned list
        assert len(history.get_history()) == 1  # Internal list unchanged

    def test_thread_safety(self):
        """Multiple threads can record actions without corruption."""
        history = GameHistory()

        def record_actions(thread_id):
            for i in range(50):
                history.record_action("draw", player_id=thread_id, tile=f"tile_{i}")

        threads = [threading.Thread(target=record_actions, args=(tid,)) for tid in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        actions = history.get_history()
        assert len(actions) == 200  # 4 threads x 50 actions

    def test_action_count(self):
        """action_count returns the number of recorded actions."""
        history = GameHistory()
        assert history.action_count == 0

        history.record_action("draw", player_id=0, tile="🀇")
        history.record_action("discard", player_id=0, tile="🀈")
        assert history.action_count == 2
