# Agent Configuration Directory

This directory contains the configuration for the hybrid agent orchestration system.

## Directory Structure

```
.claude/agents/
├── roles/              # Agent role definitions (like specialized team members)
│   ├── frontend.md     # Frontend development agent
│   ├── backend.md      # Backend development agent
│   ├── devops.md       # DevOps/infrastructure agent
│   ├── qa.md           # QA/testing agent
│   └── architect.md    # Architecture/documentation agent
│
├── project-context/    # Project-specific knowledge
│   ├── 00-tech-stack.md    # Technologies used in this project
│   ├── 01-architecture.md  # System architecture and structure
│   ├── 02-conventions.md   # Coding standards and conventions
│   ├── 03-setup.md         # Development environment setup
│   └── 04-apis.md          # API documentation and patterns
│
└── session-state/      # Persistent session data between runs
    └── (agent checkpoints stored here)
```

## How It Works

### Agent Roles
Each role file (e.g., `frontend.md`) defines:
- **Identity**: What this agent specializes in
- **Capabilities**: What this agent can do
- **Responsibilities**: What this agent should focus on
- **Context Needs**: What information this agent needs from others
- **Communication Patterns**: How this agent interacts with other agents
- **Tools & Commands**: Commands this agent commonly uses
- **Success Criteria**: How to know when the work is done

Think of these as **job descriptions** for specialized team members.

### Project Context
These files provide project-specific knowledge that all agents need:
- **Tech Stack**: What frameworks, languages, and tools you're using
- **Architecture**: How your codebase is organized
- **Conventions**: Your team's coding standards and practices
- **Setup**: How to get the project running locally
- **APIs**: How your services communicate

Think of these as your **team handbook** - every agent reads these to understand the project.

### Session State
When agents are working and need to be paused or crash, their state is saved here. This allows:
- **Resuming work** after stopping
- **Recovery** from crashes
- **Context handoff** between agents

## Getting Started

### 1. Define Your Agent Roles
Copy the template role files and customize them for your needs:

```bash
# Roles are already templated - customize them for your workflow
vim .claude/agents/roles/frontend.md
vim .claude/agents/roles/backend.md
```

### 2. Configure Your Project Context
Fill out the project context files with your project's specifics:

```bash
# Start with the tech stack
vim .claude/agents/project-context/00-tech-stack.md

# Then document your architecture
vim .claude/agents/project-context/01-architecture.md

# Continue with conventions, setup, and APIs
```

### 3. Use Orchestration
Once configured, you can use multi-agent orchestration:

```bash
# Start a multi-agent workflow
claude "orchestrate feature: user authentication"

# Resume a paused workflow
claude "resume workflow: user-authentication"

# Check status
claude "show orchestration status"
```

## When Agents Spawn

When an agent is spawned, it receives:

1. **Role Definition** - Who it is and what it does
2. **Project Context** - Understanding of your project
3. **Current Task** - What it needs to accomplish
4. **Shared Knowledge** - Information from other agents (API contracts, etc.)
5. **Checkpoint State** - Where it left off (if resuming)

This combined context allows each agent to work autonomously while staying coordinated with the team.

## Best Practices

### Role Definitions
- Keep roles focused and specialized
- Define clear boundaries between roles
- Document common tasks for each role
- Include real commands agents should use

### Project Context
- Keep it up-to-date as your project evolves
- Be specific about file locations and patterns
- Include examples where helpful
- Document edge cases and gotchas

### Session State
- Let the system manage this automatically
- Don't manually edit checkpoint files
- Review logs to understand what happened

## Example Workflow

```
USER: "orchestrate feature: add user profile page"

ORCHESTRATOR:
  1. Reads all role definitions
  2. Reads all project context
  3. Breaks down feature into tasks:
     - [Backend] Create user profile API endpoint
     - [Frontend] Create profile page component
     - [Frontend] Integrate with API
     - [QA] Write tests
     - [DevOps] Deploy to staging

  4. Spawns agents with appropriate roles:
     Backend Agent → Starts with backend.md + project context + task
     Frontend Agent → Starts with frontend.md + project context + task

  5. Agents work and communicate:
     Backend publishes API contract to shared-knowledge/
     Frontend reads contract and implements integration

  6. Workflow completes:
     All tasks done, feature ready!
```

## Troubleshooting

### Agents don't understand my project
→ Fill out project-context files with more detail

### Agents aren't collaborating well
→ Review communication patterns in role definitions
→ Check shared-knowledge/ to see if information is being published

### Agents keep crashing
→ Review .agent-comm/logs/ to see what's happening
→ Check if tasks are too complex (break them down more)

### Workflow won't resume
→ Check .agent-comm/checkpoints/ for valid checkpoint files
→ Review .agent-comm/orchestration/workflows/ for workflow state

## Learn More

See the main documentation for more details:
- `README-ORCHESTRATION.md` - Full orchestration guide
- `AGENT-ROLES.md` - Guide to customizing roles
- `PROJECT-CONTEXT.md` - How to configure project context
- `WORKFLOW-GUIDE.md` - Managing workflows
