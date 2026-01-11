# API Reference

Complete API documentation for the Agent Orchestration System.

## Table of Contents

- [MainOrchestrator](#mainorchestrator)
- [TaskManager](#taskmanager)
- [DependencyManager](#dependencymanager)
- [AgentRegistry](#agentregistry)
- [MessageBus](#messagebus)
- [CheckpointManager](#checkpointmanager)
- [HealthMonitor](#healthmonitor)
- [RecoveryManager](#recoverymanager)
- [Dashboard](#dashboard)
- [Data Classes](#data-classes)
- [Enums](#enums)
- [Utility Functions](#utility-functions)

---

## MainOrchestrator

**Module**: `orchestrator_main.py`

Main orchestration class that coordinates workflows, agents, and tasks.

### Constructor

```python
MainOrchestrator(comm_dir: str = ".agent-comm", max_agents: int = 5)
```

**Parameters**:
- `comm_dir` (str): Communication directory path. Default: `.agent-comm`
- `max_agents` (int): Maximum concurrent agents. Default: `5`

**Example**:
```python
from orchestrator_main import MainOrchestrator

orchestrator = MainOrchestrator()
# or with custom settings
orchestrator = MainOrchestrator(comm_dir="/tmp/agents", max_agents=3)
```

### Methods

#### create_workflow

```python
create_workflow(
    name: str,
    description: str,
    tasks_breakdown: List[Dict[str, Any]]
) -> str
```

Create a new workflow with tasks.

**Parameters**:
- `name` (str): Workflow name
- `description` (str): Workflow description
- `tasks_breakdown` (List[Dict]): List of task definitions

**Returns**: `str` - Workflow ID

**Example**:
```python
tasks = [
    {
        "description": "Task 1",
        "role": "backend",
        "priority": "P1",
        "dependencies": []
    }
]

workflow_id = orchestrator.create_workflow(
    name="My Feature",
    description="Implement feature X",
    tasks_breakdown=tasks
)
```

#### start_workflow

```python
start_workflow(workflow_id: str) -> None
```

Start workflow execution.

**Parameters**:
- `workflow_id` (str): Workflow identifier

**Example**:
```python
orchestrator.start_workflow(workflow_id)
```

#### pause_workflow

```python
pause_workflow(workflow_id: str) -> bool
```

Pause workflow and save snapshot.

**Parameters**:
- `workflow_id` (str): Workflow identifier

**Returns**: `bool` - True if paused successfully

**Example**:
```python
if orchestrator.pause_workflow(workflow_id):
    print("Workflow paused")
```

#### resume_workflow

```python
resume_workflow(workflow_id: str) -> bool
```

Resume paused workflow from snapshot.

**Parameters**:
- `workflow_id` (str): Workflow identifier

**Returns**: `bool` - True if resumed successfully

**Example**:
```python
if orchestrator.resume_workflow(workflow_id):
    print("Workflow resumed")
```

#### get_workflow_status

```python
get_workflow_status(workflow_id: str) -> Dict[str, Any]
```

Get current workflow status.

**Parameters**:
- `workflow_id` (str): Workflow identifier

**Returns**: `Dict` with structure:
```python
{
    "workflow": {
        "workflow_id": str,
        "name": str,
        "status": str,
        "created_at": str
    },
    "progress": {
        "total": int,
        "completed": int,
        "in_progress": int,
        "pending": int
    },
    "tasks": {
        "task-id": {
            "description": str,
            "status": str,
            "assigned_to": str
        }
    },
    "agents": {
        "agent-id": {
            "role": str,
            "status": str,
            "current_task": str
        }
    }
}
```

**Example**:
```python
status = orchestrator.get_workflow_status(workflow_id)
print(f"Progress: {status['progress']['completed']}/{status['progress']['total']}")
```

#### list_paused_workflows

```python
list_paused_workflows() -> List[Dict[str, Any]]
```

Get list of paused workflows.

**Returns**: List of workflow info dicts

**Example**:
```python
paused = orchestrator.list_paused_workflows()
for wf in paused:
    print(f"{wf['name']} paused at {wf['paused_at']}")
```

#### get_blocked_tasks

```python
get_blocked_tasks() -> List[Task]
```

Get list of blocked tasks.

**Returns**: List of Task objects

**Example**:
```python
blocked = orchestrator.get_blocked_tasks()
for task in blocked:
    print(f"Blocked: {task.description}")
    print(f"Reason: {task.metadata.get('blocked_reason')}")
```

---

## TaskManager

**Module**: `orchestrator.py`

Manages task lifecycle and assignment.

### Constructor

```python
TaskManager(comm_dir: str = ".agent-comm")
```

**Parameters**:
- `comm_dir` (str): Communication directory path

### Methods

#### create_task

```python
create_task(
    task_id: str,
    description: str,
    role: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    metadata: Optional[Dict] = None
) -> Task
```

Create a new task.

**Parameters**:
- `task_id` (str): Unique task identifier
- `description` (str): Task description
- `role` (str, optional): Required agent role
- `priority` (TaskPriority): Task priority. Default: `MEDIUM`
- `metadata` (Dict, optional): Additional task metadata

**Returns**: `Task` object

**Example**:
```python
from orchestrator import TaskManager, TaskPriority

task_mgr = TaskManager()

task = task_mgr.create_task(
    task_id="task-001",
    description="Implement user authentication",
    role="backend",
    priority=TaskPriority.HIGH,
    metadata={"estimated_hours": 4}
)
```

#### get_task

```python
get_task(task_id: str) -> Optional[Task]
```

Get task by ID.

**Parameters**:
- `task_id` (str): Task identifier

**Returns**: `Task` object or `None`

**Example**:
```python
task = task_mgr.get_task("task-001")
if task:
    print(f"Status: {task.status}")
```

#### assign_task

```python
assign_task(task_id: str, agent_id: str) -> bool
```

Assign task to an agent.

**Parameters**:
- `task_id` (str): Task identifier
- `agent_id` (str): Agent identifier

**Returns**: `bool` - True if assigned successfully

**Example**:
```python
if task_mgr.assign_task("task-001", "backend-001"):
    print("Task assigned")
```

#### start_task

```python
start_task(task_id: str) -> bool
```

Mark task as started.

**Parameters**:
- `task_id` (str): Task identifier

**Returns**: `bool` - True if status changed

**Example**:
```python
task_mgr.start_task("task-001")
```

#### complete_task

```python
complete_task(task_id: str, result: Optional[Dict] = None) -> bool
```

Mark task as completed.

**Parameters**:
- `task_id` (str): Task identifier
- `result` (Dict, optional): Task result data

**Returns**: `bool` - True if completed successfully

**Example**:
```python
result = {
    "files_modified": ["src/auth.py"],
    "tests_added": 5
}
task_mgr.complete_task("task-001", result)
```

#### get_tasks_by_role

```python
get_tasks_by_role(role: str) -> List[Task]
```

Get all tasks for a specific role.

**Parameters**:
- `role` (str): Agent role

**Returns**: List of `Task` objects

**Example**:
```python
backend_tasks = task_mgr.get_tasks_by_role("backend")
```

#### get_tasks_for_agent

```python
get_tasks_for_agent(agent_id: str) -> List[Task]
```

Get all tasks assigned to an agent.

**Parameters**:
- `agent_id` (str): Agent identifier

**Returns**: List of `Task` objects

**Example**:
```python
my_tasks = task_mgr.get_tasks_for_agent("backend-001")
```

#### get_blocked_tasks

```python
get_blocked_tasks() -> List[Task]
```

Get all blocked tasks.

**Returns**: List of `Task` objects with status `BLOCKED`

---

## DependencyManager

**Module**: `orchestrator.py`

Manages task dependencies and execution order.

### Constructor

```python
DependencyManager(comm_dir: str = ".agent-comm")
```

### Methods

#### add_dependency

```python
add_dependency(task_id: str, depends_on_task_id: str) -> bool
```

Add dependency between tasks.

**Parameters**:
- `task_id` (str): Task that depends on another
- `depends_on_task_id` (str): Task that must complete first

**Returns**: `bool` - True if added, False if circular dependency detected

**Example**:
```python
from orchestrator import DependencyManager

dep_mgr = DependencyManager()

# Task B depends on Task A
dep_mgr.add_dependency("task-B", "task-A")
```

#### get_dependencies

```python
get_dependencies(task_id: str) -> List[str]
```

Get list of task IDs that a task depends on.

**Parameters**:
- `task_id` (str): Task identifier

**Returns**: List of task IDs

**Example**:
```python
deps = dep_mgr.get_dependencies("task-B")
print(f"Task B depends on: {deps}")  # ["task-A"]
```

#### get_ready_tasks

```python
get_ready_tasks(task_manager: TaskManager) -> List[str]
```

Get tasks ready to execute (all dependencies met).

**Parameters**:
- `task_manager` (TaskManager): Task manager instance

**Returns**: List of task IDs ready for execution

**Example**:
```python
ready = dep_mgr.get_ready_tasks(task_mgr)
for task_id in ready:
    print(f"Ready: {task_id}")
```

#### check_circular_dependency

```python
check_circular_dependency() -> Optional[List[str]]
```

Check for circular dependencies in task graph.

**Returns**: List of task IDs in circular path, or `None` if no cycles

**Example**:
```python
cycle = dep_mgr.check_circular_dependency()
if cycle:
    print(f"Circular dependency: {' → '.join(cycle)}")
```

---

## AgentRegistry

**Module**: `orchestrator.py`

Manages agent registration and tracking.

### Constructor

```python
AgentRegistry(comm_dir: str = ".agent-comm", max_agents: int = 5)
```

**Parameters**:
- `comm_dir` (str): Communication directory
- `max_agents` (int): Maximum concurrent agents

### Methods

#### register_agent

```python
register_agent(
    agent_id: str,
    role: str,
    capabilities: List[str]
) -> bool
```

Register a new agent.

**Parameters**:
- `agent_id` (str): Unique agent identifier
- `role` (str): Agent role
- `capabilities` (List[str]): List of agent capabilities

**Returns**: `bool` - True if registered, False if max agents reached

**Example**:
```python
from orchestrator import AgentRegistry

registry = AgentRegistry()

registered = registry.register_agent(
    agent_id="backend-001",
    role="backend",
    capabilities=["api", "database", "business-logic"]
)
```

#### unregister_agent

```python
unregister_agent(agent_id: str) -> bool
```

Unregister an agent.

**Parameters**:
- `agent_id` (str): Agent identifier

**Returns**: `bool` - True if unregistered

**Example**:
```python
registry.unregister_agent("backend-001")
```

#### update_agent_status

```python
update_agent_status(
    agent_id: str,
    status: str,
    current_task: Optional[str] = None
) -> bool
```

Update agent status (heartbeat).

**Parameters**:
- `agent_id` (str): Agent identifier
- `status` (str): Status ("idle", "working", "error")
- `current_task` (str, optional): Current task ID

**Returns**: `bool` - True if updated

**Example**:
```python
registry.update_agent_status(
    agent_id="backend-001",
    status="working",
    current_task="task-001"
)
```

#### list_agents

```python
list_agents(role: Optional[str] = None) -> List[Dict[str, Any]]
```

List all registered agents.

**Parameters**:
- `role` (str, optional): Filter by role

**Returns**: List of agent info dicts

**Example**:
```python
# All agents
all_agents = registry.list_agents()

# Only backend agents
backend_agents = registry.list_agents(role="backend")
```

---

## MessageBus

**Module**: `message_bus.py`

Manages peer-to-peer agent communication.

### Constructor

```python
MessageBus(comm_dir: str = ".agent-comm")
```

### Methods

#### send_message

```python
send_message(
    from_agent: str,
    to_agent: str,
    message_type: MessageType,
    payload: Dict[str, Any],
    reply_to: Optional[str] = None
) -> str
```

Send message from one agent to another.

**Parameters**:
- `from_agent` (str): Sender agent ID
- `to_agent` (str): Recipient agent ID
- `message_type` (MessageType): Type of message
- `payload` (Dict): Message payload
- `reply_to` (str, optional): ID of message being replied to

**Returns**: `str` - Message ID

**Example**:
```python
from message_bus import MessageBus, MessageType

bus = MessageBus()

msg_id = bus.send_message(
    from_agent="frontend-001",
    to_agent="backend-001",
    message_type=MessageType.REQUEST_INFO,
    payload={"question": "What's the login API endpoint?"}
)
```

#### broadcast_message

```python
broadcast_message(
    from_agent: str,
    message_type: MessageType,
    payload: Dict[str, Any],
    exclude: Optional[List[str]] = None
) -> List[str]
```

Broadcast message to all agents.

**Parameters**:
- `from_agent` (str): Sender agent ID
- `message_type` (MessageType): Message type
- `payload` (Dict): Message payload
- `exclude` (List[str], optional): Agent IDs to exclude

**Returns**: List of message IDs

**Example**:
```python
msg_ids = bus.broadcast_message(
    from_agent="devops-001",
    message_type=MessageType.NOTIFICATION,
    payload={"message": "Deployment complete!"}
)
```

#### get_messages

```python
get_messages(
    agent_id: str,
    unread_only: bool = True,
    limit: Optional[int] = None
) -> List[Message]
```

Get messages for an agent.

**Parameters**:
- `agent_id` (str): Agent identifier
- `unread_only` (bool): Only return unread messages. Default: `True`
- `limit` (int, optional): Max messages to return

**Returns**: List of `Message` objects

**Example**:
```python
# Get unread messages
unread = bus.get_messages("frontend-001", unread_only=True)

for msg in unread:
    print(f"From: {msg.from_agent}")
    print(f"Type: {msg.message_type}")
    print(f"Payload: {msg.payload}")
```

#### mark_message_read

```python
mark_message_read(agent_id: str, message_id: str) -> bool
```

Mark message as read.

**Parameters**:
- `agent_id` (str): Agent identifier
- `message_id` (str): Message identifier

**Returns**: `bool` - True if marked

**Example**:
```python
bus.mark_message_read("frontend-001", msg_id)
```

#### get_conversation

```python
get_conversation(
    agent1_id: str,
    agent2_id: str,
    limit: Optional[int] = None
) -> List[Message]
```

Get conversation between two agents.

**Parameters**:
- `agent1_id` (str): First agent ID
- `agent2_id` (str): Second agent ID
- `limit` (int, optional): Max messages

**Returns**: List of `Message` objects sorted by timestamp

**Example**:
```python
conversation = bus.get_conversation("frontend-001", "backend-001", limit=10)
```

---

## CheckpointManager

**Module**: `checkpoint_manager.py`

Manages agent state checkpoints for crash recovery.

### Constructor

```python
CheckpointManager(checkpoint_dir: str = ".agent-comm/checkpoints")
```

### Methods

#### save_checkpoint

```python
save_checkpoint(agent_id: str, checkpoint_data: CheckpointData) -> str
```

Save agent checkpoint.

**Parameters**:
- `agent_id` (str): Agent identifier
- `checkpoint_data` (CheckpointData): Checkpoint data object

**Returns**: `str` - Checkpoint ID

**Example**:
```python
from checkpoint_manager import CheckpointManager, CheckpointData

cp_mgr = CheckpointManager()

checkpoint = CheckpointData(
    agent_id="backend-001",
    role="backend",
    task_id="task-001",
    checkpoint_time=datetime.utcnow().isoformat(),
    state={"current_step": 3, "total_steps": 5}
)

cp_id = cp_mgr.save_checkpoint("backend-001", checkpoint)
```

#### load_latest_checkpoint

```python
load_latest_checkpoint(agent_id: str) -> Optional[CheckpointData]
```

Load latest checkpoint for agent.

**Parameters**:
- `agent_id` (str): Agent identifier

**Returns**: `CheckpointData` object or `None`

**Example**:
```python
checkpoint = cp_mgr.load_latest_checkpoint("backend-001")
if checkpoint:
    print(f"Resume from: {checkpoint.state}")
```

#### load_checkpoint

```python
load_checkpoint(agent_id: str, checkpoint_id: str) -> Optional[CheckpointData]
```

Load specific checkpoint.

**Parameters**:
- `agent_id` (str): Agent identifier
- `checkpoint_id` (str): Checkpoint identifier

**Returns**: `CheckpointData` object or `None`

**Example**:
```python
checkpoint = cp_mgr.load_checkpoint("backend-001", "cp-20260111-153045")
```

#### list_checkpoints

```python
list_checkpoints(agent_id: str) -> List[str]
```

List all checkpoint IDs for agent.

**Parameters**:
- `agent_id` (str): Agent identifier

**Returns**: List of checkpoint IDs (newest first)

**Example**:
```python
checkpoints = cp_mgr.list_checkpoints("backend-001")
print(f"Available checkpoints: {checkpoints}")
```

---

## HealthMonitor

**Module**: `health_monitor.py`

Monitors agent health via heartbeats.

### Constructor

```python
HealthMonitor(
    comm_dir: str = ".agent-comm",
    check_interval: int = 30,
    stale_threshold: int = 60,
    dead_threshold: int = 120
)
```

**Parameters**:
- `comm_dir` (str): Communication directory
- `check_interval` (int): Seconds between health checks. Default: `30`
- `stale_threshold` (int): Seconds before agent considered stale. Default: `60`
- `dead_threshold` (int): Seconds before agent considered dead. Default: `120`

### Methods

#### check_agent_health

```python
check_agent_health() -> Dict[str, AgentHealth]
```

Check health of all agents.

**Returns**: Dict mapping agent_id to `AgentHealth` object

**Example**:
```python
from health_monitor import HealthMonitor

monitor = HealthMonitor()

health = monitor.check_agent_health()
for agent_id, h in health.items():
    print(f"{agent_id}: {h.status}")
    if h.status == "healthy":
        print(f"  Last heartbeat: {h.last_heartbeat}")
```

#### get_stale_agents

```python
get_stale_agents() -> List[AgentHealth]
```

Get list of stale agents (no heartbeat for 60-120s).

**Returns**: List of `AgentHealth` objects

**Example**:
```python
stale = monitor.get_stale_agents()
for agent in stale:
    print(f"Stale: {agent.agent_id}")
```

#### get_dead_agents

```python
get_dead_agents() -> List[AgentHealth]
```

Get list of dead agents (no heartbeat for 120+s).

**Returns**: List of `AgentHealth` objects

**Example**:
```python
dead = monitor.get_dead_agents()
for agent in dead:
    print(f"Dead: {agent.agent_id}")
```

#### start_monitoring

```python
start_monitoring() -> None
```

Start continuous health monitoring in background thread.

**Example**:
```python
monitor.start_monitoring()
# Monitoring runs in background
```

#### stop_monitoring

```python
stop_monitoring() -> None
```

Stop background monitoring.

---

## RecoveryManager

**Module**: `health_monitor.py`

Handles agent crash recovery.

### Constructor

```python
RecoveryManager(
    comm_dir: str = ".agent-comm",
    max_recovery_attempts: int = 3
)
```

**Parameters**:
- `comm_dir` (str): Communication directory
- `max_recovery_attempts` (int): Max recovery attempts per agent. Default: `3`

### Methods

#### recover_agent

```python
recover_agent(crashed_agent: AgentHealth) -> bool
```

Attempt to recover crashed agent.

**Parameters**:
- `crashed_agent` (AgentHealth): Health info of crashed agent

**Returns**: `bool` - True if recovery successful

**Example**:
```python
from health_monitor import RecoveryManager

recovery_mgr = RecoveryManager()

# Get dead agents
dead_agents = monitor.get_dead_agents()

for agent in dead_agents:
    if recovery_mgr.recover_agent(agent):
        print(f"Recovered: {agent.agent_id}")
    else:
        print(f"Recovery failed: {agent.agent_id}")
```

---

## Dashboard

**Module**: `dashboard.py`

Generates visual dashboard for monitoring.

### Constructor

```python
Dashboard(comm_dir: str = ".agent-comm")
```

### Methods

#### generate_summary

```python
generate_summary(workflow_status: Optional[Dict] = None) -> str
```

Generate dashboard summary.

**Parameters**:
- `workflow_status` (Dict, optional): Workflow status from `get_workflow_status()`

**Returns**: `str` - Formatted dashboard text

**Example**:
```python
from dashboard import Dashboard

dashboard = Dashboard()

status = orchestrator.get_workflow_status(workflow_id)
summary = dashboard.generate_summary(status)
print(summary)
```

#### start_live_view

```python
start_live_view(
    workflow_status_func: Callable,
    refresh_interval: int = 2
) -> None
```

Start live auto-refreshing dashboard.

**Parameters**:
- `workflow_status_func` (Callable): Function that returns workflow status
- `refresh_interval` (int): Refresh interval in seconds. Default: `2`

**Example**:
```python
dashboard.start_live_view(
    lambda: orchestrator.get_workflow_status(workflow_id),
    refresh_interval=2
)
# Press Ctrl+C to exit
```

---

## Data Classes

### Task

**Module**: `orchestrator.py`

```python
@dataclass
class Task:
    task_id: str
    description: str
    status: TaskStatus
    role: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Message

**Module**: `message_bus.py`

```python
@dataclass
class Message:
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reply_to: Optional[str] = None
    read: bool = False
```

### CheckpointData

**Module**: `checkpoint_manager.py`

```python
@dataclass
class CheckpointData:
    agent_id: str
    role: str
    task_id: str
    checkpoint_time: str
    state: Dict[str, Any] = field(default_factory=dict)
    work_in_progress: Dict[str, Any] = field(default_factory=dict)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)
```

### AgentHealth

**Module**: `health_monitor.py`

```python
@dataclass
class AgentHealth:
    agent_id: str
    role: str
    status: str  # "healthy", "stale", "dead"
    last_heartbeat: datetime
    current_task: Optional[str] = None
```

---

## Enums

### TaskStatus

**Module**: `orchestrator.py`

```python
class TaskStatus(str, Enum):
    PLANNED = "planned"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"
```

### TaskPriority

**Module**: `orchestrator.py`

```python
class TaskPriority(str, Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low
```

### MessageType

**Module**: `message_bus.py`

```python
class MessageType(str, Enum):
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
```

---

## Utility Functions

### break_down_feature

**Module**: `orchestrator_main.py`

```python
def break_down_feature(feature_description: str) -> List[Dict[str, Any]]
```

Break down a feature description into task list.

**Parameters**:
- `feature_description` (str): Feature description

**Returns**: List of task definitions

**Example**:
```python
from orchestrator_main import break_down_feature

tasks = break_down_feature("Add user authentication with OAuth")

for task in tasks:
    print(f"- [{task['role']}] {task['description']}")
```

### create_agent_context_file

**Module**: `fork_terminal.py`

```python
def create_agent_context_file(
    agent_id: str,
    role: str,
    task: Optional[Dict] = None,
    checkpoint: Optional[Dict] = None
) -> str
```

Create context file for agent with role, project context, task, and checkpoint.

**Parameters**:
- `agent_id` (str): Agent identifier
- `role` (str): Agent role
- `task` (Dict, optional): Task information
- `checkpoint` (Dict, optional): Checkpoint data

**Returns**: `str` - Path to context file

**Example**:
```python
from fork_terminal import create_agent_context_file

context_file = create_agent_context_file(
    agent_id="backend-001",
    role="backend",
    task={"description": "Implement auth API", "priority": "P1"}
)
```

### fork_agent

**Module**: `fork_terminal.py`

```python
def fork_agent(
    agent_id: str,
    role: str,
    task: Optional[Dict] = None
) -> str
```

Fork a new agent in a terminal window.

**Parameters**:
- `agent_id` (str): Agent identifier
- `role` (str): Agent role
- `task` (Dict, optional): Initial task

**Returns**: `str` - Terminal session ID

**Example**:
```python
from fork_terminal import fork_agent

session_id = fork_agent(
    agent_id="backend-001",
    role="backend",
    task={"description": "Implement API"}
)
```

### send_request

**Module**: `message_bus.py`

```python
def send_request(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    question: str
) -> str
```

Convenience function to send information request.

**Example**:
```python
from message_bus import send_request

msg_id = send_request(
    bus,
    from_agent="frontend-001",
    to_agent="backend-001",
    question="What's the auth endpoint?"
)
```

### send_response

**Module**: `message_bus.py`

```python
def send_response(
    message_bus: MessageBus,
    from_agent: str,
    to_agent: str,
    response: str,
    reply_to: str
) -> str
```

Send response to a previous message.

### broadcast_notification

**Module**: `message_bus.py`

```python
def broadcast_notification(
    message_bus: MessageBus,
    from_agent: str,
    notification: str
) -> List[str]
```

Broadcast notification to all agents.

---

## Complete Example

```python
from orchestrator_main import MainOrchestrator, break_down_feature
from dashboard import Dashboard
from message_bus import MessageBus, MessageType

# Create orchestrator
orchestrator = MainOrchestrator(max_agents=5)

# Break down feature
feature = "Add user authentication with OAuth"
tasks = break_down_feature(feature)

# Create workflow
workflow_id = orchestrator.create_workflow(
    name="User Authentication",
    description=feature,
    tasks_breakdown=tasks
)

# Start workflow
orchestrator.start_workflow(workflow_id)

# Monitor with dashboard
dashboard = Dashboard()
dashboard.start_live_view(
    lambda: orchestrator.get_workflow_status(workflow_id),
    refresh_interval=2
)

# Or check status programmatically
status = orchestrator.get_workflow_status(workflow_id)
print(f"Progress: {status['progress']['completed']}/{status['progress']['total']}")

# Pause if needed
orchestrator.pause_workflow(workflow_id)

# Resume later
orchestrator.resume_workflow(workflow_id)

# Agent communication example
bus = MessageBus()
msg_id = bus.send_message(
    from_agent="frontend-001",
    to_agent="backend-001",
    message_type=MessageType.REQUEST_INFO,
    payload={"question": "API endpoint for login?"}
)
```

---

## Error Handling

All methods that can fail return `bool` or `Optional` types. Always check return values:

```python
# Good
if orchestrator.pause_workflow(workflow_id):
    print("Paused successfully")
else:
    print("Failed to pause")

# Good
task = task_mgr.get_task(task_id)
if task:
    print(f"Found: {task.description}")
else:
    print("Task not found")

# Good
try:
    workflow_id = orchestrator.create_workflow(name, desc, tasks)
    orchestrator.start_workflow(workflow_id)
except Exception as e:
    print(f"Error: {e}")
```

## Further Reading

- [README-ORCHESTRATION.md](README-ORCHESTRATION.md) - Main guide
- [AGENT-ROLES.md](AGENT-ROLES.md) - Agent roles
- [PROJECT-CONTEXT.md](PROJECT-CONTEXT.md) - Project context
- [WORKFLOW-GUIDE.md](WORKFLOW-GUIDE.md) - Workflow patterns
