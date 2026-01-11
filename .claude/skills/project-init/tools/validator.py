"""
Project Setup Validator
Validates that a project is properly configured for orchestration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ValidationResult:
    """Result of validation check."""

    passed: bool
    category: str
    check: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Complete validation report."""

    results: list[ValidationResult] = field(default_factory=list)
    is_ready: bool = False
    errors: int = 0
    warnings: int = 0
    suggestions: list[str] = field(default_factory=list)

    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result."""
        self.results.append(result)
        if not result.passed:
            if result.severity == "error":
                self.errors += 1
            elif result.severity == "warning":
                self.warnings += 1

    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion for improvement."""
        self.suggestions.append(suggestion)

    def finalize(self) -> None:
        """Finalize the report."""
        self.is_ready = self.errors == 0


class ProjectValidator:
    """Validates project configuration for orchestration."""

    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.claude_dir = self.project_path / ".claude"
        self.agents_dir = self.claude_dir / "agents"
        self.context_dir = self.agents_dir / "project-context"
        self.roles_dir = self.agents_dir / "roles"
        self.agent_comm_dir = self.project_path / ".agent-comm"

    def validate(self) -> ValidationReport:
        """Run all validations and return report."""
        report = ValidationReport()

        # Run validation checks
        self._validate_project_manifest(report)
        self._validate_context_files(report)
        self._validate_agent_roles(report)
        self._validate_runtime_directories(report)
        self._validate_context_content(report)

        # Finalize report
        report.finalize()

        return report

    def _validate_project_manifest(self, report: ValidationReport) -> None:
        """Validate project.yaml exists and is valid."""
        manifest_path = self.claude_dir / "project.yaml"

        if not manifest_path.exists():
            report.add_result(
                ValidationResult(
                    passed=False,
                    category="Configuration",
                    check="Project Manifest",
                    message="project.yaml not found - run 'init project' to create",
                    severity="error",
                )
            )
            return

        try:
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)

            # Check required fields
            required_fields = ["name", "type", "stack"]
            for field in required_fields:
                if field not in manifest:
                    report.add_result(
                        ValidationResult(
                            passed=False,
                            category="Configuration",
                            check=f"Manifest: {field}",
                            message=f"Required field '{field}' missing in project.yaml",
                            severity="error",
                        )
                    )
                else:
                    report.add_result(
                        ValidationResult(
                            passed=True,
                            category="Configuration",
                            check=f"Manifest: {field}",
                            message=f"Field '{field}' present",
                        )
                    )

        except yaml.YAMLError as e:
            report.add_result(
                ValidationResult(
                    passed=False,
                    category="Configuration",
                    check="Project Manifest",
                    message=f"Invalid YAML in project.yaml: {e}",
                    severity="error",
                )
            )

    def _validate_context_files(self, report: ValidationReport) -> None:
        """Validate project context files exist."""
        required_files = [
            ("00-tech-stack.md", "Tech Stack"),
            ("01-architecture.md", "Architecture"),
            ("02-conventions.md", "Conventions"),
            ("03-setup.md", "Setup"),
            ("04-apis.md", "APIs"),
        ]

        if not self.context_dir.exists():
            report.add_result(
                ValidationResult(
                    passed=False,
                    category="Context Files",
                    check="Context Directory",
                    message="project-context directory not found",
                    severity="error",
                )
            )
            return

        for filename, name in required_files:
            path = self.context_dir / filename
            if path.exists():
                # Check file size
                size = path.stat().st_size
                if size < 100:
                    report.add_result(
                        ValidationResult(
                            passed=True,
                            category="Context Files",
                            check=name,
                            message=f"{name} exists but appears minimal ({size} bytes)",
                            severity="warning",
                        )
                    )
                    report.add_suggestion(f"Consider adding more detail to {filename}")
                else:
                    report.add_result(
                        ValidationResult(
                            passed=True,
                            category="Context Files",
                            check=name,
                            message=f"{name} exists ({size} bytes)",
                        )
                    )
            else:
                report.add_result(
                    ValidationResult(
                        passed=False,
                        category="Context Files",
                        check=name,
                        message=f"{filename} not found",
                        severity="error",
                    )
                )

    def _validate_agent_roles(self, report: ValidationReport) -> None:
        """Validate agent role definitions exist."""
        required_roles = ["frontend", "backend", "devops", "qa", "architect"]

        if not self.roles_dir.exists():
            report.add_result(
                ValidationResult(
                    passed=False,
                    category="Agent Roles",
                    check="Roles Directory",
                    message="roles directory not found",
                    severity="error",
                )
            )
            return

        for role in required_roles:
            path = self.roles_dir / f"{role}.md"
            if path.exists():
                report.add_result(
                    ValidationResult(
                        passed=True,
                        category="Agent Roles",
                        check=f"{role.title()} Role",
                        message=f"{role}.md configured",
                    )
                )
            else:
                report.add_result(
                    ValidationResult(
                        passed=False,
                        category="Agent Roles",
                        check=f"{role.title()} Role",
                        message=f"{role}.md not found",
                        severity="warning",
                    )
                )

    def _validate_runtime_directories(self, report: ValidationReport) -> None:
        """Validate runtime directory structure."""
        required_dirs = [
            ("orchestration/tasks", "Task Queue"),
            ("messaging", "Messaging"),
            ("checkpoints", "Checkpoints"),
            ("shared-knowledge", "Shared Knowledge"),
        ]

        if not self.agent_comm_dir.exists():
            report.add_result(
                ValidationResult(
                    passed=False,
                    category="Runtime",
                    check="Agent Communication Directory",
                    message=".agent-comm directory not found",
                    severity="error",
                )
            )
            return

        for subdir, name in required_dirs:
            path = self.agent_comm_dir / subdir
            if path.exists():
                report.add_result(
                    ValidationResult(
                        passed=True,
                        category="Runtime",
                        check=name,
                        message=f"{subdir}/ ready",
                    )
                )
            else:
                report.add_result(
                    ValidationResult(
                        passed=False,
                        category="Runtime",
                        check=name,
                        message=f"{subdir}/ not found - run 'init project' to create",
                        severity="error",
                    )
                )

    def _validate_context_content(self, report: ValidationReport) -> None:
        """Validate content quality of context files."""
        # Check tech stack has framework info
        tech_stack = self.context_dir / "00-tech-stack.md"
        if tech_stack.exists():
            content = tech_stack.read_text().lower()
            if "framework" not in content or "[" in content:
                report.add_suggestion(
                    "Fill in actual framework names in 00-tech-stack.md (remove placeholders)"
                )

        # Check APIs file has endpoints
        apis = self.context_dir / "04-apis.md"
        if apis.exists():
            content = apis.read_text()
            if content.count("|") < 10:  # Basic table detection
                report.add_suggestion(
                    "Document your API endpoints in 04-apis.md for better agent context"
                )


