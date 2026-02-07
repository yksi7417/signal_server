import json

import pytest

from mahjong_engine.chat import ChatMessage


class TestChatMessage:
    """Tests for ChatMessage data model."""

    def test_create_text_message(self):
        """Create a basic text message."""
        msg = ChatMessage(sender_id="player_1", content="Hello!")
        assert msg.sender_id == "player_1"
        assert msg.content == "Hello!"
        assert msg.message_type == "text"
        assert msg.timestamp is not None

    def test_create_system_message(self):
        """Create a system message."""
        msg = ChatMessage(sender_id=None, content="Player joined.", message_type="system")
        assert msg.sender_id is None
        assert msg.message_type == "system"

    def test_message_has_unique_id(self):
        """Each message gets a unique ID."""
        m1 = ChatMessage(sender_id="p1", content="a")
        m2 = ChatMessage(sender_id="p1", content="b")
        assert m1.message_id != m2.message_id

    def test_message_id_format(self):
        """Message ID is a UUID string."""
        msg = ChatMessage(sender_id="p1", content="hi")
        assert len(msg.message_id) == 36

    def test_to_dict(self):
        """Message serializes to dictionary."""
        msg = ChatMessage(sender_id="p1", content="test", message_type="text")
        data = msg.to_dict()
        assert data["sender_id"] == "p1"
        assert data["content"] == "test"
        assert data["type"] == "text"
        assert "timestamp" in data
        assert "message_id" in data

    def test_to_json(self):
        """Message serializes to valid JSON string."""
        msg = ChatMessage(sender_id="p1", content="hello")
        json_str = msg.to_json()
        parsed = json.loads(json_str)
        assert parsed["content"] == "hello"

    def test_from_dict(self):
        """Message can be reconstructed from dictionary."""
        msg = ChatMessage(sender_id="p1", content="test")
        data = msg.to_dict()
        restored = ChatMessage.from_dict(data)
        assert restored.message_id == msg.message_id
        assert restored.sender_id == msg.sender_id
        assert restored.content == msg.content
        assert restored.message_type == msg.message_type
        assert restored.timestamp == msg.timestamp

    def test_default_type_is_text(self):
        """Default message type is 'text'."""
        msg = ChatMessage(sender_id="p1", content="hi")
        assert msg.message_type == "text"

    def test_empty_content(self):
        """Message can have empty content."""
        msg = ChatMessage(sender_id="p1", content="")
        assert msg.content == ""

    def test_repr(self):
        """String representation includes key fields."""
        msg = ChatMessage(sender_id="p1", content="hi", message_type="text")
        r = repr(msg)
        assert "p1" in r
        assert "text" in r
