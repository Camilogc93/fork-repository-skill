"""
Project Configuration Generator
Generates project configuration files from templates and detected/specified tech stacks.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from detector import DetectedStack


@dataclass
class ProjectConfig:
    """Project configuration for orchestration."""

    name: str
    type: str
    stack: dict
    directories: dict
    agents: dict
    orchestration: dict


class ProjectGenerator:
    """Generates project configuration files."""

    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.claude_dir = self.project_path / ".claude"
        self.agents_dir = self.claude_dir / "agents"
        self.context_dir = self.agents_dir / "project-context"
        self.agent_comm_dir = self.project_path / ".agent-comm"

    def generate_from_stack(
        self, stack: DetectedStack, project_name: str = None
    ) -> ProjectConfig:
        """Generate project configuration from detected stack."""
        if project_name is None:
            project_name = self.project_path.name

        # Determine project type
        project_type = self._determine_project_type(stack)

        config = ProjectConfig(
            name=project_name,
            type=project_type,
            stack=self._build_stack_config(stack),
            directories=self._build_directories_config(stack),
            agents=self._build_agents_config(stack),
            orchestration=self._build_orchestration_config(),
        )

        return config

    def generate_from_template(
        self, template_name: str, variables: dict
    ) -> ProjectConfig:
        """Generate project configuration from template."""
        template_path = (
            self.claude_dir
            / "agents"
            / "templates"
            / "projects"
            / f"{template_name}.yaml"
        )

        if not template_path.exists():
            raise ValueError(f"Template not found: {template_name}")

        with open(template_path) as f:
            template = yaml.safe_load(f)

        # Apply variables to template
        config = ProjectConfig(
            name=variables.get("project_name", self.project_path.name),
            type=template_name,
            stack=self._apply_template_variables(
                template.get("context_templates", {}), variables
            ),
            directories=self._extract_directories(template),
            agents=self._extract_agents(template, variables),
            orchestration=template.get("orchestration", {}),
        )

        return config

    def write_configuration(self, config: ProjectConfig) -> list[str]:
        """Write all configuration files."""
        created_files = []

        # Ensure directories exist
        self._ensure_directories()

        # Write project manifest
        manifest_path = self.claude_dir / "project.yaml"
        self._write_project_manifest(config, manifest_path)
        created_files.append(str(manifest_path))

        # Write context files
        context_files = self._write_context_files(config)
        created_files.extend(context_files)

        # Setup runtime directories
        runtime_dirs = self._setup_runtime_directories()
        created_files.extend(runtime_dirs)

        return created_files

    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.claude_dir,
            self.agents_dir,
            self.context_dir,
            self.agents_dir / "roles",
            self.agents_dir / "session-state",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _determine_project_type(self, stack: DetectedStack) -> str:
        """Determine project type from stack."""
        has_frontend = bool(stack.frontend.get("framework"))
        has_backend = bool(stack.backend.get("framework"))

        if has_frontend and has_backend:
            return "fullstack-web"
        elif has_backend:
            return "api-service"
        elif has_frontend:
            return "frontend-spa"
        else:
            return "unknown"

    def _build_stack_config(self, stack: DetectedStack) -> dict:
        """Build stack configuration dict."""
        return {
            "frontend": stack.frontend,
            "backend": stack.backend,
            "database": stack.database,
            "infrastructure": stack.infrastructure,
            "testing": stack.testing,
            "ci_cd": stack.ci_cd,
        }

    def _build_directories_config(self, stack: DetectedStack) -> dict:
        """Build directories configuration."""
        dirs = {}

        # Check for common directory patterns
        frontend_dirs = ["frontend", "client", "web", "app"]
        backend_dirs = ["backend", "server", "api", "src"]

        for d in frontend_dirs:
            if (self.project_path / d).exists():
                dirs["frontend"] = d
                break

        for d in backend_dirs:
            if (self.project_path / d).exists():
                dirs["backend"] = d
                break

        if (self.project_path / "shared").exists():
            dirs["shared"] = "shared"

        if (self.project_path / "tests").exists():
            dirs["tests"] = "tests"

        return dirs

    def _build_agents_config(self, stack: DetectedStack) -> dict:
        """Build agent configuration."""
        enabled_roles = []

        if stack.frontend.get("framework"):
            enabled_roles.append("frontend")

        if stack.backend.get("framework"):
            enabled_roles.append("backend")

        enabled_roles.append("qa")  # Always enable QA

        if stack.infrastructure.get("containerization"):
            enabled_roles.append("devops")

        return {
            "enabled_roles": enabled_roles,
            "max_concurrent": 5,
            "auto_recovery": True,
        }

    def _build_orchestration_config(self) -> dict:
        """Build orchestration configuration."""
        return {
            "max_concurrent_agents": 5,
            "checkpoint_interval": 30,
            "heartbeat_interval": 10,
            "auto_recovery": True,
        }

    def _write_project_manifest(self, config: ProjectConfig, path: Path) -> None:
        """Write project.yaml manifest."""
        manifest = {
            "version": "1.0",
            "name": config.name,
            "type": config.type,
            "generated": datetime.now().isoformat(),
            "stack": config.stack,
            "directories": config.directories,
            "agents": config.agents,
            "orchestration": config.orchestration,
        }

        with open(path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    def _write_context_files(self, config: ProjectConfig) -> list[str]:
        """Write project context markdown files."""
        created = []

        files = [
            ("00-tech-stack.md", self._generate_tech_stack_content(config)),
            ("01-architecture.md", self._generate_architecture_content(config)),
            ("02-conventions.md", self._generate_conventions_content(config)),
            ("03-setup.md", self._generate_setup_content(config)),
            ("04-apis.md", self._generate_apis_content(config)),
        ]

        for filename, content in files:
            path = self.context_dir / filename
            with open(path, "w") as f:
                f.write(content)
            created.append(str(path))

        return created

    def _setup_runtime_directories(self) -> list[str]:
        """Create runtime directory structure."""
        created = []

        runtime_dirs = [
            self.agent_comm_dir / "orchestration" / "tasks" / "pending",
            self.agent_comm_dir / "orchestration" / "tasks" / "in-progress",
            self.agent_comm_dir / "orchestration" / "tasks" / "completed",
            self.agent_comm_dir / "orchestration" / "tasks" / "blocked",
            self.agent_comm_dir / "messaging" / "inbox",
            self.agent_comm_dir / "messaging" / "sent",
            self.agent_comm_dir / "checkpoints",
            self.agent_comm_dir / "shared-knowledge" / "api-contracts",
            self.agent_comm_dir / "shared-knowledge" / "design-decisions",
            self.agent_comm_dir / "logs",
        ]

        for directory in runtime_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            gitkeep = directory / ".gitkeep"
            gitkeep.touch()
            created.append(str(directory))

        # Create registry file
        registry_path = self.agent_comm_dir / "agents" / "registry.json"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(registry_path, "w") as f:
            f.write('{"agents": [], "last_updated": null}')
        created.append(str(registry_path))

        return created

    def _generate_tech_stack_content(self, config: ProjectConfig) -> str:
        """Generate tech stack markdown content."""
        lines = ["# Project Tech Stack\n"]
        lines.append(f"> Generated for: {config.name}\n")

        stack = config.stack

        if stack.get("frontend"):
            lines.append("## Frontend\n")
            fe = stack["frontend"]
            if fe.get("framework"):
                lines.append(f"- **Framework**: {fe['framework']}")
                if fe.get("version"):
                    lines[-1] += f" {fe['version']}"
            if fe.get("language"):
                lines.append(f"- **Language**: {fe['language']}")
            if fe.get("build_tool"):
                lines.append(f"- **Build Tool**: {fe['build_tool']}")
            if fe.get("state_management"):
                lines.append(f"- **State Management**: {fe['state_management']}")
            lines.append("")

        if stack.get("backend"):
            lines.append("## Backend\n")
            be = stack["backend"]
            if be.get("framework"):
                lines.append(f"- **Framework**: {be['framework']}")
            if be.get("language"):
                lines.append(f"- **Language**: {be['language']}")
            if be.get("orm"):
                lines.append(f"- **ORM**: {be['orm']}")
            lines.append("")

        if stack.get("database") and stack["database"].get("type"):
            lines.append("## Database\n")
            lines.append(f"- **Primary**: {stack['database']['type']}")
            lines.append("")

        if stack.get("infrastructure"):
            lines.append("## Infrastructure\n")
            infra = stack["infrastructure"]
            if infra.get("containerization"):
                lines.append(f"- **Containers**: {infra['containerization']}")
            if infra.get("orchestration"):
                lines.append(f"- **Orchestration**: {infra['orchestration']}")
            if infra.get("cache"):
                lines.append(f"- **Cache**: {infra['cache']}")
            lines.append("")

        if stack.get("ci_cd") and stack["ci_cd"].get("platform"):
            lines.append("## CI/CD\n")
            lines.append(f"- **Platform**: {stack['ci_cd']['platform']}")
            lines.append("")

        return "\n".join(lines)

    def _generate_architecture_content(self, config: ProjectConfig) -> str:
        """Generate architecture markdown content."""
        lines = [f"# {config.name} Architecture\n"]

        lines.append("## Overview\n")
        lines.append(f"Project type: {config.type}\n")

        if config.directories:
            lines.append("## Directory Structure\n")
            lines.append("```")
            lines.append(f"{config.name}/")
            for key, path in config.directories.items():
                lines.append(f"├── {path}/")
            lines.append("```\n")

        lines.append("## Key Components\n")
        lines.append("Document your main components and their responsibilities here.\n")

        lines.append("## Data Flow\n")
        lines.append("Document how data flows through your system.\n")

        return "\n".join(lines)

    def _generate_conventions_content(self, config: ProjectConfig) -> str:
        """Generate conventions markdown content."""
        lines = ["# Coding Conventions\n"]

        lines.append("## General\n")
        lines.append("- Use meaningful, descriptive names")
        lines.append("- Keep functions small and focused")
        lines.append("- Write self-documenting code")
        lines.append("- Add comments only for complex logic\n")

        stack = config.stack

        if stack.get("frontend", {}).get("language") == "TypeScript":
            lines.append("## TypeScript/Frontend\n")
            lines.append("- Components: `PascalCase.tsx`")
            lines.append("- Hooks: `useCamelCase.ts`")
            lines.append("- Utils: `camelCase.ts`\n")

        if stack.get("backend", {}).get("language") == "Python":
            lines.append("## Python/Backend\n")
            lines.append("- Files: `snake_case.py`")
            lines.append("- Classes: `PascalCase`")
            lines.append("- Functions: `snake_case`\n")

        lines.append("## Git\n")
        lines.append("### Commit Messages")
        lines.append("```")
        lines.append("<type>(<scope>): <description>")
        lines.append("")
        lines.append("Types: feat, fix, docs, style, refactor, test, chore")
        lines.append("```\n")

        return "\n".join(lines)

    def _generate_setup_content(self, config: ProjectConfig) -> str:
        """Generate setup markdown content."""
        lines = ["# Development Setup\n"]

        lines.append("## Prerequisites\n")
        stack = config.stack

        if stack.get("frontend"):
            lines.append("- Node.js 20+ (for frontend)")

        if stack.get("backend", {}).get("language") == "Python":
            lines.append("- Python 3.11+")
        elif stack.get("backend", {}).get("language") == "Go":
            lines.append("- Go 1.21+")

        if stack.get("infrastructure", {}).get("containerization"):
            lines.append("- Docker and Docker Compose")

        lines.append("")

        lines.append("## Quick Start\n")
        lines.append("```bash")
        lines.append(f"# Clone repository")
        lines.append(f"git clone <repo-url>")
        lines.append(f"cd {config.name}")
        lines.append("")
        lines.append("# Using Docker (recommended)")
        lines.append("docker-compose up")
        lines.append("```\n")

        lines.append("## Local Development\n")
        lines.append("Document local development setup here.\n")

        lines.append("## Environment Variables\n")
        lines.append("Copy `.env.example` to `.env` and configure:\n")
        lines.append("```bash")
        lines.append("# Add your environment variables here")
        lines.append("```\n")

        return "\n".join(lines)

    def _generate_apis_content(self, config: ProjectConfig) -> str:
        """Generate APIs markdown content."""
        lines = ["# API Documentation\n"]

        lines.append("## Base URL\n")
        lines.append("- Development: `http://localhost:8000`")
        lines.append("- Production: `https://api.yourproject.com`\n")

        lines.append("## Authentication\n")
        lines.append("Document authentication method here.\n")

        lines.append("## Endpoints\n")
        lines.append("| Method | Endpoint | Description | Auth |")
        lines.append("|--------|----------|-------------|------|")
        lines.append("| GET | `/health` | Health check | No |")
        lines.append("| ... | ... | ... | ... |\n")

        lines.append("## Response Format\n")
        lines.append("```json")
        lines.append("{")
        lines.append('  "data": { ... },')
        lines.append('  "meta": { "timestamp": "..." }')
        lines.append("}")
        lines.append("```\n")

        return "\n".join(lines)

    def _apply_template_variables(self, templates: dict, variables: dict) -> dict:
        """Apply variables to template strings."""
        # Simple variable substitution
        # In production, use a proper template engine like Jinja2
        return templates

    def _extract_directories(self, template: dict) -> dict:
        """Extract directory configuration from template."""
        structure = template.get("structure", {})
        dirs = {}

        for item in structure.get("directories", []):
            path = item.get("path", "")
            if "/" in path:
                base = path.split("/")[0]
                if base not in dirs:
                    dirs[base] = base

        return dirs

    def _extract_agents(self, template: dict, variables: dict) -> dict:
        """Extract agent configuration from template."""
        agent_roles = template.get("agent_roles", {})
        return {
            "enabled_roles": agent_roles.get("required", [])
            + agent_roles.get("optional", []),
            "customizations": agent_roles.get("customizations", {}),
        }


def generate_project(
    project_path: str,
    stack: DetectedStack = None,
    template: str = None,
    variables: dict = None,
) -> list[str]:
    """Main function to generate project configuration."""
    generator = ProjectGenerator(project_path)

    if template:
        config = generator.generate_from_template(template, variables or {})
    elif stack:
        config = generator.generate_from_stack(stack)
    else:
        raise ValueError("Either stack or template must be provided")

    return generator.write_configuration(config)


if __name__ == "__main__":
    import sys

    from detector import TechStackDetector

    path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Detect stack
    detector = TechStackDetector(path)
    stack = detector.detect()

    # Generate configuration
    files = generate_project(path, stack=stack)

    print("Generated files:")
    for f in files:
        print(f"  - {f}")
