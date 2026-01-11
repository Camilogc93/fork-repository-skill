# Agent Orchestration System

A hybrid orchestration system that coordinates multiple specialized AI agents working collaboratively on complex software development tasks. Agents work in parallel with specialized roles (frontend, backend, devops, qa, architect), communicate peer-to-peer, and automatically recover from crashes.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Workflow Management](#workflow-management)
- [Agent Roles](#agent-roles)
- [Communication Patterns](#communication-patterns)
- [Monitoring and Dashboard](#monitoring-and-dashboard)
- [Crash Recovery](#crash-recovery)
- [Session Persistence](#session-persistence)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

## Overview

The Agent Orchestration System enables Claude to coordinate multiple specialized AI agents that work together like a software development team. Each agent runs in its own terminal window with specific expertise and can communicate both with a central orchestrator and directly with other agents.

### Key Features

- **Hybrid Architecture**: Combines centralized orchestration with peer-to-peer collaboration
- **5 Specialized Roles**: Frontend, Backend, DevOps, QA, Architect
- **Automatic Crash Recovery**: Agents checkpoint every 30s and auto-restart from last state
- **Session Persistence**: Pause and resume workflows across sessions
- **Real-time Dashboard**: Monitor agent progress and system health
- **Task Dependencies**: Automatic dependency resolution and execution ordering
- **Max 5 Concurrent Agents**: Efficient resource management with queuing

### System Requirements

- Python 3.7+
- Git
- Terminal multiplexer support (for forking terminals)
- 2GB+ available memory (for running multiple agents)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                        │
│  - Workflow management                                      │
│  - Task assignment                                          │
│  - Dependency resolution                                    │
│  - Health monitoring                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│Agent 1│    │Agent 2│    │Agent 3│
│Frontend│   │Backend│   │DevOps │
└───┬───┘    └───┬───┘    └───┬───┘
    │            │            │
    └────────────┼────────────┘
                 │
         Peer-to-Peer
         Message Bus
```

**Components:**

1. **Main Orchestrator** (`orchestrator_main.py`)
   - Creates and manages workflows
   - Assigns tasks to agents based on roles
   - Monitors agent health
   - Handles crash recovery

2. **Agent Workers** (`agent_worker.py`)
   - Execute tasks in forked terminals
   - Send heartbeat signals every 10s
   - Checkpoint state every 30s
   - Process peer messages
   - Report results

3. **Message Bus** (`message_bus.py`)
   - Enables peer-to-peer communication
   - Supports request/response patterns
   - Broadcasts notifications
   - Maintains conversation threads

4. **Checkpoint Manager** (`checkpoint_manager.py`)
   - Saves agent state snapshots
   - Supports crash recovery
   - Compresses large checkpoints
   - Rotates old checkpoints

5. **Health Monitor** (`health_monitor.py`)
   - Tracks agent heartbeats
   - Detects stale/dead agents
   - Triggers auto-recovery

6. **Dashboard** (`dashboard.py`)
   - Real-time visualization
   - Progress tracking
   - Activity feed

## Quick Start

### 1. Setup

```bash
# Run setup script
./scripts/setup-orchestration.sh

# Or manually create directories
mkdir -p .agent-comm/{orchestration,messaging,checkpoints,logs}
mkdir -p .claude/agents/{roles,project-context,session-state}
```

### 2. Configure Project Context

Fill out the project context templates in `.claude/agents/project-context/`:

```bash
# Edit these files to describe your project
nano .claude/agents/project-context/00-tech-stack.md
nano .claude/agents/project-context/01-architecture.md
nano .claude/agents/project-context/02-conventions.md
nano .claude/agents/project-context/03-setup.md
nano .claude/agents/project-context/04-apis.md
```

### 3. Start a Workflow

Using the Claude Code skill:

```
orchestrate feature: add user authentication with OAuth
```

Or programmatically:

```python
from orchestrator_main import MainOrchestrator, break_down_feature

# Create orchestrator
orchestrator = MainOrchestrator()

# Break down feature
tasks = break_down_feature("Add user authentication with OAuth")

# Create workflow
workflow_id = orchestrator.create_workflow(
    name="User Authentication",
    description="Implement OAuth authentication",
    tasks_breakdown=tasks
)

# Start execution
orchestrator.start_workflow(workflow_id)
```

### 4. Monitor Progress

```python
from dashboard import Dashboard

dashboard = Dashboard()

# Get status
status = orchestrator.get_workflow_status(workflow_id)
dashboard.generate_summary(status)

# Or start live view
dashboard.start_live_view(
    lambda: orchestrator.get_workflow_status(workflow_id)
)
```

## Core Concepts

### Workflows

A **workflow** is a coordinated set of tasks that accomplish a feature or goal. Workflows have:

- **Name**: Descriptive name (e.g., "User Authentication")
- **Tasks**: List of tasks with dependencies
- **Status**: running, paused, completed, failed
- **Progress**: Completed/total task count

Example workflow structure:

```json
{
  "workflow_id": "workflow-20260111-153045",
  "name": "User Authentication",
  "status": "running",
  "tasks": [
    {
      "task_id": "task-workflow-xxx-001",
      "description": "Implement OAuth flow",
      "role": "backend",
      "priority": "P1",
      "dependencies": [],
      "status": "in_progress"
    },
    {
      "task_id": "task-workflow-xxx-002",
      "description": "Create login UI",
      "role": "frontend",
      "priority": "P1",
      "dependencies": ["task-workflow-xxx-001"]
    }
  ]
}
```

### Tasks

**Tasks** are atomic units of work assigned to agents. Each task has:

- **Description**: What needs to be done
- **Role**: Which type of agent should handle it (frontend, backend, etc.)
- **Priority**: P0 (critical), P1 (high), P2 (medium), P3 (low)
- **Dependencies**: Other tasks that must complete first
- **Status**: planned → queued → assigned → in_progress → completed

### Dependencies

Tasks can depend on other tasks. The orchestrator:

1. Builds a dependency graph (DAG)
2. Detects circular dependencies
3. Only assigns tasks when dependencies are met
4. Uses topological sorting for execution order

Example with dependencies:

```python
tasks = [
    {
        "description": "Design auth architecture",
        "role": "architect",
        "priority": "P1"
    },
    {
        "description": "Implement OAuth backend",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]  # Depends on task 0
    },
    {
        "description": "Create login UI",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [1]  # Depends on task 1
    }
]
```

### Agent Roles

Five specialized agent roles:

1. **Frontend** 🎨 - UI components, styling, forms
2. **Backend** ⚙️ - APIs, database, business logic
3. **DevOps** 🚀 - Infrastructure, deployment, CI/CD
4. **QA** ✅ - Testing, quality assurance
5. **Architect** 📐 - Design, documentation, decisions

Each agent receives:
- Role definition (expertise, patterns, tools)
- Project context (tech stack, architecture, conventions)
- Assigned task details
- Shared knowledge (API contracts, design decisions)
- Previous checkpoint (if resuming)

### Checkpoints

Agents save state every 30 seconds:

```python
{
  "agent_id": "backend-001",
  "role": "backend",
  "task_id": "task-xxx",
  "checkpoint_time": "2026-01-11T15:30:45Z",
  "state": {
    "current_step": 3,
    "total_steps": 5,
    "completed_steps": ["Analyze", "Read files", "Implement"],
    "next_steps": ["Write tests", "Verify"]
  },
  "work_in_progress": {
    "files_modified": ["src/auth/oauth.py"],
    "summary": "Implemented OAuth flow"
  }
}
```

Used for:
- Crash recovery
- Progress tracking
- Handover to replacement agents

### Health States

Agents have three health states based on heartbeat:

- **Healthy**: Heartbeat within last 60 seconds
- **Stale**: No heartbeat for 60-120 seconds (warning)
- **Dead**: No heartbeat for 120+ seconds (auto-recovery triggered)

## Usage Examples

### Example 1: Simple Feature

```
User: orchestrate feature: add contact form

Claude:
1. Analyzing feature requirements...
2. Breaking down into tasks:
   - [Backend] Create contact API endpoint
   - [Frontend] Build contact form component
   - [QA] Write form validation tests

3. Creating workflow...
   ✓ Workflow created: workflow-20260111-153045

4. Starting agents...
   🤖 Spawning backend agent: backend-001
      Task: Create contact API endpoint

   🤖 Spawning frontend agent: frontend-001
      Task: Build contact form component
      (Waiting for backend API contract)

5. Monitoring progress...
   [Dashboard shows real-time status]

6. Workflow complete!
   ✓ Backend: API endpoint /api/contact created
   ✓ Frontend: ContactForm component created
   ✓ QA: Tests passing (12/12)
```

### Example 2: Complex Multi-Agent Feature

```python
from orchestrator_main import MainOrchestrator

orchestrator = MainOrchestrator()

# Define complex feature
tasks = [
    {
        "description": "Design notification system architecture",
        "role": "architect",
        "priority": "P1"
    },
    {
        "description": "Set up Redis for pub/sub",
        "role": "devops",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Implement WebSocket server",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0, 1]
    },
    {
        "description": "Create notification UI component",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [2]
    },
    {
        "description": "Write integration tests",
        "role": "qa",
        "priority": "P1",
        "dependencies": [3]
    }
]

workflow_id = orchestrator.create_workflow(
    name="Real-time Notifications",
    description="Implement WebSocket-based notification system",
    tasks_breakdown=tasks
)

orchestrator.start_workflow(workflow_id)
```

### Example 3: Pause and Resume

```python
# Pause workflow
orchestrator.pause_workflow(workflow_id)
# Output: ⏸️  Workflow paused and snapshot saved

# Later, resume
orchestrator.resume_workflow(workflow_id)
# Output:
# ▶️  Resuming workflow: Real-time Notifications
#    - Found 2 agents that were working
#    - Restarting with checkpoints...
```

### Example 4: Monitoring with Dashboard

```python
from dashboard import Dashboard

dashboard = Dashboard()

# One-time summary
status = orchestrator.get_workflow_status(workflow_id)
print(dashboard.generate_summary(status))

# Live view (auto-refreshing)
dashboard.start_live_view(
    lambda: orchestrator.get_workflow_status(workflow_id),
    refresh_interval=2
)
```

## Configuration

### Orchestration Settings

Edit `.agent-comm/config.json`:

```json
{
  "max_concurrent_agents": 5,
  "checkpoint_interval": 30,
  "heartbeat_interval": 10,
  "stale_threshold": 60,
  "dead_threshold": 120,
  "max_recovery_attempts": 3,
  "auto_recovery": true
}
```

### Agent Role Customization

Create custom roles in `.claude/agents/roles/custom-role.md`:

```markdown
# Custom Role Name

## Identity
- Role: Custom specialized role
- Focus: Your specific domain
- Expertise: List key capabilities

## Capabilities
- Capability 1
- Capability 2

## Tools and Technologies
- Tool 1
- Tool 2

## Communication Patterns
### Reads From
- Other roles this agent gets info from

### Publishes To
- Other roles this agent sends info to

## Best Practices
- Practice 1
- Practice 2
```

## Workflow Management

### Creating Workflows

```python
orchestrator = MainOrchestrator()

workflow_id = orchestrator.create_workflow(
    name="Workflow Name",
    description="What this workflow does",
    tasks_breakdown=[
        {
            "description": "Task description",
            "role": "backend",
            "priority": "P1",
            "dependencies": []
        }
    ]
)
```

### Starting Workflows

```python
orchestrator.start_workflow(workflow_id)
```

This will:
1. Start health monitoring
2. Spawn agents for ready tasks (no dependencies)
3. Monitor progress
4. Handle crashes automatically
5. Complete when all tasks done

### Pausing Workflows

```python
orchestrator.pause_workflow(workflow_id)
```

Saves a snapshot including:
- Workflow state
- All task states
- Active agent checkpoints
- Shared knowledge references

### Resuming Workflows

```python
orchestrator.resume_workflow(workflow_id)
```

Restores from snapshot and:
1. Loads workflow state
2. Restarts agents from checkpoints
3. Resumes task execution

### Getting Workflow Status

```python
status = orchestrator.get_workflow_status(workflow_id)

# Returns:
{
    "workflow": {
        "workflow_id": "...",
        "name": "...",
        "status": "running"
    },
    "progress": {
        "total": 5,
        "completed": 2,
        "in_progress": 2,
        "pending": 1
    },
    "tasks": {
        "task-xxx": {
            "description": "...",
            "status": "in_progress",
            "assigned_to": "backend-001"
        }
    },
    "agents": {
        "backend-001": {
            "role": "backend",
            "status": "healthy",
            "current_task": "task-xxx"
        }
    }
}
```

## Agent Roles

See [AGENT-ROLES.md](AGENT-ROLES.md) for detailed information on:
- Role capabilities and expertise
- Communication patterns
- Customization guide
- Creating new roles

## Communication Patterns

### Orchestrator → Agent

```python
# Task assignment (orchestrator assigns task)
# Status request (orchestrator asks for update)
# Priority change (orchestrator changes task priority)
```

### Agent → Orchestrator

```python
# Status update (agent reports progress)
# Task complete (agent reports completion)
# Blocker reported (agent encounters issue)
```

### Agent ↔ Agent (Peer-to-Peer)

```python
from message_bus import MessageBus, MessageType

bus = MessageBus()

# Agent requests information
bus.send_message(
    from_agent="frontend-001",
    to_agent="backend-001",
    message_type=MessageType.REQUEST_INFO,
    payload={"question": "What's the auth API endpoint?"}
)

# Agent provides information
bus.send_message(
    from_agent="backend-001",
    to_agent="frontend-001",
    message_type=MessageType.PROVIDE_INFO,
    payload={"response": "POST /api/v1/auth/login"}
)

# Broadcast notification
bus.broadcast_message(
    from_agent="devops-001",
    message_type=MessageType.NOTIFICATION,
    payload={"message": "Deployment complete!"}
)
```

## Monitoring and Dashboard

### Dashboard Views

The dashboard shows:

1. **Active Agents** - Current agents with health status
2. **Task Queue** - Pending and in-progress tasks
3. **Recent Activity** - Communication log

### Example Dashboard Output

```
┌──────────────────────────────────────────────────────────┐
│          🎯 AGENT ORCHESTRATION DASHBOARD                 │
│                                                           │
│  Workflow: Real-time Notifications                       │
│  Status: running                                         │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  👥 ACTIVE AGENTS                                         │
└──────────────────────────────────────────────────────────┘
Active: 3/5

  ✅ ⚙️  backend-001
     Task: Implement WebSocket server
     Progress: ████████████░░░░░░░░░░░░░░░░░░ 40%
     Last update: 5s ago

  ✅ 🎨 frontend-001
     Task: Create notification UI
     Progress: ██████░░░░░░░░░░░░░░░░░░░░░░░░ 20%
     Last update: 3s ago

  ✅ 🚀 devops-001
     Task: Configure Redis pub/sub
     Progress: ████████████████████████░░░░░░ 80%
     Last update: 2s ago

┌──────────────────────────────────────────────────────────┐
│  📋 TASK QUEUE                                            │
└──────────────────────────────────────────────────────────┘
Total: 5
Completed: 1
In Progress: 3
Pending: 1

  [P1] 🔨 Implement WebSocket server
     → backend-001

  [P1] 🔨 Create notification UI component
     → frontend-001

  [P1] 📝 Write integration tests
     (Waiting for dependencies)
```

### Commands During Execution

- `status` - Show current workflow status
- `pause` - Pause workflow
- `resume <workflow-id>` - Resume paused workflow
- `details <agent-id>` - Show agent details
- `logs` - View communication logs

## Crash Recovery

### How It Works

1. **Heartbeat Monitoring**: Agents send heartbeat every 10s
2. **Health Check**: Monitor checks every 30s
3. **Detection**:
   - Stale: 60s without heartbeat (warning)
   - Dead: 120s without heartbeat (trigger recovery)
4. **Recovery**:
   - Load latest checkpoint (< 30s old)
   - Create handover context
   - Spawn replacement agent with same role
   - Resume from checkpoint state
   - Notify other agents

### Recovery Example

```
💀 Agent backend-001 crashed (no heartbeat for 120s)
   Current task: task-workflow-xxx-002

🔄 Recovery initiated...
   ✓ Loaded checkpoint from 25s ago
   ✓ Creating handover context
   ✓ Spawning replacement: backend-004
   ✓ Replacement resumed from step 4/7
   ✓ Other agents notified

✅ Recovery complete - workflow continuing
```

### Max Recovery Attempts

Each agent can be recovered up to 3 times. After 3 failures:
- Task marked as failed
- Workflow paused
- User notified

## Session Persistence

### Workflow Snapshots

Workflows can be paused and resumed across sessions:

```python
# Before shutdown
orchestrator.pause_workflow(workflow_id)

# After restart
orchestrator = MainOrchestrator()
orchestrator.resume_workflow(workflow_id)
```

Snapshots include:
- Workflow metadata
- Task states and dependencies
- Agent checkpoints
- Shared knowledge references
- Communication history

### Checkpoint Storage

Checkpoints stored in `.agent-comm/checkpoints/{agent-id}/`:
- Latest 5 checkpoints per agent
- Compressed for large states
- Symlink to latest for quick access

## Troubleshooting

### Agents Not Starting

**Symptom**: Workflow created but no agents spawn

**Solutions**:
1. Check `.agent-comm/logs/` for errors
2. Verify project context files exist:
   ```bash
   ls -la .claude/agents/project-context/
   ```
3. Check agent registry capacity:
   ```python
   from orchestrator import AgentRegistry
   registry = AgentRegistry()
   print(f"Active: {len(registry.list_agents())}/5")
   ```

### Agents Not Communicating

**Symptom**: Agents stuck waiting for information

**Solutions**:
1. Check inbox directories:
   ```bash
   ls -la .agent-comm/messaging/inbox/
   ```
2. Review communication log:
   ```bash
   tail -f .agent-comm/logs/communications.log
   ```
3. Verify agents are registered:
   ```python
   registry.list_agents()
   ```

### Workflow Stuck

**Symptom**: Tasks remain in "pending" state

**Solutions**:
1. Check for blocked tasks:
   ```python
   from orchestrator import TaskManager
   task_mgr = TaskManager()
   blocked = task_mgr.get_blocked_tasks()
   for task in blocked:
       print(f"Blocked: {task.description}")
       print(f"Reason: {task.metadata.get('blocked_reason')}")
   ```
2. Review dependencies:
   ```python
   from orchestrator import DependencyManager
   dep_mgr = DependencyManager()
   ready = dep_mgr.get_ready_tasks(task_mgr)
   print(f"Ready tasks: {ready}")
   ```
3. Check agent health:
   ```python
   from health_monitor import HealthMonitor
   monitor = HealthMonitor()
   health = monitor.check_agent_health()
   for agent_id, h in health.items():
       print(f"{agent_id}: {h.status}")
   ```

### Recovery Not Working

**Symptom**: Dead agents not auto-recovering

**Solutions**:
1. Verify checkpoints exist:
   ```bash
   ls -la .agent-comm/checkpoints/
   ```
2. Check checkpoint age (should be < 60s):
   ```python
   from checkpoint_manager import CheckpointManager
   cp_mgr = CheckpointManager()
   cp = cp_mgr.load_latest_checkpoint("backend-001")
   if cp:
       print(f"Checkpoint age: {cp.checkpoint_time}")
   ```
3. Review recovery logs:
   ```bash
   grep "Recovery" .agent-comm/logs/health_monitor.log
   ```
4. Check max recovery attempts:
   ```python
   # In health_monitor.py
   # max_recovery_attempts = 3
   ```

### High Memory Usage

**Symptom**: System running out of memory

**Solutions**:
1. Reduce max concurrent agents (default: 5):
   ```python
   orchestrator = MainOrchestrator(max_agents=3)
   ```
2. Clean old checkpoints:
   ```bash
   find .agent-comm/checkpoints -type f -mtime +1 -delete
   ```
3. Monitor agent count:
   ```python
   registry = AgentRegistry()
   print(f"Active agents: {len(registry.list_agents())}")
   ```

## API Reference

See [API-REFERENCE.md](API-REFERENCE.md) for complete API documentation including:
- MainOrchestrator class
- TaskManager class
- AgentRegistry class
- MessageBus class
- CheckpointManager class
- HealthMonitor class
- Dashboard class

## Further Reading

- [AGENT-ROLES.md](AGENT-ROLES.md) - Detailed role descriptions and customization
- [PROJECT-CONTEXT.md](PROJECT-CONTEXT.md) - Setting up project context
- [WORKFLOW-GUIDE.md](WORKFLOW-GUIDE.md) - Advanced workflow patterns
- [API-REFERENCE.md](API-REFERENCE.md) - Complete API documentation

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review troubleshooting guide above
- Check communication logs in `.agent-comm/logs/`
- Inspect checkpoints in `.agent-comm/checkpoints/`
