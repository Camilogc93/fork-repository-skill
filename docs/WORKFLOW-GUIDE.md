# Workflow Management Guide

This guide covers advanced workflow patterns, optimization strategies, and best practices for managing multi-agent orchestration.

## Table of Contents

- [Workflow Basics](#workflow-basics)
- [Task Decomposition](#task-decomposition)
- [Dependency Management](#dependency-management)
- [Workflow Patterns](#workflow-patterns)
- [Optimization Strategies](#optimization-strategies)
- [Monitoring and Control](#monitoring-and-control)
- [Error Handling](#error-handling)
- [Advanced Techniques](#advanced-techniques)
- [Real-World Examples](#real-world-examples)

## Workflow Basics

### What is a Workflow?

A **workflow** is a coordinated sequence of tasks executed by specialized agents to accomplish a larger goal (feature, bug fix, refactoring, etc.).

### Workflow Lifecycle

```
Created → Running → [Paused] → Completed
                  ↓
                Failed
```

**States**:
- **Created**: Workflow defined, tasks queued
- **Running**: Agents actively executing tasks
- **Paused**: Workflow suspended, can be resumed
- **Completed**: All tasks successfully finished
- **Failed**: Critical failure, manual intervention needed

### Creating a Basic Workflow

```python
from orchestrator_main import MainOrchestrator

orchestrator = MainOrchestrator()

tasks = [
    {
        "description": "Task 1",
        "role": "backend",
        "priority": "P1"
    },
    {
        "description": "Task 2",
        "role": "frontend",
        "priority": "P1"
    }
]

workflow_id = orchestrator.create_workflow(
    name="My Feature",
    description="Implement feature X",
    tasks_breakdown=tasks
)

orchestrator.start_workflow(workflow_id)
```

## Task Decomposition

### Breaking Down Features

The key to successful orchestration is decomposing features into appropriate tasks.

### Decomposition Principles

1. **Atomic Tasks**: Each task should be independently executable
2. **Clear Ownership**: Each task should map to one role
3. **Testable**: Each task should produce verifiable output
4. **Reasonable Size**: Tasks should take 10-60 minutes
5. **Well-Defined**: Clear description and acceptance criteria

### Example: User Authentication Feature

**Feature**: "Add user authentication with OAuth"

**Bad Decomposition** (too coarse):
```python
tasks = [
    {
        "description": "Implement authentication",
        "role": "backend"  # Too vague, too large
    }
]
```

**Good Decomposition**:
```python
tasks = [
    {
        "description": "Design auth architecture (flow, tokens, session management)",
        "role": "architect",
        "priority": "P1"
    },
    {
        "description": "Implement OAuth provider configuration (Google, GitHub)",
        "role": "backend",
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
    },
    {
        "description": "Configure OAuth credentials in production",
        "role": "devops",
        "priority": "P2",
        "dependencies": [6]
    }
]
```

### Decomposition by Role

Think about which roles are needed:

```python
def analyze_feature_for_roles(feature_description):
    """
    Analyze feature to determine which roles are needed.

    Returns dict of roles and their involvement.
    """
    roles_needed = {
        "architect": False,   # System design needed?
        "backend": False,     # Server-side logic?
        "frontend": False,    # UI changes?
        "devops": False,      # Infrastructure/deployment?
        "qa": False          # Testing required?
    }

    # Example logic
    if "database" in feature_description or "API" in feature_description:
        roles_needed["backend"] = True

    if "UI" in feature_description or "component" in feature_description:
        roles_needed["frontend"] = True

    if "deploy" in feature_description or "infrastructure" in feature_description:
        roles_needed["devops"] = True

    # QA always needed for new features
    roles_needed["qa"] = True

    # Architect needed for complex features
    if any(word in feature_description for word in ["system", "architecture", "design"]):
        roles_needed["architect"] = True

    return roles_needed
```

### Task Size Guidelines

**Too Small** (< 5 minutes):
```python
{
    "description": "Import React",
    "role": "frontend"  # Too trivial
}
```

**Good Size** (10-60 minutes):
```python
{
    "description": "Create LoginForm component with email/password inputs and validation",
    "role": "frontend"
}
```

**Too Large** (> 2 hours):
```python
{
    "description": "Build entire e-commerce checkout system",
    "role": "backend"  # Should be broken into multiple tasks
}
```

## Dependency Management

### Understanding Dependencies

Tasks often depend on other tasks completing first. The orchestrator uses a **Directed Acyclic Graph (DAG)** to manage dependencies.

### Defining Dependencies

```python
tasks = [
    {
        "description": "Task A",
        "role": "backend",
        "priority": "P1"
        # No dependencies - will start immediately
    },
    {
        "description": "Task B",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [0]  # Depends on Task A (index 0)
    },
    {
        "description": "Task C",
        "role": "qa",
        "priority": "P1",
        "dependencies": [0, 1]  # Depends on both Task A and Task B
    }
]
```

### Dependency Patterns

#### Sequential (Chain)

Tasks must execute in order:

```python
# Task A → Task B → Task C
tasks = [
    {"description": "Design schema", "role": "architect"},
    {"description": "Create tables", "role": "backend", "dependencies": [0]},
    {"description": "Add test data", "role": "backend", "dependencies": [1]}
]
```

**Execution Timeline**:
```
T0: Task A starts
T1: Task A completes, Task B starts
T2: Task B completes, Task C starts
T3: Task C completes
```

#### Parallel (Fan-out)

Multiple tasks depend on one prerequisite:

```python
# Task A → [Task B, Task C, Task D]
tasks = [
    {"description": "Design API", "role": "architect"},
    {"description": "Implement endpoint 1", "role": "backend", "dependencies": [0]},
    {"description": "Implement endpoint 2", "role": "backend", "dependencies": [0]},
    {"description": "Implement endpoint 3", "role": "backend", "dependencies": [0]}
]
```

**Execution Timeline** (assuming 3+ agents available):
```
T0: Task A starts
T1: Task A completes, Tasks B, C, D start in parallel
T2: All parallel tasks complete
```

#### Join (Fan-in)

Multiple tasks must complete before next task:

```python
# [Task A, Task B, Task C] → Task D
tasks = [
    {"description": "Backend API", "role": "backend"},
    {"description": "Frontend UI", "role": "frontend"},
    {"description": "DevOps config", "role": "devops"},
    {"description": "Integration tests", "role": "qa", "dependencies": [0, 1, 2]}
]
```

**Execution Timeline**:
```
T0: Tasks A, B, C start in parallel
T1-3: Tasks complete at different times
T4: When all are done, Task D starts
```

#### Diamond

Combination of fan-out and fan-in:

```python
#     Task A
#    /   |   \
#   B    C    D
#    \   |   /
#     Task E
tasks = [
    {"description": "Design", "role": "architect"},
    {"description": "Backend", "role": "backend", "dependencies": [0]},
    {"description": "Frontend", "role": "frontend", "dependencies": [0]},
    {"description": "DevOps", "role": "devops", "dependencies": [0]},
    {"description": "QA", "role": "qa", "dependencies": [1, 2, 3]}
]
```

### Circular Dependency Detection

The orchestrator automatically detects circular dependencies:

```python
# This will fail
tasks = [
    {"description": "Task A", "role": "backend", "dependencies": [1]},
    {"description": "Task B", "role": "frontend", "dependencies": [0]}  # Circular!
]
# Error: Circular dependency detected: Task A → Task B → Task A
```

### Dependency Best Practices

1. **Minimize Dependencies**: Only add dependencies when truly required
2. **Prefer Parallel**: Design tasks to run in parallel when possible
3. **Clear Communication**: Use peer messages for optional coordination
4. **Document Reasons**: Comment why dependencies exist

```python
tasks = [
    {
        "description": "Create user API",
        "role": "backend"
    },
    {
        "description": "Create user UI",
        "role": "frontend",
        "dependencies": [0],  # REASON: UI needs API contract
        "metadata": {
            "dependency_reason": "Frontend needs API endpoint contract"
        }
    }
]
```

## Workflow Patterns

### Pattern 1: Linear Workflow

**Use Case**: Simple sequential tasks

```python
tasks = [
    {"description": "Step 1", "role": "backend"},
    {"description": "Step 2", "role": "backend", "dependencies": [0]},
    {"description": "Step 3", "role": "backend", "dependencies": [1]}
]
```

**Characteristics**:
- Simple to understand
- No parallelism
- Predictable execution
- Good for: Migrations, one-time scripts

### Pattern 2: Parallel Independent

**Use Case**: Multiple unrelated tasks

```python
tasks = [
    {"description": "Fix bug A", "role": "backend"},
    {"description": "Fix bug B", "role": "frontend"},
    {"description": "Update docs", "role": "architect"}
]
```

**Characteristics**:
- Maximum parallelism
- Fast completion
- No coordination needed
- Good for: Bug fixes, independent features

### Pattern 3: Architect-Led

**Use Case**: Complex features needing design first

```python
tasks = [
    {"description": "Design system", "role": "architect"},
    {"description": "Backend impl", "role": "backend", "dependencies": [0]},
    {"description": "Frontend impl", "role": "frontend", "dependencies": [0]},
    {"description": "DevOps setup", "role": "devops", "dependencies": [0]},
    {"description": "QA tests", "role": "qa", "dependencies": [1, 2, 3]}
]
```

**Characteristics**:
- Design-first approach
- Parallel implementation
- Final testing phase
- Good for: New features, architecture changes

### Pattern 4: Iterative Development

**Use Case**: MVP then enhancements

```python
# Phase 1: MVP
mvp_tasks = [
    {"description": "Basic backend", "role": "backend"},
    {"description": "Basic frontend", "role": "frontend"},
    {"description": "Basic tests", "role": "qa", "dependencies": [0, 1]}
]

# Create and complete MVP workflow
mvp_id = orchestrator.create_workflow("MVP", "Minimal version", mvp_tasks)
orchestrator.start_workflow(mvp_id)
# ... wait for completion ...

# Phase 2: Enhancements
enhancement_tasks = [
    {"description": "Add feature X", "role": "backend"},
    {"description": "Add UI for X", "role": "frontend"},
    {"description": "Test X", "role": "qa", "dependencies": [0, 1]}
]

enh_id = orchestrator.create_workflow("Enhancements", "Add features", enhancement_tasks)
orchestrator.start_workflow(enh_id)
```

**Characteristics**:
- Multiple workflow phases
- Deploy incrementally
- Get feedback between phases
- Good for: Large features, experiments

### Pattern 5: Hotfix

**Use Case**: Urgent production fixes

```python
tasks = [
    {"description": "Fix critical bug", "role": "backend", "priority": "P0"},
    {"description": "Add regression test", "role": "qa", "priority": "P0", "dependencies": [0]},
    {"description": "Deploy to prod", "role": "devops", "priority": "P0", "dependencies": [1]}
]
```

**Characteristics**:
- All P0 priority
- Minimal tasks
- Fast deployment
- Good for: Production incidents

### Pattern 6: Full-Stack Feature

**Use Case**: Complete feature spanning all layers

```python
tasks = [
    # Design phase
    {"description": "Design architecture", "role": "architect", "priority": "P1"},

    # Infrastructure phase
    {"description": "Set up database", "role": "devops", "priority": "P1", "dependencies": [0]},

    # Implementation phase (parallel)
    {"description": "Create backend API", "role": "backend", "priority": "P1", "dependencies": [1]},
    {"description": "Create frontend UI", "role": "frontend", "priority": "P1", "dependencies": [0]},

    # Integration phase
    {"description": "Connect FE to BE", "role": "frontend", "priority": "P1", "dependencies": [2, 3]},

    # Testing phase
    {"description": "Unit tests", "role": "qa", "priority": "P1", "dependencies": [2]},
    {"description": "Integration tests", "role": "qa", "priority": "P1", "dependencies": [4]},
    {"description": "E2E tests", "role": "qa", "priority": "P1", "dependencies": [4]},

    # Deployment phase
    {"description": "Deploy to staging", "role": "devops", "priority": "P2", "dependencies": [6, 7]},
    {"description": "Smoke test staging", "role": "qa", "priority": "P2", "dependencies": [8]},
    {"description": "Deploy to prod", "role": "devops", "priority": "P2", "dependencies": [9]}
]
```

**Characteristics**:
- Multiple phases
- Mix of parallel and sequential
- All roles involved
- Good for: Major features

## Optimization Strategies

### Maximizing Parallelism

**Goal**: Reduce total workflow time by running tasks in parallel.

**Strategy 1: Independent Task Design**

```python
# Bad: Unnecessary dependency
tasks = [
    {"description": "Backend task", "role": "backend"},
    {"description": "Frontend task", "role": "frontend", "dependencies": [0]}  # Why?
]

# Good: Parallel execution
tasks = [
    {"description": "Backend task", "role": "backend"},
    {"description": "Frontend task", "role": "frontend"}  # No dependency needed
]
```

**Strategy 2: Early Fan-out**

```python
# Design once, then fan out to multiple parallel implementations
tasks = [
    {"description": "Design API", "role": "architect"},
    {"description": "Endpoint /users", "role": "backend", "dependencies": [0]},
    {"description": "Endpoint /posts", "role": "backend", "dependencies": [0]},
    {"description": "Endpoint /comments", "role": "backend", "dependencies": [0]},
    {"description": "Endpoint /likes", "role": "backend", "dependencies": [0]}
]
```

### Resource Management

**Agent Capacity**: Max 5 concurrent agents

**Strategy**: Balance task distribution

```python
# Bad: All tasks for one role (sequential execution)
tasks = [
    {"description": "Task 1", "role": "backend"},
    {"description": "Task 2", "role": "backend"},
    {"description": "Task 3", "role": "backend"},
    {"description": "Task 4", "role": "backend"},
    {"description": "Task 5", "role": "backend"}
]
# Only 1 agent working at a time

# Good: Distribute across roles (parallel execution)
tasks = [
    {"description": "Backend task", "role": "backend"},
    {"description": "Frontend task", "role": "frontend"},
    {"description": "DevOps task", "role": "devops"},
    {"description": "QA task", "role": "qa"},
    {"description": "Docs task", "role": "architect"}
]
# All 5 agents working in parallel
```

### Priority Management

Use priorities to control execution order:

```python
tasks = [
    {"description": "Critical security fix", "role": "backend", "priority": "P0"},
    {"description": "High: User feature", "role": "frontend", "priority": "P1"},
    {"description": "Medium: Optimization", "role": "backend", "priority": "P2"},
    {"description": "Low: Refactoring", "role": "backend", "priority": "P3"}
]
```

**Priority Levels**:
- **P0** (Critical): Security issues, production down, data loss
- **P1** (High): User-facing features, important bugs
- **P2** (Medium): Enhancements, non-critical bugs
- **P3** (Low): Nice-to-haves, tech debt, refactoring

### Task Batching

Group related small tasks:

```python
# Bad: Too granular
tasks = [
    {"description": "Create User model", "role": "backend"},
    {"description": "Create Post model", "role": "backend"},
    {"description": "Create Comment model", "role": "backend"},
    # 10 more model tasks...
]

# Good: Batched
tasks = [
    {"description": "Create all database models (User, Post, Comment, Like, ...)", "role": "backend"},
    {"description": "Create API endpoints", "role": "backend", "dependencies": [0]},
    {"description": "Create frontend components", "role": "frontend", "dependencies": [1]}
]
```

## Monitoring and Control

### Real-Time Monitoring

```python
from dashboard import Dashboard

dashboard = Dashboard()

# Start live view
dashboard.start_live_view(
    lambda: orchestrator.get_workflow_status(workflow_id),
    refresh_interval=2  # Update every 2 seconds
)
```

### Workflow Status

```python
status = orchestrator.get_workflow_status(workflow_id)

print(f"Workflow: {status['workflow']['name']}")
print(f"Status: {status['workflow']['status']}")
print(f"Progress: {status['progress']['completed']}/{status['progress']['total']}")

# Check individual tasks
for task_id, task_info in status['tasks'].items():
    print(f"Task: {task_info['description']}")
    print(f"Status: {task_info['status']}")
    print(f"Assigned to: {task_info.get('assigned_to', 'Unassigned')}")
```

### Pausing Workflows

```python
# Pause for later
orchestrator.pause_workflow(workflow_id)

# Check paused workflows
paused = orchestrator.list_paused_workflows()
for wf in paused:
    print(f"Paused: {wf['name']} at {wf['paused_at']}")
```

### Resuming Workflows

```python
# Resume from pause
orchestrator.resume_workflow(workflow_id)

# Or resume specific agents
orchestrator.resume_agent("backend-001")
```

### Manual Intervention

```python
# Check blocked tasks
blocked = orchestrator.get_blocked_tasks()
for task in blocked:
    print(f"Blocked: {task.description}")
    print(f"Reason: {task.metadata.get('blocked_reason')}")

# Manually unblock
orchestrator.unblock_task(task_id, resolution="Issue resolved manually")

# Reassign task to different agent
orchestrator.reassign_task(task_id, new_agent_id="backend-002")
```

## Error Handling

### Agent Failures

The system automatically handles agent crashes through checkpoints and recovery.

**What Happens**:
1. Agent stops sending heartbeat
2. Health monitor detects (after 120s)
3. Recovery manager loads last checkpoint
4. New agent spawned with checkpoint data
5. Task resumed from last checkpoint

**Max Recovery Attempts**: 3 per agent

After 3 failures:
```python
# Task marked as failed
# Workflow paused
# User notified

status = orchestrator.get_workflow_status(workflow_id)
failed_tasks = [t for t in status['tasks'].values() if t['status'] == 'failed']

for task in failed_tasks:
    print(f"Failed: {task['description']}")
    print(f"Error: {task.get('error')}")
    print(f"Recovery attempts: {task.get('recovery_attempts')}")
```

### Task Failures

Handle specific task failures:

```python
# Check for failed tasks
status = orchestrator.get_workflow_status(workflow_id)

if status['workflow']['status'] == 'failed':
    # Get failed tasks
    failed = [t for t in status['tasks'].values() if t['status'] == 'failed']

    for task in failed:
        # Option 1: Retry task
        orchestrator.retry_task(task['task_id'])

        # Option 2: Skip task
        orchestrator.skip_task(task['task_id'], reason="Not critical")

        # Option 3: Reassign to different role
        orchestrator.reassign_task(task['task_id'], new_role="backend")
```

### Dependency Deadlocks

If tasks are stuck waiting for dependencies:

```python
# Identify stuck tasks
stuck_tasks = orchestrator.get_stuck_tasks(timeout_minutes=30)

for task in stuck_tasks:
    # Check dependencies
    deps = orchestrator.get_task_dependencies(task['task_id'])

    for dep in deps:
        dep_task = orchestrator.get_task(dep)
        if dep_task['status'] == 'failed':
            # Dependency failed, current task will never start
            print(f"Task {task['task_id']} blocked by failed dependency {dep}")

            # Option: Remove dependency if not critical
            orchestrator.remove_dependency(task['task_id'], dep)
```

### Timeout Handling

```python
# Set task timeout
tasks = [
    {
        "description": "Long running task",
        "role": "backend",
        "priority": "P1",
        "metadata": {
            "timeout_minutes": 60  # Fail if not complete in 60 min
        }
    }
]

# Monitor timeouts
orchestrator.check_timeouts()  # Called automatically by health monitor
```

## Advanced Techniques

### Dynamic Task Addition

Add tasks to running workflow:

```python
# Workflow running
workflow_id = orchestrator.start_workflow(...)

# Discover need for additional task
new_task = {
    "description": "Additional security check",
    "role": "qa",
    "priority": "P1"
}

orchestrator.add_task_to_workflow(workflow_id, new_task)
```

### Conditional Tasks

Tasks that only run based on conditions:

```python
tasks = [
    {
        "description": "Run integration tests",
        "role": "qa",
        "priority": "P1",
        "metadata": {
            "conditional": True,
            "condition": "if unit_tests_pass"
        }
    }
]

# In agent completion
if unit_tests_passed:
    orchestrator.enable_conditional_task(task_id)
else:
    orchestrator.skip_task(task_id, reason="Unit tests failed")
```

### Sub-Workflows

Break large workflows into smaller sub-workflows:

```python
# Main workflow
def create_feature_workflow(feature_name):
    # Phase 1: Design
    design_wf = orchestrator.create_workflow(
        f"{feature_name}: Design",
        "Design phase",
        [{"description": "Design", "role": "architect"}]
    )
    orchestrator.start_workflow(design_wf)
    orchestrator.wait_for_completion(design_wf)

    # Phase 2: Implementation
    impl_wf = orchestrator.create_workflow(
        f"{feature_name}: Implementation",
        "Implementation phase",
        [
            {"description": "Backend", "role": "backend"},
            {"description": "Frontend", "role": "frontend"}
        ]
    )
    orchestrator.start_workflow(impl_wf)
    orchestrator.wait_for_completion(impl_wf)

    # Phase 3: Testing
    test_wf = orchestrator.create_workflow(
        f"{feature_name}: Testing",
        "Testing phase",
        [{"description": "QA", "role": "qa"}]
    )
    orchestrator.start_workflow(test_wf)

    return test_wf
```

### Workflow Templates

Reusable workflow patterns:

```python
def create_crud_workflow(entity_name):
    """Template for CRUD feature workflows."""
    tasks = [
        {
            "description": f"Create {entity_name} database model",
            "role": "backend",
            "priority": "P1"
        },
        {
            "description": f"Implement {entity_name} API endpoints (CRUD)",
            "role": "backend",
            "priority": "P1",
            "dependencies": [0]
        },
        {
            "description": f"Create {entity_name} UI components",
            "role": "frontend",
            "priority": "P1",
            "dependencies": [1]
        },
        {
            "description": f"Write {entity_name} tests",
            "role": "qa",
            "priority": "P1",
            "dependencies": [1, 2]
        }
    ]

    return orchestrator.create_workflow(
        f"CRUD: {entity_name}",
        f"Implement CRUD operations for {entity_name}",
        tasks
    )

# Usage
user_wf = create_crud_workflow("User")
post_wf = create_crud_workflow("Post")
comment_wf = create_crud_workflow("Comment")
```

## Real-World Examples

### Example 1: E-commerce Product Page

```python
tasks = [
    # Design
    {
        "description": "Design product page architecture (components, data flow, state)",
        "role": "architect",
        "priority": "P1"
    },

    # Backend
    {
        "description": "Create product API endpoints (GET /products/:id, related products)",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Implement inventory check service",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Add product reviews API",
        "role": "backend",
        "priority": "P2",
        "dependencies": [1]
    },

    # Frontend
    {
        "description": "Create ProductPage component with image gallery",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [1]
    },
    {
        "description": "Implement AddToCart functionality",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [2, 4]
    },
    {
        "description": "Add ProductReviews component",
        "role": "frontend",
        "priority": "P2",
        "dependencies": [3]
    },

    # QA
    {
        "description": "Test product page load and rendering",
        "role": "qa",
        "priority": "P1",
        "dependencies": [4]
    },
    {
        "description": "Test add-to-cart flow end-to-end",
        "role": "qa",
        "priority": "P1",
        "dependencies": [5]
    },
    {
        "description": "Test reviews display and submission",
        "role": "qa",
        "priority": "P2",
        "dependencies": [6]
    },

    # DevOps
    {
        "description": "Configure CDN for product images",
        "role": "devops",
        "priority": "P2",
        "dependencies": [4]
    },
    {
        "description": "Set up caching for product data",
        "role": "devops",
        "priority": "P2",
        "dependencies": [1]
    }
]

workflow_id = orchestrator.create_workflow(
    "Product Page Feature",
    "Implement product detail page with reviews and cart",
    tasks
)
```

### Example 2: API Migration

```python
tasks = [
    # Planning
    {
        "description": "Document current API v1 endpoints and usage",
        "role": "architect",
        "priority": "P1"
    },
    {
        "description": "Design API v2 with improvements",
        "role": "architect",
        "priority": "P1",
        "dependencies": [0]
    },

    # Implementation
    {
        "description": "Implement API v2 endpoints (parallel with v1)",
        "role": "backend",
        "priority": "P1",
        "dependencies": [1]
    },
    {
        "description": "Add versioning middleware",
        "role": "backend",
        "priority": "P1",
        "dependencies": [1]
    },
    {
        "description": "Create migration guide documentation",
        "role": "architect",
        "priority": "P1",
        "dependencies": [1]
    },

    # Testing
    {
        "description": "Test API v2 endpoints",
        "role": "qa",
        "priority": "P1",
        "dependencies": [2]
    },
    {
        "description": "Test v1/v2 coexistence",
        "role": "qa",
        "priority": "P1",
        "dependencies": [2, 3]
    },

    # Frontend Migration
    {
        "description": "Update frontend to use API v2",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [5]
    },
    {
        "description": "Test frontend with API v2",
        "role": "qa",
        "priority": "P1",
        "dependencies": [7]
    },

    # Deployment
    {
        "description": "Deploy API v2 to staging",
        "role": "devops",
        "priority": "P1",
        "dependencies": [6]
    },
    {
        "description": "Smoke test staging",
        "role": "qa",
        "priority": "P1",
        "dependencies": [9]
    },
    {
        "description": "Deploy to production (with feature flag)",
        "role": "devops",
        "priority": "P1",
        "dependencies": [10]
    },

    # Deprecation (later phase)
    {
        "description": "Add deprecation warnings to API v1",
        "role": "backend",
        "priority": "P2",
        "dependencies": [11]
    },
    {
        "description": "Monitor v1 usage and coordinate sunset",
        "role": "devops",
        "priority": "P3",
        "dependencies": [12]
    }
]
```

### Example 3: Performance Optimization Sprint

```python
tasks = [
    # Analysis
    {
        "description": "Profile application and identify bottlenecks",
        "role": "architect",
        "priority": "P1"
    },

    # Database Optimization (parallel)
    {
        "description": "Add database indexes for slow queries",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Optimize N+1 queries",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Implement query result caching",
        "role": "backend",
        "priority": "P1",
        "dependencies": [0]
    },

    # Frontend Optimization (parallel)
    {
        "description": "Implement code splitting and lazy loading",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Optimize bundle size (tree shaking, compression)",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Add React.memo to expensive components",
        "role": "frontend",
        "priority": "P1",
        "dependencies": [0]
    },

    # Infrastructure Optimization
    {
        "description": "Configure CDN for static assets",
        "role": "devops",
        "priority": "P1",
        "dependencies": [0]
    },
    {
        "description": "Set up Redis caching layer",
        "role": "devops",
        "priority": "P1",
        "dependencies": [0]
    },

    # Verification
    {
        "description": "Run performance tests and compare metrics",
        "role": "qa",
        "priority": "P1",
        "dependencies": [1, 2, 3, 4, 5, 6, 7, 8]
    },
    {
        "description": "Document optimization results",
        "role": "architect",
        "priority": "P1",
        "dependencies": [9]
    }
]
```

## Best Practices Summary

1. **Task Decomposition**
   - Keep tasks atomic and independently executable
   - Size tasks appropriately (10-60 minutes)
   - Clear descriptions with acceptance criteria

2. **Dependencies**
   - Only add when truly required
   - Prefer parallel execution
   - Document dependency reasons

3. **Priorities**
   - Use P0 for critical issues only
   - P1 for user-facing features
   - P2/P3 for nice-to-haves

4. **Resource Management**
   - Distribute tasks across roles
   - Maximize parallelism
   - Monitor agent utilization

5. **Monitoring**
   - Use dashboard for real-time view
   - Check for blocked tasks
   - Monitor agent health

6. **Error Handling**
   - Trust auto-recovery for transient failures
   - Manual intervention for persistent issues
   - Document failure patterns

7. **Documentation**
   - Keep workflow descriptions clear
   - Document task dependencies
   - Maintain workflow templates for common patterns

## Further Reading

- [README-ORCHESTRATION.md](README-ORCHESTRATION.md) - Main orchestration guide
- [AGENT-ROLES.md](AGENT-ROLES.md) - Understanding agent roles
- [PROJECT-CONTEXT.md](PROJECT-CONTEXT.md) - Setting up project context
- [API-REFERENCE.md](API-REFERENCE.md) - Complete API documentation
