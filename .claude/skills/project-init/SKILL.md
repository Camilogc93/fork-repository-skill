# Project Initialization Skill

## Metadata
- **Name**: Project Initialization
- **Description**: Set up new or existing projects for multi-agent orchestration with automatic tech stack detection, templates, and guided configuration
- **Version**: 1.0.0
- **Author**: Claude Code
- **Triggers**:
  - "init project"
  - "init project:"
  - "setup project"
  - "configure orchestration"
  - "add project to orchestration"
  - "project setup"

## Configuration

```yaml
detection:
  scan_depth: 3          # Directory depth for auto-detection
  file_patterns:
    - "package.json"
    - "pyproject.toml"
    - "requirements.txt"
    - "Cargo.toml"
    - "go.mod"
    - "Dockerfile"
    - "docker-compose.yml"
    - ".github/workflows/*.yml"

templates:
  directory: ".claude/agents/templates/projects/"
  available:
    - fullstack-web
    - api-service
    - frontend-spa
    - cli-tool
    - library

output:
  project_manifest: ".claude/project.yaml"
  context_directory: ".claude/agents/project-context/"
  runtime_directory: ".agent-comm/"
```

## Overview

This skill helps you set up any project for multi-agent orchestration. It can:
- **Auto-detect** your tech stack from existing files
- **Use templates** for common project types
- **Guide you** through interactive configuration
- **Import** settings from existing config files
- **Validate** your setup is ready for orchestration

## Workflow

### When user triggers project initialization:

1. **Determine Initialization Mode**

   ```
   User input analysis:
   - "init project" → Auto-detect mode
   - "init project: fullstack-web" → Template mode
   - "init project --wizard" → Wizard mode
   - "init project --validate" → Validation only
   - "init project --update" → Update existing config
   ```

2. **Execute Initialization**

   **Auto-Detect Mode:**
   ```python
   # Scan project for configuration files
   detected = scan_project_files(project_path)

   # Identify tech stack
   stack = identify_tech_stack(detected)
   # - Frontend: framework, language, build tool
   # - Backend: framework, language, database
   # - Infrastructure: containers, CI/CD, cloud

   # Present findings to user
   present_detection_results(stack)

   # Confirm or adjust
   confirmed_stack = get_user_confirmation(stack)
   ```

   **Template Mode:**
   ```python
   # Load template definition
   template = load_template(template_name)

   # Prompt for template variables
   variables = prompt_template_variables(template)

   # Generate configuration
   config = generate_from_template(template, variables)
   ```

   **Wizard Mode:**
   ```python
   # Step through configuration sections
   config = {}

   config['tech_stack'] = wizard_step_tech_stack()
   config['architecture'] = wizard_step_architecture()
   config['conventions'] = wizard_step_conventions()
   config['setup'] = wizard_step_setup()
   config['apis'] = wizard_step_apis()
   ```

3. **Generate Configuration Files**

   ```python
   # Create project manifest
   write_project_manifest(config)
   # Output: .claude/project.yaml

   # Generate project context files
   generate_context_file('00-tech-stack.md', config['tech_stack'])
   generate_context_file('01-architecture.md', config['architecture'])
   generate_context_file('02-conventions.md', config['conventions'])
   generate_context_file('03-setup.md', config['setup'])
   generate_context_file('04-apis.md', config['apis'])

   # Set up runtime directories
   setup_runtime_directories()
   # Creates: .agent-comm/orchestration/, messaging/, checkpoints/, etc.
   ```

4. **Validate Setup**

   ```python
   validation_results = validate_orchestration_setup()

   # Checks:
   # - All required files exist
   # - Configuration is complete
   # - No conflicting settings
   # - Runtime directories ready
   # - Agent roles accessible
   ```

