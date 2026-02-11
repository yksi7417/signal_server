"""Sign in with Apple (SIWA) authentication service.

Validates Apple identity tokens (JWTs), manages server-side sessions,
and integrates with the Database layer for user persistence.
"""
import logging
import os
import secrets
import time

import jwt
import requests

from mahjong_engine.database import sanitize_display_name

logger = logging.getLogger(__name__)

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
APPLE_TOKEN_AUDIENCE = None  # Set from env or config

SESSION_TTL_SECONDS = 86400 * 7  # 7 days


class AuthService:
    """Handles Sign in with Apple verification and session management."""

    def __init__(self, database=None, client_id=None, team_id=None):
        self.database = database
        self.client_id = client_id or os.environ.get("APPLE_CLIENT_ID", "")
        self.team_id = team_id or os.environ.get("APPLE_TEAM_ID", "")
        self._apple_keys = None
        self._apple_keys_fetched_at = 0
        # In-memory session store: token → {user_id, created_at}
        self._sessions = {}

    def _fetch_apple_keys(self):
        """Fetch Apple's public keys for JWT verification. Cached for 1 hour."""
        now = time.time()
        if self._apple_keys and (now - self._apple_keys_fetched_at) < 3600:
            return self._apple_keys
        try:
            resp = requests.get(APPLE_JWKS_URL, timeout=10)
            resp.raise_for_status()
            self._apple_keys = resp.json()
            self._apple_keys_fetched_at = now
            return self._apple_keys
        except Exception as e:
            logger.error("Failed to fetch Apple JWKS: %s", e)
            if self._apple_keys:
                return self._apple_keys
            raise

    async def verify_apple_token(self, identity_token):
        """Validate an Apple identity token JWT.

        Returns decoded payload dict with 'sub', 'email', etc.
        Raises ValueError on invalid token.
        """
        jwks = self._fetch_apple_keys()
        try:
            header = jwt.get_unverified_header(identity_token)
            kid = header.get("kid")

            key = None
            for jwk_data in jwks.get("keys", []):
                if jwk_data.get("kid") == kid:
                    key = jwt.PyJWK(jwk_data)
                    break

            if not key:
                raise ValueError("No matching key found in Apple JWKS")

            payload = jwt.decode(
                identity_token,
                key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=APPLE_ISSUER,
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Apple identity token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid Apple identity token: {e}")

    async def authenticate_apple(self, identity_token, display_name=None):
        """Full SIWA authentication flow.

        1. Verify the Apple JWT
        2. Extract user info
        3. Upsert user in database
        4. Create session

        Returns dict with session_token and user info.
        """
        payload = await self.verify_apple_token(identity_token)
        apple_sub = payload["sub"]
        email = payload.get("email")
        name = display_name or email or f"Player_{apple_sub[:8]}"
        name = sanitize_display_name(name)

        user = await self.database.upsert_user(apple_sub, name, email=email)
        token = self.create_session(user["id"])

        return {
            "session_token": token,
            "user": {
                "id": user["id"],
                "display_name": user["display_name"],
            },
        }

    def create_session(self, user_id):
        """Generate a random session token and store it."""
        token = secrets.token_hex(32)
        self._sessions[token] = {
            "user_id": user_id,
            "created_at": time.time(),
        }
        return token

    def validate_session(self, token):
        """Check if a session token is valid. Returns session dict or None."""
        session = self._sessions.get(token)
        if not session:
            return None
        if time.time() - session["created_at"] > SESSION_TTL_SECONDS:
            del self._sessions[token]
            return None
        return session

    def invalidate_session(self, token):
        """Remove a session token (logout)."""
        self._sessions.pop(token, None)
