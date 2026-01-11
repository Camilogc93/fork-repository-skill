# Agent Orchestration Skill

## Metadata
- **Name**: Agent Orchestration
- **Description**: Coordinate multiple specialized AI agents (frontend, backend, devops, qa, architect) to work on complex development tasks collaboratively
- **Version**: 1.0.0
- **Author**: Claude Code
- **Triggers**:
  - "orchestrate feature:"
  - "multi-agent:"
  - "coordinate agents"
  - "spawn agents for"
  - "agent workflow:"

## Configuration

```yaml
max_concurrent_agents: 5
agent_roles:
  - frontend   # UI/UX, components, styling
  - backend    # APIs, database, business logic
  - devops     # Infrastructure, deployment, CI/CD
  - qa         # Testing, quality assurance
  - architect  # Design, documentation, decisions

checkpoint_interval: 30  # seconds
heartbeat_interval: 10   # seconds
auto_recovery: true
```

## Overview

This skill enables Claude to orchestrate multiple specialized AI agents working in parallel on complex software development tasks. Each agent runs in its own terminal with a specific role and expertise.

### Key Features

- **Task Decomposition**: Break down complex features into specialized tasks
- **Dependency Management**: Handle task dependencies and execution order
- **Agent Specialization**: 5 role types with specific expertise
- **Crash Recovery**: Auto-restart failed agents from checkpoints
- **Peer Communication**: Agents collaborate directly
- **Session Persistence**: Pause and resume workflows
- **Real-time Dashboard**: Monitor agent progress

## Workflow

### When user requests orchestration:

1. **Analyze Request**
   ```python
   User: "orchestrate feature: add user authentication with OAuth"
   ```

2. **Break Down Feature**
   - Analyze the feature requirements
   - Identify which agent roles are needed
   - Create task breakdown with dependencies
   - Example breakdown:
     ```
     Task 1 [Backend]: Implement OAuth flow + JWT
     Task 2 [DevOps]: Configure OAuth credentials
     Task 3 [Frontend]: Create login UI (depends on Task 1)
     Task 4 [QA]: Write integration tests (depends on Tasks 1,3)
     Task 5 [DevOps]: Deploy to staging (depends on Task 4)
     ```

3. **Create Workflow**
   ```python
   from orchestrator_main import MainOrchestrator, break_down_feature

   orchestrator = MainOrchestrator()

   # Break down feature
   tasks = break_down_feature(user_request)

   # Create workflow
   workflow_id = orchestrator.create_workflow(
       name="User Authentication",
       description=user_request,
       tasks_breakdown=tasks
   )
   ```

4. **Start Workflow**
   ```python
   # Start execution
   orchestrator.start_workflow(workflow_id)
   ```

   This will:
   - Start health monitoring
   - Spawn agents for ready tasks
   - Monitor progress
   - Handle agent crashes
   - Show dashboard

5. **Monitor Progress**
   ```python
   from dashboard import Dashboard

   dashboard = Dashboard()

   # Get current status
   status = orchestrator.get_workflow_status(workflow_id)

   # Print dashboard
   dashboard.generate_summary(status)

   # Or start live view
   dashboard.start_live_view(
       lambda: orchestrator.get_workflow_status(workflow_id)
   )
   ```

6. **Handle User Commands**
   - `status`: Show current workflow status
   - `pause`: Pause workflow and save snapshot
   - `resume <workflow-id>`: Resume paused workflow
   - `details <agent-id>`: Show agent details
   - `logs`: View communication logs

## Usage Examples

### Example 1: Simple Feature

```
User: "orchestrate feature: add contact form"

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

### Example 2: Complex Feature with All Roles

```
User: "orchestrate feature: implement real-time notifications"

Claude:
1. Analyzing requirements...
   This requires: backend (WebSocket), frontend (UI), devops (Redis), qa (tests), architect (design)

2. Task breakdown:
   Task 1 [Architect]: Design notification system architecture
   Task 2 [DevOps]: Set up Redis for pub/sub
   Task 3 [Backend]: Implement WebSocket server
   Task 4 [Frontend]: Create notification UI component
   Task 5 [Backend]: Integrate with Redis pub/sub
   Task 6 [Frontend]: Connect to WebSocket
   Task 7 [QA]: Test real-time messaging
   Task 8 [DevOps]: Deploy with WebSocket support

3. Creating workflow with dependencies...
   [Dependency graph created]

4. Starting workflow...
   [5 agents spawn in sequence as dependencies are met]

5. Agents collaborate:
   - Architect publishes design doc
   - Backend requests env vars from DevOps
   - Frontend requests WebSocket API from Backend
   - QA finds bug, notifies Frontend
   - All agents see deployment notification from DevOps

6. Workflow complete with full traceability!
```

### Example 3: Resume After Pause

```
User: "pause the notification workflow"

Claude: ⏸️  Workflow paused and snapshot saved

[Later...]

User: "resume workflow: workflow-20260111-153045"

Claude:
▶️  Resuming workflow: Real-time Notifications
   - Found 2 agents that were working
   - Restarting with checkpoints...

🔄 Resuming frontend-003
   Previous progress: 75% (step 3/4)
   Continuing from: Add WebSocket connection logic

🔄 Resuming backend-002
   Previous progress: 60% (step 2/3)
   Continuing from: Integrate Redis pub/sub