5. **Report Results**

   ```
   ✓ Project initialized for orchestration

   Files created:
   - .claude/project.yaml
   - .claude/agents/project-context/00-tech-stack.md
   - .claude/agents/project-context/01-architecture.md
   - .claude/agents/project-context/02-conventions.md
   - .claude/agents/project-context/03-setup.md
   - .claude/agents/project-context/04-apis.md

   Ready to orchestrate!
   ```

## Usage Examples

### Example 1: Auto-Detect Existing Project

```
User: "init project"

Claude:
Scanning your project...

📦 Detected Configuration:
┌────────────────────────────────────────────┐
│ Frontend                                   │
│   Framework: React 18.2                    │
│   Language: TypeScript 5.0                 │
│   Build Tool: Vite 5.0                     │
│   Package Manager: npm                     │
├────────────────────────────────────────────┤
│ Backend                                    │
│   Framework: FastAPI 0.104                 │
│   Language: Python 3.11                    │
│   Database: PostgreSQL (from docker-compose)│
│   ORM: SQLAlchemy 2.0                      │
├────────────────────────────────────────────┤
│ Infrastructure                             │
│   Containers: Docker + Docker Compose      │
│   CI/CD: GitHub Actions                    │
└────────────────────────────────────────────┘

Is this correct? [Y]es / [N]o / [E]dit
> Y

✓ Project manifest created
✓ Tech stack documented
✓ Architecture analyzed
✓ Conventions extracted
✓ Setup instructions generated
✓ API patterns documented
✓ Runtime directories ready

🎉 Your project is ready for multi-agent orchestration!

Next: "orchestrate feature: <describe your feature>"
```

### Example 2: Use Template for New Project

```
User: "init project: api-service"

Claude:
📋 Template: API Service

Let's configure your API service:

1️⃣ Backend Framework:
   [1] FastAPI (Python) - Recommended
   [2] Express (Node.js)
   [3] Django REST (Python)
   [4] Gin (Go)
> 1

2️⃣ Database:
   [1] PostgreSQL - Recommended
   [2] MySQL
   [3] MongoDB
   [4] SQLite (development only)
> 1

3️⃣ Authentication:
   [1] JWT tokens - Recommended
   [2] OAuth2 / OpenID Connect
   [3] API Keys
   [4] None (add later)
> 1

4️⃣ API Style:
   [1] REST - Recommended
   [2] GraphQL
   [3] gRPC
> 1

Generating configuration...

✓ Created .claude/project.yaml
✓ Generated 5 project context files
✓ Configured for FastAPI + PostgreSQL + JWT
✓ Runtime directories ready

🎉 API service configured!

Suggested first feature:
"orchestrate feature: add health check endpoint"
```

### Example 3: Interactive Wizard

```
User: "init project --wizard"

Claude:
🧙 Project Setup Wizard

Step 1/5: Tech Stack
━━━━━━━━━━━━━━━━━━━━
What technologies does your project use?

Frontend Framework: React
Frontend Language: TypeScript
Backend Framework: Express
Backend Language: TypeScript
Database: MongoDB

[Continue]

Step 2/5: Architecture
━━━━━━━━━━━━━━━━━━━━━━
How is your project structured?

Repository Style: [Monorepo] / Polyrepo
Architecture: Monolith / [Microservices]
Directory Structure:
  /apps
    /web (frontend)
    /api (backend)
  /packages
    /shared (common code)

[Continue]

... (continues through all steps)

Step 5/5: Review
━━━━━━━━━━━━━━━━
Please review your configuration:

[Shows complete configuration summary]

[Generate] / [Edit] / [Cancel]
> Generate

✓ Configuration complete!
```

### Example 4: Validate Existing Setup

