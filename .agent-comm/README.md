# Agent Communication Directory

This directory contains **runtime coordination data** for the agent orchestration system. Files here are generated during agent execution and are generally ephemeral (temporary).

⚠️ **Note**: Most files in this directory are gitignored. Only logs are committed to the repository.

## Directory Structure

```
.agent-comm/
├── agents/                    # Agent registry and status
│   ├── registry.json          # Active agents and their capabilities
│   └── status/                # Agent heartbeat files (ephemeral)
│       └── {agent-id}.json
│
├── orchestration/             # Task management and workflow coordination
│   ├── tasks/
│   │   ├── pending/           # Tasks waiting to be assigned
│   │   ├── in-progress/       # Tasks currently being worked on
│   │   ├── blocked/           # Tasks that are blocked
│   │   └── completed/         # Finished tasks
│   ├── workflows/             # Workflow state and snapshots
│   └── dependencies.json      # Task dependency graph
│
├── messaging/                 # Peer-to-peer agent communication
│   ├── inbox/                 # Agent inboxes
│   │   └── {agent-id}/        # Messages for specific agent
│   └── sent/                  # Sent message history
│
├── shared-knowledge/          # Team-wide shared information
│   ├── api-contracts/         # API specifications agents share
│   ├── design-decisions/      # Architectural decisions
│   └── handoffs/              # Work handoffs between agents
│
├── checkpoints/               # Agent state snapshots
│   └── {agent-id}-*.json      # Checkpoint files for crash recovery
│
└── logs/                      # Audit logs (committed to git)
    ├── decisions.log          # Architectural decisions
    ├── tasks.log              # Task lifecycle events
    └── communications.log     # Inter-agent messages
```

## File Purposes

### Agent Registry (`agents/registry.json`)
Tracks all currently active agents, their roles, capabilities, and status.

**Example:**
```json
{
  "version": "1.0.0",
  "max_concurrent_agents": 5,
  "agents": {
    "frontend-001": {
      "agent_id": "frontend-001",
      "role": "frontend",
      "capabilities": ["react", "ui", "components"],
      "status": "active",
      "current_task": "task-042",
      "registered_at": "2026-01-11T10:30:00Z"
    }
  },
  "last_updated": "2026-01-11T10:30:00Z"
}
```

### Agent Status (`agents/status/{agent-id}.json`)
Heartbeat files written by agents every 10 seconds to prove they're alive.

**Example:**
```json
{
  "agent_id": "frontend-001",
  "status": "working",
  "current_task": "task-042",
  "last_heartbeat": "2026-01-11T10:30:40Z",
  "pid": 12345
}
```

### Task Files (`orchestration/tasks/*/`)
Each task is a JSON file with its details and status.

**Example:**
```json
{
  "task_id": "task-042",
  "created_at": "2026-01-11T10:00:00Z",
  "assigned_to": "frontend-001",
  "priority": "high",
  "status": "in_progress",
  "task_type": "implementation",
  "description": "Implement login form with email validation",
  "dependencies": ["task-041"],
  "outputs": {
    "expected_files": ["frontend/src/components/LoginForm.tsx"]
  }
}
```

### Messages (`messaging/inbox/{agent-id}/`)
Agents send messages to each other for collaboration.

**Example:**
```json
{
  "message_id": "msg-1234567890",
  "from": "frontend-001",
  "to": "backend-001",
  "type": "request_info",
  "payload": {
    "question": "What's the auth API endpoint?"
  },
  "timestamp": "2026-01-11T10:25:00Z"
}
```

### Shared Knowledge (`shared-knowledge/`)
Agents publish information here for others to consume.

**Example API Contract (`api-contracts/auth.yaml`):**
```yaml
service: auth
version: v1
endpoints:
  - path: /api/v1/auth/login
    method: POST
    request:
      email: string
      password: string
    response:
      token: string
      user: object
```

### Checkpoints (`checkpoints/{agent-id}-*.json`)
Agent state snapshots for crash recovery.

**Example:**
```json
{
  "agent_id": "frontend-001",
  "role": "frontend",
  "task_id": "task-042",
  "checkpoint_time": "2026-01-11T10:30:00Z",
  "state": {
    "current_step": 3,
    "total_steps": 5,
    "completed_steps": ["Created LoginForm skeleton", "Added state management"],
    "next_steps": ["Add validation", "Integrate API"]
  },
  "work_in_progress": {
    "files_modified": ["frontend/src/components/LoginForm.tsx"],
    "branch": "feature/login-form"
  }
}
```

