#!/usr/bin/env python3
"""
Summary Dashboard for Agent Orchestration

Provides a real-time view of agent activity, task progress, and system status.
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from orchestrator import TaskManager, AgentRegistry, TaskStatus
from health_monitor import HealthMonitor


class Dashboard:
    """Visual dashboard for orchestration system."""

    def __init__(self, comm_dir: str = ".agent-comm"):
        """
        Initialize dashboard.

        Args:
            comm_dir: Communication directory
        """
        self.comm_dir = comm_dir
        self.task_mgr = TaskManager(comm_dir)
        self.agent_registry = AgentRegistry(comm_dir)
        self.health_monitor = HealthMonitor(comm_dir)

    def generate_summary(self, workflow_status: Optional[Dict] = None) -> str:
        """
        Generate summary dashboard view.

        Args:
            workflow_status: Optional workflow status dict

        Returns:
            Formatted dashboard string
        """
        lines = []

        # Header
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " " * 10 + "🎯 AGENT ORCHESTRATION DASHBOARD" + " " * 15 + "│")

        if workflow_status and workflow_status.get('workflow'):
            workflow = workflow_status['workflow']
            lines.append("│" + " " * 58 + "│")
            lines.append(f"│  Workflow: {workflow['name']:<44} │")
            lines.append(f"│  Status: {workflow['status']:<46} │")

        lines.append("└" + "─" * 58 + "┘")
        lines.append("")

        # Active agents section
        agents_view = self.generate_active_agents_view(workflow_status)
        lines.append(agents_view)

        # Task queue section
        if workflow_status:
            task_queue_view = self.generate_task_queue_view(workflow_status)
            lines.append(task_queue_view)

        # Recent activity
        activity_view = self.generate_activity_feed()
        lines.append(activity_view)

        return "\n".join(lines)

    def generate_active_agents_view(self, workflow_status: Optional[Dict] = None) -> str:
        """
        Generate active agents view.

        Args:
            workflow_status: Optional workflow status

        Returns:
            Formatted agents view
        """
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│  👥 ACTIVE AGENTS" + " " * 40 + "│")
        lines.append("└" + "─" * 58 + "┘")

        # Get agent health
        agent_health = self.health_monitor.check_agent_health()
        active_count = len([h for h in agent_health.values() if h.status == "healthy"])
        max_agents = self.agent_registry.max_agents

        lines.append(f"Active: {active_count}/{max_agents}")
        lines.append("")

        if not agent_health:
            lines.append("  No agents currently active")
            lines.append("")
            return "\n".join(lines)

        # List each agent
        for agent_id, health in sorted(agent_health.items()):
            # Status symbol
            if health.status == "healthy":
                symbol = "✅"
            elif health.status == "stale":
                symbol = "⚠️ "
            else:
                symbol = "💀"

            # Role emoji
            role_emoji = {
                "frontend": "🎨",
                "backend": "⚙️ ",
                "devops": "🚀",
                "qa": "✅",
                "architect": "📐"
            }.get(health.role, "🤖")

            lines.append(f"  {symbol} {role_emoji} {agent_id}")

            # Current task
            if health.current_task:
                task = self.task_mgr.get_task(health.current_task)
                if task:
                    # Progress bar (simplified)
                    progress = self._estimate_task_progress(task)
                    bar = self._generate_progress_bar(progress, width=30)
                    lines.append(f"     Task: {task.description[:40]}")
                    lines.append(f"     Progress: {bar} {progress}%")

                    # Time since last heartbeat
                    age = (datetime.utcnow() - health.last_heartbeat).total_seconds()
                    lines.append(f"     Last update: {int(age)}s ago")
            else:
                lines.append(f"     Status: Idle")

            lines.append("")

        return "\n".join(lines)

    def generate_task_queue_view(self, workflow_status: Dict) -> str:
        """
        Generate task queue view.

        Args:
            workflow_status: Workflow status dict

        Returns:
            Formatted task queue view
        """
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│  📋 TASK QUEUE" + " " * 43 + "│")
        lines.append("└" + "─" * 58 + "┘")

        progress_info = workflow_status.get('progress', {})
        lines.append(f"Total: {progress_info.get('total', 0)}")
        lines.append(f"Completed: {progress_info.get('completed', 0)}")
        lines.append(f"In Progress: {progress_info.get('in_progress', 0)}")
        lines.append(f"Pending: {progress_info.get('pending', 0)}")
        lines.append("")

        # Show pending/in-progress tasks
        tasks = workflow_status.get('tasks', {})
        shown = 0
        for task_id, task_info in tasks.items():
            if task_info['status'] in ['in_progress', 'assigned', 'queued'] and shown < 3:
                priority = self._get_task_priority_symbol(task_id)
                status_symbol = self._get_task_status_symbol(task_info['status'])

                lines.append(f"  {priority} {status_symbol} {task_info['description'][:45]}")

                if task_info.get('assigned_to'):
                    lines.append(f"     → {task_info['assigned_to']}")

                shown += 1

        if shown == 0:
            lines.append("  All tasks completed or no tasks active")

        lines.append("")
        return "\n".join(lines)

    def generate_activity_feed(self, limit: int = 5) -> str:
        """
        Generate recent activity feed.

        Args:
            limit: Number of recent activities to show

        Returns:
            Formatted activity feed
        """
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│  💬 RECENT ACTIVITY" + " " * 38 + "│")
        lines.append("└" + "─" * 58 + "┘")

        # Read communication log
        log_file = f"{self.comm_dir}/logs/communications.log"
        if not os.path.exists(log_file):
            lines.append("  No recent activity")
            lines.append("")
            return "\n".join(lines)

        try:
            with open(log_file) as f:
                log_lines = f.readlines()

            # Get last N lines
            recent = log_lines[-limit:] if len(log_lines) > limit else log_lines

            for line in recent:
                # Parse log line: [TIME] FROM → TO [TYPE] ID
                if "→" in line:
                    parts = line.split("→")
                    if len(parts) >= 2:
                        time_from = parts[0].strip()
                        to_rest = parts[1].strip()

                        # Extract time
                        if "[" in time_from:
                            time_str = time_from.split("[")[1].split("]")[0]
                            try:
                                dt = datetime.fromisoformat(time_str)
                                time_display = dt.strftime("%H:%M:%S")
                            except:
                                time_display = time_str[:8]
                        else:
                            time_display = "..."

                        # Truncate message
                        message = line[line.find("]")+1:].strip() if "]" in line else line.strip()
                        message = message[:48] + "..." if len(message) > 48 else message

                        lines.append(f"  {time_display}  {message}")

        except Exception as e:
            lines.append(f"  Error reading activity: {str(e)}")

        lines.append("")
        return "\n".join(lines)

    def generate_notifications(self) -> str:
        """
        Generate notifications section.

        Returns:
            Formatted notifications
        """
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│  🔔 NOTIFICATIONS" + " " * 40 + "│")
        lines.append("└" + "─" * 58 + "┘")

        # Check for blocked tasks
        blocked_tasks = self.task_mgr.get_blocked_tasks()
        if blocked_tasks:
            for task in blocked_tasks[:3]:  # Show max 3
                lines.append(f"  ⚠️  Task blocked: {task.description[:40]}")
                reason = task.metadata.get('blocked_reason', 'Unknown')
                lines.append(f"     Reason: {reason}")

        # Check for stale agents
        stale_agents = self.health_monitor.get_stale_agents()
        if stale_agents:
            for agent in stale_agents[:2]:  # Show max 2
                lines.append(f"  ⚠️  Agent stale: {agent.agent_id}")

        if not blocked_tasks and not stale_agents:
            lines.append("  No notifications")

        lines.append("")
        return "\n".join(lines)

    def _generate_progress_bar(self, percentage: int, width: int = 20) -> str:
        """
        Generate ASCII progress bar.

        Args:
            percentage: Progress percentage (0-100)
            width: Bar width in characters

        Returns:
            Progress bar string
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def _estimate_task_progress(self, task) -> int:
        """Estimate task progress based on status."""
        status_progress = {
            TaskStatus.PLANNED: 0,
            TaskStatus.QUEUED: 10,
            TaskStatus.ASSIGNED: 20,
            TaskStatus.IN_PROGRESS: 50,
            TaskStatus.BLOCKED: 50,
            TaskStatus.REVIEW: 80,
            TaskStatus.COMPLETED: 100,
            TaskStatus.VERIFIED: 100
        }
        return status_progress.get(task.status, 0)

    def _get_task_priority_symbol(self, task_id: str) -> str:
        """Get priority symbol for task."""
        task = self.task_mgr.get_task(task_id)
        if not task:
            return "[P?]"

        priority_symbols = {
            "P0": "[P0]",  # Critical
            "P1": "[P1]",  # High
            "P2": "[P2]",  # Medium
            "P3": "[P3]"   # Low
        }
        return priority_symbols.get(task.priority.value, "[P?]")

    def _get_task_status_symbol(self, status: str) -> str:
        """Get status symbol for task."""
        symbols = {
            "planned": "📝",
            "queued": "⏳",
            "assigned": "👤",
            "in_progress": "🔨",
            "blocked": "🚫",
            "review": "👀",
            "completed": "✅",
            "verified": "✅"
        }
        return symbols.get(status, "❓")

    def start_live_view(self, workflow_status_func, refresh_interval: int = 2):
        """
        Start live dashboard view that refreshes automatically.

        Args:
            workflow_status_func: Function that returns workflow status
            refresh_interval: Refresh interval in seconds
        """
        try:
            print("\n🔴 Live Dashboard (Press Ctrl+C to exit)\n")

            while True:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')

                # Get current status
                workflow_status = workflow_status_func()

                # Generate and print dashboard
                dashboard = self.generate_summary(workflow_status)
                print(dashboard)

                # Print instructions
                print("Commands:")
                print("  Press Ctrl+C to exit")
                print(f"  Refreshing every {refresh_interval}s...")

                # Sleep
                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n\n👋 Live dashboard stopped")


def print_dashboard(comm_dir: str = ".agent-comm", workflow_status: Optional[Dict] = None):
    """
    Convenience function to print dashboard.

    Args:
        comm_dir: Communication directory
        workflow_status: Optional workflow status
    """
    dashboard = Dashboard(comm_dir)
    summary = dashboard.generate_summary(workflow_status)
    print(summary)


if __name__ == "__main__":
    # Example usage
    print("Dashboard - Example Usage")
    print("=" * 60)

    # Create dashboard
    dashboard = Dashboard()

    # Generate summary
    print("\nDashboard Summary:")
    print("=" * 60)
    summary = dashboard.generate_summary()
    print(summary)

    print("\n✅ Dashboard generation complete!")
    print("\n💡 For live view:")
    print("   dashboard.start_live_view(lambda: orchestrator.get_workflow_status(wf_id))")