✅ Workflow resumed successfully
```

### Example 4: Agent Crash Recovery

```
[During workflow execution]

💀 Agent backend-001 crashed (no heartbeat for 120s)
   Current task: task-workflow-xxx-002

🔄 Recovery initiated...
   ✓ Loaded checkpoint from 30s ago
   ✓ Creating handover context
   ✓ Spawning replacement: backend-004
   ✓ Replacement resumed from step 4/7
   ✓ Other agents notified

✅ Recovery complete - workflow continuing
```

## Agent Roles

### Frontend Agent 🎨
- **Expertise**: React/Vue/Svelte, UI components, styling, forms
- **Reads**: API contracts from Backend
- **Publishes**: Component documentation
- **Tools**: npm, webpack, testing libraries

### Backend Agent ⚙️
- **Expertise**: APIs, database, business logic, authentication
- **Reads**: Requirements from Architect
- **Publishes**: API contracts, database schemas
- **Tools**: Python/Node/Go, SQL, Redis

### DevOps Agent 🚀
- **Expertise**: Docker, CI/CD, infrastructure, deployment
- **Reads**: Service requirements from Backend/Frontend
- **Publishes**: Deployment status, environment configs
- **Tools**: Docker, Terraform, CI/CD platforms

### QA Agent ✅
- **Expertise**: Testing, quality assurance, bug detection
- **Reads**: Implementation from all agents
- **Publishes**: Test results, bug reports
- **Tools**: Jest, Pytest, Playwright, test frameworks

### Architect Agent 📐
- **Expertise**: System design, documentation, decisions
- **Reads**: Requirements and constraints
- **Publishes**: Architecture docs, design decisions, standards
- **Tools**: Documentation tools, diagramming

## Communication Patterns

### Orchestrator → Agent
- Task assignments
- Priority changes
- Status requests

### Agent → Orchestrator
- Status updates
- Task completion
- Blocker reports

### Agent ↔ Agent (Peer-to-Peer)
- Information requests/responses
- Work handoffs
- Review requests
- Notifications

## File Structure

```
.claude/agents/
├── roles/              # Agent role definitions
├── project-context/    # Project-specific knowledge
└── session-state/      # Persistent state

.agent-comm/            # Runtime coordination
├── orchestration/      # Task queue, workflows
├── messaging/          # Peer messages
├── checkpoints/        # Agent state snapshots
└── shared-knowledge/   # API contracts, decisions
```

## Commands

When orchestration is active, you can use:

- **`status`**: Show workflow dashboard
- **`pause`**: Pause current workflow
- **`resume <workflow-id>`**: Resume paused workflow
- **`details <agent-id>`**: Show agent details
- **`logs`**: View communication logs
- **`kill <agent-id>`**: Stop specific agent
- **`restart <agent-id>`**: Restart agent with checkpoint

## Best Practices

1. **Configure Project Context**: Fill out `.claude/agents/project-context/` files before starting
2. **Define Clear Tasks**: Break features into concrete, testable tasks
3. **Set Dependencies**: Use task dependencies to ensure correct order
4. **Monitor Progress**: Watch the dashboard for issues
5. **Review Logs**: Check communication logs for agent collaboration
6. **Checkpoint Often**: Agents auto-checkpoint every 30s
7. **Test Recovery**: Verify crash recovery works for your workflow

## Troubleshooting

### Agents Not Starting
- Check `.agent-comm/logs/` for errors
- Verify project context files exist
- Ensure Docker/dependencies installed

### Agents Not Communicating
- Check `.agent-comm/messaging/inbox/<agent-id>/`
- Review communication logs
- Verify agents are registered

### Workflow Stuck
- Check for blocked tasks: `orchestrator.get_blocked_tasks()`
- Review task dependencies
- Check agent health status

### Recovery Not Working
- Verify checkpoints exist in `.agent-comm/checkpoints/`
- Check checkpoint age (should be < 60s for good recovery)
- Review recovery logs

## Advanced Usage

### Custom Agent Roles

You can create custom roles by adding new files to `.claude/agents/roles/`:

```markdown
# Custom-Role.md

## Identity
- Role: Custom specialized role
- Focus: Your specific domain

## Capabilities
[List capabilities]

## Communication Patterns
[Define how this agent interacts]
```

### Programmatic Control

```python
from orchestrator_main import MainOrchestrator
from dashboard import Dashboard

# Create orchestrator
orch = MainOrchestrator()

# Create custom workflow
tasks = [
    {"description": "Task 1", "role": "backend", "priority": "P1"},
    {"description": "Task 2", "role": "frontend", "priority": "P1", "dependencies": [0]}
]

wf_id = orch.create_workflow("Custom Workflow", "Description", tasks)
orch.start_workflow(wf_id)

# Monitor
dashboard = Dashboard()
dashboard.start_live_view(lambda: orch.get_workflow_status(wf_id))
```

## Notes

- Maximum 5 concurrent agents (configurable)
- Agents auto-checkpoint every 30 seconds
- Heartbeat every 10 seconds
- Stale threshold: 60 seconds
- Dead threshold: 120 seconds
- Max recovery attempts: 3 per agent
- Workflow snapshots enable pause/resume across sessions

## See Also

- **fork-terminal skill**: Base terminal forking functionality
- **Project context templates**: `.claude/agents/project-context/`
- **Agent role definitions**: `.claude/agents/roles/`
- **Communication logs**: `.agent-comm/logs/`
