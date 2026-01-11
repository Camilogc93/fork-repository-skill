#!/usr/bin/env python3
"""
Main Orchestrator - Hybrid Agent Coordination System

The orchestrator manages complex development workflows by:
- Breaking down features into tasks
- Assigning tasks to specialized agents
- Monitoring agent health and progress
- Coordinating peer-to-peer communication
- Handling workflow pause/resume
- Providing visibility into progress

This is the main entry point for multi-agent orchestration.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from orchestrator import (
    TaskManager, DependencyManager, AgentRegistry,
    Task, TaskStatus, TaskPriority
)
from checkpoint_manager import CheckpointManager
from message_bus import MessageBus
from health_monitor import create_integrated_monitor
from fork_terminal import fork_agent


@dataclass
class Workflow:
    """Workflow data structure."""
    workflow_id: str
    name: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    paused_at: Optional[str] = None
    status: str = "planned"  # planned, running, paused, completed, failed
    tasks: List[str] = field(default_factory=list)  # Task IDs
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "paused_at": self.paused_at,
            "status": self.status,
            "tasks": self.tasks,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Workflow':
        """Create from dictionary."""
        return cls(**data)


class MainOrchestrator:
    """
    Main orchestrator for hybrid agent system.

    Coordinates multiple specialized agents working on complex tasks.
    """

    def __init__(self, comm_dir: str = ".agent-comm"):
        """
        Initialize main orchestrator.

        Args:
            comm_dir: Communication directory
        """
        self.comm_dir = Path(comm_dir)
        self.workflows_dir = self.comm_dir / "orchestration" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        # Core managers
        self.task_mgr = TaskManager(str(self.comm_dir))
        self.dep_mgr = DependencyManager(str(self.comm_dir))
        self.agent_registry = AgentRegistry(str(self.comm_dir))
        self.checkpoint_mgr = CheckpointManager(str(self.comm_dir / "checkpoints"))
        self.message_bus = MessageBus(str(self.comm_dir))

        # Health monitoring with auto-recovery
        self.health_monitor, self.recovery_mgr = create_integrated_monitor(
            str(self.comm_dir),
            auto_recover=True
        )

        # Current workflow
        self.current_workflow: Optional[Workflow] = None

        # Agent counter
        self._agent_counter = 0

    def create_workflow(
        self,
        name: str,
        description: str,
        tasks_breakdown: List[Dict[str, Any]]
    ) -> str:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            description: Workflow description
            tasks_breakdown: List of task definitions

        Returns:
            Workflow ID

        Example:
            >>> tasks = [
            ...     {
            ...         "description": "Implement OAuth flow",
            ...         "role": "backend",
            ...         "priority": "high"
            ...     },
            ...     {
            ...         "description": "Create login UI",
            ...         "role": "frontend",
            ...         "priority": "high",
            ...         "dependencies": ["task-001"]
            ...     }
            ... ]
            >>> workflow_id = orchestrator.create_workflow(
            ...     "User Authentication",
            ...     "Add OAuth authentication",
            ...     tasks
            ... )
        """
        # Generate workflow ID
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        workflow_id = f"workflow-{timestamp}"

        # Create tasks
        task_ids = []
        task_id_map = {}  # Map index to task_id for dependencies

        for i, task_def in enumerate(tasks_breakdown):
            task_id = f"task-{workflow_id}-{i+1:03d}"
            task_id_map[i] = task_id

            # Create task
            task = self.task_mgr.create_task(
                task_id=task_id,
                description=task_def["description"],
                role=task_def.get("role"),
                priority=TaskPriority(task_def.get("priority", "P2")),
                metadata=task_def.get("metadata", {})
            )

            task_ids.append(task_id)

            # Add dependencies (by index)
            if "dependencies" in task_def:
                for dep_index in task_def["dependencies"]:
                    if isinstance(dep_index, int):
                        dep_task_id = task_id_map[dep_index]
                        self.dep_mgr.add_dependency(task_id, dep_task_id)

        # Create workflow
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            tasks=task_ids
        )

        # Save workflow
        self._save_workflow(workflow)

        print(f"✅ Created workflow: {workflow_id}")
        print(f"   Name: {name}")
        print(f"   Tasks: {len(task_ids)}")

        return workflow_id

    def start_workflow(self, workflow_id: str):
        """
        Start a workflow.

        Args:
            workflow_id: Workflow identifier
        """
        # Load workflow
        workflow = self._load_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow.status == "running":
            print(f"⚠️  Workflow {workflow_id} is already running")
            return

        print(f"\n🚀 Starting Workflow: {workflow.name}")
        print(f"   ID: {workflow_id}")
        print(f"   Tasks: {len(workflow.tasks)}")
        print("=" * 60)

        # Update workflow status
        workflow.status = "running"
        workflow.started_at = datetime.utcnow().isoformat()
        self._save_workflow(workflow)

        self.current_workflow = workflow

        # Start health monitoring
        self.health_monitor.start_monitoring()
        print("✅ Health monitoring started")

        # Execute workflow
        self._execute_workflow(workflow)

    def _execute_workflow(self, workflow: Workflow):
        """
        Execute workflow by spawning agents and monitoring progress.

        Args:
            workflow: Workflow to execute
        """
        print(f"\n📋 Executing workflow: {workflow.name}\n")

        try:
            while True:
                # Check if workflow is complete
                if self._is_workflow_complete(workflow):
                    print(f"\n✅ Workflow complete: {workflow.name}")
                    workflow.status = "completed"
                    workflow.completed_at = datetime.utcnow().isoformat()
                    self._save_workflow(workflow)
                    break

                # Get ready tasks (dependencies met)
                ready_tasks = self.dep_mgr.get_ready_tasks(self.task_mgr)

                # Filter to workflow tasks
                workflow_ready_tasks = [
                    tid for tid in ready_tasks
                    if tid in workflow.tasks
                ]

                # Spawn agents for ready tasks
                for task_id in workflow_ready_tasks:
                    task = self.task_mgr.get_task(task_id)
                    if task and task.status == TaskStatus.PLANNED:
                        # Check if we have capacity
                        if self.agent_registry.can_spawn_agent():
                            self._spawn_agent_for_task(task)
                        else:
                            print(f"⏳ Waiting for agent capacity (task: {task_id})")

                # Sleep and check again
                time.sleep(5)

                # Check for failed tasks
                failed_tasks = [
                    self.task_mgr.get_task(tid)
                    for tid in workflow.tasks
                ]
                failed_tasks = [
                    t for t in failed_tasks
                    if t and t.status == TaskStatus.FAILED
                ]

                if failed_tasks:
                    print(f"\n❌ Workflow failed: {len(failed_tasks)} task(s) failed")
                    workflow.status = "failed"
                    workflow.metadata['failed_tasks'] = [t.task_id for t in failed_tasks]
                    self._save_workflow(workflow)
                    break

        except KeyboardInterrupt:
            print(f"\n\n⏸️  Workflow paused by user")
            self.pause_workflow(workflow.workflow_id)

        finally:
            # Stop health monitoring
            self.health_monitor.stop_monitoring()

    def _spawn_agent_for_task(self, task: Task):
        """
        Spawn an agent to execute a task.

        Args:
            task: Task to execute
        """
        if not task.role:
            print(f"⚠️  Task {task.task_id} has no role specified")
            return

        # Generate agent ID
        self._agent_counter += 1
        agent_id = f"{task.role}-{self._agent_counter:03d}"

        print(f"\n🤖 Spawning {task.role} agent: {agent_id}")
        print(f"   Task: {task.task_id}")
        print(f"   Description: {task.description}")

        try:
            # Prepare task dict for agent
            task_dict = {
                "task_id": task.task_id,
                "description": task.description,
                "priority": task.priority.value,
                "metadata": task.metadata
            }

            # Spawn agent
            fork_agent(
                agent_id=agent_id,
                role=task.role,
                task=task_dict,
                comm_dir=str(self.comm_dir)
            )

            # Mark task as assigned
            self.task_mgr.assign_task(task.task_id, agent_id)

            print(f"✅ Agent spawned successfully")

        except Exception as e:
            print(f"❌ Failed to spawn agent: {str(e)}")
            import traceback
            traceback.print_exc()

    def _is_workflow_complete(self, workflow: Workflow) -> bool:
        """Check if all workflow tasks are complete."""
        for task_id in workflow.tasks:
            task = self.task_mgr.get_task(task_id)
            if not task:
                return False
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]:
                return False
        return True

    def pause_workflow(self, workflow_id: str):
        """
        Pause a workflow.

        Args:
            workflow_id: Workflow identifier
        """
        workflow = self._load_workflow(workflow_id)
        if not workflow:
            return

        print(f"\n⏸️  Pausing workflow: {workflow.name}")

        workflow.status = "paused"
        workflow.paused_at = datetime.utcnow().isoformat()

        # Save snapshot
        self._save_workflow_snapshot(workflow)

        print(f"✅ Workflow paused and snapshot saved")

    def resume_workflow(self, workflow_id: str):
        """
        Resume a paused workflow.

        Args:
            workflow_id: Workflow identifier
        """
        workflow = self._load_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow.status != "paused":
            raise ValueError(f"Workflow {workflow_id} is not paused")

        print(f"\n▶️  Resuming workflow: {workflow.name}")
        print(f"   Paused: {workflow.paused_at}")

        # Check for agents that need to resume
        for task_id in workflow.tasks:
            task = self.task_mgr.get_task(task_id)
            if task and task.status == TaskStatus.IN_PROGRESS:
                # Check if agent still exists
                if task.assigned_to:
                    if not self.health_monitor.is_agent_alive(task.assigned_to):
                        print(f"   🔄 Resuming task {task_id} (agent was offline)")
                        # Spawn new agent with checkpoint
                        self._spawn_agent_for_task(task)

        # Resume workflow
        workflow.status = "running"
        workflow.paused_at = None
        self._save_workflow(workflow)

        # Continue execution
        self.start_workflow(workflow_id)

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow status.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Status dictionary
        """
        workflow = self._load_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        # Get task statuses
        task_statuses = {}
        for task_id in workflow.tasks:
            task = self.task_mgr.get_task(task_id)
            if task:
                task_statuses[task_id] = {
                    "description": task.description,
                    "status": task.status.value,
                    "assigned_to": task.assigned_to,
                    "role": task.role
                }

        # Get agent health
        agent_health = self.health_monitor.check_agent_health()

        return {
            "workflow": workflow.to_dict(),
            "tasks": task_statuses,
            "agents": {
                aid: {"status": h.status, "last_heartbeat": h.last_heartbeat.isoformat()}
                for aid, h in agent_health.items()
            },
            "progress": {
                "total": len(workflow.tasks),
                "completed": sum(
                    1 for t in task_statuses.values()
                    if t["status"] in ["completed", "verified"]
                ),
                "in_progress": sum(
                    1 for t in task_statuses.values()
                    if t["status"] == "in_progress"
                ),
                "pending": sum(
                    1 for t in task_statuses.values()
                    if t["status"] in ["planned", "queued", "assigned"]
                )
            }
        }

    def _save_workflow(self, workflow: Workflow):
        """Save workflow to file."""
        workflow_file = self.workflows_dir / f"{workflow.workflow_id}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow.to_dict(), f, indent=2)

    def _load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load workflow from file."""
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        if not workflow_file.exists():
            return None

        with open(workflow_file) as f:
            data = json.load(f)
        return Workflow.from_dict(data)

    def _save_workflow_snapshot(self, workflow: Workflow):
        """Save workflow snapshot for resuming."""
        snapshot = {
            "workflow": workflow.to_dict(),
            "tasks": {},
            "agents": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Save task states
        for task_id in workflow.tasks:
            task = self.task_mgr.get_task(task_id)
            if task:
                snapshot["tasks"][task_id] = task.to_dict()

        # Save agent states
        for agent in self.agent_registry.get_active_agents():
            checkpoint = self.checkpoint_mgr.load_latest_checkpoint(agent.agent_id)
            if checkpoint:
                snapshot["agents"][agent.agent_id] = checkpoint.to_dict()

        # Write snapshot
        snapshot_file = self.workflows_dir / f"{workflow.workflow_id}-snapshot.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)


def break_down_feature(feature_description: str) -> List[Dict[str, Any]]:
    """
    Break down a feature into tasks.

    In a real implementation, this would use Claude to analyze the feature
    and create a detailed task breakdown. For now, returns example breakdown.

    Args:
        feature_description: Feature description

    Returns:
        List of task definitions
    """
    # This is a simplified version. Real implementation would use Claude API.
    # For demonstration, return a template breakdown

    print(f"🤔 Analyzing feature: {feature_description}")
    print("   (In production, Claude would break this down intelligently)")

    # Example breakdown for authentication feature
    if "auth" in feature_description.lower():
        return [
            {
                "description": "Implement OAuth flow and JWT token generation",
                "role": "backend",
                "priority": "P1",
                "metadata": {"expected_files": ["backend/auth.py", "backend/jwt.py"]}
            },
            {
                "description": "Configure OAuth credentials in environment",
                "role": "devops",
                "priority": "P1",
                "dependencies": []
            },
            {
                "description": "Create login UI component with form validation",
                "role": "frontend",
                "priority": "P1",
                "dependencies": [0],  # Depends on backend OAuth
                "metadata": {"expected_files": ["frontend/components/Login.tsx"]}
            },
            {
                "description": "Write integration tests for authentication flow",
                "role": "qa",
                "priority": "P1",
                "dependencies": [0, 2]
            },
            {
                "description": "Deploy to staging environment",
                "role": "devops",
                "priority": "P2",
                "dependencies": [3]
            }
        ]

    # Generic breakdown
    return [
        {
            "description": f"Implement {feature_description}",
            "role": "backend",
            "priority": "P1"
        }
    ]


if __name__ == "__main__":
    # Example usage
    print("Main Orchestrator - Example Usage")
    print("=" * 60)

    # Create orchestrator
    orchestrator = MainOrchestrator()

    # Break down feature
    tasks = break_down_feature("user authentication with OAuth")

    # Create workflow
    workflow_id = orchestrator.create_workflow(
        name="User Authentication",
        description="Add OAuth authentication to application",
        tasks_breakdown=tasks
    )

    print(f"\n✅ Workflow created: {workflow_id}")
    print("\n💡 To start the workflow:")
    print(f"   orchestrator.start_workflow('{workflow_id}')")
    print("\n💡 To check status:")
    print(f"   status = orchestrator.get_workflow_status('{workflow_id}')")
