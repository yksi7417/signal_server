"""Tests for the SQLite database layer."""
import asyncio
import os
import tempfile

import pytest

from mahjong_engine.database import Database, sanitize_display_name


@pytest.fixture
def db():
    """Create an in-memory database for testing."""
    database = Database(db_path=":memory:")
    asyncio.get_event_loop().run_until_complete(database.initialize())
    yield database
    asyncio.get_event_loop().run_until_complete(database.close())


def _run(coro):
    """Helper to run async coroutines in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestUpsertUser:
    def test_create_new_user(self, db):
        user = _run(db.upsert_user("apple_001", "Alice"))
        assert user["apple_sub"] == "apple_001"
        assert user["display_name"] == "Alice"
        assert user["id"] is not None

    def test_create_user_with_email(self, db):
        user = _run(db.upsert_user("apple_002", "Bob", email="bob@example.com"))
        assert user["email"] == "bob@example.com"

    def test_upsert_idempotent(self, db):
        user1 = _run(db.upsert_user("apple_003", "Charlie"))
        user2 = _run(db.upsert_user("apple_003", "Charlie Updated"))
        assert user1["id"] == user2["id"]
        assert user2["display_name"] == "Charlie Updated"

    def test_upsert_preserves_email_if_not_provided(self, db):
        _run(db.upsert_user("apple_004", "Dana", email="dana@example.com"))
        user = _run(db.upsert_user("apple_004", "Dana"))
        assert user["email"] == "dana@example.com"

    def test_upsert_creates_stats_row(self, db):
        user = _run(db.upsert_user("apple_005", "Eve"))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats is not None
        assert stats["games_played"] == 0
        assert stats["games_won"] == 0


class TestGetUser:
    def test_get_user_by_id(self, db):
        user = _run(db.upsert_user("apple_010", "Frank"))
        fetched = _run(db.get_user_by_id(user["id"]))
        assert fetched["display_name"] == "Frank"

    def test_get_nonexistent_user(self, db):
        fetched = _run(db.get_user_by_id(9999))
        assert fetched is None


class TestRecordMatch:
    def test_record_win(self, db):
        user = _run(db.upsert_user("apple_020", "Gina"))
        _run(db.record_match(user["id"], "sess_1", "win", faan=5))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["games_played"] == 1
        assert stats["games_won"] == 1
        assert stats["highest_faan"] == 5
        assert stats["total_faan"] == 5

    def test_record_loss(self, db):
        user = _run(db.upsert_user("apple_021", "Hank"))
        _run(db.record_match(user["id"], "sess_2", "loss"))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["games_played"] == 1
        assert stats["games_lost"] == 1

    def test_record_draw(self, db):
        user = _run(db.upsert_user("apple_022", "Iris"))
        _run(db.record_match(user["id"], "sess_3", "draw"))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["games_played"] == 1
        assert stats["games_drawn"] == 1

    def test_highest_faan_tracks_max(self, db):
        user = _run(db.upsert_user("apple_023", "Jack"))
        _run(db.record_match(user["id"], "sess_a", "win", faan=3))
        _run(db.record_match(user["id"], "sess_b", "win", faan=7))
        _run(db.record_match(user["id"], "sess_c", "win", faan=5))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["highest_faan"] == 7
        assert stats["total_faan"] == 15

    def test_multiple_results_aggregate(self, db):
        user = _run(db.upsert_user("apple_024", "Kate"))
        _run(db.record_match(user["id"], "s1", "win", faan=4))
        _run(db.record_match(user["id"], "s2", "loss"))
        _run(db.record_match(user["id"], "s3", "win", faan=6))
        _run(db.record_match(user["id"], "s4", "draw"))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["games_played"] == 4
        assert stats["games_won"] == 2
        assert stats["games_lost"] == 1
        assert stats["games_drawn"] == 1


class TestMatchHistory:
    def test_get_match_history(self, db):
        user = _run(db.upsert_user("apple_030", "Leo"))
        _run(db.record_match(user["id"], "s1", "win", faan=3))
        _run(db.record_match(user["id"], "s2", "loss"))
        history = _run(db.get_match_history(user["id"]))
        assert len(history) == 2
        # Both results present
        results = {h["result"] for h in history}
        assert results == {"win", "loss"}

    def test_match_history_limit(self, db):
        user = _run(db.upsert_user("apple_031", "Mia"))
        for i in range(5):
            _run(db.record_match(user["id"], f"s{i}", "win", faan=i))
        history = _run(db.get_match_history(user["id"], limit=3))
        assert len(history) == 3


class TestLeaderboard:
    def test_leaderboard_ordering(self, db):
        u1 = _run(db.upsert_user("apple_040", "Player1"))
        u2 = _run(db.upsert_user("apple_041", "Player2"))
        u3 = _run(db.upsert_user("apple_042", "Player3"))

        # Player2 has most wins
        _run(db.record_match(u1["id"], "s", "win", faan=3))
        _run(db.record_match(u2["id"], "s", "win", faan=5))
        _run(db.record_match(u2["id"], "s", "win", faan=7))
        _run(db.record_match(u3["id"], "s", "loss"))

        board = _run(db.get_leaderboard())
        # All 3 have games_played > 0, so all are listed
        assert len(board) == 3
        # Player2 with 2 wins should be first
        assert board[0]["display_name"] == "Player2"
        assert board[0]["games_won"] == 2

    def test_empty_leaderboard(self, db):
        board = _run(db.get_leaderboard())
        assert board == []

    def test_leaderboard_limit(self, db):
        for i in range(15):
            u = _run(db.upsert_user(f"apple_05{i}", f"Player{i}"))
            _run(db.record_match(u["id"], "s", "win", faan=i))

        board = _run(db.get_leaderboard(limit=10))
        assert len(board) == 10


class TestWALMode:
    def test_wal_mode_enabled_on_file_db(self):
        """WAL mode should be enabled after initialize() on a file-based DB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_wal.db")
            database = Database(db_path=db_path)
            _run(database.initialize())
            try:
                result = _run(database.db.execute("PRAGMA journal_mode"))
                row = _run(result.fetchone())
                assert row[0] == "wal"
            finally:
                _run(database.close())

    def test_foreign_keys_enabled(self, db):
        result = _run(db.db.execute("PRAGMA foreign_keys"))
        row = _run(result.fetchone())
        assert row[0] == 1


