"""SQLite database layer for user identity and stats persistence.

Uses aiosqlite for async access, compatible with aiohttp's event loop.
Database file is stored in data/mahjong.db (volume-mounted on fly.dev).
"""
import os

import aiosqlite

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mahjong.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apple_sub TEXT UNIQUE,
    display_name TEXT NOT NULL,
    email TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_login TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    games_played INTEGER DEFAULT 0,
    games_won INTEGER DEFAULT 0,
    games_lost INTEGER DEFAULT 0,
    games_drawn INTEGER DEFAULT 0,
    highest_faan INTEGER DEFAULT 0,
    total_faan INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS match_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    session_id TEXT,
    result TEXT NOT NULL,
    faan_scored INTEGER DEFAULT 0,
    played_at TEXT DEFAULT (datetime('now'))
);
"""


class Database:
    """Async SQLite database for user accounts, stats, and match history."""

    def __init__(self, db_path=None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db = None

    async def initialize(self):
        """Create data directory, connect to DB, and create tables."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        await self.db.executescript(SCHEMA_SQL)
        await self.db.commit()

    async def close(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
            self.db = None

    async def upsert_user(self, apple_sub, display_name, email=None):
        """Create or update a user by Apple subject ID. Returns user dict."""
        await self.db.execute(
            """INSERT INTO users (apple_sub, display_name, email)
               VALUES (?, ?, ?)
               ON CONFLICT(apple_sub) DO UPDATE SET
                   display_name = excluded.display_name,
                   email = COALESCE(excluded.email, users.email),
                   last_login = datetime('now')""",
            (apple_sub, display_name, email),
        )
        await self.db.commit()

        async with self.db.execute(
            "SELECT * FROM users WHERE apple_sub = ?", (apple_sub,)
        ) as cursor:
            row = await cursor.fetchone()
            user = dict(row)

        # Ensure user_stats row exists
        await self.db.execute(
            "INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user["id"],)
        )
        await self.db.commit()
        return user

    async def get_user_by_id(self, user_id):
        """Get user by internal ID. Returns dict or None."""
        async with self.db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def record_match(self, user_id, session_id, result, faan=0):
        """Record a match result and update aggregate stats.

        Args:
            user_id: Internal user ID.
            session_id: Game session identifier.
            result: One of 'win', 'loss', 'draw'.
            faan: Faan scored (for wins).
        """
        await self.db.execute(
            """INSERT INTO match_history (user_id, session_id, result, faan_scored)
               VALUES (?, ?, ?, ?)""",
            (user_id, session_id, result, faan),
        )

        # Update aggregate stats
        stat_col = {"win": "games_won", "loss": "games_lost", "draw": "games_drawn"}.get(result)
        if stat_col:
            await self.db.execute(
                f"""UPDATE user_stats SET
                        games_played = games_played + 1,
                        {stat_col} = {stat_col} + 1,
                        highest_faan = MAX(highest_faan, ?),
                        total_faan = total_faan + ?,
                        updated_at = datetime('now')
                    WHERE user_id = ?""",
                (faan, faan, user_id),
            )
        await self.db.commit()

    async def get_user_stats(self, user_id):
        """Get aggregated stats for a user. Returns dict or None."""
        async with self.db.execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_match_history(self, user_id, limit=20):
        """Get recent match history for a user."""
        async with self.db.execute(
            """SELECT * FROM match_history
               WHERE user_id = ?
               ORDER BY played_at DESC
               LIMIT ?""",
            (user_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_leaderboard(self, limit=10):
        """Get top players ranked by wins."""
        async with self.db.execute(
            """SELECT u.id, u.display_name, s.games_played, s.games_won,
                      s.games_lost, s.games_drawn, s.highest_faan, s.total_faan
               FROM users u
               JOIN user_stats s ON u.id = s.user_id
               WHERE s.games_played > 0
               ORDER BY s.games_won DESC, s.highest_faan DESC
               LIMIT ?""",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
