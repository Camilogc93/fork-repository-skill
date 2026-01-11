#!/usr/bin/env python3
"""
Message Bus for Agent-to-Agent Communication

Handles peer-to-peer messaging between agents, enabling collaboration
and information sharing without orchestrator mediation.
"""

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any


class MessageType(str, Enum):
    """Message types for agent communication."""

    # Orchestrator ↔ Agent
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_REQUEST = "status_request"
    STATUS_UPDATE = "status_update"
    TASK_COMPLETE = "task_complete"
    BLOCKER_REPORTED = "blocker_reported"
    PRIORITY_CHANGE = "priority_change"

    # Agent ↔ Agent (Peer-to-Peer)
    REQUEST_INFO = "request_info"
    PROVIDE_INFO = "provide_info"
    HANDOFF = "handoff"
    REVIEW_REQUEST = "review_request"
    REVIEW_COMPLETE = "review_complete"
    DEPENDENCY_READY = "dependency_ready"
    QUESTION = "question"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"


@dataclass
class Message:
    """Message data structure."""

    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reply_to: Optional[str] = None  # For threading
    read: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)


class MessageBus:
    """Manages agent-to-agent messaging."""

    def __init__(self, comm_dir: str = ".agent-comm"):
        """
        Initialize message bus.

        Args:
            comm_dir: Communication directory
        """
        self.comm_dir = Path(comm_dir)
        self.inbox_dir = self.comm_dir / "messaging" / "inbox"
        self.sent_dir = self.comm_dir / "messaging" / "sent"
        self.log_file = self.comm_dir / "logs" / "communications.log"

        # Create directories
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.sent_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self._message_counter = 0

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        reply_to: Optional[str] = None
    ) -> str:
        """
        Send a message from one agent to another.

        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            payload: Message payload
            reply_to: Message ID this is replying to (for threading)

        Returns:
            Message ID
        """
        # Generate unique message ID
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        self._message_counter += 1
        message_id = f"msg-{timestamp}-{self._message_counter:04d}"

        # Create message
        message = Message(
            message_id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            reply_to=reply_to
        )

        # Save to recipient's inbox
        recipient_inbox = self.inbox_dir / to_agent
        recipient_inbox.mkdir(exist_ok=True)
        inbox_file = recipient_inbox / f"{message_id}.json"

        with open(inbox_file, 'w') as f:
            json.dump(message.to_dict(), f, indent=2)

        # Save to sent folder
        sent_file = self.sent_dir / f"{message_id}.json"
        with open(sent_file, 'w') as f:
            json.dump(message.to_dict(), f, indent=2)

        # Log communication
        self._log_message(message)

        return message_id

    def broadcast_message(
        self,
        from_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        exclude: Optional[List[str]] = None
    ) -> List[str]:
        """
        Broadcast message to all agents.

        Args:
            from_agent: Sender agent ID
            message_type: Type of message
            payload: Message payload
            exclude: List of agent IDs to exclude

        Returns:
            List of message IDs
        """
        exclude = exclude or []
        message_ids = []

        # Get all agent inbox directories
        if self.inbox_dir.exists():
            for agent_inbox in self.inbox_dir.iterdir():
                if agent_inbox.is_dir():
                    agent_id = agent_inbox.name
                    if agent_id != from_agent and agent_id not in exclude:
                        msg_id = self.send_message(
                            from_agent,
                            agent_id,
                            message_type,
                            payload
                        )
                        message_ids.append(msg_id)

        return message_ids

    def get_messages(
        self,
        agent_id: str,
        unread_only: bool = True,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages for an agent.

        Args:
            agent_id: Agent identifier
            unread_only: Only return unread messages
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        agent_inbox = self.inbox_dir / agent_id
        if not agent_inbox.exists():
            return []

        messages = []
        message_files = sorted(
            agent_inbox.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True  # Newest first
        )

        for msg_file in message_files:
            try:
                with open(msg_file) as f:
                    data = json.load(f)
                message = Message.from_dict(data)

                if unread_only and message.read:
                    continue

                messages.append(message)

                if limit and len(messages) >= limit:
                    break

            except Exception:
                pass  # Skip corrupted files

        return messages

    def mark_message_read(self, agent_id: str, message_id: str) -> bool:
        """
        Mark a message as read.

        Args:
            agent_id: Agent identifier
            message_id: Message identifier

        Returns:
            True if marked, False if message not found
        """
        msg_file = self.inbox_dir / agent_id / f"{message_id}.json"
        if not msg_file.exists():
            return False

        try:
            with open(msg_file) as f:
                data = json.load(f)

            data['read'] = True

            with open(msg_file, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception:
            return False

    def delete_message(self, agent_id: str, message_id: str) -> bool:
        """
        Delete a message from an agent's inbox.

        Args:
            agent_id: Agent identifier
            message_id: Message identifier

        Returns:
            True if deleted, False if not found
        """
        msg_file = self.inbox_dir / agent_id / f"{message_id}.json"
        if not msg_file.exists():
            return False

        msg_file.unlink()
        return True

    def get_message(self, agent_id: str, message_id: str) -> Optional[Message]:
        """
        Get a specific message.

        Args:
            agent_id: Agent identifier
            message_id: Message identifier

        Returns:
            Message object or None
        """
        msg_file = self.inbox_dir / agent_id / f"{message_id}.json"
        if not msg_file.exists():
            return None

        try:
            with open(msg_file) as f:
                data = json.load(f)
            return Message.from_dict(data)
        except Exception:
            return None

    def get_message_history(
        self,
        agent_id: str,
        limit: int = 50
    ) -> List[Message]:
        """
        Get message history for an agent (including read messages).

        Args:
            agent_id: Agent identifier
            limit: Maximum number of messages

        Returns:
            List of messages
        """
        return self.get_messages(agent_id, unread_only=False, limit=limit)

    def get_conversation(
        self,
        agent1_id: str,
        agent2_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get conversation between two agents.

        Args:
            agent1_id: First agent ID
            agent2_id: Second agent ID
            limit: Maximum number of messages

        Returns:
            List of messages sorted by timestamp
        """
        messages = []

        # Get messages from agent1's inbox sent by agent2
        agent1_inbox = self.inbox_dir / agent1_id
        if agent1_inbox.exists():
            for msg_file in agent1_inbox.glob("*.json"):
                try:
                    with open(msg_file) as f:
                        data = json.load(f)
                    message = Message.from_dict(data)
                    if message.from_agent == agent2_id:
                        messages.append(message)
                except Exception:
                    pass

        # Get messages from agent2's inbox sent by agent1
        agent2_inbox = self.inbox_dir / agent2_id
        if agent2_inbox.exists():
            for msg_file in agent2_inbox.glob("*.json"):
                try:
                    with open(msg_file) as f:
                        data = json.load(f)
                    message = Message.from_dict(data)
                    if message.from_agent == agent1_id:
                        messages.append(message)
                except Exception:
                    pass

        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)

        if limit:
            messages = messages[-limit:]  # Get last N messages

        return messages

    def get_thread(self, message_id: str) -> List[Message]:
        """
        Get message thread (original message and all replies).

        Args:
            message_id: Original message ID

        Returns:
            List of messages in thread
        """
        thread = []

        # Search all sent messages
        for msg_file in self.sent_dir.glob("*.json"):
            try:
                with open(msg_file) as f:
                    data = json.load(f)
                message = Message.from_dict(data)

                if message.message_id == message_id or message.reply_to == message_id:
                    thread.append(message)

            except Exception:
                pass

        # Sort by timestamp
        thread.sort(key=lambda m: m.timestamp)
        return thread

    def get_unread_count(self, agent_id: str) -> int:
        """
        Get count of unread messages for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Number of unread messages
        """
        messages = self.get_messages(agent_id, unread_only=True)
        return len(messages)

    def cleanup_agent_messages(self, agent_id: str):
        """
        Delete all messages for an agent (when agent is removed).

        Args:
            agent_id: Agent identifier
        """
        agent_inbox = self.inbox_dir / agent_id
        if agent_inbox.exists():
            for msg_file in agent_inbox.glob("*.json"):
                msg_file.unlink()
            agent_inbox.rmdir()

    def _log_message(self, message: Message):
        """Log message to communications log."""
        log_entry = (
            f"[{message.timestamp}] "
            f"{message.from_agent} → {message.to_agent} "
            f"[{message.message_type.value}] "
            f"ID: {message.message_id}\n"
        )

        with open(self.log_file, 'a') as f:
            f.write(log_entry)


# Convenience functions for common message patterns

def send_request(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    question: str
) -> str:
    """Send a question/request to another agent."""
    return message_bus.send_message(
        from_agent,
        to_agent,
        MessageType.REQUEST_INFO,
        {"question": question}
    )


def send_response(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    response: str,
    reply_to: str
) -> str:
    """Send a response to a previous message."""
    return message_bus.send_message(
        from_agent,
        to_agent,
        MessageType.PROVIDE_INFO,
        {"response": response},
        reply_to=reply_to
    )


def send_notification(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    notification: str
) -> str:
    """Send a notification to another agent."""
    return message_bus.send_message(
        from_agent,
        to_agent,
        MessageType.NOTIFICATION,
        {"message": notification}
    )


def send_handoff(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    task_id: str,
    handoff_data: Dict[str, Any]
) -> str:
    """Send a handoff to another agent."""
    return message_bus.send_message(
        from_agent,
        to_agent,
        MessageType.HANDOFF,
        {
            "task_id": task_id,
            "handoff_data": handoff_data
        }
    )


def broadcast_notification(
    message_bus: MessageBus,
    from_agent: str,
    notification: str
) -> List[str]:
    """Broadcast a notification to all agents."""
    return message_bus.broadcast_message(
        from_agent,
        MessageType.NOTIFICATION,
        {"message": notification}
    )


if __name__ == "__main__":
    # Example usage
    print("Message Bus - Example Usage")
    print("=" * 50)

    # Create message bus
    bus = MessageBus()

    # Send message from backend to frontend
    msg_id = bus.send_message(
        from_agent="backend-001",
        to_agent="frontend-001",
        message_type=MessageType.PROVIDE_INFO,
        payload={
            "api_contract": {
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "request": {"email": "string", "password": "string"},
                "response": {"token": "string"}
            }
        }
    )
    print(f"✓ Sent message: {msg_id}")

    # Get unread messages
    messages = bus.get_messages("frontend-001", unread_only=True)
    print(f"✓ Frontend has {len(messages)} unread message(s)")

    # Read first message
    if messages:
        msg = messages[0]
        print(f"✓ Message from {msg.from_agent}:")
        print(f"  Type: {msg.message_type.value}")
        print(f"  Payload: {msg.payload}")

        # Mark as read
        bus.mark_message_read("frontend-001", msg.message_id)
        print(f"✓ Marked message as read")

    # Send reply
    reply_id = send_response(
        bus,
        from_agent="frontend-001",
        to_agent="backend-001",
        response="Thanks! I'll use this API contract.",
        reply_to=msg_id
    )
    print(f"✓ Sent reply: {reply_id}")

    # Broadcast notification
    broadcast_ids = broadcast_notification(
        bus,
        from_agent="orchestrator",
        notification="Deployment scheduled for 2pm UTC"
    )
    print(f"✓ Broadcast to {len(broadcast_ids)} agent(s)")

    # Get conversation
    conversation = bus.get_conversation("backend-001", "frontend-001")
    print(f"✓ Conversation has {len(conversation)} message(s)")

    print("\n✓ Message bus working correctly!")
