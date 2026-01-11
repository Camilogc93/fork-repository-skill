# Multi-Agent Orchestration System

A Claude Code skill that coordinates multiple specialized AI agents working together on complex development tasks. Each agent has specific expertise (frontend, backend, devops, qa, architect) and they communicate peer-to-peer while automatically recovering from failures.

## Overview

This system enables Claude to manage a team of AI agents that:
- Work in parallel on independent tasks
- Communicate directly with each other
- Automatically checkpoint and recover from crashes
- Handle complex features spanning multiple domains

Perfect for large features requiring coordination across frontend, backend, infrastructure, and testing.

## Prerequisites

**Required**:
- **Claude Code CLI** - Install with: `npm install -g @anthropic-ai/claude-code`
- **Python 3.11+** - Required for agent orchestration
- **uv** (Python package manager) - Install with:
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd fork-repository-skill

# 2. Initialize Python environment
cd .claude/skills/fork-terminal/tools
uv sync
cd ../../../..

# 3. Start Claude Code
claude

# 4. Initialize your project for orchestration
init project
```

## Project Initialization

Before using orchestration, initialize your project to configure the system for your tech stack:

```bash
# Auto-detect your project's tech stack
init project

# Or use a template
init project: fullstack-web
init project: api-service

# Validate your setup
init project --validate
```

The initialization process:
1. **Detects** your tech stack (frameworks, languages, databases)
2. **Generates** project context files for agents
3. **Sets up** runtime directories for coordination
4. **Validates** everything is ready for orchestration

See [Project Initialization Guide](docs/PROJECT-INIT-DESIGN.md) for detailed documentation.

## Usage with Claude Code

Once inside Claude Code CLI, use natural language to orchestrate agents:

```
# Start a multi-agent workflow
orchestrate feature: add user authentication with OAuth

# Or fork individual agents
fork terminal use claude code to implement the backend API
```

## Available Agent Roles

The system includes 5 specialized agent types:

| Role | Icon | Responsibilities |
|------|------|------------------|
| **Architect** | 📐 | System design, architecture decisions, technical documentation |
| **Backend** | ⚙️ | APIs, business logic, database operations, server-side code |
| **Frontend** | 🎨 | UI components, styling, client-side interactions |
| **DevOps** | 🚀 | Infrastructure, CI/CD, deployment, monitoring |
| **QA** | ✅ | Testing, quality assurance, test automation |

Each agent receives project context and communicates with others automatically.

## Monitoring Dashboard

View real-time agent progress and system health:

```bash
cd .claude/skills/fork-terminal/tools
uv run python dashboard.py
```

**Dashboard View**:
```
┌──────────────────────────────────────────────┐
│     🎯 AGENT ORCHESTRATION DASHBOARD          │
│  Workflow: User Authentication               │
│  Status: running                              │
└──────────────────────────────────────────────┘

👥 ACTIVE AGENTS
Active: 3/5

  ✅ ⚙️  backend-001
     Task: Implement OAuth endpoints
     Progress: ████████████░░░░░░░░░░ 60%
     Last update: 5s ago

  ✅ 🎨 frontend-001
     Task: Create login UI components
     Progress: ██████░░░░░░░░░░░░░░░░ 30%
     Last update: 3s ago

  ✅ 🚀 devops-001
     Task: Configure auth service
     Progress: ████████████████░░░░░░ 80%
     Last update: 2s ago
