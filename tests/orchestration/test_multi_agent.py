#!/usr/bin/env python3
"""
Test Multi-Agent Coordination - Authentication Feature

Tests complex workflow with multiple agents working in parallel, dependencies,
and agent-to-agent communication.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude/skills/fork-terminal/tools"))

from orchestrator_main import MainOrchestrator, break_down_feature
from orchestrator import TaskManager, AgentRegistry, DependencyManager
from message_bus import MessageBus, MessageType
from dashboard import Dashboard


def test_multi_agent_workflow():
    """Test authentication feature requiring all 5 agent roles."""
    print("=" * 60)
    print("TEST: Multi-Agent Workflow - Authentication")
    print("=" * 60)

    comm_dir = "/tmp/test-orchestration-multiagent"
    os.makedirs(comm_dir, exist_ok=True)

    orchestrator = MainOrchestrator(comm_dir=comm_dir)

    # Complex workflow with all roles
    tasks = [
        {
            "description": "Design authentication architecture (OAuth flow, JWT, session management)",
            "role": "architect",
            "priority": "P1"
        },
        {
            "description": "Set up OAuth provider configuration (Google, GitHub)",
            "role": "devops",
            "priority": "P1",
            "dependencies": [0]
        },
        {
            "description": "Create user model and database schema",
            "role": "backend",
            "priority": "P1",
            "dependencies": [0]
        },
        {
            "description": "Implement OAuth callback handler and JWT generation",
            "role": "backend",
            "priority": "P1",
            "dependencies": [1, 2]
        },
        {
            "description": "Create login UI with OAuth buttons",
            "role": "frontend",
            "priority": "P1",
            "dependencies": [3]
        },
        {
            "description": "Add authentication middleware and route protection",
            "role": "backend",
            "priority": "P1",
            "dependencies": [3]
        },
        {
            "description": "Write integration tests for auth flow",
            "role": "qa",
            "priority": "P1",
            "dependencies": [4, 5]
        }
    ]

    print("\n✓ Creating complex workflow...")
    workflow_id = orchestrator.create_workflow(
        name="User Authentication",
        description="Implement OAuth authentication with JWT",
        tasks_breakdown=tasks
    )
    print(f"✓ Workflow created: {workflow_id}")

    # Verify all roles are represented
    task_mgr = TaskManager(comm_dir)

    architect_tasks = task_mgr.get_tasks_by_role("architect")
    backend_tasks = task_mgr.get_tasks_by_role("backend")
    frontend_tasks = task_mgr.get_tasks_by_role("frontend")
    devops_tasks = task_mgr.get_tasks_by_role("devops")
    qa_tasks = task_mgr.get_tasks_by_role("qa")

    assert len(architect_tasks) == 1, "Should have 1 architect task"
    assert len(backend_tasks) == 3, "Should have 3 backend tasks"
    assert len(frontend_tasks) == 1, "Should have 1 frontend task"
    assert len(devops_tasks) == 1, "Should have 1 devops task"
    assert len(qa_tasks) == 1, "Should have 1 QA task"

    print("\n✓ All agent roles represented:")
    print(f"  - Architect: {len(architect_tasks)} task(s)")
    print(f"  - Backend: {len(backend_tasks)} task(s)")
    print(f"  - Frontend: {len(frontend_tasks)} task(s)")
    print(f"  - DevOps: {len(devops_tasks)} task(s)")
    print(f"  - QA: {len(qa_tasks)} task(s)")

    # Check dependency graph
    dep_mgr = DependencyManager(comm_dir)

    # Get first task (architect) - should have no dependencies
    arch_task = architect_tasks[0]
    arch_deps = dep_mgr.get_dependencies(arch_task.task_id)
    assert len(arch_deps) == 0, "Architect task should have no dependencies"
    print(f"\n✓ Architect task (Task 0) has no dependencies")

    # Check ready tasks - only architect should be ready
    ready = dep_mgr.get_ready_tasks(task_mgr)
    assert len(ready) == 1, "Only architect task should be ready initially"
    print(f"✓ Ready tasks: {len(ready)} (Architect only)")

    # Display workflow status
    status = orchestrator.get_workflow_status(workflow_id)

    print("\n✓ Workflow status:")
    print(f"  - Total tasks: {status['progress']['total']}")
    print(f"  - Pending: {status['progress']['pending']}")

    # Display dashboard
    dashboard = Dashboard(comm_dir)
    print("\n" + "=" * 60)
    print("DASHBOARD VIEW:")
    print("=" * 60)
    summary = dashboard.generate_summary(status)
    print(summary)

    assert status['progress']['total'] == 7, "Should have 7 total tasks"

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Multi-Agent Workflow")
    print("=" * 60)

    return True


def test_break_down_feature():
    """Test automatic feature breakdown."""
    print("\n" + "=" * 60)
    print("TEST: Automatic Feature Breakdown")
    print("=" * 60)

    feature = "Add user authentication with OAuth"
    tasks = break_down_feature(feature)

    print(f"\n✓ Breaking down feature: '{feature}'")
    print(f"✓ Generated {len(tasks)} tasks:")

    # Verify tasks were generated
    assert len(tasks) > 0, "Should generate at least one task"

    roles_found = set()
    for i, task in enumerate(tasks):
        print(f"\n  Task {i+1}:")
        print(f"    Role: {task['role']}")
        print(f"    Priority: {task['priority']}")
        print(f"    Description: {task['description'][:60]}...")
        roles_found.add(task['role'])

        # Verify required fields
        assert 'description' in task
        assert 'role' in task
        assert 'priority' in task

    print(f"\n✓ Roles involved: {', '.join(sorted(roles_found))}")
    print(f"✓ All tasks have required fields")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Feature Breakdown")
    print("=" * 60)

    return True


def test_agent_registry():
    """Test agent registration and capacity management."""
    print("\n" + "=" * 60)
    print("TEST: Agent Registry")
    print("=" * 60)

    comm_dir = "/tmp/test-orchestration-registry"
    os.makedirs(comm_dir, exist_ok=True)

    registry = AgentRegistry(comm_dir, max_agents=3)

    # Register agents
    registered = []

    agent1 = registry.register_agent(
        agent_id="backend-001",
        role="backend",
        capabilities=["api", "database"]
    )
    assert agent1 == True, "First agent should register successfully"
    registered.append("backend-001")
    print("✓ Registered backend-001")

    agent2 = registry.register_agent(
        agent_id="frontend-001",
        role="frontend",
        capabilities=["react", "ui"]
    )
    assert agent2 == True, "Second agent should register successfully"
    registered.append("frontend-001")
    print("✓ Registered frontend-001")

    agent3 = registry.register_agent(
        agent_id="devops-001",
        role="devops",
        capabilities=["docker", "ci-cd"]
    )
    assert agent3 == True, "Third agent should register successfully"
    registered.append("devops-001")
    print("✓ Registered devops-001")

    # Try to register 4th agent (should fail - max is 3)
    agent4 = registry.register_agent(
        agent_id="qa-001",
        role="qa",
        capabilities=["testing"]
    )
    assert agent4 == False, "Fourth agent should fail to register (max 3)"
    print("✓ Fourth agent correctly rejected (max capacity reached)")

    # List agents
    all_agents = registry.list_agents()
    assert len(all_agents) == 3, "Should have 3 registered agents"
    print(f"\n✓ Total agents: {len(all_agents)}")

    # List by role
    backend_agents = registry.list_agents(role="backend")
    assert len(backend_agents) == 1, "Should have 1 backend agent"
    print(f"✓ Backend agents: {len(backend_agents)}")

    # Unregister one agent
    registry.unregister_agent("backend-001")
    remaining = registry.list_agents()
    assert len(remaining) == 2, "Should have 2 agents after unregistering one"
    print(f"✓ After unregistering backend-001: {len(remaining)} agents")

    # Now 4th agent should register successfully
    agent4 = registry.register_agent(
        agent_id="qa-001",
        role="qa",
        capabilities=["testing"]
    )
    assert agent4 == True, "Fourth agent should now register (slot available)"
    print("✓ Fourth agent successfully registered after slot freed")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Agent Registry")
    print("=" * 60)

    return True


def test_parallel_execution():
    """Test that independent tasks can execute in parallel."""
    print("\n" + "=" * 60)
    print("TEST: Parallel Task Execution")
    print("=" * 60)

    comm_dir = "/tmp/test-orchestration-parallel"
    os.makedirs(comm_dir, exist_ok=True)

    orchestrator = MainOrchestrator(comm_dir=comm_dir)

    # Create 5 independent tasks (no dependencies)
    tasks = [
        {"description": "Backend API task", "role": "backend", "priority": "P1"},
        {"description": "Frontend UI task", "role": "frontend", "priority": "P1"},
        {"description": "DevOps setup task", "role": "devops", "priority": "P1"},
        {"description": "QA test task", "role": "qa", "priority": "P1"},
        {"description": "Architecture docs", "role": "architect", "priority": "P1"}
    ]

    workflow_id = orchestrator.create_workflow(
        name="Parallel Tasks",
        description="Test parallel execution",
        tasks_breakdown=tasks
    )

    print(f"\n✓ Workflow created: {workflow_id}")

    # All tasks should be ready (no dependencies)
    dep_mgr = DependencyManager(comm_dir)
    task_mgr = TaskManager(comm_dir)

    ready = dep_mgr.get_ready_tasks(task_mgr)
    assert len(ready) == 5, "All 5 tasks should be ready (no dependencies)"

    print(f"✓ All {len(ready)} tasks are ready for parallel execution")
    print("✓ No dependencies blocking any tasks")

    # Verify we could spawn 5 agents (one per task)
    registry = AgentRegistry(comm_dir, max_agents=5)
    print(f"✓ Max agents ({registry.max_agents}) matches task count ({len(ready)})")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Parallel Execution")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\n🧪 Running Multi-Agent Coordination Tests\n")

    try:
        test_multi_agent_workflow()
        test_break_down_feature()
        test_agent_registry()
        test_parallel_execution()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
