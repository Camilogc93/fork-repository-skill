# Completion Design: Auto-Close Terminal & Orchestrator Callback

## Overview

Mechanism for terminals to auto-close on agent completion and notify the orchestrator via file-based signals.

## 1. Completion Signal Format

### Location
```
.agent-comm/completion/{agent_id}.json
```

### Schema
```json
{
  "agent_id": "backend-001",
  "task_id": "task-042",
  "status": "completed",
  "result": {
    "summary": "Task completed successfully",
    "output": "...",
    "errors": null
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Status values**: `completed`, `failed`, `error`

## 2. Terminal Auto-Close Mechanism

### Implementation: Use `cmd /c`

Change from:
```python
# OLD - keeps terminal open
cmd = f'start cmd /k "cd /d {work_dir} && {command}"'
```

To:
```python
# NEW - auto-closes when command finishes
cmd = f'start cmd /c "cd /d {work_dir} && {command}"'
```

### Fallback: Explicit exit

For reliability, agent_worker.py should explicitly call `sys.exit()` after writing completion signal:

```python
def write_completion_signal(agent_id, task_id, status, result):
    signal_file = Path(f".agent-comm/completion/{agent_id}.json")
    signal_file.parent.mkdir(parents=True, exist_ok=True)
    signal_file.write_text(json.dumps({
        "agent_id": agent_id,
        "task_id": task_id,
        "status": status,
        "result": result,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }, indent=2))
```

## 3. Orchestrator Callback Implementation

### Polling Method

Add to `orchestrator_main.py`:

```python
def watch_completions(self, interval: int = 5):
    """Poll for completion signals every interval seconds."""
    completion_dir = Path(".agent-comm/completion")
    completion_dir.mkdir(parents=True, exist_ok=True)

    while self.running:
        for signal_file in completion_dir.glob("*.json"):
            self._process_completion_signal(signal_file)
        time.sleep(interval)

def _process_completion_signal(self, signal_file: Path):
    """Process a single completion signal."""
    try:
        data = json.loads(signal_file.read_text())
        agent_id = data["agent_id"]
        task_id = data["task_id"]
        status = data["status"]

        # Update task status
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["result"] = data.get("result")
            self.tasks[task_id]["completed_at"] = data["timestamp"]

        # Log completion
        self.logger.info(f"Agent {agent_id} completed task {task_id}: {status}")

        # Clean up signal file
        signal_file.unlink()

    except Exception as e:
        self.logger.error(f"Error processing {signal_file}: {e}")
```

### Integration

Start watcher thread in orchestrator initialization:

```python
def start(self):
    """Start the orchestrator."""
    self.running = True
    self.watcher_thread = threading.Thread(
        target=self.watch_completions,
        daemon=True
    )
    self.watcher_thread.start()
    self.logger.info("Orchestrator started with completion watcher")
```

## 4. Component Changes Summary

### agent_worker.py
- Write completion signal before exit
- Call `sys.exit(0)` after signal written

### fork_terminal.py
- Change `cmd /k` to `cmd /c` on Windows
- Keep existing macOS behavior with exit command

### orchestrator_main.py
- Add `watch_completions()` polling method
- Add `_process_completion_signal()` handler
- Start watcher thread on orchestrator start

## 5. Error Handling

- If agent crashes: No signal written, orchestrator detects timeout
- If signal write fails: Agent logs error, orchestrator detects timeout
- If orchestrator misses signal: Signal files persist, processed on next poll
- Stale signals: Add cleanup for signals older than 1 hour

## 6. Testing Checklist

- [ ] Terminal closes automatically after agent completes
- [ ] Completion signal written with correct format
- [ ] Orchestrator detects and processes signals
- [ ] Task status updated correctly in orchestrator
- [ ] Failed tasks generate proper error signals
- [ ] Signal files cleaned up after processing