```

## Project Structure

Key directories for the orchestration system:

```
fork-repository-skill/
├── .claude/
│   ├── skills/
│   │   ├── fork-terminal/             # Main orchestration skill
│   │   │   ├── SKILL.md               # Skill definition
│   │   │   └── tools/                 # Python orchestration modules
│   │   │       ├── orchestrator_main.py
│   │   │       ├── orchestrator.py
│   │   │       ├── message_bus.py
│   │   │       ├── checkpoint_manager.py
│   │   │       ├── health_monitor.py
│   │   │       ├── agent_worker.py
│   │   │       ├── dashboard.py
│   │   │       └── fork_terminal.py
│   │   │
│   │   └── project-init/              # Project initialization skill
│   │       ├── SKILL.md               # Skill definition
│   │       └── tools/                 # Initialization tools
│   │           ├── detector.py        # Tech stack auto-detection
│   │           ├── generator.py       # Config file generation
│   │           ├── validator.py       # Setup validation
│   │           └── main.py            # CLI entry point
│   │
│   └── agents/
│       ├── roles/                     # Agent role definitions
│       │   ├── architect.md           # 📐 System design role
│       │   ├── backend.md             # ⚙️ Backend development role
│       │   ├── frontend.md            # 🎨 Frontend development role
│       │   ├── devops.md              # 🚀 Infrastructure role
│       │   └── qa.md                  # ✅ Testing role
│       ├── project-context/           # Project-specific context
│       │   ├── 00-tech-stack.md
│       │   ├── 01-architecture.md
│       │   ├── 02-conventions.md
│       │   ├── 03-setup.md
│       │   └── 04-apis.md
│       └── templates/                 # Project templates
│           └── projects/
│               ├── fullstack-web.yaml
│               └── api-service.yaml
│
└── .agent-comm/                       # Runtime coordination
    ├── orchestration/tasks/           # Task queue
    ├── messaging/                     # Inter-agent messages
    ├── checkpoints/                   # Agent state snapshots
    ├── shared-knowledge/              # Shared artifacts
    └── logs/                          # Execution logs
```

## Example Workflow

Here's how the system handles a complex feature:

**User Request**: "Implement real-time notifications"

**Claude orchestrates**:

1. **Architect** 📐 - Designs notification system architecture
2. **DevOps** 🚀 - Sets up Redis for pub/sub (runs in parallel with step 1)
3. **Backend** ⚙️ - Implements WebSocket server (waits for steps 1-2)
4. **Frontend** 🎨 - Creates notification UI (waits for step 3)
5. **QA** ✅ - Tests real-time messaging (waits for steps 3-4)

Agents communicate peer-to-peer, checkpoint every 30 seconds, and auto-recover from crashes.

## Advanced Features

**Key Capabilities**:
- **Auto Crash Recovery** - Agents checkpoint every 30s and restart automatically
- **Session Persistence** - Pause and resume workflows across sessions
- **Dependency Management** - Automatic task ordering and parallel execution
- **Peer-to-Peer Communication** - Agents collaborate directly without bottlenecks
- **Max 5 Concurrent Agents** - Efficient resource management

**When to Use**:
- Complex features spanning multiple domains (frontend + backend + infrastructure)
- Large refactoring efforts requiring coordination
- Parallel development of independent components
- Long-running tasks that need crash recovery

**When NOT to Use**:
- Simple single-task operations
- Quick bug fixes
- Tasks requiring heavy shared context

## Additional Documentation

Complete guides available in the `docs/` directory:

- **[README-ORCHESTRATION.md](docs/README-ORCHESTRATION.md)** - Complete orchestration guide
- **[PROJECT-INIT-DESIGN.md](docs/PROJECT-INIT-DESIGN.md)** - Project initialization feature design
- **[AGENT-ROLES.md](docs/AGENT-ROLES.md)** - Role descriptions and customization
- **[PROJECT-CONTEXT.md](docs/PROJECT-CONTEXT.md)** - Project context setup
- **[WORKFLOW-GUIDE.md](docs/WORKFLOW-GUIDE.md)** - Advanced workflow patterns
- **[API-REFERENCE.md](docs/API-REFERENCE.md)** - Python API documentation

## Platform Support

| Platform | Status | Terminal Method |
|----------|--------|-----------------|
| **macOS** | ✅ Supported | AppleScript → Terminal.app |
| **Windows** | ✅ Supported | `cmd /k` via `start` |
| **Linux** | ⚠️ Not implemented | — |

## Resources

**Learn More**:
- [YouTube: Building this skill from scratch](https://youtu.be/X2ciJedw2vU)
- [Tactical Agentic Coding Course](https://agenticengineer.com/tactical-agentic-coding?y=frktskl)
- [IndyDevDan YouTube Channel](https://www.youtube.com/@indydevdan)
