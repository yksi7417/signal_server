"""Tests for the Sign in with Apple authentication service."""
import asyncio
import time

import pytest

from mahjong_engine.auth import SESSION_TTL_SECONDS, AuthService
from mahjong_engine.database import Database


@pytest.fixture
def db():
    """Create an in-memory database for auth tests."""
    database = Database(db_path=":memory:")
    asyncio.get_event_loop().run_until_complete(database.initialize())
    yield database
    asyncio.get_event_loop().run_until_complete(database.close())


@pytest.fixture
def auth(db):
    """Create an AuthService with test database."""
    return AuthService(database=db, client_id="com.test.app", team_id="TESTTEAM")


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestSessionManagement:
    def test_create_session(self, auth):
        token = auth.create_session(user_id=1)
        assert isinstance(token, str)
        assert len(token) == 64  # 32 bytes hex

    def test_validate_session(self, auth):
        token = auth.create_session(user_id=42)
        session = auth.validate_session(token)
        assert session is not None
        assert session["user_id"] == 42

    def test_validate_invalid_token(self, auth):
        assert auth.validate_session("bogus_token") is None

    def test_invalidate_session(self, auth):
        token = auth.create_session(user_id=1)
        auth.invalidate_session(token)
        assert auth.validate_session(token) is None

    def test_invalidate_nonexistent_session(self, auth):
        # Should not raise
        auth.invalidate_session("does_not_exist")

    def test_session_expiry(self, auth):
        token = auth.create_session(user_id=1)
        # Manually backdate the session
        auth._sessions[token]["created_at"] = time.time() - SESSION_TTL_SECONDS - 1
        assert auth.validate_session(token) is None
        # Session should be cleaned up
        assert token not in auth._sessions

    def test_multiple_sessions_independent(self, auth):
        t1 = auth.create_session(user_id=1)
        t2 = auth.create_session(user_id=2)
        assert t1 != t2
        assert auth.validate_session(t1)["user_id"] == 1
        assert auth.validate_session(t2)["user_id"] == 2
        auth.invalidate_session(t1)
        assert auth.validate_session(t1) is None
        assert auth.validate_session(t2) is not None


class TestAppleTokenVerification:
    """Test the Apple JWT verification path.

    Full SIWA verification requires Apple's real JWKS endpoint,
    so we test error handling paths here.
    """

    def test_verify_invalid_token_raises(self, auth):
        with pytest.raises(Exception):
            _run(auth.verify_apple_token("not.a.jwt"))

    def test_authenticate_apple_requires_valid_token(self, auth):
        with pytest.raises(Exception):
            _run(auth.authenticate_apple("invalid_token"))


class TestAuthServiceInit:
    def test_default_config(self):
        svc = AuthService()
        assert svc.client_id == ""
        assert svc.team_id == ""
        assert svc._sessions == {}

    def test_custom_config(self, db):
        svc = AuthService(database=db, client_id="com.example", team_id="TEAM123")
        assert svc.client_id == "com.example"
        assert svc.team_id == "TEAM123"
