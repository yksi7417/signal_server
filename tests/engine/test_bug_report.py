"""Tests for BugReport class."""

import json
import os
import tempfile

import pytest

from mahjong_engine.action_log import ActionLog
from mahjong_engine.bug_report import BugReport
from mahjong_engine.tile import TileFactory
from mahjong_engine.constants import SUIT_CHARACTERS, SUIT_WINDS, WIND_EAST


class TestBugReport:
    """Tests for BugReport creation, persistence, and markdown generation."""

    def _make_log_with_actions(self, n=5):
        """Helper to create an ActionLog with some sample actions."""
        log = ActionLog()
        tile = TileFactory.get_tile(SUIT_CHARACTERS, "3")
        log.record("game_init", extra={"wall": ["a"]})
        for i in range(n):
            log.record("draw", player_id=i % 4, tile=tile)
            log.record("discard", player_id=i % 4, tile=tile)
        return log

    def _make_snapshot(self):
        """Helper to create a sample game state snapshot."""
        return {
            "turn_number": 5,
            "current_player_index": 1,
            "wall_size": 80,
            "game_wind": "East",
            "winner_found": False,
            "winning_player_id": None,
            "players": [
                {
                    "player_id": 0,
                    "wind": "East",
                    "hand": ["\U0001F007", "\U0001F008"],
                    "discards": [],
                    "revealed_sets": [],
                },
                {
                    "player_id": 1,
                    "wind": "South",
                    "hand": ["\U0001F010"],
                    "discards": ["\U0001F019"],
                    "revealed_sets": [
                        {"type": "Pung", "tiles": ["\U0001F007"] * 3}
                    ],
                },
            ],
        }

    def test_creation(self):
        log = self._make_log_with_actions()
        report = BugReport("Test bug", log)
        assert report.description == "Test bug"
        assert report.bug_id  # non-empty
        assert report.created_at

    def test_bug_id_is_short(self):
        log = self._make_log_with_actions()
        report = BugReport("desc", log)
        assert len(report.bug_id) == 8

    def test_save_creates_directory_and_files(self):
        log = self._make_log_with_actions()
        snapshot = self._make_snapshot()
        report = BugReport("Something broke", log, snapshot)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = report.save(base_dir=tmpdir)
            assert os.path.isdir(report_dir)
            assert os.path.exists(os.path.join(report_dir, "actions.parquet"))
            assert os.path.exists(os.path.join(report_dir, "report.json"))

    def test_save_report_json_content(self):
        log = self._make_log_with_actions(3)
        snapshot = self._make_snapshot()
        report = BugReport("JSON check", log, snapshot)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = report.save(base_dir=tmpdir)
            with open(os.path.join(report_dir, "report.json"), "r",
                       encoding="utf-8") as f:
                data = json.load(f)
            assert data["bug_id"] == report.bug_id
            assert data["description"] == "JSON check"
            assert data["action_count"] == log.count
            assert "game_state" in data

    def test_save_parquet_loadable(self):
        log = self._make_log_with_actions(2)
        report = BugReport("Parquet check", log)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = report.save(base_dir=tmpdir)
            loaded = ActionLog.load(os.path.join(report_dir, "actions.parquet"))
            assert loaded.count == log.count

    def test_to_github_markdown_contains_description(self):
        log = self._make_log_with_actions()
        report = BugReport("The pung button doesn't work", log)
        md = report.to_github_markdown()
        assert "The pung button doesn't work" in md
        assert "## Bug Report" in md

    def test_to_github_markdown_contains_game_state(self):
        log = self._make_log_with_actions()
        snapshot = self._make_snapshot()
        report = BugReport("State check", log, snapshot)
        md = report.to_github_markdown()
        assert "Turn" in md
        assert "Wall Remaining" in md
        assert "P0" in md
        assert "East" in md

    def test_to_github_markdown_contains_action_table(self):
        log = self._make_log_with_actions(3)
        report = BugReport("Actions check", log)
        md = report.to_github_markdown()
        assert "Action Log" in md
        assert "draw" in md
        assert "discard" in md
        assert "| #" in md  # table header

    def test_to_github_markdown_truncates_long_logs(self):
        log = self._make_log_with_actions(100)
        report = BugReport("Long log", log)
        md = report.to_github_markdown(max_actions=10)
        assert "Showing last 10" in md

    def test_to_github_markdown_shows_all_actions_by_default(self):
        """By default, all actions should be shown (not truncated)."""
        log = self._make_log_with_actions(75)
        report = BugReport("Full log", log)
        md = report.to_github_markdown()  # No max_actions parameter
        # Helper creates 1 game_init + 75*2 (draw+discard pairs) = 151 actions
        assert "Showing all 151 actions" in md
        # Verify first and last actions are present
        assert "| 0 |" in md  # First action
        assert "| 150 |" in md  # Last action (0-indexed)

    def test_to_github_markdown_contains_bug_id(self):
        log = self._make_log_with_actions()
        report = BugReport("ID check", log)
        md = report.to_github_markdown()
        assert report.bug_id in md

    def test_to_dict(self):
        log = self._make_log_with_actions(2)
        snapshot = self._make_snapshot()
        report = BugReport("Dict check", log, snapshot)
        d = report.to_dict()
        assert d["bug_id"] == report.bug_id
        assert d["description"] == "Dict check"
        assert d["action_count"] == log.count
        assert "game_state" in d

    def test_pending_claim_in_markdown(self):
        log = self._make_log_with_actions()
        snapshot = self._make_snapshot()
        snapshot["pending_claim"] = {
            "player_id": 0,
            "claim_type": "PUNG",
            "tile": "\U0001F007",
        }
        report = BugReport("Pending claim bug", log, snapshot)
        md = report.to_github_markdown()
        assert "Pending Claim" in md
        assert "PUNG" in md
