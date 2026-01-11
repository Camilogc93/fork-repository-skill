#!/usr/bin/env python3
"""
Orchestration Layer for Agent System

Handles task management, dependency resolution, and agent registry for
coordinating multiple agents working on complex development workflows.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
from collections import defaultdict


class TaskStatus(str, Enum):
    """Task status states."""
    PLANNED = "planned"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    WAITING_HANDOFF = "waiting_handoff"
    REVIEW = "review"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"


@dataclass
class Task:
    """Task data structure."""
    task_id: str
    description: str
    assigned_to: Optional[str] = None
    role: Optional[str] = None
    status: TaskStatus = TaskStatus.PLANNED
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create from dictionary."""
        data['status'] = TaskStatus(data.get('status', TaskStatus.PLANNED))
        data['priority'] = TaskPriority(data.get('priority', TaskPriority.MEDIUM))
        return cls(**data)


class TaskManager:
    """Manages task lifecycle and operations."""

    def __init__(self, comm_dir: str = ".agent-comm"):
        """Initialize task manager."""
        self.comm_dir = Path(comm_dir)
        self.tasks_dir = self.comm_dir / "orchestration" / "tasks"

        # Create task directories
        for status in ["pending", "in-progress", "blocked", "completed"]:
            (self.tasks_dir / status).mkdir(parents=True, exist_ok=True)

    def create_task(
        self,
        task_id: str,
        description: str,
        role: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            task_id: Unique task identifier
            description: Task description
            role: Required agent role
            priority: Task priority
            dependencies: List of task IDs this task depends on
            metadata: Additional task metadata

        Returns:
            Created Task object
        """
        task = Task(
            task_id=task_id,
            description=description,
            role=role,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )

        # Save to pending directory
        self._save_task(task, "pending")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object or None if not found
        """
        # Search in all directories
        for status_dir in ["pending", "in-progress", "blocked", "completed"]:
            task_file = self.tasks_dir / status_dir / f"{task_id}.json"
            if task_file.exists():
                return self._load_task(task_file)
        return None

    def update_task(self, task: Task) -> bool:
        """
        Update an existing task.

        Args:
            task: Task object with updated data

        Returns:
            True if successful, False if task not found
        """
        # Find current location
        current_file = self._find_task_file(task.task_id)
        if not current_file:
            return False

        # Delete old file
        current_file.unlink()

        # Save to appropriate directory based on status
        status_map = {
            TaskStatus.PLANNED: "pending",
            TaskStatus.QUEUED: "pending",
            TaskStatus.ASSIGNED: "pending",
            TaskStatus.IN_PROGRESS: "in-progress",
            TaskStatus.BLOCKED: "blocked",
            TaskStatus.WAITING_HANDOFF: "in-progress",
            TaskStatus.REVIEW: "in-progress",
            TaskStatus.COMPLETED: "completed",
            TaskStatus.VERIFIED: "completed",
            TaskStatus.FAILED: "completed"
        }

        directory = status_map.get(task.status, "pending")
        self._save_task(task, directory)
        return True

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if deleted, False if not found
        """
        task_file = self._find_task_file(task_id)
        if not task_file:
            return False

        task_file.unlink()
        return True

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign task to an agent.

        Args:
            task_id: Task identifier
            agent_id: Agent identifier

        Returns:
            True if successful, False if task not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.assigned_to = agent_id
        task.status = TaskStatus.ASSIGNED
        return self.update_task(task)

    def start_task(self, task_id: str) -> bool:
        """
        Mark task as started.

        Args:
            task_id: Task identifier

        Returns:
            True if successful, False if task not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow().isoformat()
        return self.update_task(task)

    def block_task(self, task_id: str, reason: str) -> bool:
        """
        Mark task as blocked.

        Args:
            task_id: Task identifier
            reason: Reason for blocking

        Returns:
            True if successful, False if task not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.status = TaskStatus.BLOCKED
        task.metadata['blocked_reason'] = reason
        task.metadata['blocked_at'] = datetime.utcnow().isoformat()
        return self.update_task(task)

    def complete_task(self, task_id: str, result: Optional[Dict] = None) -> bool:
        """
        Mark task as completed.

        Args:
            task_id: Task identifier
            result: Task result data

        Returns:
            True if successful, False if task not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow().isoformat()
        if result:
            task.metadata['result'] = result
        return self.update_task(task)

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return self._get_tasks_in_directory("pending")

    def get_tasks_for_agent(self, agent_id: str) -> List[Task]:
        """Get all tasks assigned to an agent."""
        all_tasks = []
        for status_dir in ["pending", "in-progress", "blocked"]:
            all_tasks.extend(self._get_tasks_in_directory(status_dir))

        return [t for t in all_tasks if t.assigned_to == agent_id]

    def get_blocked_tasks(self) -> List[Task]:
        """Get all blocked tasks."""
        return self._get_tasks_in_directory("blocked")

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with given status."""
        all_tasks = []
        for status_dir in ["pending", "in-progress", "blocked", "completed"]:
            all_tasks.extend(self._get_tasks_in_directory(status_dir))

        return [t for t in all_tasks if t.status == status]

    def get_tasks_by_role(self, role: str) -> List[Task]:
        """Get all tasks requiring a specific role."""
        all_tasks = []
        for status_dir in ["pending", "in-progress", "blocked"]:
            all_tasks.extend(self._get_tasks_in_directory(status_dir))

        return [t for t in all_tasks if t.role == role]

    def _save_task(self, task: Task, directory: str):
        """Save task to file."""
        task_file = self.tasks_dir / directory / f"{task.task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)

    def _load_task(self, task_file: Path) -> Task:
        """Load task from file."""
        with open(task_file) as f:
            data = json.load(f)
        return Task.from_dict(data)

    def _find_task_file(self, task_id: str) -> Optional[Path]:
        """Find task file in any directory."""
        for status_dir in ["pending", "in-progress", "blocked", "completed"]:
            task_file = self.tasks_dir / status_dir / f"{task_id}.json"
            if task_file.exists():
                return task_file
        return None

    def _get_tasks_in_directory(self, directory: str) -> List[Task]:
        """Get all tasks in a directory."""
        tasks = []
        task_dir = self.tasks_dir / directory
        for task_file in task_dir.glob("*.json"):
            try:
                tasks.append(self._load_task(task_file))
            except Exception:
                pass  # Skip corrupted files
        return tasks


class DependencyManager:
    """Manages task dependencies and resolution."""

    def __init__(self, comm_dir: str = ".agent-comm"):
        """Initialize dependency manager."""
        self.comm_dir = Path(comm_dir)
        self.dependencies_file = (
            self.comm_dir / "orchestration" / "dependencies.json"
        )
        self.dependencies_file.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize dependencies
        self.dependencies: Dict[str, List[str]] = self._load_dependencies()

    def add_dependency(self, task_id: str, depends_on_task_id: str):
        """
        Add a dependency: task_id depends on depends_on_task_id.

        Args:
            task_id: Task that has the dependency
            depends_on_task_id: Task that must complete first
        """
        if task_id not in self.dependencies:
            self.dependencies[task_id] = []

        if depends_on_task_id not in self.dependencies[task_id]:
            self.dependencies[task_id].append(depends_on_task_id)

        # Check for circular dependencies
        if self._has_circular_dependency(task_id):
            # Remove the dependency that created the cycle
            self.dependencies[task_id].remove(depends_on_task_id)
            raise ValueError(f"Circular dependency detected: {task_id} -> {depends_on_task_id}")

        self._save_dependencies()

    def remove_dependency(self, task_id: str, depends_on_task_id: str):
        """Remove a dependency."""
        if task_id in self.dependencies:
            if depends_on_task_id in self.dependencies[task_id]:
                self.dependencies[task_id].remove(depends_on_task_id)
                self._save_dependencies()

    def get_dependencies(self, task_id: str) -> List[str]:
        """Get all tasks that task_id depends on."""
        return self.dependencies.get(task_id, [])

    def get_dependents(self, task_id: str) -> List[str]:
        """Get all tasks that depend on task_id."""
        dependents = []
        for task, deps in self.dependencies.items():
            if task_id in deps:
                dependents.append(task)
        return dependents

    def is_task_ready(self, task_id: str, task_manager: TaskManager) -> bool:
        """
        Check if all dependencies are completed.

        Args:
            task_id: Task to check
            task_manager: TaskManager instance to check task status

        Returns:
            True if all dependencies are completed
        """
        deps = self.get_dependencies(task_id)

        for dep_id in deps:
            dep_task = task_manager.get_task(dep_id)
            if not dep_task:
                return False  # Dependency doesn't exist
            if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.VERIFIED]:
                return False  # Dependency not completed

        return True

    def get_ready_tasks(self, task_manager: TaskManager) -> List[str]:
        """
        Get all pending tasks whose dependencies are satisfied.

        Args:
            task_manager: TaskManager instance

        Returns:
            List of task IDs that are ready to start
        """
        pending_tasks = task_manager.get_pending_tasks()
        ready = []

        for task in pending_tasks:
            if self.is_task_ready(task.task_id, task_manager):
                ready.append(task.task_id)

        return ready

    def resolve_dependency_chain(self, task_id: str) -> List[str]:
        """
        Resolve the full dependency chain for a task (topological sort).

        Args:
            task_id: Task identifier

        Returns:
            List of task IDs in execution order
        """
        visited = set()
        order = []

        def visit(tid: str):
            if tid in visited:
                return
            visited.add(tid)

            # Visit dependencies first
            for dep_id in self.get_dependencies(tid):
                visit(dep_id)

            order.append(tid)

        visit(task_id)
        return order

    def _has_circular_dependency(self, start_task: str) -> bool:
        """Check if there's a circular dependency starting from start_task."""
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep_id in self.get_dependencies(task_id):
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        return has_cycle(start_task)

    def _load_dependencies(self) -> Dict[str, List[str]]:
        """Load dependencies from file."""
        if not self.dependencies_file.exists():
            return {}

        try:
            with open(self.dependencies_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_dependencies(self):
        """Save dependencies to file."""
        with open(self.dependencies_file, 'w') as f:
            json.dump(self.dependencies, f, indent=2)


@dataclass
class AgentInfo:
    """Agent registry information."""
    agent_id: str
    role: str
    capabilities: List[str]
    status: str  # "active", "idle", "working", "offline"
    current_task: Optional[str] = None
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_heartbeat: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'AgentInfo':
        """Create from dictionary."""
        return cls(**data)


class AgentRegistry:
    """Manages active agents."""

    def __init__(self, comm_dir: str = ".agent-comm", max_agents: int = 5):
        """
        Initialize agent registry.

        Args:
            comm_dir: Communication directory
            max_agents: Maximum concurrent agents
        """
        self.comm_dir = Path(comm_dir)
        self.registry_file = self.comm_dir / "agents" / "registry.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_agents = max_agents

        # Load registry
        self.agents: Dict[str, AgentInfo] = self._load_registry()

    def register_agent(
        self,
        agent_id: str,
        role: str,
        capabilities: List[str]
    ) -> bool:
        """
        Register a new agent.

        Args:
            agent_id: Agent identifier
            role: Agent role
            capabilities: List of capabilities

        Returns:
            True if registered, False if capacity reached
        """
        if len(self.agents) >= self.max_agents:
            return False

        agent = AgentInfo(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            status="active"
        )

        self.agents[agent_id] = agent
        self._save_registry()
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save_registry()
            return True
        return False

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: Optional[str] = None
    ) -> bool:
        """Update agent status."""
        if agent_id not in self.agents:
            return False

        self.agents[agent_id].status = status
        if current_task is not None:
            self.agents[agent_id].current_task = current_task
        self.agents[agent_id].last_heartbeat = datetime.utcnow().isoformat()

        self._save_registry()
        return True

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent info."""
        return self.agents.get(agent_id)

    def get_agents_by_role(self, role: str) -> List[AgentInfo]:
        """Get all agents with a specific role."""
        return [a for a in self.agents.values() if a.role == role]

    def get_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """Get all agents with a specific capability."""
        return [
            a for a in self.agents.values()
            if capability in a.capabilities
        ]

    def get_active_agents(self) -> List[AgentInfo]:
        """Get all active agents."""
        return [
            a for a in self.agents.values()
            if a.status in ["active", "idle", "working"]
        ]

    def get_available_slots(self) -> int:
        """Get number of available agent slots."""
        return self.max_agents - len(self.agents)

    def can_spawn_agent(self) -> bool:
        """Check if there's capacity for a new agent."""
        return len(self.agents) < self.max_agents

    def _load_registry(self) -> Dict[str, AgentInfo]:
        """Load registry from file."""
        if not self.registry_file.exists():
            return {}

        try:
            with open(self.registry_file) as f:
                data = json.load(f)
                agents_data = data.get('agents', {})
                return {
                    aid: AgentInfo.from_dict(info)
                    for aid, info in agents_data.items()
                }
        except Exception:
            return {}

    def _save_registry(self):
        """Save registry to file."""
        data = {
            "version": "1.0.0",
            "max_concurrent_agents": self.max_agents,
            "agents": {
                aid: agent.to_dict()
                for aid, agent in self.agents.items()
            },
            "last_updated": datetime.utcnow().isoformat()
        }

        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    # Example usage
    print("Orchestration Layer - Example Usage")
    print("=" * 50)

    # Initialize managers
    task_mgr = TaskManager()
    dep_mgr = DependencyManager()
    agent_reg = AgentRegistry()

    # Create tasks
    task1 = task_mgr.create_task(
        "task-001",
        "Implement OAuth flow",
        role="backend",
        priority=TaskPriority.HIGH
    )
    print(f"✓ Created task: {task1.task_id}")

    task2 = task_mgr.create_task(
        "task-002",
        "Create login UI",
        role="frontend",
        priority=TaskPriority.HIGH,
        dependencies=["task-001"]
    )
    print(f"✓ Created task: {task2.task_id}")

    # Add dependency
    dep_mgr.add_dependency("task-002", "task-001")
    print(f"✓ Added dependency: task-002 depends on task-001")

    # Register agent
    agent_reg.register_agent("backend-001", "backend", ["python", "fastapi"])
    print(f"✓ Registered agent: backend-001")

    # Check ready tasks
    ready = dep_mgr.get_ready_tasks(task_mgr)
    print(f"✓ Ready tasks: {ready}")

    print("\n✓ Orchestration layer working correctly!")
