"""WebSocket chat protocol message handlers.

Processes chat-related WebSocket messages and delegates to the
room's chat persistence layer. Each handler returns a dict that
can be serialized to JSON and broadcast to room peers.

Message types:
    chat:message  - Send a text or system message
    chat:history  - Request chat history for a room
    chat:typing   - Typing indicator broadcast
"""

from .chat import ChatMessage


def handle_chat_message(data, room):
    """Process an incoming chat:message.

    Args:
        data: Parsed JSON dict with 'content', 'sender_id', optional 'message_type'.
        room: GameRoom instance to store the message in.

    Returns:
        dict with 'success', 'type', and either 'message' (serialized) or 'error'.
    """
    if room is None:
        return {"success": False, "type": "chat:message", "error": "No room found"}

    content = data.get("content")
    sender_id = data.get("sender_id")
    message_type = data.get("message_type", "text")

    if message_type != "system" and not sender_id:
        return {"success": False, "type": "chat:message", "error": "Missing sender_id"}

    if not content:
        return {"success": False, "type": "chat:message", "error": "Empty message content"}

    msg = ChatMessage(sender_id=sender_id, content=content, message_type=message_type)
    room.add_message(msg)

    return {
        "success": True,
        "type": "chat:message",
        "message": msg.to_dict(),
    }


def handle_chat_history(data, room):
    """Process a chat:history request.

    Args:
        data: Parsed JSON dict (no required fields beyond 'type').
        room: GameRoom instance to read history from.

    Returns:
        dict with 'success', 'type', 'messages' list, and 'count'.
    """
    if room is None:
        return {"success": False, "type": "chat:history", "error": "No room found"}

    messages = room.get_messages_as_dicts()
    return {
        "success": True,
        "type": "chat:history",
        "messages": messages,
        "count": len(messages),
    }


def handle_chat_typing(data, room):
    """Process a chat:typing indicator.

    Args:
        data: Parsed JSON dict with 'sender_id' and 'is_typing'.
        room: GameRoom instance (used for validation).

    Returns:
        dict with 'success', 'type', 'sender_id', and 'is_typing'.
    """
    if room is None:
        return {"success": False, "type": "chat:typing", "error": "No room found"}

    sender_id = data.get("sender_id")
    if not sender_id:
        return {"success": False, "type": "chat:typing", "error": "Missing sender_id"}

    is_typing = data.get("is_typing", False)

    return {
        "success": True,
        "type": "chat:typing",
        "sender_id": sender_id,
        "is_typing": is_typing,
    }
