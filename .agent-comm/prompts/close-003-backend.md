# Task: Update agent_worker.py for Completion Signal

**Task ID**: close-003
**File**: `.claude/skills/fork-terminal/tools/agent_worker.py`

## Changes Required

Add completion signal writing at end of agent execution:

```python
import json
from datetime import datetime
from pathlib import Path

def write_completion_signal(agent_id: str, task_id: str, status: str, result: dict = None):
    """Write completion signal for orchestrator."""
    signal_dir = Path(".agent-comm/completion")
    signal_dir.mkdir(parents=True, exist_ok=True)

    signal_file = signal_dir / f"{agent_id}.json"
    signal_data = {
        "agent_id": agent_id,
        "task_id": task_id,
        "status": status,
        "result": result or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    with open(signal_file, 'w', encoding='utf-8') as f:
        json.dump(signal_data, f, indent=2)

# Call at end of main() or run():
# write_completion_signal(agent_id, task_id, "completed", {"summary": "Task done"})
# sys.exit(0)
```

Add the function and call it before the agent exits.
