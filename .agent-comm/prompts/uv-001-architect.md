# Task: Design UV Environment Structure

**Task ID**: uv-001
**Role**: Architect
**Priority**: P0 (Critical)

## Objective

Design the uv environment structure and script execution pattern for the agent orchestration system.

## Context

The orchestration tools are in `.claude/skills/fork-terminal/tools/` and include:
- orchestrator.py - Task management
- message_bus.py - Agent communication
- health_monitor.py - Agent health tracking
- checkpoint_manager.py - State persistence
- dashboard.py - Monitoring UI
- fork_terminal.py - Terminal forking
- agent_worker.py - Agent execution

## Deliverables

Create `.claude/skills/fork-terminal/tools/ENV_SETUP.md` documenting:

1. **pyproject.toml Structure**
   - Project name: `agent-orchestration`
   - Python version: >=3.11
   - Dependencies needed (if any external)
   - uv configuration

2. **Script Execution Pattern**
   - How agents should use `uv run` to execute scripts
   - Shebang line format: `#!/usr/bin/env -S uv run`
   - Working directory conventions

3. **Environment Setup Instructions**
   - How to initialize: `uv sync`
   - How to run scripts: `uv run python script.py`
   - How to add dependencies: `uv add package`

4. **Integration with fork_terminal.py**
   - Update fork_agent() to use `uv run`
   - Update fork_terminal() command construction

## Success Criteria

- Clear documentation that other agents can follow
- pyproject.toml template ready for DevOps agent
- Script execution pattern defined for Backend agents
