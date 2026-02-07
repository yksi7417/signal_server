"""Chat message data model for in-game communication."""

import json
import uuid
from datetime import datetime


class ChatMessage:
    """Represents a single chat message.

    Attributes:
        message_id: Unique identifier for the message.
        sender_id: ID of the sender (None for system messages).
        content: Message text content.
        message_type: Type of message ('text' or 'system').
        timestamp: ISO 8601 timestamp of when the message was created.
    """

    def __init__(self, sender_id, content, message_type="text"):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        """Serialize message to dictionary.

        Returns:
            dict with message_id, sender_id, content, type, timestamp.
        """
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "type": self.message_type,
            "timestamp": self.timestamp,
        }

    def to_json(self):
        """Serialize message to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a ChatMessage from a dictionary.

        Args:
            data: Dictionary with message fields.

        Returns:
            ChatMessage instance.
        """
        msg = cls(
            sender_id=data["sender_id"],
            content=data["content"],
            message_type=data.get("type", "text"),
        )
        msg.message_id = data["message_id"]
        msg.timestamp = data["timestamp"]
        return msg

    def __repr__(self):
        return f"ChatMessage(sender={self.sender_id!r}, type={self.message_type!r}, content={self.content!r})"
