# Task: Create pyproject.toml for Orchestration Tools

**Task ID**: uv-002
**Role**: DevOps
**Priority**: P1 (High)
**Depends on**: uv-001

## Objective

Create a pyproject.toml file that configures the uv environment for the agent orchestration tools.

## Location

Create file at: `.claude/skills/fork-terminal/tools/pyproject.toml`

## Requirements

1. **Project Configuration**
   ```toml
   [project]
   name = "agent-orchestration"
   version = "1.0.0"
   description = "Multi-agent orchestration system for Claude Code"
   requires-python = ">=3.11"
   ```

2. **Dependencies** (if needed)
   - The current scripts use only standard library
   - Add any missing dependencies discovered

3. **UV Configuration**
   ```toml
   [tool.uv]
   dev-dependencies = []
   ```

4. **Scripts Entry Points** (optional)
   ```toml
   [project.scripts]
   dashboard = "dashboard:print_dashboard"
   orchestrate = "orchestrator_main:main"
   ```

## Verification

After creating, verify with:
```bash
cd .claude/skills/fork-terminal/tools
uv sync
uv run python dashboard.py
```

## Success Criteria

- pyproject.toml is valid TOML
- `uv sync` completes without errors
- All orchestration scripts can be run with `uv run`