def format_validation_report(report: ValidationReport) -> str:
    """Format validation report as readable text."""
    lines = []
    lines.append("Orchestration Setup Validation")
    lines.append("=" * 50)
    lines.append("")

    # Group by category
    categories: dict[str, list[ValidationResult]] = {}
    for result in report.results:
        if result.category not in categories:
            categories[result.category] = []
        categories[result.category].append(result)

    for category, results in categories.items():
        lines.append(f"{category}:")
        for result in results:
            if result.passed:
                status = "[OK]" if result.severity != "warning" else "[WARN]"
            else:
                status = "[FAIL]" if result.severity == "error" else "[WARN]"

            lines.append(f"  {status} {result.check}: {result.message}")
        lines.append("")

    # Summary
    lines.append("-" * 50)
    if report.is_ready:
        lines.append("Status: READY for orchestration")
    else:
        lines.append(f"Status: NOT READY ({report.errors} errors, {report.warnings} warnings)")

    if report.suggestions:
        lines.append("")
        lines.append("Suggestions:")
        for suggestion in report.suggestions:
            lines.append(f"  - {suggestion}")

    return "\n".join(lines)


def validate_project(project_path: str) -> ValidationReport:
    """Main function to validate project setup."""
    validator = ProjectValidator(project_path)
    return validator.validate()


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."

    report = validate_project(path)
    print(format_validation_report(report))

    # Exit with error code if not ready
    sys.exit(0 if report.is_ready else 1)
