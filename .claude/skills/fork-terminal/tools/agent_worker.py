#!/usr/bin/env python3
"""
Agent Worker Script

This script runs in forked terminal windows and executes tasks assigned
to specialized agents (frontend, backend, devops, qa, architect).

The worker:
- Loads role and project context
- Registers with orchestrator
- Polls for tasks or executes assigned task
- Sends heartbeat signals
- Saves checkpoints for crash recovery
- Handles peer-to-peer messages
- Reports results
"""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Import our orchestration modules
from checkpoint_manager import CheckpointManager
from orchestrator import TaskManager, AgentRegistry, Task, TaskStatus
from message_bus import MessageBus, MessageType


class AgentWorker:
    """Agent worker that executes tasks in a forked terminal."""

    def __init__(
        self,
        agent_id: str,
        role: str,
        task_id: Optional[str],
        context_file: str,
        comm_dir: str = ".agent-comm"
    ):
        """
        Initialize agent worker.

        Args:
            agent_id: Unique agent identifier
            role: Agent role (frontend, backend, devops, qa, architect)
            task_id: Initial task ID (if resuming)
            context_file: Path to context file with role + project info
            comm_dir: Communication directory
        """
        self.agent_id = agent_id
        self.role = role
        self.task_id = task_id
        self.context_file = context_file
        self.comm_dir = comm_dir

        # Initialize managers
        self.checkpoint_mgr = CheckpointManager(f"{comm_dir}/checkpoints")
        self.task_mgr = TaskManager(comm_dir)
        self.agent_registry = AgentRegistry(comm_dir)
        self.message_bus = MessageBus(comm_dir)

        # Agent state
        self.current_task: Optional[Task] = None
        self.running = False
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.context: Dict[str, Any] = {}

        # Checkpoint interval (seconds)
        self.checkpoint_interval = 30

    def start(self):
        """Start the agent worker."""
        print(f"🚀 Starting Agent Worker: {self.agent_id}")
        print(f"   Role: {self.role}")
        print(f"   Task: {self.task_id or 'Will poll for tasks'}")
        print("=" * 60)

        try:
            # Load context
            self._load_context()

            # Load previous checkpoint if resuming
            checkpoint = self.checkpoint_mgr.load_latest_checkpoint(self.agent_id)
            if checkpoint:
                print(f"📂 Resuming from checkpoint")
                print(f"   Previous task: {checkpoint.task_id}")
                print(f"   Step: {checkpoint.state.get('current_step', '?')}/{checkpoint.state.get('total_steps', '?')}")
                self.context['checkpoint'] = checkpoint

            # Register with orchestrator
            capabilities = self._get_capabilities()
            if not self.agent_registry.register_agent(
                self.agent_id,
                self.role,
                capabilities
            ):
                print("❌ Failed to register: Maximum agents reached")
                return

            print(f"✅ Registered with orchestrator")
            print(f"   Capabilities: {', '.join(capabilities)}")

            # Start heartbeat
            self.running = True
            self._start_heartbeat()
            print(f"💓 Heartbeat started (every 10s)")

            # Main task loop
            if self.task_id:
                # Execute specific task
                self._execute_assigned_task()
            else:
                # Poll for tasks
                self._task_polling_loop()

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self._shutdown()

    def _load_context(self):
        """Load role and project context from file."""
        print(f"📖 Loading context from {self.context_file}")

        if not os.path.exists(self.context_file):
            raise FileNotFoundError(f"Context file not found: {self.context_file}")

        with open(self.context_file) as f:
            self.context['full_context'] = f.read()

        # Parse context sections (simplified - in reality would parse markdown)
        self.context['role_description'] = "Loaded from context file"
        self.context['project_context'] = "Loaded from context file"

        print(f"✅ Context loaded ({len(self.context['full_context'])} chars)")

    def _get_capabilities(self) -> list:
        """Get agent capabilities based on role."""
        capabilities_map = {
            'frontend': ['react', 'ui', 'components', 'styling'],
            'backend': ['api', 'database', 'business-logic'],
            'devops': ['docker', 'ci-cd', 'infrastructure'],
            'qa': ['testing', 'quality-assurance', 'automation'],
            'architect': ['design', 'documentation', 'architecture']
        }
        return capabilities_map.get(self.role, [])

    def _start_heartbeat(self):
        """Start heartbeat thread."""
        def heartbeat_loop():
            while self.running:
                self.agent_registry.update_agent_status(
                    self.agent_id,
                    "working" if self.current_task else "idle",
                    self.current_task.task_id if self.current_task else None
                )
                time.sleep(10)

        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

    def _execute_assigned_task(self):
        """Execute a specific assigned task."""
        task = self.task_mgr.get_task(self.task_id)
        if not task:
            print(f"❌ Task {self.task_id} not found")
            return

        self._execute_task(task)

    def _task_polling_loop(self):
        """Poll for tasks and execute them."""
        print(f"\n🔄 Polling for tasks (role: {self.role})")
        print("   Press Ctrl+C to stop")

        checkpoint_counter = 0

        while self.running:
            # Check for new messages
            self._process_messages()

            # Look for tasks assigned to this agent
            my_tasks = self.task_mgr.get_tasks_for_agent(self.agent_id)

            # Also check for unassigned tasks for our role
            if not my_tasks:
                role_tasks = self.task_mgr.get_tasks_by_role(self.role)
                pending_role_tasks = [
                    t for t in role_tasks
                    if t.status == TaskStatus.QUEUED and not t.assigned_to
                ]

                if pending_role_tasks:
                    # Claim the first pending task
                    task = pending_role_tasks[0]
                    self.task_mgr.assign_task(task.task_id, self.agent_id)
                    my_tasks = [task]

            if my_tasks:
                # Execute first task
                task = my_tasks[0]
                if task.status in [TaskStatus.ASSIGNED, TaskStatus.QUEUED]:
                    self._execute_task(task)
            else:
                # No tasks, wait and poll again
                time.sleep(5)

            checkpoint_counter += 1
            if checkpoint_counter >= 6:  # Every 30 seconds (5s * 6)
                checkpoint_counter = 0
                if self.current_task:
                    self._save_checkpoint("polling")

    def _execute_task(self, task: Task):
        """
        Execute a task.

        Args:
            task: Task to execute
        """
        self.current_task = task
        print(f"\n{'='*60}")
        print(f"📋 Task: {task.task_id}")
        print(f"   Description: {task.description}")
        print(f"   Priority: {task.priority.value}")
        print(f"{'='*60}\n")

        try:
            # Mark task as started
            self.task_mgr.start_task(task.task_id)

            # Save initial checkpoint
            self._save_checkpoint("started")

            # Execute task based on role
            result = self._do_work(task)

            # Save final checkpoint
            self._save_checkpoint("completed", result)

            # Mark task as completed
            self.task_mgr.complete_task(task.task_id, result)

            print(f"\n✅ Task {task.task_id} completed")

            # Notify dependent tasks
            self._notify_dependents(task.task_id)

        except Exception as e:
            print(f"\n❌ Task {task.task_id} failed: {str(e)}")
            import traceback
            traceback.print_exc()

            # Mark task as failed
            task.status = TaskStatus.FAILED
            task.metadata['error'] = str(e)
            self.task_mgr.update_task(task)

        finally:
            self.current_task = None

    def _do_work(self, task: Task) -> Dict[str, Any]:
        """
        Perform the actual work for a task.

        In a real implementation, this would invoke Claude Code with the
        full context and task description. For now, it's a simulation.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        print(f"🔨 Executing task as {self.role} agent...")

        # Simulate work with checkpoints
        steps = [
            "Analyzing requirements",
            "Reading relevant files",
            "Implementing changes",
            "Writing tests",
            "Verifying results"
        ]

        for i, step in enumerate(steps, 1):
            print(f"   [{i}/{len(steps)}] {step}...")
            time.sleep(2)  # Simulate work

            # Save checkpoint every step
            self._save_checkpoint(f"step_{i}", {
                "current_step": i,
                "total_steps": len(steps),
                "completed_steps": steps[:i],
                "next_steps": steps[i:] if i < len(steps) else []
            })

            # Check for messages during execution
            self._process_messages()

        # Return result
        return {
            "status": "completed",
            "files_modified": [f"example_{self.role}_file.txt"],
            "summary": f"Completed {task.description} as {self.role} agent"
        }

    def _save_checkpoint(self, phase: str, additional_state: Optional[Dict] = None):
        """Save current state checkpoint."""
        if not self.current_task:
            return

        state = additional_state or {}
        state['phase'] = phase

        checkpoint = self.checkpoint_mgr.create_checkpoint_from_dict(
            agent_id=self.agent_id,
            role=self.role,
            task_id=self.current_task.task_id,
            state=state,
            work_in_progress={
                "task_description": self.current_task.description,
                "task_status": self.current_task.status.value
            },
            context_snapshot={
                "last_save": datetime.utcnow().isoformat()
            },
            communication_log=[]  # Would include recent messages
        )

        self.checkpoint_mgr.save_checkpoint(self.agent_id, checkpoint)

    def _process_messages(self):
        """Check and process incoming messages."""
        messages = self.message_bus.get_messages(self.agent_id, unread_only=True)

        for msg in messages:
            print(f"\n📨 Message from {msg.from_agent}")
            print(f"   Type: {msg.message_type.value}")

            if msg.message_type == MessageType.REQUEST_INFO:
                # Respond to information request
                question = msg.payload.get('question', '')
                print(f"   Question: {question}")

                # Send response
                self.message_bus.send_message(
                    self.agent_id,
                    msg.from_agent,
                    MessageType.PROVIDE_INFO,
                    {"response": f"Response from {self.role} agent: Acknowledged"},
                    reply_to=msg.message_id
                )
                print(f"   ✅ Sent response")

            elif msg.message_type == MessageType.NOTIFICATION:
                # Display notification
                notification = msg.payload.get('message', '')
                print(f"   Notification: {notification}")

            elif msg.message_type == MessageType.HANDOFF:
                # Handle work handoff
                task_id = msg.payload.get('task_id', '')
                print(f"   Handoff for task: {task_id}")

            # Mark message as read
            self.message_bus.mark_message_read(self.agent_id, msg.message_id)

    def _notify_dependents(self, completed_task_id: str):
        """Notify other agents that depend on this task."""
        # This would check dependency graph and notify waiting agents
        # For now, just broadcast a notification
        self.message_bus.broadcast_message(
            self.agent_id,
            MessageType.DEPENDENCY_READY,
            {
                "task_id": completed_task_id,
                "message": f"Task {completed_task_id} completed"
            }
        )

    def _shutdown(self):
        """Clean shutdown."""
        print(f"\n🛑 Shutting down agent {self.agent_id}")

        # Stop heartbeat
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)

        # Save final checkpoint if working on task
        if self.current_task:
            print(f"   Saving final checkpoint...")
            self._save_checkpoint("shutdown")

        # Unregister
        self.agent_registry.unregister_agent(self.agent_id)
        print(f"   Unregistered from orchestrator")

        print(f"✅ Agent {self.agent_id} stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Worker for Orchestration System"
    )
    parser.add_argument(
        "--agent-id",
        required=True,
        help="Unique agent identifier (e.g., frontend-001)"
    )
    parser.add_argument(
        "--role",
        required=True,
        choices=['frontend', 'backend', 'devops', 'qa', 'architect'],
        help="Agent role"
    )
    parser.add_argument(
        "--task-id",
        help="Task ID to execute (if not polling)"
    )
    parser.add_argument(
        "--context-file",
        required=True,
        help="Path to context file (role + project context)"
    )
    parser.add_argument(
        "--comm-dir",
        default=".agent-comm",
        help="Communication directory (default: .agent-comm)"
    )

    args = parser.parse_args()

    # Create worker
    worker = AgentWorker(
        agent_id=args.agent_id,
        role=args.role,
        task_id=args.task_id,
        context_file=args.context_file,
        comm_dir=args.comm_dir
    )

    # Start worker
    worker.start()


if __name__ == "__main__":
    main()
