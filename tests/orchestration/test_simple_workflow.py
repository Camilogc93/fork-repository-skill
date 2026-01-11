#!/usr/bin/env python3
"""
Test Simple Workflow - Contact Form Feature

Tests basic workflow creation, task assignment, and completion with a simple
single-agent scenario.
"""

import os
import sys
import time
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude/skills/fork-terminal/tools"))

from orchestrator_main import MainOrchestrator
from orchestrator import TaskManager, AgentRegistry, TaskStatus, TaskPriority
from dashboard import Dashboard


def test_simple_workflow():
    """Test simple contact form workflow with 3 tasks."""
    print("=" * 60)
    print("TEST: Simple Workflow - Contact Form")
    print("=" * 60)

    # Create orchestrator
    comm_dir = "/tmp/test-orchestration-simple"
    os.makedirs(comm_dir, exist_ok=True)

    orchestrator = MainOrchestrator(comm_dir=comm_dir)

    # Define simple workflow
    tasks = [
        {
            "description": "Create contact API endpoint (/api/contact POST)",
            "role": "backend",
            "priority": "P1"
        },
        {
            "description": "Build ContactForm component with name, email, message fields",
            "role": "frontend",
            "priority": "P1",
            "dependencies": [0]  # Needs API contract from backend
        },
        {
            "description": "Write form validation tests (email format, required fields)",
            "role": "qa",
            "priority": "P1",
            "dependencies": [1]  # Needs frontend component
        }
    ]

    print("\n✓ Creating workflow...")
    workflow_id = orchestrator.create_workflow(
        name="Contact Form Feature",
        description="Add contact form with backend API",
        tasks_breakdown=tasks
    )
    print(f"✓ Workflow created: {workflow_id}")

    # Verify workflow was created
    assert workflow_id is not None
    assert len(workflow_id) > 0

    # Check task creation
    task_mgr = TaskManager(comm_dir)
    all_tasks = []

    # Get tasks by role
    backend_tasks = task_mgr.get_tasks_by_role("backend")
    frontend_tasks = task_mgr.get_tasks_by_role("frontend")
    qa_tasks = task_mgr.get_tasks_by_role("qa")

    assert len(backend_tasks) == 1, "Should have 1 backend task"
    assert len(frontend_tasks) == 1, "Should have 1 frontend task"
    assert len(qa_tasks) == 1, "Should have 1 QA task"

    print("\n✓ Task breakdown verified:")
    print(f"  - Backend tasks: {len(backend_tasks)}")
    print(f"  - Frontend tasks: {len(frontend_tasks)}")
    print(f"  - QA tasks: {len(qa_tasks)}")

    # Get workflow status
    status = orchestrator.get_workflow_status(workflow_id)

    print("\n✓ Workflow status:")
    print(f"  - Name: {status['workflow']['name']}")
    print(f"  - Status: {status['workflow']['status']}")
    print(f"  - Total tasks: {status['progress']['total']}")
    print(f"  - Pending: {status['progress']['pending']}")

    # Display dashboard
    dashboard = Dashboard(comm_dir)
    print("\n" + "=" * 60)
    print("DASHBOARD VIEW:")
    print("=" * 60)
    summary = dashboard.generate_summary(status)
    print(summary)

    # Verify workflow structure
    assert status['workflow']['name'] == "Contact Form Feature"
    assert status['progress']['total'] == 3
    assert status['progress']['pending'] == 3  # None started yet

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Simple Workflow")
    print("=" * 60)

    return True


