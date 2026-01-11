# Task: Enhance Dashboard

Enhance the terminal dashboard in `.claude/skills/fork-terminal/tools/dashboard.py`

## New Sections to Add

1. **System Statistics** - Add `generate_system_stats()` method showing:
   - Total tasks by status
   - Available agent slots
   - Session info

2. **Priority Distribution** - Add `generate_priority_distribution()` method showing:
   - Visual bars for P0/P1/P2/P3 task counts

3. **Dependencies View** - Add `generate_dependency_view()` method showing:
   - Tasks blocking others
   - Tasks waiting on dependencies

4. **Agent Workload** - Add `generate_agent_workload()` method showing:
   - Completed tasks per agent
   - In-progress tasks per agent

5. **Message Stats** - Add `generate_message_stats()` method showing:
   - Total messages sent
   - Unread counts per agent

6. **Checkpoint Status** - Add `generate_checkpoint_status()` method showing:
   - Last checkpoint time per agent
   - Checkpoint file sizes

7. **Workflow Timeline** - Add `generate_workflow_timeline()` method showing:
   - Visual progress bar
   - Phase status

## Integration

- Add all new sections to `generate_summary()` method
- Keep dashboard width at 60 characters
- Import MessageBus and CheckpointManager as needed

## Test

Run `python dashboard.py` to verify it works
