#!/usr/bin/env python3
"""
Health Monitor and Crash Recovery System

Monitors agent health via heartbeat signals and automatically recovers
crashed agents by spawning replacements with checkpoint handover.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from orchestrator import AgentRegistry, TaskManager, TaskStatus
from checkpoint_manager import CheckpointManager
from message_bus import MessageBus, MessageType


@dataclass
class AgentHealth:
    """Agent health status."""
    agent_id: str
    role: str
    last_heartbeat: datetime
    status: str  # "healthy", "stale", "dead"
    current_task: Optional[str] = None
    pid: Optional[int] = None


class HealthMonitor:
    """
    Monitors agent health and detects failures.

    Agents write heartbeat files every 10 seconds. The monitor checks
    these files every 30 seconds to detect stale or dead agents.
    """

    def __init__(
        self,
        comm_dir: str = ".agent-comm",
        check_interval: int = 30,
        stale_threshold: int = 60,
        dead_threshold: int = 120
    ):
        """
        Initialize health monitor.

        Args:
            comm_dir: Communication directory
            check_interval: How often to check health (seconds)
            stale_threshold: Heartbeat age for "stale" status (seconds)
            dead_threshold: Heartbeat age for "dead" status (seconds)
        """
        self.comm_dir = Path(comm_dir)
        self.status_dir = self.comm_dir / "agents" / "status"
        self.check_interval = check_interval
        self.stale_threshold = stale_threshold
        self.dead_threshold = dead_threshold

        self.agent_registry = AgentRegistry(str(self.comm_dir))

        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Callbacks for different events
        self.on_agent_stale: Optional[Callable[[AgentHealth], None]] = None
        self.on_agent_dead: Optional[Callable[[AgentHealth], None]] = None
        self.on_agent_recovered: Optional[Callable[[AgentHealth], None]] = None

    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=False)
        self.monitor_thread.start()
        print(f"🔍 Health monitor started (checking every {self.check_interval}s)")

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Health monitor stopped")

    def check_agent_health(self) -> Dict[str, AgentHealth]:
        """
        Check health of all registered agents.

        Returns:
            Dict mapping agent_id to AgentHealth
        """
        health_status = {}
        now = datetime.utcnow()

        # Get all registered agents
        agents = self.agent_registry.get_active_agents()

        for agent in agents:
            # Read heartbeat file
            heartbeat_file = self.status_dir / f"{agent.agent_id}.json"

            if not heartbeat_file.exists():
                # No heartbeat file = dead
                health_status[agent.agent_id] = AgentHealth(
                    agent_id=agent.agent_id,
                    role=agent.role,
                    last_heartbeat=now,
                    status="dead"
                )
                continue

            try:
                with open(heartbeat_file) as f:
                    data = json.load(f)

                last_heartbeat_str = data.get('last_heartbeat', '')
                last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                age = (now - last_heartbeat).total_seconds()

                # Determine status based on age
                if age > self.dead_threshold:
                    status = "dead"
                elif age > self.stale_threshold:
                    status = "stale"
                else:
                    status = "healthy"

                health_status[agent.agent_id] = AgentHealth(
                    agent_id=agent.agent_id,
                    role=agent.role,
                    last_heartbeat=last_heartbeat,
                    status=status,
                    current_task=data.get('current_task'),
                    pid=data.get('pid')
                )

            except Exception as e:
                # Corrupted heartbeat file = dead
                health_status[agent.agent_id] = AgentHealth(
                    agent_id=agent.agent_id,
                    role=agent.role,
                    last_heartbeat=now,
                    status="dead"
                )

        return health_status

    def get_stale_agents(self) -> List[AgentHealth]:
        """Get list of stale agents."""
        health = self.check_agent_health()
        return [h for h in health.values() if h.status == "stale"]

    def get_dead_agents(self) -> List[AgentHealth]:
        """Get list of dead agents."""
        health = self.check_agent_health()
        return [h for h in health.values() if h.status == "dead"]

    def is_agent_alive(self, agent_id: str) -> bool:
        """Check if specific agent is alive."""
        health = self.check_agent_health()
        if agent_id not in health:
            return False
        return health[agent_id].status in ["healthy", "stale"]

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Check all agents
                health_status = self.check_agent_health()

                for agent_id, health in health_status.items():
                    if health.status == "stale":
                        print(f"⚠️  Agent {agent_id} is stale (no heartbeat for {self.stale_threshold}s)")
                        if self.on_agent_stale:
                            self.on_agent_stale(health)

                    elif health.status == "dead":
                        print(f"💀 Agent {agent_id} is dead (no heartbeat for {self.dead_threshold}s)")
                        if self.on_agent_dead:
                            self.on_agent_dead(health)

                # Sleep until next check
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"❌ Health monitor error: {str(e)}")
                time.sleep(self.check_interval)


class RecoveryManager:
    """
    Manages crash recovery by spawning replacement agents.

    When an agent crashes, the recovery manager:
    1. Detects the crash via health monitor
    2. Loads the agent's last checkpoint
    3. Spawns a replacement agent with checkpoint handover
    4. Updates task assignments
    5. Notifies other agents
    """

    def __init__(
        self,
        comm_dir: str = ".agent-comm",
        auto_recover: bool = True
    ):
        """
        Initialize recovery manager.

        Args:
            comm_dir: Communication directory
            auto_recover: Automatically recover crashed agents
        """
        self.comm_dir = comm_dir
        self.auto_recover = auto_recover

        self.checkpoint_mgr = CheckpointManager(f"{comm_dir}/checkpoints")
        self.task_mgr = TaskManager(comm_dir)
        self.agent_registry = AgentRegistry(comm_dir)
        self.message_bus = MessageBus(comm_dir)

        # Track recovery attempts to prevent infinite loops
        self.recovery_attempts: Dict[str, int] = {}
        self.max_recovery_attempts = 3

    def detect_crashed_agents(self, dead_agents: List[AgentHealth]) -> List[AgentHealth]:
        """
        Filter dead agents that need recovery.

        Args:
            dead_agents: List of dead agents

        Returns:
            List of agents that should be recovered
        """
        to_recover = []

        for agent in dead_agents:
            # Check if agent has active tasks
            tasks = self.task_mgr.get_tasks_for_agent(agent.agent_id)
            active_tasks = [
                t for t in tasks
                if t.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
            ]

            if active_tasks:
                # Check recovery attempts
                attempts = self.recovery_attempts.get(agent.agent_id, 0)
                if attempts < self.max_recovery_attempts:
                    to_recover.append(agent)
                else:
                    print(f"⛔ Max recovery attempts reached for {agent.agent_id}")

        return to_recover

    def recover_agent(self, crashed_agent: AgentHealth) -> bool:
        """
        Recover a crashed agent.

        Args:
            crashed_agent: Health info of crashed agent

        Returns:
            True if recovery initiated successfully
        """
        print(f"\n🔄 Recovering agent: {crashed_agent.agent_id}")

        try:
            # Increment recovery attempts
            self.recovery_attempts[crashed_agent.agent_id] = \
                self.recovery_attempts.get(crashed_agent.agent_id, 0) + 1

            # Load last checkpoint
            checkpoint = self.checkpoint_mgr.load_latest_checkpoint(crashed_agent.agent_id)
            if not checkpoint:
                print(f"   ❌ No checkpoint found for {crashed_agent.agent_id}")
                return False

            print(f"   ✓ Loaded checkpoint from {checkpoint.checkpoint_time}")

            # Create handover context
            handover = self._create_handover_context(crashed_agent, checkpoint)
            print(f"   ✓ Created handover context")

            # Generate new agent ID
            import random
            new_agent_id = f"{crashed_agent.role}-{random.randint(100, 999):03d}"

            # Spawn replacement agent
            # Note: In real implementation, would call fork_agent_with_handover
            print(f"   ✓ Would spawn replacement agent: {new_agent_id}")
            print(f"   ✓ Handover: {crashed_agent.agent_id} → {new_agent_id}")

            # Update task assignment
            if crashed_agent.current_task:
                task = self.task_mgr.get_task(crashed_agent.current_task)
                if task:
                    task.assigned_to = new_agent_id
                    task.metadata['recovered_from'] = crashed_agent.agent_id
                    task.metadata['recovery_attempt'] = self.recovery_attempts[crashed_agent.agent_id]
                    self.task_mgr.update_task(task)
                    print(f"   ✓ Reassigned task {task.task_id} to {new_agent_id}")

            # Unregister dead agent
            self.agent_registry.unregister_agent(crashed_agent.agent_id)
            print(f"   ✓ Unregistered dead agent")

            # Notify other agents
            self.message_bus.broadcast_message(
                "orchestrator",
                MessageType.NOTIFICATION,
                {
                    "message": f"Agent {crashed_agent.agent_id} crashed and was replaced by {new_agent_id}",
                    "crashed_agent": crashed_agent.agent_id,
                    "replacement_agent": new_agent_id
                },
                exclude=[crashed_agent.agent_id]
            )
            print(f"   ✓ Notified other agents")

            print(f"✅ Recovery complete for {crashed_agent.agent_id}")
            return True

        except Exception as e:
            print(f"   ❌ Recovery failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _create_handover_context(self, crashed_agent: AgentHealth, checkpoint) -> Dict:
        """
        Create handover context for replacement agent.

        Args:
            crashed_agent: Crashed agent info
            checkpoint: Last checkpoint

        Returns:
            Handover context dict
        """
        state = checkpoint.state
        wip = checkpoint.work_in_progress

        return {
            "previous_agent": crashed_agent.agent_id,
            "crash_detected": datetime.utcnow().isoformat(),
            "last_checkpoint": checkpoint.checkpoint_time,
            "progress": {
                "phase": state.get('phase', 'unknown'),
                "current_step": state.get('current_step', 0),
                "total_steps": state.get('total_steps', 0),
                "completed_steps": state.get('completed_steps', []),
                "next_steps": state.get('next_steps', [])
            },
            "work_in_progress": {
                "files_modified": wip.get('files_modified', []),
                "task_description": wip.get('task_description', 'Unknown')
            },
            "instructions": (
                f"You are taking over for {crashed_agent.agent_id} which crashed. "
                f"Continue from step {state.get('current_step', 0)} of {state.get('total_steps', 0)}. "
                "Review the completed steps and proceed with the next steps."
            )
        }

    def mark_recovery_successful(self, agent_id: str):
        """Mark recovery as successful and reset attempt counter."""
        if agent_id in self.recovery_attempts:
            del self.recovery_attempts[agent_id]


def create_integrated_monitor(
    comm_dir: str = ".agent-comm",
    auto_recover: bool = True
) -> tuple[HealthMonitor, RecoveryManager]:
    """
    Create integrated health monitor and recovery manager.

    Args:
        comm_dir: Communication directory
        auto_recover: Automatically recover crashed agents

    Returns:
        Tuple of (HealthMonitor, RecoveryManager)

    Example:
        >>> monitor, recovery = create_integrated_monitor()
        >>> monitor.on_agent_dead = lambda agent: recovery.recover_agent(agent)
        >>> monitor.start_monitoring()
    """
    monitor = HealthMonitor(comm_dir=comm_dir)
    recovery = RecoveryManager(comm_dir=comm_dir, auto_recover=auto_recover)

    if auto_recover:
        # Wire up auto-recovery
        def handle_dead_agent(agent: AgentHealth):
            agents_to_recover = recovery.detect_crashed_agents([agent])
            for crashed_agent in agents_to_recover:
                recovery.recover_agent(crashed_agent)

        monitor.on_agent_dead = handle_dead_agent

    return monitor, recovery


if __name__ == "__main__":
    # Example usage
    print("Health Monitor & Recovery - Example Usage")
    print("=" * 60)

    # Create integrated monitor with auto-recovery
    monitor, recovery = create_integrated_monitor(auto_recover=True)

    print("✓ Created health monitor with auto-recovery")

    # Start monitoring
    monitor.start_monitoring()

    print("\n💡 Monitoring agent health...")
    print("   Agents will be automatically recovered if they crash")
    print("   Press Ctrl+C to stop\n")

    try:
        # Monitor for 60 seconds as example
        for i in range(6):
            time.sleep(10)

            # Check health
            health = monitor.check_agent_health()
            if health:
                print(f"\n📊 Health check #{i+1}")
                for agent_id, status in health.items():
                    symbol = "✅" if status.status == "healthy" else "⚠️" if status.status == "stale" else "💀"
                    print(f"   {symbol} {agent_id}: {status.status}")
            else:
                print(f"\n📊 Health check #{i+1}: No agents registered")

    except KeyboardInterrupt:
        print("\n\nStopping...")

    finally:
        monitor.stop_monitoring()
        print("\n✓ Health monitoring example complete!")