def test_task_dependencies():
    """Test that task dependencies are properly set up."""
    print("\n" + "=" * 60)
    print("TEST: Task Dependencies")
    print("=" * 60)

    comm_dir = "/tmp/test-orchestration-deps"
    os.makedirs(comm_dir, exist_ok=True)

    orchestrator = MainOrchestrator(comm_dir=comm_dir)

    tasks = [
        {
            "description": "Task A - No dependencies",
            "role": "backend",
            "priority": "P1"
        },
        {
            "description": "Task B - Depends on A",
            "role": "frontend",
            "priority": "P1",
            "dependencies": [0]
        },
        {
            "description": "Task C - Depends on A and B",
            "role": "qa",
            "priority": "P1",
            "dependencies": [0, 1]
        }
    ]

    workflow_id = orchestrator.create_workflow(
        name="Dependency Test",
        description="Test task dependencies",
        tasks_breakdown=tasks
    )

    print(f"\n✓ Workflow created: {workflow_id}")

    # Check dependencies
    from orchestrator import DependencyManager
    dep_mgr = DependencyManager(comm_dir)

    task_mgr = TaskManager(comm_dir)
    all_tasks = task_mgr.get_tasks_by_role("backend") + \
                task_mgr.get_tasks_by_role("frontend") + \
                task_mgr.get_tasks_by_role("qa")

    task_a = [t for t in all_tasks if "Task A" in t.description][0]
    task_b = [t for t in all_tasks if "Task B" in t.description][0]
    task_c = [t for t in all_tasks if "Task C" in t.description][0]

    # Task A has no dependencies
    deps_a = dep_mgr.get_dependencies(task_a.task_id)
    assert len(deps_a) == 0, "Task A should have no dependencies"
    print(f"✓ Task A has {len(deps_a)} dependencies")

    # Task B depends on A
    deps_b = dep_mgr.get_dependencies(task_b.task_id)
    assert len(deps_b) == 1, "Task B should depend on 1 task"
    assert task_a.task_id in deps_b, "Task B should depend on Task A"
    print(f"✓ Task B depends on {len(deps_b)} task(s)")

    # Task C depends on A and B
    deps_c = dep_mgr.get_dependencies(task_c.task_id)
    assert len(deps_c) == 2, "Task C should depend on 2 tasks"
    assert task_a.task_id in deps_c, "Task C should depend on Task A"
    assert task_b.task_id in deps_c, "Task C should depend on Task B"
    print(f"✓ Task C depends on {len(deps_c)} task(s)")

    # Check ready tasks (only Task A should be ready)
    ready = dep_mgr.get_ready_tasks(task_mgr)
    assert len(ready) == 1, "Only Task A should be ready initially"
    assert task_a.task_id in ready, "Task A should be ready"
    print(f"\n✓ Ready tasks: {len(ready)} (Task A only)")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Task Dependencies")
    print("=" * 60)

    return True


def test_priority_levels():
    """Test that tasks with different priorities are created correctly."""
    print("\n" + "=" * 60)
    print("TEST: Priority Levels")
    print("=" * 60)

    comm_dir = "/tmp/test-orchestration-priority"
    os.makedirs(comm_dir, exist_ok=True)

    task_mgr = TaskManager(comm_dir)

    # Create tasks with different priorities
    p0_task = task_mgr.create_task(
        "task-p0",
        "Critical security fix",
        role="backend",
        priority=TaskPriority.P0
    )

    p1_task = task_mgr.create_task(
        "task-p1",
        "High priority feature",
        role="frontend",
        priority=TaskPriority.P1
    )

    p2_task = task_mgr.create_task(
        "task-p2",
        "Medium priority enhancement",
        role="backend",
        priority=TaskPriority.P2
    )

    p3_task = task_mgr.create_task(
        "task-p3",
        "Low priority refactoring",
        role="backend",
        priority=TaskPriority.P3
    )

    # Verify priorities
    assert p0_task.priority == TaskPriority.P0
    assert p1_task.priority == TaskPriority.P1
    assert p2_task.priority == TaskPriority.P2
    assert p3_task.priority == TaskPriority.P3

    print("\n✓ Task priorities verified:")
    print(f"  - P0 (Critical): {p0_task.description}")
    print(f"  - P1 (High): {p1_task.description}")
    print(f"  - P2 (Medium): {p2_task.description}")
    print(f"  - P3 (Low): {p3_task.description}")

    print("\n" + "=" * 60)
    print("✅ TEST PASSED: Priority Levels")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\n🧪 Running Simple Workflow Tests\n")

    try:
        # Run tests
        test_simple_workflow()
        test_task_dependencies()
        test_priority_levels()

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
