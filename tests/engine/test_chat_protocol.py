"""Tests for WebSocket chat protocol message handling.

Tests the chat message processing logic extracted from the WebSocket handler.
These are unit tests that don't require a running server.
"""

import pytest

from mahjong_engine.chat import ChatMessage
from mahjong_engine.chat_protocol import (
    handle_chat_message,
    handle_chat_history,
    handle_chat_typing,
)
from mahjong_engine.room import GameRoom
from mahjong_engine.room_manager import RoomManager


@pytest.fixture
def room_manager():
    """Provide a fresh RoomManager."""
    return RoomManager()


@pytest.fixture
def room_with_players(room_manager):
    """Provide a room with two players."""
    room = room_manager.create_room()
    room.add_player("alice")
    room.add_player("bob")
    return room


class TestHandleChatMessage:
    """Tests for processing incoming chat:message WebSocket messages."""

    def test_valid_text_message(self, room_with_players):
        """A valid chat message is stored and returned for broadcast."""
        data = {
            "type": "chat:message",
            "content": "Hello everyone!",
            "sender_id": "alice",
        }
        result = handle_chat_message(data, room_with_players)
        assert result["success"] is True
        assert result["type"] == "chat:message"
        assert result["message"]["content"] == "Hello everyone!"
        assert result["message"]["sender_id"] == "alice"
        assert "timestamp" in result["message"]
        assert "message_id" in result["message"]

    def test_message_stored_in_room(self, room_with_players):
        """Message is persisted in the room's chat history."""
        data = {
            "type": "chat:message",
            "content": "Test message",
            "sender_id": "alice",
        }
        handle_chat_message(data, room_with_players)
        assert room_with_players.message_count == 1
        msgs = room_with_players.get_messages()
        assert msgs[0].content == "Test message"

    def test_empty_content_rejected(self, room_with_players):
        """Empty content is rejected."""
        data = {
            "type": "chat:message",
            "content": "",
            "sender_id": "alice",
        }
        result = handle_chat_message(data, room_with_players)
        assert result["success"] is False
        assert "error" in result

    def test_missing_content_rejected(self, room_with_players):
        """Missing content field is rejected."""
        data = {
            "type": "chat:message",
            "sender_id": "alice",
        }
        result = handle_chat_message(data, room_with_players)
        assert result["success"] is False

    def test_missing_sender_rejected(self, room_with_players):
        """Missing sender_id is rejected."""
        data = {
            "type": "chat:message",
            "content": "Hello",
        }
        result = handle_chat_message(data, room_with_players)
        assert result["success"] is False

    def test_system_message_type(self, room_with_players):
        """System messages can be sent with message_type='system'."""
        data = {
            "type": "chat:message",
            "content": "Player joined the room",
            "sender_id": None,
            "message_type": "system",
        }
        result = handle_chat_message(data, room_with_players)
        assert result["success"] is True
        assert result["message"]["type"] == "system"

    def test_none_room_rejected(self):
        """Passing None as room is rejected."""
        data = {
            "type": "chat:message",
            "content": "Hello",
            "sender_id": "alice",
        }
        result = handle_chat_message(data, None)
        assert result["success"] is False


class TestHandleChatHistory:
    """Tests for processing chat:history requests."""

    def test_empty_history(self, room_with_players):
        """Empty room returns empty history."""
        data = {"type": "chat:history"}
        result = handle_chat_history(data, room_with_players)
        assert result["success"] is True
        assert result["type"] == "chat:history"
        assert result["messages"] == []
        assert result["count"] == 0

    def test_history_with_messages(self, room_with_players):
        """History returns all stored messages."""
        room_with_players.add_message(ChatMessage("alice", "Hi"))
        room_with_players.add_message(ChatMessage("bob", "Hello"))
        data = {"type": "chat:history"}
        result = handle_chat_history(data, room_with_players)
        assert result["success"] is True
        assert result["count"] == 2
        assert result["messages"][0]["content"] == "Hi"
        assert result["messages"][1]["content"] == "Hello"

    def test_none_room_rejected(self):
        """Passing None as room is rejected."""
        data = {"type": "chat:history"}
        result = handle_chat_history(data, None)
        assert result["success"] is False


class TestHandleChatTyping:
    """Tests for processing chat:typing indicators."""

    def test_typing_indicator(self, room_with_players):
        """Typing indicator returns broadcast data."""
        data = {
            "type": "chat:typing",
            "sender_id": "alice",
            "is_typing": True,
        }
        result = handle_chat_typing(data, room_with_players)
        assert result["success"] is True
        assert result["type"] == "chat:typing"
        assert result["sender_id"] == "alice"
        assert result["is_typing"] is True

    def test_stopped_typing(self, room_with_players):
        """Stopped typing indicator."""
        data = {
            "type": "chat:typing",
            "sender_id": "bob",
            "is_typing": False,
        }
        result = handle_chat_typing(data, room_with_players)
        assert result["success"] is True
        assert result["is_typing"] is False

    def test_missing_sender(self, room_with_players):
        """Missing sender_id is rejected."""
        data = {
            "type": "chat:typing",
            "is_typing": True,
        }
        result = handle_chat_typing(data, room_with_players)
        assert result["success"] is False

    def test_none_room_rejected(self):
        """Passing None as room is rejected."""
        data = {
            "type": "chat:typing",
            "sender_id": "alice",
            "is_typing": True,
        }
        result = handle_chat_typing(data, None)
        assert result["success"] is False
