# Task: Design Auto-Close Terminal & Orchestrator Callback

**Task ID**: close-001
**Role**: Architect
**Priority**: P0 (Critical)

## Objective

Design a mechanism where:
1. When an agent finishes a task, the terminal automatically closes
2. The main orchestrator is notified of task completion

## Current System

- `fork_terminal.py` spawns terminals with `start cmd /k` (Windows) or AppleScript (macOS)
- `agent_worker.py` runs in the forked terminal
- No callback mechanism exists when agents finish

## Design Requirements

### 1. Completion Signal Mechanism

Create a file-based completion signal:
```
.agent-comm/completion/{agent_id}.json
{
  "agent_id": "backend-001",
  "task_id": "task-042",
  "status": "completed",  // or "failed"
  "result": {...},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. Terminal Auto-Close

Options for auto-closing terminal:
- **Option A**: Use `cmd /c` instead of `cmd /k` (closes when command finishes)
- **Option B**: Add `exit` command at end of agent script
- **Option C**: Use wrapper script that exits after agent completes

**Recommendation**: Option A + exit command for reliability

### 3. Orchestrator Polling/Watching

The orchestrator should watch for completion signals:
- Poll `.agent-comm/completion/` directory
- When signal found, update task status
- Remove the signal file after processing

## Implementation Plan

1. **agent_worker.py**:
   - Write completion signal file when done
   - Exit cleanly (terminal will close)

2. **fork_terminal.py**:
   - Change `cmd /k` to `cmd /c` for auto-close
   - Or append `&& exit` to command

3. **orchestrator_main.py**:
   - Add `watch_completions()` method
   - Poll completion directory every 5 seconds
   - Update task status when signals found

## Deliverable

Create `.claude/skills/fork-terminal/tools/COMPLETION_DESIGN.md` with:
- Completion signal format
- Terminal close mechanism
- Orchestrator callback implementation
- Code examples for each component
