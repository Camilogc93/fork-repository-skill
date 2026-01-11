# Task: Update README Documentation

## Objective

Update the main README.md to focus on:
1. How to work with the agent orchestration system
2. How to set it up
3. Claude Code CLI usage only (no other tools)

## Location

Update: `README.md` in the project root

## Structure

Create a clear, practical README with these sections:

### 1. Overview
- Brief description of the multi-agent orchestration system
- What it does: coordinate multiple AI agents for complex development tasks

### 2. Prerequisites
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code` or similar)
- Python 3.11+
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 3. Quick Start
Step-by-step setup:
```bash
# Clone the repo
git clone <repo-url>
cd fork-repository-skill

# Initialize uv environment
cd .claude/skills/fork-terminal/tools
uv sync
cd ../../../..

# Start Claude Code
claude
```

### 4. Usage with Claude Code
Show how to use the orchestration:
```
# In Claude Code, use the fork-terminal skill:
orchestrate feature: <description of what you want to build>

# Or fork a specific agent:
fork terminal use claude code to <task description>
```

### 5. Available Agent Roles
- Architect (📐): System design, documentation
- Backend (⚙️): APIs, business logic
- Frontend (🎨): UI components
- DevOps (🚀): Infrastructure, CI/CD
- QA (✅): Testing

### 6. Dashboard
How to view the monitoring dashboard:
```bash
cd .claude/skills/fork-terminal/tools
uv run python dashboard.py
```

### 7. Project Structure
Key directories:
- `.claude/skills/fork-terminal/` - Main orchestration skill
- `.claude/agents/roles/` - Agent role definitions
- `.agent-comm/` - Runtime communication directory

### 8. Example Workflow
Show a simple example of orchestrating a feature

## Style Guidelines
- Keep it concise and practical
- Use code blocks for commands
- Focus on Claude Code CLI only
- Include the dashboard screenshot/output example
