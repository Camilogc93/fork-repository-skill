#!/usr/bin/env python3
"""
Test Peer-to-Peer Communication

Tests agent-to-agent messaging, conversation threading, and broadcast messages.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude/skills/fork-terminal/tools"))

from message_bus import MessageBus, MessageType, send_request, send_response, broadcast_notification


def test_basic_messaging():
    """Test basic message sending and receiving."""
    print("=" * 60)
    print("TEST: Basic Peer-to-Peer Messaging")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-basic"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Send message from frontend to backend
    msg_id = bus.send_message(
        from_agent="frontend-001",
        to_agent="backend-001",
        message_type=MessageType.REQUEST_INFO,
        payload={"question": "What's the login API endpoint?"}
    )

    print(f"\n✓ Message sent: {msg_id}")
    print("  From: frontend-001")
    print("  To: backend-001")
    print("  Type: REQUEST_INFO")

    # Get messages for backend
    messages = bus.get_messages("backend-001", unread_only=True)
    assert len(messages) == 1, "Backend should have 1 unread message"

    msg = messages[0]
    assert msg.from_agent == "frontend-001"
    assert msg.to_agent == "backend-001"
    assert msg.message_type == MessageType.REQUEST_INFO
    assert "question" in msg.payload

    print(f"\n✓ Backend received {len(messages)} message(s)")
    print(f"  Question: {msg.payload['question']}")

    # Mark as read
    bus.mark_message_read("backend-001", msg.message_id)
    unread = bus.get_messages("backend-001", unread_only=True)
    assert len(unread) == 0, "No unread messages after marking read"

    print("✓ Message marked as read")

    # Send response
    response_id = bus.send_message(
        from_agent="backend-001",
        to_agent="frontend-001",
        message_type=MessageType.PROVIDE_INFO,
        payload={"response": "POST /api/v1/auth/login"},
        reply_to=msg_id
    )

    print(f"\n✓ Response sent: {response_id}")
    print("  Reply to:", msg_id)

    # Frontend gets response
    frontend_messages = bus.get_messages("frontend-001", unread_only=True)
    assert len(frontend_messages) == 1, "Frontend should have 1 unread message"

    response_msg = frontend_messages[0]
    assert response_msg.reply_to == msg_id, "Response should reference original message"
    assert response_msg.message_type == MessageType.PROVIDE_INFO

    print(f"✓ Frontend received response: {response_msg.payload['response']}")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Basic Messaging")
    print("=" * 60)

    return True


def test_broadcast():
    """Test broadcast messages to all agents."""
    print("\n" + "=" * 60)
    print("TEST: Broadcast Messages")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-broadcast"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Create inbox directories for agents (simulating registered agents)
    agents = ["backend-001", "frontend-001", "devops-001", "qa-001"]
    for agent in agents:
        inbox = Path(comm_dir) / "messaging" / "inbox" / agent
        inbox.mkdir(parents=True, exist_ok=True)

    # Broadcast notification
    msg_ids = bus.broadcast_message(
        from_agent="devops-001",
        message_type=MessageType.NOTIFICATION,
        payload={"message": "Deployment complete!"}
    )

    print(f"\n✓ Broadcast sent to {len(msg_ids)} agent(s)")
    print("  Message: Deployment complete!")

    # Verify each agent received the message
    for agent in agents:
        if agent == "devops-001":  # Sender shouldn't receive their own broadcast
            messages = bus.get_messages(agent, unread_only=True)
            assert len(messages) == 0, f"{agent} (sender) should not receive broadcast"
        else:
            messages = bus.get_messages(agent, unread_only=True)
            assert len(messages) == 1, f"{agent} should have 1 broadcast message"
            msg = messages[0]
            assert msg.from_agent == "devops-001"
            assert msg.message_type == MessageType.NOTIFICATION
            print(f"  ✓ {agent} received broadcast")

    print("\n✓ All agents received broadcast (except sender)")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Broadcast")
    print("=" * 60)

    return True


def test_conversation():
    """Test conversation tracking between two agents."""
    print("\n" + "=" * 60)
    print("TEST: Conversation Threading")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-conversation"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Simulate conversation
    # Frontend asks backend about API
    msg1 = bus.send_message(
        "frontend-001",
        "backend-001",
        MessageType.REQUEST_INFO,
        {"question": "Auth API endpoint?"}
    )
    print("\n✓ Frontend → Backend: Auth API endpoint?")

    # Backend responds
    msg2 = bus.send_message(
        "backend-001",
        "frontend-001",
        MessageType.PROVIDE_INFO,
        {"response": "POST /api/v1/auth/login"},
        reply_to=msg1
    )
    print("✓ Backend → Frontend: POST /api/v1/auth/login")

    # Frontend asks follow-up
    msg3 = bus.send_message(
        "frontend-001",
        "backend-001",
        MessageType.QUESTION,
        {"question": "What's the request format?"},
        reply_to=msg2
    )
    print("✓ Frontend → Backend: What's the request format?")

    # Backend responds
    msg4 = bus.send_message(
        "backend-001",
        "frontend-001",
        MessageType.PROVIDE_INFO,
        {"response": "JSON: {email, password}"},
        reply_to=msg3
    )
    print("✓ Backend → Frontend: JSON: {email, password}")

    # Get full conversation
    conversation = bus.get_conversation("frontend-001", "backend-001")
    assert len(conversation) == 4, "Should have 4 messages in conversation"

    print(f"\n✓ Conversation has {len(conversation)} messages")

    # Verify message order
    assert conversation[0].message_id == msg1
    assert conversation[1].message_id == msg2
    assert conversation[2].message_id == msg3
    assert conversation[3].message_id == msg4

    print("✓ Messages are in correct chronological order")

    # Verify reply threading
    assert conversation[1].reply_to == msg1
    assert conversation[2].reply_to == msg2
    assert conversation[3].reply_to == msg3

    print("✓ Reply threading is correct")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Conversation Threading")
    print("=" * 60)

    return True


def test_message_types():
    """Test different message types."""
    print("\n" + "=" * 60)
    print("TEST: Message Types")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-types"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Test all peer-to-peer message types
    message_types = [
        (MessageType.REQUEST_INFO, {"question": "What's the API?"}),
        (MessageType.PROVIDE_INFO, {"response": "Here's the API"}),
        (MessageType.HANDOFF, {"task_id": "task-001", "data": {}}),
        (MessageType.REVIEW_REQUEST, {"code": "review this"}),
        (MessageType.NOTIFICATION, {"message": "FYI: deployed"}),
        (MessageType.DEPENDENCY_READY, {"task_id": "task-001"}),
    ]

    print("\n✓ Testing message types:")

    for msg_type, payload in message_types:
        msg_id = bus.send_message(
            "agent-001",
            "agent-002",
            msg_type,
            payload
        )
        print(f"  ✓ {msg_type.value}")

    # Verify all received
    messages = bus.get_messages("agent-002", unread_only=True)
    assert len(messages) == len(message_types), f"Should have {len(message_types)} messages"

    received_types = [msg.message_type for msg in messages]
    expected_types = [mt for mt, _ in message_types]

    for expected in expected_types:
        assert expected in received_types, f"Should have received {expected}"

    print(f"\n✓ All {len(message_types)} message types sent and received correctly")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Message Types")
    print("=" * 60)

    return True


def test_helper_functions():
    """Test convenience helper functions."""
    print("\n" + "=" * 60)
    print("TEST: Helper Functions")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-helpers"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Test send_request helper
    msg_id = send_request(
        bus,
        "frontend-001",
        "backend-001",
        "What's the API endpoint?"
    )

    messages = bus.get_messages("backend-001", unread_only=True)
    assert len(messages) == 1
    assert messages[0].message_type == MessageType.REQUEST_INFO
    print("✓ send_request() helper works")

    # Test send_response helper
    response_id = send_response(
        bus,
        "backend-001",
        "frontend-001",
        "POST /api/v1/endpoint",
        reply_to=msg_id
    )

    response_msgs = bus.get_messages("frontend-001", unread_only=True)
    assert len(response_msgs) == 1
    assert response_msgs[0].message_type == MessageType.PROVIDE_INFO
    assert response_msgs[0].reply_to == msg_id
    print("✓ send_response() helper works")

    # Test broadcast_notification helper
    # Create some agent inboxes
    for agent in ["agent-001", "agent-002", "agent-003"]:
        inbox = Path(comm_dir) / "messaging" / "inbox" / agent
        inbox.mkdir(parents=True, exist_ok=True)

    broadcast_ids = broadcast_notification(
        bus,
        "orchestrator",
        "System maintenance scheduled"
    )

    assert len(broadcast_ids) > 0
    print(f"✓ broadcast_notification() helper works ({len(broadcast_ids)} recipients)")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Helper Functions")
    print("=" * 60)

    return True


def test_unread_count():
    """Test unread message counting."""
    print("\n" + "=" * 60)
    print("TEST: Unread Message Counting")
    print("=" * 60)

    comm_dir = "/tmp/test-messaging-unread"
    os.makedirs(comm_dir, exist_ok=True)

    bus = MessageBus(comm_dir)

    # Send 3 messages
    for i in range(3):
        bus.send_message(
            "agent-001",
            "agent-002",
            MessageType.NOTIFICATION,
            {"message": f"Message {i+1}"}
        )

    # Check unread count
    unread_count = bus.get_unread_count("agent-002")
    assert unread_count == 3, "Should have 3 unread messages"
    print(f"\n✓ Unread count: {unread_count}")

    # Mark one as read
    messages = bus.get_messages("agent-002", unread_only=True)
    bus.mark_message_read("agent-002", messages[0].message_id)

    # Check again
    unread_count = bus.get_unread_count("agent-002")
    assert unread_count == 2, "Should have 2 unread messages after marking one read"
    print(f"✓ After marking 1 read: {unread_count}")

    # Mark all as read
    for msg in messages[1:]:
        bus.mark_message_read("agent-002", msg.message_id)

    # Check again
    unread_count = bus.get_unread_count("agent-002")
    assert unread_count == 0, "Should have 0 unread messages"
    print(f"✓ After marking all read: {unread_count}")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Unread Counting")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\n🧪 Running Peer-to-Peer Communication Tests\n")

    try:
        test_basic_messaging()
        test_broadcast()
        test_conversation()
        test_message_types()
        test_helper_functions()
        test_unread_count()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
