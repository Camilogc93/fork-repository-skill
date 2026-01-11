# Task: Update fork_terminal.py for Auto-Close

**Task ID**: close-002
**File**: `.claude/skills/fork-terminal/tools/fork_terminal.py`

## Changes Required

1. **Line 39** - Change `cmd /k` to `cmd /c`:
```python
# FROM:
subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", full_command], shell=True)

# TO:
subprocess.Popen(["cmd", "/c", "start", "cmd", "/c", full_command], shell=True)
```

2. **Add completion directory creation** in fork_agent():
```python
# Add near top of fork_agent function:
completion_dir = Path(comm_dir) / "completion"
completion_dir.mkdir(parents=True, exist_ok=True)
```

That's it - minimal changes. The `cmd /c` flag makes the terminal close when the command finishes.
