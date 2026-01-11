# Project Initialization Feature Design

## Problem Statement

Users want to easily set up new projects to work with the existing multi-agent orchestration methodology. Currently, this requires:
- Manually copying template files
- Editing multiple project context files
- Setting up runtime directory structure
- Understanding the complex configuration hierarchy

## Solution Overview

Create a **project initialization skill** that:
1. Detects or prompts for project characteristics
2. Auto-generates customized project context files
3. Sets up runtime infrastructure
4. Validates readiness for orchestration

---

## Feature Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Project Initialization Skill                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Detector   │───▶│   Wizard     │───▶│  Generator   │      │
│  │  (analyze    │    │ (interactive │    │ (create      │      │
│  │   codebase)  │    │  prompts)    │    │  configs)    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                    │               │
│         ▼                   ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Project Configuration                     │      │
│  │  - Tech stack detection/specification                 │      │
│  │  - Architecture patterns                              │      │
│  │  - Coding conventions                                 │      │
│  │  - Development setup                                  │      │
│  │  - API patterns                                       │      │
│  └──────────────────────────────────────────────────────┘      │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              File Generator                           │      │
│  │  - .claude/agents/project-context/*.md               │      │
│  │  - .agent-comm/ runtime structure                    │      │
│  │  - Custom role modifications (optional)              │      │
│  └──────────────────────────────────────────────────────┘      │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Validator                                │      │
│  │  - Verify all required files exist                   │      │
│  │  - Check configuration completeness                  │      │
│  │  - Test orchestration readiness                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow Design

### 1. Trigger Commands

```yaml
triggers:
  - "init project"
  - "setup project for orchestration"
  - "configure orchestration for"
  - "add project:"
  - "orchestration setup"
```

### 2. Initialization Modes

#### Mode A: Auto-Detect (Smart Setup)
```
User: "init project"

Claude:
1. Scans codebase for:
   - package.json → Node.js project details
   - requirements.txt/pyproject.toml → Python project details
   - Dockerfile → Container configuration
   - .github/workflows → CI/CD patterns
   - src/ structure → Architecture patterns

2. Presents detected configuration:
   "I detected a React + FastAPI project with:
   - Frontend: React 18, TypeScript, Vite
   - Backend: Python 3.11, FastAPI, SQLAlchemy
   - Database: PostgreSQL
   - Deployment: Docker + GitHub Actions

   Is this correct? [Y/n]"

3. Generates project context files
4. Sets up runtime infrastructure
5. Reports readiness
```

#### Mode B: Template-Based (Quick Setup)
```
User: "init project: fullstack-web"

Claude:
1. Uses predefined template for fullstack-web
2. Prompts for customization:
   "Template: Full Stack Web Application

   Quick configuration:
   - Frontend framework? [React/Vue/Svelte/Angular]
   - Backend framework? [FastAPI/Express/Django/Rails]
   - Database? [PostgreSQL/MySQL/MongoDB]
   - Cloud provider? [AWS/GCP/Azure/None]"

3. Generates customized configuration
```

#### Mode C: Interactive Wizard (Guided Setup)
```
User: "setup project for orchestration"

Claude:
1. Step-by-step wizard:

   Step 1/5: Tech Stack
   "What technologies does your project use?
   - Frontend: ___
   - Backend: ___
   - Database: ___"

   Step 2/5: Architecture
   "How is your project structured?
   - Monorepo / Polyrepo
   - Microservices / Monolith
   - Directory structure..."

   Step 3/5: Conventions
   "What coding standards do you follow?..."

   Step 4/5: Development Setup
   "How do developers set up locally?..."

   Step 5/5: APIs
   "What API patterns do you use?..."

2. Generates configuration from answers
```

#### Mode D: Import Existing (Migration)
```
User: "init project from existing config"

Claude:
1. Looks for existing configuration:
   - .editorconfig
   - tsconfig.json / pyproject.toml
   - docker-compose.yml
   - Existing docs/

2. Extracts information automatically
3. Fills project context from existing sources
```

---

## Project Templates

### Template Structure

```
.claude/agents/templates/
├── projects/
│   ├── fullstack-web.yaml       # React/Vue + API backend
│   ├── api-service.yaml         # Pure API/microservice
│   ├── frontend-spa.yaml        # Single page application
│   ├── cli-tool.yaml            # Command line tool
│   ├── library.yaml             # Shared library/package
│   ├── data-pipeline.yaml       # ETL/data processing
│   └── mobile-app.yaml          # React Native/Flutter
│
├── stacks/
│   ├── react-typescript.yaml    # React + TS specifics
│   ├── vue-nuxt.yaml            # Vue/Nuxt specifics
│   ├── python-fastapi.yaml      # FastAPI specifics
│   ├── node-express.yaml        # Express specifics
│   ├── go-gin.yaml              # Go/Gin specifics
│   └── rust-axum.yaml           # Rust/Axum specifics
│
└── cloud/
    ├── aws.yaml                 # AWS-specific patterns
    ├── gcp.yaml                 # GCP-specific patterns
    ├── azure.yaml               # Azure-specific patterns
    └── docker-local.yaml        # Local Docker setup
```

### Template Definition Format

```yaml
# fullstack-web.yaml
name: Full Stack Web Application
description: Modern web app with frontend SPA and backend API

variables:
  frontend_framework:
    prompt: "Frontend framework"
    options: [React, Vue, Svelte, Angular]
    default: React

  backend_framework:
    prompt: "Backend framework"
    options: [FastAPI, Express, Django, Rails, Go]
    default: FastAPI

  database:
    prompt: "Primary database"
    options: [PostgreSQL, MySQL, MongoDB, SQLite]
    default: PostgreSQL

structure:
  directories:
    - "frontend/src/components"
    - "frontend/src/pages"
    - "frontend/src/hooks"
    - "backend/src/api"
    - "backend/src/services"
    - "backend/src/models"
    - "shared/types"

agent_roles:
  required: [frontend, backend, qa]
  optional: [devops, architect]

  customizations:
    frontend:
      tools_add: ["npm", "vite"]
    backend:
      tools_add: ["pytest", "alembic"]

context_templates:
  tech-stack: |
    ## Frontend
    - **Framework**: {{ frontend_framework }}
    - **Language**: TypeScript
    ...

  architecture: |
    ## Project Structure
    ```
    {{ project_name }}/
    ├── frontend/     # {{ frontend_framework }} SPA
    ├── backend/      # {{ backend_framework }} API
    └── shared/       # Shared types and utilities
    ```
```

---

## Configuration Schema

### Project Manifest (`.claude/project.yaml`)

```yaml
# Project manifest for orchestration
version: "1.0"
name: "my-awesome-project"
type: "fullstack-web"

# Tech stack summary (auto-detected or specified)
stack:
  frontend:
    framework: "React"
    version: "18.2"
    language: "TypeScript"
    build: "Vite"

  backend:
    framework: "FastAPI"
    version: "0.104"
    language: "Python 3.11"
    orm: "SQLAlchemy"

  database:
    primary: "PostgreSQL 15"
    cache: "Redis 7"

  infrastructure:
    containerization: "Docker"
    orchestration: "Docker Compose"
    ci_cd: "GitHub Actions"
    cloud: "AWS"

# Directory mappings for agents
directories:
  frontend: "frontend/"
  backend: "backend/"
  shared: "shared/"
  docs: "docs/"
  tests: "tests/"

# Agent configuration
agents:
  enabled_roles:
    - frontend
    - backend
    - devops
    - qa

  role_customizations:
    frontend:
      focus_areas:
        - "React components with hooks"
        - "Tailwind CSS styling"
    backend:
      focus_areas:
        - "REST API with FastAPI"
        - "SQLAlchemy models"

# Orchestration settings
orchestration:
  max_concurrent_agents: 5
  auto_recovery: true
  checkpoint_interval: 30

# Custom commands for this project
commands:
  start_frontend: "cd frontend && npm run dev"
  start_backend: "cd backend && uvicorn main:app --reload"
  run_tests: "pytest && npm test"
  build: "docker-compose build"
```

---

## CLI/Skill Interface

### New Skill: `project-init`

```markdown
# Project Initialization Skill

## Metadata
- **Name**: Project Initialization
- **Description**: Set up a new project for multi-agent orchestration
- **Version**: 1.0.0
- **Triggers**:
  - "init project"
  - "init project:"
  - "setup orchestration"
  - "configure project"
  - "add project to orchestration"

## Workflow

### When user triggers initialization:

1. **Determine Mode**
   - If project path specified: analyze that project
   - If template specified: use that template
   - If neither: offer mode selection

2. **Gather Configuration**
   ```
   Mode: [Auto-detect / Template / Wizard / Import]

   Auto-detect:
   → Scan for package.json, requirements.txt, etc.
   → Identify frameworks and tools
   → Present findings for confirmation

   Template:
   → List available templates
   → Prompt for template variables

   Wizard:
   → Step through configuration sections
   → Build configuration incrementally

   Import:
   → Look for existing config files
   → Extract and migrate settings
   ```

3. **Generate Configuration**
   - Create/update `.claude/project.yaml`
   - Generate project context files (00-04)
   - Customize agent roles if needed
   - Set up `.agent-comm/` structure

4. **Validate Setup**
   - Check all required files exist
   - Verify directory structure
   - Test that orchestration can start

5. **Report Results**
   ```
   ✓ Project initialized for orchestration

   Created files:
   - .claude/project.yaml
   - .claude/agents/project-context/00-tech-stack.md
   - .claude/agents/project-context/01-architecture.md
   - .claude/agents/project-context/02-conventions.md
   - .claude/agents/project-context/03-setup.md
   - .claude/agents/project-context/04-apis.md

   Runtime directories:
   - .agent-comm/orchestration/
   - .agent-comm/messaging/
   - .agent-comm/checkpoints/

   Ready to orchestrate! Try:
   → "orchestrate feature: <your feature>"
   ```

## Commands

- `init project` - Auto-detect and initialize
- `init project: <template>` - Use specific template
- `init project --wizard` - Interactive wizard
- `init project --import` - Import from existing configs
- `init project --validate` - Validate existing setup
- `init project --update` - Update configuration
```

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create project manifest schema (`project.yaml`)
2. Implement tech stack detector
3. Create base template structure
4. Build configuration generator

### Phase 2: Templates
1. Create fullstack-web template
2. Create api-service template
3. Create frontend-spa template
4. Add stack-specific configurations

### Phase 3: Wizard & Detection
1. Implement interactive wizard flow
2. Build auto-detection logic
3. Add import from existing configs
4. Create validation system

### Phase 4: Integration
1. Create project-init skill
2. Integrate with agent-orchestration skill
3. Add project management commands
4. Documentation and examples

---

## File Changes Summary

### New Files to Create
```
.claude/
├── project.yaml                          # Project manifest (per-project)
├── agents/
│   └── templates/
│       ├── projects/
│       │   ├── fullstack-web.yaml
│       │   ├── api-service.yaml
│       │   └── frontend-spa.yaml
│       └── stacks/
│           ├── react-typescript.yaml
│           └── python-fastapi.yaml
└── skills/
    └── project-init/
        ├── SKILL.md                      # Main skill definition
        └── tools/
            ├── detector.py               # Tech stack detection
            ├── generator.py              # Config file generator
            ├── validator.py              # Setup validation
            └── templates.py              # Template processing
```

### Files to Modify
```
.claude/skills/agent-orchestration/SKILL.md
  → Add project validation step before orchestration
  → Reference project.yaml for configuration

.claude/agents/README.md
  → Add project initialization instructions
  → Reference new skill
```

---

## Usage Examples

### Example 1: Initialize Existing React + FastAPI Project
```
User: init project

Claude:
Analyzing your codebase...

Detected configuration:
┌─────────────────────────────────────────┐
│ Frontend                                │
│   Framework: React 18.2                 │
│   Language: TypeScript 5.0              │
│   Build: Vite 5.0                       │
│   Package Manager: npm                  │
├─────────────────────────────────────────┤
│ Backend                                 │
│   Framework: FastAPI 0.104              │
│   Language: Python 3.11                 │
│   ORM: SQLAlchemy 2.0                   │
│   Database: PostgreSQL                  │
├─────────────────────────────────────────┤
│ Infrastructure                          │
│   Containers: Docker + Docker Compose   │
│   CI/CD: GitHub Actions                 │
└─────────────────────────────────────────┘

Is this correct? [Y/n/edit]
> Y

Generating project configuration...
✓ Created .claude/project.yaml
✓ Generated project context files
✓ Set up runtime directories
✓ Validated orchestration readiness

Your project is ready for multi-agent orchestration!

Try: "orchestrate feature: add user authentication"
```

### Example 2: New Project from Template
```
User: init project: api-service

Claude:
Using template: API Service

Configure your API service:

1. Backend Framework
   [1] FastAPI (Recommended)
   [2] Express
   [3] Django REST
   [4] Go/Gin
   > 1

2. Database
   [1] PostgreSQL (Recommended)
   [2] MySQL
   [3] MongoDB
   [4] SQLite (dev only)
   > 1

3. Authentication
   [1] JWT (Recommended)
   [2] OAuth2
   [3] API Keys
   [4] None
   > 1

Generating configuration for FastAPI + PostgreSQL + JWT...
✓ Project configured!

Next steps:
1. Review .claude/agents/project-context/ files
2. Customize agent roles if needed
3. Start orchestrating: "orchestrate feature: ..."
```

### Example 3: Validate Existing Setup
```
User: init project --validate

Claude:
Validating orchestration setup...

✓ .claude/project.yaml exists
✓ Project context files complete (5/5)
✓ Agent roles configured (5/5)
✓ Runtime directories ready
✓ No configuration errors

Orchestration readiness: READY

Suggestions:
- Consider adding more detail to 02-conventions.md
- API documentation in 04-apis.md is minimal
```

---

## Success Criteria

1. **Ease of Use**: New project setup in < 2 minutes
2. **Flexibility**: Support auto-detect, templates, and manual
3. **Accuracy**: Correctly identify 90%+ of common tech stacks
4. **Completeness**: Generate all required configuration files
5. **Validation**: Catch configuration errors before orchestration
6. **Documentation**: Clear guidance throughout process