### Logs (`logs/*.log`)
Human-readable audit trail of what happened.

**Format:**
```
[2026-01-11T10:30:00Z] [TASK_CREATED] task-042: Implement login form
[2026-01-11T10:30:10Z] [TASK_ASSIGNED] task-042 → frontend-001
[2026-01-11T10:30:15Z] [TASK_STARTED] frontend-001 started task-042
[2026-01-11T10:35:20Z] [MESSAGE] frontend-001 → backend-001: request_info
[2026-01-11T10:35:25Z] [MESSAGE] backend-001 → frontend-001: provide_info
[2026-01-11T10:45:00Z] [TASK_COMPLETED] frontend-001 completed task-042
```

## Lifecycle

### 1. Workflow Starts
- Orchestrator creates tasks in `orchestration/tasks/pending/`
- Builds dependency graph in `orchestration/dependencies.json`
- Creates workflow snapshot in `orchestration/workflows/`

### 2. Agents Spawn
- Register in `agents/registry.json`
- Start writing heartbeats to `agents/status/`
- Begin polling for tasks

### 3. Agents Work
- Move task from `pending/` → `in-progress/`
- Write checkpoints to `checkpoints/`
- Send messages via `messaging/`
- Publish shared knowledge to `shared-knowledge/`

### 4. Agents Complete
- Move task to `completed/`
- Unregister from registry
- Stop heartbeat
- Final checkpoint saved

### 5. Workflow Ends
- Orchestrator collects results
- Saves final workflow snapshot
- Cleans up old checkpoints
- Logs summary

## Monitoring

### Check Active Agents
```bash
cat .agent-comm/agents/registry.json | jq '.agents'
```

### Check Agent Health
```bash
ls -la .agent-comm/agents/status/
```

### View Recent Activity
```bash
tail -f .agent-comm/logs/communications.log
```

### Check Task Status
```bash
ls .agent-comm/orchestration/tasks/in-progress/
```

### View Checkpoints
```bash
ls -lth .agent-comm/checkpoints/ | head -10
```

## Cleanup

Old runtime files accumulate over time. Clean up periodically:

```bash
# Remove old checkpoints (keep last 5 per agent)
# Handled automatically by checkpoint manager

# Remove completed task files older than 7 days
find .agent-comm/orchestration/tasks/completed/ -name "*.json" -mtime +7 -delete

# Remove old sent messages
find .agent-comm/messaging/sent/ -name "*.json" -mtime +7 -delete
```

## Debugging

### Agent Crashed
1. Check last heartbeat: `.agent-comm/agents/status/{agent-id}.json`
2. Load last checkpoint: `.agent-comm/checkpoints/{agent-id}-latest.json`
3. Review logs: `.agent-comm/logs/tasks.log`
4. Check error messages in agent terminal output

### Task Stuck
1. Check task file: `.agent-comm/orchestration/tasks/blocked/{task-id}.json`
2. Review dependencies: `.agent-comm/orchestration/dependencies.json`
3. Check if agent is alive: `.agent-comm/agents/status/`
4. Review communication logs: `.agent-comm/logs/communications.log`

### Agents Not Communicating
1. Check inbox: `.agent-comm/messaging/inbox/{agent-id}/`
2. Check sent messages: `.agent-comm/messaging/sent/`
3. Verify shared knowledge published: `.agent-comm/shared-knowledge/`
4. Review communication log: `.agent-comm/logs/communications.log`

## Best Practices

### For Agents
- Write checkpoints frequently (every major step)
- Keep heartbeat updated (every 10 seconds)
- Publish shared knowledge early (don't hoard information)
- Log important decisions and actions

### For Orchestrator
- Monitor agent health continuously
- Clean up old files periodically
- Save workflow snapshots at milestones
- Keep dependency graph updated

### For Users
- Review logs to understand what happened
- Don't manually edit JSON files (can corrupt state)
- Use dashboard/CLI tools to inspect state
- Backup checkpoints before major changes

## Security Notes

⚠️ **Important**: This directory may contain sensitive information:
- API keys in shared knowledge
- Code snippets in checkpoints
- System paths in task files

Ensure `.agent-comm/` is properly gitignored (except logs) to avoid committing secrets.