class TestBackup:
    def test_backup_creates_valid_file(self):
        """backup() should create a valid SQLite file in the backups/ dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            database = Database(db_path=db_path)
            _run(database.initialize())
            _run(database.upsert_user("sub_backup", "BackupUser"))
            backup_path = _run(database.backup())

            assert backup_path is not None
            assert os.path.exists(backup_path)
            assert "backups" in backup_path

            # Verify backup is a valid SQLite DB with data
            backup_db = Database(db_path=backup_path)
            _run(backup_db.initialize())
            board = _run(backup_db.get_leaderboard())
            _run(backup_db.close())
            # User exists but has no games, so leaderboard is empty — just confirm no crash
            assert isinstance(board, list)

            _run(database.close())

    def test_backup_returns_none_for_memory_db(self, db):
        result = _run(db.backup())
        assert result is None

    def test_backup_prunes_old_files(self):
        """Only MAX_BACKUPS files should be kept."""
        import time as time_mod

        from mahjong_engine.database import MAX_BACKUPS

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            database = Database(db_path=db_path)
            _run(database.initialize())

            for _ in range(MAX_BACKUPS + 3):
                _run(database.backup())
                time_mod.sleep(0.01)  # ensure unique timestamps

            backup_dir = os.path.join(tmpdir, "backups")
            backups = [f for f in os.listdir(backup_dir) if f.endswith(".db")]
            assert len(backups) <= MAX_BACKUPS

            _run(database.close())


class TestDisplayNameValidation:
    def test_sanitize_strips_whitespace(self):
        assert sanitize_display_name("  Alice  ") == "Alice"

    def test_sanitize_truncates_long_name(self):
        long_name = "A" * 100
        result = sanitize_display_name(long_name)
        assert len(result) == 50

    def test_sanitize_rejects_empty(self):
        with pytest.raises(ValueError, match="must not be empty"):
            sanitize_display_name("")

    def test_sanitize_rejects_whitespace_only(self):
        with pytest.raises(ValueError, match="must not be empty"):
            sanitize_display_name("   ")

    def test_sanitize_rejects_none(self):
        with pytest.raises(ValueError, match="must not be empty"):
            sanitize_display_name(None)

    def test_upsert_user_truncates_name(self, db):
        long_name = "B" * 100
        user = _run(db.upsert_user("apple_trunc", long_name))
        assert len(user["display_name"]) == 50

    def test_upsert_user_strips_whitespace(self, db):
        user = _run(db.upsert_user("apple_strip", "  Padded  "))
        assert user["display_name"] == "Padded"

    def test_upsert_user_rejects_empty_name(self, db):
        with pytest.raises(ValueError):
            _run(db.upsert_user("apple_empty", ""))


class TestRecordMatchValidation:
    def test_rejects_invalid_result(self, db):
        user = _run(db.upsert_user("apple_val", "Validator"))
        with pytest.raises(ValueError, match="Invalid result"):
            _run(db.record_match(user["id"], "s1", "invalid_result"))

    def test_rejects_empty_result(self, db):
        user = _run(db.upsert_user("apple_val2", "Validator2"))
        with pytest.raises(ValueError, match="Invalid result"):
            _run(db.record_match(user["id"], "s1", ""))

    def test_accepts_all_valid_results(self, db):
        user = _run(db.upsert_user("apple_val3", "Validator3"))
        for result in ("win", "loss", "draw"):
            _run(db.record_match(user["id"], "s", result))
        stats = _run(db.get_user_stats(user["id"]))
        assert stats["games_played"] == 3
