# Project Initialization Guide

Quick reference for setting up projects with the multi-agent orchestration system.

## Quick Start

```bash
# Auto-detect and configure your project
init project

# Use a template
init project: fullstack-web

# Validate existing setup
init project --validate
```

## Initialization Modes

### 1. Auto-Detect Mode

Best for: Existing projects with configuration files

```
init project
```

The system scans for:
- `package.json` - Node.js/frontend frameworks
- `pyproject.toml` / `requirements.txt` - Python projects
- `go.mod` - Go projects
- `Cargo.toml` - Rust projects
- `Dockerfile` / `docker-compose.yml` - Container setup
- `.github/workflows/` - CI/CD configuration

### 2. Template Mode

Best for: New projects or standardized setups

```
init project: <template-name>
```

Available templates:

| Template | Stack | Description |
|----------|-------|-------------|
| `fullstack-web` | React/Vue + FastAPI/Express | Full-stack web application |
| `api-service` | FastAPI/Express/Go | Backend API service |

### 3. Validation Mode

Best for: Checking existing configuration

```
init project --validate
```

Validates:
- Project manifest exists
- Context files are complete
- Agent roles are configured
- Runtime directories are ready

## What Gets Generated

### Project Manifest (`.claude/project.yaml`)

Central configuration file:

```yaml
version: "1.0"
name: "my-project"
type: "fullstack-web"

stack:
  frontend:
    framework: "React"
    language: "TypeScript"
  backend:
    framework: "FastAPI"
    language: "Python"
  database:
    type: "PostgreSQL"

agents:
  enabled_roles:
    - frontend
    - backend
    - qa
    - devops
```

### Project Context Files

| File | Purpose |
|------|---------|
| `00-tech-stack.md` | Technologies, frameworks, versions |
| `01-architecture.md` | System structure and patterns |
| `02-conventions.md` | Coding standards |
| `03-setup.md` | Development environment |
| `04-apis.md` | API documentation |

### Runtime Directories

```
.agent-comm/
├── orchestration/tasks/    # Task queue
├── messaging/              # Agent communication
├── checkpoints/            # State snapshots
├── shared-knowledge/       # Shared artifacts
└── logs/                   # Execution logs
```

## After Initialization

### 1. Review Generated Files

```bash
# Check the project manifest
cat .claude/project.yaml

# Review context files
ls .claude/agents/project-context/
```

### 2. Customize If Needed

Edit context files to add project-specific details:
- Add your actual API endpoints to `04-apis.md`
- Document specific conventions in `02-conventions.md`
- Update setup instructions in `03-setup.md`

### 3. Start Orchestrating

```bash
# Start Claude Code
claude

# Begin orchestration
orchestrate feature: add user authentication
```

## Troubleshooting

### Low Confidence Detection

If auto-detection reports low confidence:
1. Use a template instead: `init project: api-service`
2. Or manually edit the generated files

### Validation Errors

Run validation to see specific issues:

```
init project --validate
```

Common fixes:
- Missing context files: Re-run `init project`
- Incomplete content: Edit the flagged files
- Missing runtime dirs: Re-run initialization

### Re-Initialization

To regenerate configuration:

```bash
# Backup existing files if needed
cp -r .claude/agents/project-context .claude/agents/project-context.bak

# Re-run initialization
init project
```

## CLI Usage

For command-line usage outside Claude Code:

```bash
cd .claude/skills/project-init/tools

# Detect tech stack
python main.py detect /path/to/project

# Initialize project
python main.py init /path/to/project

# Use template
python main.py init --template api-service /path/to/project

# Validate setup
python main.py validate /path/to/project

# List templates
python main.py list-templates
```

## See Also

- [PROJECT-INIT-DESIGN.md](PROJECT-INIT-DESIGN.md) - Full design documentation
- [README-ORCHESTRATION.md](README-ORCHESTRATION.md) - Orchestration guide
- [AGENT-ROLES.md](AGENT-ROLES.md) - Agent role customization
