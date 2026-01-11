# Task: Add Completion Watcher to orchestrator_main.py

**Task ID**: close-004
**File**: `.claude/skills/fork-terminal/tools/orchestrator_main.py`

## Changes Required

Add these methods to MainOrchestrator class:

```python
import threading
from pathlib import Path

def watch_completions(self, interval: int = 5):
    """Poll for agent completion signals."""
    completion_dir = Path(self.comm_dir) / "completion"
    completion_dir.mkdir(parents=True, exist_ok=True)

    while getattr(self, 'running', True):
        for signal_file in completion_dir.glob("*.json"):
            self._process_completion_signal(signal_file)
        time.sleep(interval)

def _process_completion_signal(self, signal_file: Path):
    """Process completion signal and update task status."""
    try:
        with open(signal_file, encoding='utf-8') as f:
            data = json.load(f)

        task_id = data.get("task_id")
        status = data.get("status", "completed")

        # Update task via task manager
        if status == "completed":
            self.task_mgr.complete_task(task_id, result=data.get("result"))

        print(f"Agent {data['agent_id']} completed task {task_id}")

        # Remove processed signal
        signal_file.unlink()

    except Exception as e:
        print(f"Error processing signal: {e}")

def start_completion_watcher(self):
    """Start background thread to watch for completions."""
    self.running = True
    self.watcher_thread = threading.Thread(target=self.watch_completions, daemon=True)
    self.watcher_thread.start()
```

Call `start_completion_watcher()` in the orchestrator's start method.
