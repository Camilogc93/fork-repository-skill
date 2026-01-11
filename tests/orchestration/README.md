# Orchestration System Tests

This directory contains end-to-end tests for the agent orchestration system.

## Test Suite

### test_simple_workflow.py

Tests basic workflow functionality:
- Simple workflow creation (contact form feature)
- Task breakdown and role assignment
- Task dependency management
- Priority levels (P0-P3)

**What it tests**:
- Creating workflows with 3 tasks
- Verifying task distribution across roles
- Dependency chain setup
- Dashboard generation

### test_multi_agent.py

Tests complex multi-agent coordination:
- Authentication feature with all 5 agent roles
- Automatic feature breakdown
- Agent registry and capacity management
- Parallel task execution

**What it tests**:
- Workflows with 7+ tasks
- All 5 roles (architect, backend, frontend, devops, qa)
- Max agent capacity (5 agents)
- Dependency graph with multiple paths
- Ready task identification

### test_peer_communication.py

Tests agent-to-agent messaging:
- Basic message sending and receiving
- Broadcast messages to all agents
- Conversation threading
- Different message types
- Helper functions

**What it tests**:
- REQUEST_INFO, PROVIDE_INFO message types
- NOTIFICATION broadcasts
- Reply threading (reply_to)
- Unread message counting
- Conversation history between agents

## Running Tests

### Run All Tests

```bash
./run_all_tests.sh
```

This runs all tests and provides a summary with pass/fail statistics.

### Run Individual Tests

```bash
# Simple workflow tests
python3 test_simple_workflow.py

# Multi-agent coordination tests
python3 test_multi_agent.py

# Peer communication tests
python3 test_peer_communication.py
```

## Test Output

Tests provide detailed output including:
- ✓ marks for successful assertions
- Task breakdowns and assignments
- Agent registration status
- Message flow diagrams
- Dashboard views (ASCII art)
- Summary statistics

**Example Output**:

```
╔══════════════════════════════════════════════════════════════╗
║     Agent Orchestration System - Test Suite                 ║
╚══════════════════════════════════════════════════════════════╝

🧹 Cleaning up previous test artifacts...
✓ Cleanup complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Running: test_simple_workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEST: Simple Workflow - Contact Form
✓ Creating workflow...
✓ Workflow created: workflow-20260111-153045
...
✅ TEST PASSED: Simple Workflow

╔══════════════════════════════════════════════════════════════╗
║                       TEST SUMMARY                           ║
╚══════════════════════════════════════════════════════════════╝

  Total Tests:   3
  Passed:        3
  Failed:        0

╔══════════════════════════════════════════════════════════════╗
║          🎉 ALL TESTS PASSED! (100% Success)                 ║
╚══════════════════════════════════════════════════════════════╝

✅ The orchestration system is working correctly!
```

## Test Coverage

The test suite covers:

### Core Functionality
- ✅ Workflow creation and management
- ✅ Task breakdown and assignment
- ✅ Dependency management
- ✅ Priority levels

### Agent Management
- ✅ Agent registration
- ✅ Capacity limits (max 5 agents)
- ✅ Role-based assignment
- ✅ Capability tracking

### Communication
- ✅ Peer-to-peer messaging
- ✅ Broadcast messages
- ✅ Conversation threading
- ✅ Message types (6 types tested)
- ✅ Unread tracking

### Workflows
- ✅ Simple workflows (3 tasks)
- ✅ Complex workflows (7+ tasks, all roles)
- ✅ Parallel execution
- ✅ Dependency chains
- ✅ Diamond dependencies

## Not Covered (Future Tests)

These features work but don't have automated tests yet:

- Checkpoint saving and loading
- Crash recovery and agent restart
- Workflow pause and resume
- Health monitoring
- Dashboard live view
- Actual agent execution (simulated in current tests)

These would require:
- Mock agent processes
- Simulated crashes
- Time-based testing
- Terminal interaction

## Adding New Tests

To add a new test:

1. Create `test_<feature>.py` in this directory
2. Follow the existing test structure:
   ```python
   def test_feature():
       print("=" * 60)
       print("TEST: Feature Name")
       print("=" * 60)

       # Test code with assertions

       print("✅ TEST PASSED: Feature Name")
       return True
   ```
3. Add to `run_all_tests.sh`:
   ```bash
   run_test "$TEST_DIR/test_<feature>.py"
   ```
4. Update this README with test description

## Troubleshooting

### Tests Fail with "Module not found"

Make sure you're running from the repository root or the tests have the correct path:

```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude/skills/fork-terminal/tools"))
```

### Tests Leave Artifacts

Tests create temporary directories in `/tmp/test-orchestration-*` and `/tmp/test-messaging-*`.

Clean up manually if needed:
```bash
rm -rf /tmp/test-orchestration-* /tmp/test-messaging-*
```

Or let `run_all_tests.sh` clean them automatically.

### Tests Hang

If tests hang, it may be due to:
- File system issues (check `/tmp` permissions)
- Previous test processes still running
- JSON file corruption

Kill any stuck processes:
```bash
pkill -f "test_.*\.py"
```

## Test Philosophy

These tests follow several principles:

1. **Fast**: Tests run in seconds, no long waits
2. **Isolated**: Each test uses separate directories
3. **Repeatable**: Tests clean up after themselves
4. **Readable**: Clear output with ✓ and ❌ symbols
5. **Comprehensive**: Cover happy paths and edge cases

## Continuous Integration

To run these tests in CI:

```yaml
# .github/workflows/test.yml
name: Test Orchestration
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Run tests
        run: |
          cd tests/orchestration
          ./run_all_tests.sh
```

## Contributing

When adding features to the orchestration system:

1. Write tests first (TDD)
2. Run `./run_all_tests.sh` before committing
3. Ensure all tests pass
4. Update this README with new test descriptions

## License

Same as main repository.
