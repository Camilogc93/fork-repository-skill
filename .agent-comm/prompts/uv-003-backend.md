# Task: Update fork_terminal.py to use uv run

**Task ID**: uv-003
**Role**: Backend
**Priority**: P1 (High)
**Depends on**: uv-002

## Objective

Update fork_terminal.py to use `uv run` for executing Python scripts in the correct environment.

## File to Modify

`.claude/skills/fork-terminal/tools/fork_terminal.py`

## Changes Required

1. **Update fork_agent() function** (around line 203)

   Change from:
   ```python
   command_parts = [
       "python3",
       str(worker_script),
       ...
   ]
   ```

   To:
   ```python
   command_parts = [
       "uv", "run", "python",
       str(worker_script),
       ...
   ]
   ```

2. **Update shebang line** (line 1)

   Change from:
   ```python
   #!/usr/bin/env -S uv run
   ```

   Keep this or update to ensure it works with uv.

3. **Add helper function** for environment-aware execution:
   ```python
   def get_python_command() -> list:
       """Get the python command with uv if available."""
       # Check if uv is available
       import shutil
       if shutil.which('uv'):
           return ['uv', 'run', 'python']
       return ['python3']
   ```

## Verification

Test the changes:
```bash
cd .claude/skills/fork-terminal/tools
uv run python -c "from fork_terminal import fork_terminal; print('OK')"
```

## Success Criteria

- fork_agent() uses uv run for spawning agents
- Scripts can be executed with proper environment
- Backwards compatible (falls back to python3 if uv not available)
