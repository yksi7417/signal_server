"""Tests for LiveKit service module - token generation and room management."""
import pytest
from unittest.mock import patch, MagicMock


class TestLiveKitServiceConfig:
    """Test LiveKit service configuration."""

    def test_default_config(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService()
        assert service.api_key is not None
        assert service.api_secret is not None
        assert service.livekit_url is not None

    def test_custom_config(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(
            api_key="test-key",
            api_secret="test-secret",
            livekit_url="ws://localhost:7880"
        )
        assert service.api_key == "test-key"
        assert service.api_secret == "test-secret"
        assert service.livekit_url == "ws://localhost:7880"

    def test_config_from_env(self):
        from mahjong_engine.livekit_service import LiveKitService
        with patch.dict("os.environ", {
            "LIVEKIT_API_KEY": "env-key",
            "LIVEKIT_API_SECRET": "env-secret",
            "LIVEKIT_URL": "ws://envhost:7880",
        }):
            service = LiveKitService()
            assert service.api_key == "env-key"
            assert service.api_secret == "env-secret"
            assert service.livekit_url == "ws://envhost:7880"


class TestTokenGeneration:
    """Test LiveKit access token generation."""

    def test_generate_token_returns_string(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(room_name="test-room", participant_name="player1")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_is_valid_jwt(self):
        import jwt
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(room_name="test-room", participant_name="player1")
        # Should be decodable as JWT
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert "video" in decoded
        assert decoded["video"]["room"] == "test-room"

    def test_generate_token_includes_identity(self):
        import jwt
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(room_name="test-room", participant_name="player1")
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert decoded.get("sub") == "player1"

    def test_generate_token_has_expiry(self):
        import jwt
        import time
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(room_name="test-room", participant_name="player1")
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert "exp" in decoded
        # Expiry should be in the future
        assert decoded["exp"] > time.time()

    def test_generate_token_grants_publish_subscribe(self):
        import jwt
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(room_name="test-room", participant_name="player1")
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        video_grants = decoded.get("video", {})
        assert video_grants.get("roomJoin") is True
        assert video_grants.get("canPublish") is True
        assert video_grants.get("canSubscribe") is True

    def test_generate_token_different_rooms(self):
        import jwt
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token1 = service.generate_token(room_name="room-a", participant_name="player1")
        token2 = service.generate_token(room_name="room-b", participant_name="player1")
        decoded1 = jwt.decode(token1, "test-secret", algorithms=["HS256"])
        decoded2 = jwt.decode(token2, "test-secret", algorithms=["HS256"])
        assert decoded1["video"]["room"] == "room-a"
        assert decoded2["video"]["room"] == "room-b"

    def test_generate_token_different_participants(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token1 = service.generate_token(room_name="room-a", participant_name="player1")
        token2 = service.generate_token(room_name="room-a", participant_name="player2")
        assert token1 != token2

    def test_generate_token_custom_ttl(self):
        import jwt
        import time
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        token = service.generate_token(
            room_name="test-room", participant_name="player1", ttl_seconds=300
        )
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])
        # TTL of 5 minutes
        assert decoded["exp"] <= time.time() + 300 + 5  # small tolerance


class TestRoomNameGeneration:
    """Test room name generation for game rooms."""

    def test_room_name_for_game_room(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        room_name = service.get_video_room_name("abc-123")
        assert room_name == "mahjong-abc-123"

    def test_room_name_prefix(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(api_key="test-key", api_secret="test-secret")
        room_name = service.get_video_room_name("test")
        assert room_name.startswith("mahjong-")

    def test_get_connection_info(self):
        from mahjong_engine.livekit_service import LiveKitService
        service = LiveKitService(
            api_key="test-key",
            api_secret="test-secret",
            livekit_url="ws://localhost:7880"
        )
        info = service.get_connection_info(room_id="room-123", participant_name="player1")
        assert "token" in info
        assert info["url"] == "ws://localhost:7880"
        assert info["room_name"] == "mahjong-room-123"
        assert isinstance(info["token"], str)
        assert len(info["token"]) > 0
