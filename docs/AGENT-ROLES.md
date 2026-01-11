# Agent Roles Guide

This guide describes the five built-in agent roles and how to customize or create new roles for the orchestration system.

## Table of Contents

- [Overview](#overview)
- [Built-in Roles](#built-in-roles)
- [Role Structure](#role-structure)
- [Creating Custom Roles](#creating-custom-roles)
- [Role Selection Strategy](#role-selection-strategy)
- [Best Practices](#best-practices)

## Overview

The orchestration system uses **role-based specialization** where each agent has specific expertise, tools, and communication patterns. This mirrors how real development teams work with specialized roles (frontend developer, backend engineer, etc.).

### Why Roles Matter

1. **Focused Context**: Agents only receive relevant information for their expertise
2. **Efficient Collaboration**: Clear communication patterns between roles
3. **Task Assignment**: Orchestrator matches tasks to appropriate roles
4. **Quality**: Specialized agents produce better results in their domain

### Role Components

Each role definition includes:
- **Identity**: Role name and primary focus
- **Expertise**: Technical capabilities and knowledge areas
- **Tools**: Technologies and frameworks the agent works with
- **Communication Patterns**: What the agent reads from and publishes to other roles
- **Best Practices**: Domain-specific guidelines and standards

## Built-in Roles

### 1. Frontend Agent 🎨

**File**: `.claude/agents/roles/frontend.md`

**Primary Focus**: User interface, user experience, client-side functionality

**Expertise**:
- React, Vue, Svelte component development
- Responsive design and CSS frameworks (Tailwind, Bootstrap)
- State management (Redux, Zustand, Context API)
- Form validation and user input handling
- API integration and data fetching
- Browser compatibility and performance optimization
- Accessibility (WCAG standards)
- Component testing (Jest, React Testing Library)

**Tools and Technologies**:
- npm/yarn, webpack, vite
- TypeScript/JavaScript
- HTML/CSS/SCSS
- Testing libraries (Jest, Vitest, Playwright)
- Build tools and bundlers

**Communication Patterns**:

*Reads From*:
- **Backend**: API contracts, endpoint specifications, data schemas
- **Architect**: UI/UX designs, component architecture
- **DevOps**: Deployment URLs, environment variables

*Publishes To*:
- **Backend**: API requirements, data needs
- **QA**: Component documentation, test requirements
- **All**: UI changes, deployment readiness

**Typical Tasks**:
- Build React components for feature X
- Implement responsive layout for page Y
- Integrate with API endpoint Z
- Add form validation for input fields
- Fix styling issues in component W
- Optimize bundle size and performance

### 2. Backend Agent ⚙️

**File**: `.claude/agents/roles/backend.md`

**Primary Focus**: Server-side logic, APIs, databases, business logic

**Expertise**:
- RESTful and GraphQL API design
- Database design and optimization (SQL, NoSQL)
- Authentication and authorization (OAuth, JWT)
- Business logic implementation
- Data validation and sanitization
- Caching strategies (Redis, Memcached)
- Background jobs and queue processing
- API documentation (OpenAPI/Swagger)
- Security best practices (OWASP)

**Tools and Technologies**:
- Python (FastAPI, Django, Flask)
- Node.js (Express, NestJS)
- Go, Rust, Java
- PostgreSQL, MySQL, MongoDB
- Redis, RabbitMQ
- API testing tools (Postman, pytest, supertest)

**Communication Patterns**:

*Reads From*:
- **Frontend**: API requirements, data needs
- **Architect**: System design, database schemas
- **DevOps**: Infrastructure capabilities, deployment constraints

*Publishes To*:
- **Frontend**: API contracts, endpoint documentation
- **QA**: API test scenarios, integration points
- **DevOps**: Service requirements, dependencies
- **All**: API changes, deployment needs

**Typical Tasks**:
- Implement REST API for feature X
- Design database schema for entity Y
- Add authentication middleware
- Optimize database query performance
- Create background job for task Z
- Write API integration tests

### 3. DevOps Agent 🚀

**File**: `.claude/agents/roles/devops.md`

**Primary Focus**: Infrastructure, deployment, CI/CD, monitoring

**Expertise**:
- Docker containerization
- Kubernetes orchestration
- CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
- Cloud platforms (AWS, GCP, Azure)
- Infrastructure as Code (Terraform, CloudFormation)
- Monitoring and logging (Prometheus, Grafana, ELK)
- Security and secrets management
- Load balancing and scaling
- Database backup and recovery
- Performance tuning

**Tools and Technologies**:
- Docker, docker-compose
- Kubernetes, Helm
- Terraform, Ansible
- GitHub Actions, GitLab CI
- AWS/GCP/Azure CLI
- Nginx, HAProxy
- Monitoring tools (Datadog, New Relic)

**Communication Patterns**:

*Reads From*:
- **Backend**: Service requirements, dependencies
- **Frontend**: Build requirements, environment needs
- **Architect**: Infrastructure architecture, scaling requirements

*Publishes To*:
- **All**: Deployment status, environment URLs
- **Backend**: Database connections, secrets
- **Frontend**: CDN URLs, environment variables
- **QA**: Test environments

**Typical Tasks**:
- Dockerize application services
- Set up CI/CD pipeline
- Configure Kubernetes deployment
- Set up monitoring and alerting
- Manage SSL certificates
- Configure load balancer
- Set up staging environment

### 4. QA Agent ✅

**File**: `.claude/agents/roles/qa.md`

**Primary Focus**: Testing, quality assurance, bug detection

**Expertise**:
- Unit testing strategies
- Integration testing
- End-to-end testing
- API testing
- Performance testing
- Security testing
- Test automation
- Test coverage analysis
- Bug reporting and tracking
- Test data management

**Tools and Technologies**:
- Jest, Vitest, pytest, JUnit
- React Testing Library, Enzyme
- Playwright, Cypress, Selenium
- Postman, REST Client
- JMeter, k6 (load testing)
- Coverage tools (Istanbul, coverage.py)

**Communication Patterns**:

*Reads From*:
- **All**: Implementation details, test requirements
- **Frontend**: Component specs, user flows
- **Backend**: API contracts, business logic
- **Architect**: Quality standards, acceptance criteria

*Publishes To*:
- **All**: Test results, bug reports
- **Frontend**: UI/UX issues, accessibility problems
- **Backend**: API bugs, performance issues
- **DevOps**: Environment issues

**Typical Tasks**:
- Write unit tests for module X
- Create integration tests for feature Y
- Implement e2e test for user flow Z
- Verify API endpoint behavior
- Test error handling scenarios
- Measure and improve test coverage
- Report and document bugs

### 5. Architect Agent 📐

**File**: `.claude/agents/roles/architect.md`

**Primary Focus**: System design, documentation, technical decisions

**Expertise**:
- System architecture design
- Design patterns and principles
- Documentation (Architecture Decision Records)
- Code review and quality standards
- Technology selection
- Performance architecture
- Security architecture
- Scalability planning
- API contract design
- Database schema design

**Tools and Technologies**:
- Diagramming tools (Mermaid, PlantUML)
- Documentation platforms (Markdown, Docusaurus)
- Code review tools
- Architecture modeling tools

**Communication Patterns**:

*Reads From*:
- **All**: Requirements, constraints, technical questions

*Publishes To*:
- **All**: Architecture docs, design decisions, standards
- **Backend**: Database schemas, API contracts
- **Frontend**: Component architecture, state management
- **DevOps**: Infrastructure design
- **QA**: Quality standards, acceptance criteria

**Typical Tasks**:
- Design system architecture for feature X
- Create database schema design
- Write Architecture Decision Record (ADR)
- Define API contracts
- Establish coding standards
- Review code architecture
- Document system design

## Role Structure

Each role definition file follows this structure:

```markdown
# {Role Name}

## Identity
- **Role**: Brief role name
- **Focus**: Primary area of expertise
- **Symbol**: Emoji identifier (🎨, ⚙️, 🚀, ✅, 📐)

## Expertise

### Core Capabilities
- Capability 1
- Capability 2

### Technical Skills
- Skill 1
- Skill 2

### Specialized Knowledge
- Knowledge area 1
- Knowledge area 2

## Tools and Technologies

### Primary Tools
- Tool 1
- Tool 2

### Frameworks and Libraries
- Framework 1
- Framework 2

### Testing and Quality
- Testing tool 1
- Testing tool 2

## Communication Patterns

### Reads From
Information this role needs from other roles:
- **Role Name**: What information (e.g., "Backend: API contracts")

### Publishes To
Information this role provides to other roles:
- **Role Name**: What information (e.g., "Frontend: API documentation")

## Best Practices

### Code Quality
- Practice 1
- Practice 2

### Collaboration
- Practice 1
- Practice 2

### Documentation
- Practice 1
- Practice 2

## Common Tasks

Examples of tasks this role typically handles:
1. Task type 1
2. Task type 2
3. Task type 3

## Workflows

### Typical Workflow
1. Step 1
2. Step 2
3. Step 3

### Collaboration Points
- When to reach out to other roles
- What to share and when

## Context Requirements

What context this agent needs to be effective:
- Project-specific requirement 1
- Project-specific requirement 2
```

## Creating Custom Roles

You can create custom roles for specialized needs (e.g., data scientist, mobile developer, security engineer).

### Step 1: Create Role File

Create a new file in `.claude/agents/roles/`:

```bash
touch .claude/agents/roles/mobile.md
```

### Step 2: Define Role Structure

```markdown
# Mobile Agent

## Identity
- **Role**: Mobile Development
- **Focus**: iOS and Android application development
- **Symbol**: 📱

## Expertise

### Core Capabilities
- Native iOS development (Swift, SwiftUI)
- Native Android development (Kotlin, Jetpack Compose)
- Cross-platform development (React Native, Flutter)
- Mobile UI/UX patterns
- Mobile performance optimization
- App store deployment

### Technical Skills
- Swift, Kotlin, Dart
- React Native, Flutter
- Mobile state management
- Native modules and bridges
- Push notifications
- Local storage (Core Data, Room)

### Specialized Knowledge
- Mobile app lifecycle
- Platform-specific guidelines (HIG, Material Design)
- Mobile security best practices
- App store guidelines and submission

## Tools and Technologies

### Primary Tools
- Xcode, Android Studio
- React Native CLI, Flutter CLI
- CocoaPods, Gradle

### Frameworks and Libraries
- SwiftUI, UIKit
- Jetpack Compose, Android Views
- React Native, Flutter
- Redux, MobX, Provider

### Testing and Quality
- XCTest, XCUITest
- Espresso, JUnit
- Detox (React Native)
- Firebase Test Lab

## Communication Patterns

### Reads From
- **Backend**: Mobile API endpoints, authentication
- **Architect**: App architecture, navigation patterns
- **DevOps**: App signing, CI/CD for mobile

### Publishes To
- **Backend**: Mobile-specific API requirements
- **QA**: App build artifacts, test requirements
- **DevOps**: App bundle/APK, deployment needs

## Best Practices

### Code Quality
- Follow platform-specific style guides
- Use dependency injection
- Implement proper error handling
- Optimize for battery and performance

### Collaboration
- Share platform capabilities with backend
- Coordinate with DevOps for app signing
- Work with QA for device testing

### Documentation
- Document platform-specific implementations
- Maintain changelog for app versions
- Document API usage patterns

## Common Tasks

1. Build mobile screen for feature X
2. Implement native module for capability Y
3. Optimize app performance and bundle size
4. Integrate with device capabilities (camera, location)
5. Handle push notifications
6. Implement offline support
```

### Step 3: Register Role in Orchestrator

Update `orchestrator.py` to recognize the new role:

```python
# In capabilities_map (if needed)
capabilities_map = {
    'frontend': ['react', 'ui', 'components', 'styling'],
    'backend': ['api', 'database', 'business-logic'],
    'devops': ['docker', 'ci-cd', 'infrastructure'],
    'qa': ['testing', 'quality-assurance', 'automation'],
    'architect': ['design', 'documentation', 'architecture'],
    'mobile': ['ios', 'android', 'react-native', 'flutter']  # Add this
}
```

### Step 4: Update Agent Worker

If needed, update `agent_worker.py` to handle role-specific logic:

```python
def _get_capabilities(self) -> list:
    """Get agent capabilities based on role."""
    capabilities_map = {
        'frontend': ['react', 'ui', 'components', 'styling'],
        'backend': ['api', 'database', 'business-logic'],
        'devops': ['docker', 'ci-cd', 'infrastructure'],
        'qa': ['testing', 'quality-assurance', 'automation'],
        'architect': ['design', 'documentation', 'architecture'],
        'mobile': ['ios', 'android', 'react-native', 'flutter']  # Add this
    }
    return capabilities_map.get(self.role, [])
```

### Step 5: Use Custom Role

```python
from orchestrator_main import MainOrchestrator

orchestrator = MainOrchestrator()

tasks = [
    {
        "description": "Build mobile app login screen",
        "role": "mobile",  # Use custom role
        "priority": "P1"
    }
]

workflow_id = orchestrator.create_workflow(
    name="Mobile Login",
    description="Implement mobile login screen",
    tasks_breakdown=tasks
)

orchestrator.start_workflow(workflow_id)
```

## Role Selection Strategy

When creating tasks, the orchestrator assigns them to agents based on role matching:

### Automatic Role Assignment

```python
# Task specifies role
task = {
    "description": "Build login UI",
    "role": "frontend"  # Will be assigned to frontend agent
}
```

### Role Priority

If multiple agents have the same role:
1. Available (idle) agents first
2. Agents with matching capabilities
3. Agents with least workload
4. Round-robin if all else equal

### Multi-Role Tasks

Some tasks may benefit from multiple roles:

```python
# Backend task that requires DevOps input
{
    "description": "Set up database with replication",
    "role": "backend",
    "requires_consultation": ["devops"]  # Backend agent may message DevOps
}
```

The backend agent can then send a message to DevOps agents:

```python
# In agent execution
message_bus.send_message(
    from_agent="backend-001",
    to_agent="devops-001",
    message_type=MessageType.REQUEST_INFO,
    payload={"question": "What's the replication setup for production DB?"}
)
```

## Best Practices

### 1. Clear Role Boundaries

Define clear boundaries between roles:
- **Frontend**: Owns UI/UX, not API logic
- **Backend**: Owns API/business logic, not UI
- **DevOps**: Owns infrastructure, not application code
- **QA**: Owns testing, not implementation
- **Architect**: Owns design decisions, not implementation

### 2. Communication Over Duplication

Agents should communicate rather than duplicate work:
```python
# Good: Frontend asks Backend for API contract
message_bus.send_message(
    from_agent="frontend-001",
    to_agent="backend-001",
    message_type=MessageType.REQUEST_INFO,
    payload={"question": "What's the login API contract?"}
)

# Bad: Frontend implements its own API logic
```

### 3. Shared Knowledge

Use shared knowledge directory for common artifacts:
```bash
.agent-comm/shared-knowledge/
├── api-contracts/
│   └── auth-api.json
├── design-decisions/
│   └── adr-001-database-choice.md
└── schemas/
    └── user-schema.json
```

Agents publish to and read from shared knowledge.

### 4. Role-Specific Context

Each agent should receive only relevant context:
- **Frontend**: UI patterns, component library docs
- **Backend**: Database schemas, API patterns
- **DevOps**: Infrastructure docs, deployment procedures
- **QA**: Test strategies, quality standards
- **Architect**: Design principles, ADR templates

### 5. Progressive Disclosure

Start with minimal role set, add custom roles as needed:
1. Start with 5 built-in roles
2. Identify gaps in coverage
3. Create custom role if needed frequently
4. Avoid over-specialization (too many narrow roles)

### 6. Role Documentation

Keep role definitions updated:
- Add new capabilities as they're used
- Update communication patterns based on actual usage
- Document common task patterns
- Include examples from real workflows

### 7. Testing Role Assignments

Verify tasks are assigned to correct roles:

```python
# Test role assignment
def test_task_assignment():
    task_mgr = TaskManager()

    # Create task for frontend
    task = task_mgr.create_task(
        "task-001",
        "Build login UI",
        role="frontend"
    )

    # Verify role
    assert task.role == "frontend"

    # Assign to frontend agent
    task_mgr.assign_task("task-001", "frontend-001")

    # Verify assignment
    assigned = task_mgr.get_task("task-001")
    assert assigned.assigned_to == "frontend-001"
```

## Further Reading

- [README-ORCHESTRATION.md](README-ORCHESTRATION.md) - Main orchestration guide
- [PROJECT-CONTEXT.md](PROJECT-CONTEXT.md) - Setting up project context
- [WORKFLOW-GUIDE.md](WORKFLOW-GUIDE.md) - Advanced workflow patterns
- [API-REFERENCE.md](API-REFERENCE.md) - Complete API documentation
