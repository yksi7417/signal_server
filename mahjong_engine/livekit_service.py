"""LiveKit service for video chat room management and token generation.

Provides token generation for LiveKit SFU integration, mapping game rooms
to video chat rooms with appropriate permissions.
"""
import os
from datetime import timedelta

from livekit import api


# Default dev credentials (LiveKit --dev mode uses these)
DEFAULT_API_KEY = "devkey"
DEFAULT_API_SECRET = "secret"
DEFAULT_LIVEKIT_URL = "ws://localhost:7880"

ROOM_PREFIX = "mahjong-"
DEFAULT_TTL_SECONDS = 3600  # 1 hour


class LiveKitService:
    """Manages LiveKit video room tokens and room-to-game mapping."""

    def __init__(self, api_key=None, api_secret=None, livekit_url=None):
        self.api_key = api_key or os.environ.get("LIVEKIT_API_KEY", DEFAULT_API_KEY)
        self.api_secret = api_secret or os.environ.get("LIVEKIT_API_SECRET", DEFAULT_API_SECRET)
        self.livekit_url = livekit_url or os.environ.get("LIVEKIT_URL", DEFAULT_LIVEKIT_URL)

    def generate_token(self, room_name: str, participant_name: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
        """Generate a LiveKit access token for a participant to join a room.

        Args:
            room_name: The LiveKit room name.
            participant_name: Display name / identity for the participant.
            ttl_seconds: Token time-to-live in seconds (default 1 hour).

        Returns:
            JWT token string.
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_name)
        token.with_ttl(timedelta(seconds=ttl_seconds))
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        return token.to_jwt()

    def get_video_room_name(self, room_id: str) -> str:
        """Map a game room ID to a LiveKit room name.

        Args:
            room_id: The game room identifier.

        Returns:
            LiveKit room name with prefix.
        """
        return f"{ROOM_PREFIX}{room_id}"

    def get_connection_info(self, room_id: str, participant_name: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict:
        """Get everything a client needs to connect to a video room.

        Args:
            room_id: The game room identifier.
            participant_name: Display name / identity for the participant.
            ttl_seconds: Token time-to-live in seconds.

        Returns:
            Dict with token, url, and room_name.
        """
        room_name = self.get_video_room_name(room_id)
        token = self.generate_token(room_name, participant_name, ttl_seconds)
        return {
            "token": token,
            "url": self.livekit_url,
            "room_name": room_name,
        }