```
User: "init project --validate"

Claude:
🔍 Validating Orchestration Setup...

Configuration Files:
  ✓ .claude/project.yaml exists
  ✓ 00-tech-stack.md (complete)
  ✓ 01-architecture.md (complete)
  ⚠ 02-conventions.md (minimal - consider adding more detail)
  ✓ 03-setup.md (complete)
  ⚠ 04-apis.md (incomplete - missing endpoint documentation)

Agent Roles:
  ✓ frontend.md configured
  ✓ backend.md configured
  ✓ devops.md configured
  ✓ qa.md configured
  ✓ architect.md configured

Runtime Infrastructure:
  ✓ .agent-comm/orchestration/ ready
  ✓ .agent-comm/messaging/ ready
  ✓ .agent-comm/checkpoints/ ready

Overall Status: READY (with suggestions)

Suggestions:
1. Add coding style guidelines to 02-conventions.md
2. Document API endpoints in 04-apis.md for better agent context
```

## Available Templates

| Template | Description | Best For |
|----------|-------------|----------|
| `fullstack-web` | Frontend SPA + Backend API | Web applications |
| `api-service` | REST/GraphQL API | Backend services |
| `frontend-spa` | Single Page Application | Client-side apps |
| `cli-tool` | Command Line Tool | Developer tools |
| `library` | Shared Package/Library | Reusable code |

## Commands

| Command | Description |
|---------|-------------|
| `init project` | Auto-detect and initialize |
| `init project: <template>` | Use specific template |
| `init project --wizard` | Interactive step-by-step |
| `init project --validate` | Check existing setup |
| `init project --update` | Update configuration |
| `init project --list-templates` | Show available templates |

## Generated Files

### Project Manifest (`.claude/project.yaml`)

Central configuration file containing:
- Project metadata (name, type, version)
- Tech stack summary
- Directory mappings
- Agent configuration
- Orchestration settings

### Project Context Files

| File | Purpose |
|------|---------|
| `00-tech-stack.md` | Technologies, frameworks, versions |
| `01-architecture.md` | System structure, patterns |
| `02-conventions.md` | Coding standards, naming |
| `03-setup.md` | Development environment |
| `04-apis.md` | API documentation |

### Runtime Directories

```
.agent-comm/
├── orchestration/tasks/     # Task queue
├── messaging/               # Agent communication
├── checkpoints/             # State snapshots
├── shared-knowledge/        # Shared artifacts
└── logs/                    # Audit logs
```

## Tech Stack Detection

The skill automatically detects:

| File | Detects |
|------|---------|
| `package.json` | Node.js, npm packages, scripts |
| `pyproject.toml` | Python version, dependencies |
| `requirements.txt` | Python packages |
| `Cargo.toml` | Rust project |
| `go.mod` | Go modules |
| `Dockerfile` | Container configuration |
| `docker-compose.yml` | Service architecture |
| `.github/workflows/` | CI/CD setup |
| `tsconfig.json` | TypeScript configuration |
| `.eslintrc.*` | Linting rules |
| `.prettierrc` | Formatting rules |

## Integration with Orchestration

Once initialized, your project works with the orchestration skill:

1. **Orchestration reads project.yaml** for configuration
2. **Agents receive project context** when spawned
3. **Tasks are scoped** to your project structure
4. **Conventions are enforced** based on your settings

## Best Practices

1. **Run auto-detect first** - Even if you plan to customize, start with detection
2. **Review generated files** - Ensure accuracy before orchestrating
3. **Keep context updated** - Update files when your project evolves
4. **Use validation** - Run `--validate` periodically to check setup
5. **Customize agent roles** - Modify roles to match your specific needs

## Troubleshooting

### Detection missed something
- Check if config files exist in expected locations
- Use wizard mode for manual configuration
- Edit generated files directly

### Template doesn't fit
- Start with closest template, then customize
- Use wizard for full control
- Combine multiple stack configurations

### Validation fails
- Read error messages for specific issues
- Check file permissions
- Ensure runtime directories are writable

## See Also

- **agent-orchestration skill**: Main orchestration functionality
- **Project context templates**: `.claude/agents/project-context/`
- **Agent role definitions**: `.claude/agents/roles/`
- **Design document**: `docs/PROJECT-INIT-DESIGN.md`
