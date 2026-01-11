# UV Environment Setup for Agent Orchestration

This document defines the uv-based environment structure and script execution patterns for the agent orchestration system.

## 1. pyproject.toml Structure

The orchestration system uses `uv` for Python package and environment management. Create a `pyproject.toml` in the `.claude/skills/fork-terminal/tools/` directory:

```toml
[project]
name = "agent-orchestration"
version = "0.1.0"
description = "Multi-agent orchestration system for Claude Code"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []

[tool.uv.sources]
```

**Key Points:**
- **Project name**: `agent-orchestration`
- **Python version**: >=3.11 (required for modern type hints and enum improvements)
- **Dependencies**: Currently none - all scripts use Python standard library only
- **uv configuration**: Minimal setup, ready for expansion

## 2. Script Execution Pattern

### Shebang Line Format

All Python scripts in the orchestration system should use the uv-compatible shebang:

```python
#!/usr/bin/env -S uv run
```

**Why this format?**
- `#!/usr/bin/env -S`: Cross-platform compatibility, finds `uv` in PATH
- `-S` flag: Allows passing arguments to the interpreter
- `uv run`: Automatically uses the uv environment without activation

### Current Scripts

Update these scripts with the uv shebang:
- `orchestrator.py`
- `message_bus.py`
- `health_monitor.py`
- `checkpoint_manager.py`
- `dashboard.py`
- `agent_worker.py`
- `fork_terminal.py` ✓ (already updated)

### Working Directory Conventions

Scripts should be executed from the **project root** (where `.claude/` directory exists):

```bash
# Correct - from project root
cd /path/to/fork-repository-skill
uv run python .claude/skills/fork-terminal/tools/orchestrator_main.py

# Incorrect - from tools directory
cd .claude/skills/fork-terminal/tools
uv run python orchestrator_main.py  # May break relative paths
```

**Why?** The orchestration system relies on relative paths like:
- `.agent-comm/` - Communication directory
- `.claude/agents/` - Agent configurations
- Project files and directories

## 3. Environment Setup Instructions

### Initial Setup

From the tools directory:

```bash
# Navigate to tools directory
cd .claude/skills/fork-terminal/tools

# Initialize uv environment and install dependencies
uv sync
```

This creates:
- `.venv/` directory (if not using system Python)
- `uv.lock` file with locked dependency versions

### Running Scripts

**Method 1: Using uv run (Recommended)**

```bash
# From project root
uv run python .claude/skills/fork-terminal/tools/orchestrator_main.py

# With arguments
uv run python .claude/skills/fork-terminal/tools/dashboard.py --comm-dir .agent-comm
```

**Method 2: Direct execution with shebang**

```bash
# Make script executable (Unix/Linux/macOS)
chmod +x .claude/skills/fork-terminal/tools/orchestrator_main.py

# Run directly
./.claude/skills/fork-terminal/tools/orchestrator_main.py
```

**Method 3: From tools directory**

```bash
cd .claude/skills/fork-terminal/tools
uv run python orchestrator_main.py
```

### Adding Dependencies

If external packages are needed:

```bash
# Navigate to tools directory
cd .claude/skills/fork-terminal/tools

# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Update pyproject.toml and lock file
uv sync
```

### Checking Environment

```bash
# Show Python version
uv run python --version

# Show installed packages
uv pip list

# Show uv environment info
uv venv --help
```

## 4. Integration with fork_terminal.py

The `fork_terminal.py` module needs updates to use `uv run` when forking agent processes.

### Current Implementation

```python
def fork_agent(agent_id, role, task=None, checkpoint=None, comm_dir=".agent-comm", agents_dir=".claude/agents"):
    # ...
    command_parts = [
        "python3",  # ← Change this
        str(worker_script),
        f"--agent-id {agent_id}",
        # ...
    ]
    command = " ".join(command_parts)
    return fork_terminal(command)
```

### Updated Implementation

```python
def fork_agent(agent_id, role, task=None, checkpoint=None, comm_dir=".agent-comm", agents_dir=".claude/agents"):
    # Create context file
    context_file = create_agent_context_file(
        agent_id=agent_id,
        role=role,
        task=task,
        checkpoint=checkpoint,
        agents_dir=agents_dir
    )

    # Build command to run agent worker with uv
    worker_script = Path(__file__).parent / "agent_worker.py"

    command_parts = [
        "uv", "run", "python",  # ← Use uv run
        str(worker_script),
        f"--agent-id {agent_id}",
        f"--role {role}",
        f"--context-file {context_file}",
        f"--comm-dir {comm_dir}"
    ]

    if task and task.get('task_id'):
        command_parts.append(f"--task-id {task['task_id']}")

    command = " ".join(command_parts)

    # Fork terminal with agent worker
    return fork_terminal(command)
```

### Updated fork_terminal() for Agent Execution

No changes needed to `fork_terminal()` itself - it already handles arbitrary commands. The `uv run` command will work seamlessly with the existing terminal forking logic on macOS, Windows, and Linux.

### Testing the Integration

```python
# Test forking an agent with uv
from fork_terminal import fork_agent

result = fork_agent(
    agent_id="test-agent-001",
    role="backend",
    task={
        "task_id": "test-001",
        "description": "Test uv integration"
    }
)
print(result)
```

## 5. Benefits of This Architecture

### For Agents
- **Isolated environments**: Each project can have its own dependencies
- **Reproducible**: `uv.lock` ensures consistent environments
- **Fast**: uv is significantly faster than pip
- **No activation needed**: `uv run` handles environment automatically

### For Development
- **Simple setup**: Single `uv sync` command
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Version control friendly**: `pyproject.toml` and `uv.lock` are small and readable

### For Orchestration
- **Reliable forking**: Agents start with correct Python environment
- **No PATH issues**: `uv run` finds the right Python and packages
- **Consistency**: All agents use the same environment configuration

## 6. Migration Checklist

For Backend agents implementing this design:

- [ ] Create `pyproject.toml` in `.claude/skills/fork-terminal/tools/`
- [ ] Run `uv sync` to initialize environment
- [ ] Update all Python script shebangs to `#!/usr/bin/env -S uv run`
- [ ] Update `fork_agent()` function to use `uv run python`
- [ ] Test agent forking with `uv run`
- [ ] Document any external dependencies added
- [ ] Commit `pyproject.toml` and `uv.lock` to version control

## 7. Troubleshooting

### "uv: command not found"
Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### "Python version mismatch"
Check Python version: `uv run python --version`
Update pyproject.toml if needed: `requires-python = ">=3.10"`

### "Module not found"
Ensure dependencies are added: `uv add <package>`
Run sync: `uv sync`

### "Permission denied" (Unix/Linux/macOS)
Make scripts executable: `chmod +x .claude/skills/fork-terminal/tools/*.py`

### "Working directory issues"
Always run orchestration from project root, not tools directory.

## 8. References

- [uv documentation](https://docs.astral.sh/uv/)
- [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- Python version requirement: [PEP 621](https://peps.python.org/pep-0621/)
