import pytest

from mahjong_engine.chat import ChatMessage
from mahjong_engine.room import GameRoom


class TestChatPersistence:
    """Tests for in-memory chat persistence in GameRoom."""

    def test_room_has_empty_chat(self):
        """New room starts with empty chat history."""
        room = GameRoom()
        assert room.get_messages() == []

    def test_add_message(self):
        """Adding a chat message to a room."""
        room = GameRoom()
        msg = ChatMessage(sender_id="p1", content="Hello!")
        room.add_message(msg)
        messages = room.get_messages()
        assert len(messages) == 1
        assert messages[0].content == "Hello!"

    def test_add_multiple_messages(self):
        """Messages are stored in order."""
        room = GameRoom()
        room.add_message(ChatMessage(sender_id="p1", content="first"))
        room.add_message(ChatMessage(sender_id="p2", content="second"))
        room.add_message(ChatMessage(sender_id="p1", content="third"))
        messages = room.get_messages()
        assert len(messages) == 3
        assert messages[0].content == "first"
        assert messages[2].content == "third"

    def test_circular_buffer_limit(self):
        """Only last 100 messages are kept."""
        room = GameRoom()
        for i in range(120):
            room.add_message(ChatMessage(sender_id="p1", content=f"msg_{i}"))
        messages = room.get_messages()
        assert len(messages) == 100
        # First message should be msg_20 (oldest 20 were dropped)
        assert messages[0].content == "msg_20"
        assert messages[-1].content == "msg_119"

    def test_get_messages_returns_copy(self):
        """get_messages returns a copy, not internal reference."""
        room = GameRoom()
        room.add_message(ChatMessage(sender_id="p1", content="hi"))
        msgs = room.get_messages()
        msgs.clear()
        assert len(room.get_messages()) == 1

    def test_message_count(self):
        """message_count returns number of stored messages."""
        room = GameRoom()
        assert room.message_count == 0
        room.add_message(ChatMessage(sender_id="p1", content="hi"))
        room.add_message(ChatMessage(sender_id="p2", content="hey"))
        assert room.message_count == 2

    def test_clear_messages(self):
        """clear_messages removes all chat history."""
        room = GameRoom()
        room.add_message(ChatMessage(sender_id="p1", content="hi"))
        room.clear_messages()
        assert room.get_messages() == []

    def test_get_messages_as_dicts(self):
        """get_messages_as_dicts returns serialized messages."""
        room = GameRoom()
        room.add_message(ChatMessage(sender_id="p1", content="hello"))
        dicts = room.get_messages_as_dicts()
        assert len(dicts) == 1
        assert dicts[0]["content"] == "hello"
        assert dicts[0]["sender_id"] == "p1"
        assert "timestamp" in dicts[0]
