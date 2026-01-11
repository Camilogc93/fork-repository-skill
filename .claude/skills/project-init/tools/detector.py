"""
Tech Stack Detector
Automatically detects project technologies from configuration files.
"""

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DetectedStack:
    """Represents detected technology stack."""

    frontend: dict = field(default_factory=dict)
    backend: dict = field(default_factory=dict)
    database: dict = field(default_factory=dict)
    infrastructure: dict = field(default_factory=dict)
    testing: dict = field(default_factory=dict)
    ci_cd: dict = field(default_factory=dict)
    confidence: float = 0.0
    raw_detections: list = field(default_factory=list)


class TechStackDetector:
    """Detects technology stack from project files."""

    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.detections: list[dict] = []

    def detect(self) -> DetectedStack:
        """Run all detection methods and compile results."""
        stack = DetectedStack()

        # Run detectors
        self._detect_package_json(stack)
        self._detect_python_project(stack)
        self._detect_go_project(stack)
        self._detect_rust_project(stack)
        self._detect_docker(stack)
        self._detect_ci_cd(stack)
        self._detect_database(stack)

        # Calculate confidence
        stack.raw_detections = self.detections
        stack.confidence = self._calculate_confidence()

        return stack

    def _detect_package_json(self, stack: DetectedStack) -> None:
        """Detect Node.js/frontend technologies from package.json."""
        package_json = self.project_path / "package.json"

        # Also check frontend subdirectory
        if not package_json.exists():
            package_json = self.project_path / "frontend" / "package.json"

        if not package_json.exists():
            return

        try:
            with open(package_json) as f:
                pkg = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

        # Detect frontend framework
        frontend_frameworks = {
            "react": "React",
            "vue": "Vue",
            "svelte": "Svelte",
            "@angular/core": "Angular",
            "next": "Next.js",
            "nuxt": "Nuxt",
        }

        for dep, name in frontend_frameworks.items():
            if dep in deps:
                version = deps[dep].lstrip("^~")
                stack.frontend["framework"] = name
                stack.frontend["version"] = version
                self._add_detection("frontend_framework", name, 0.9)
                break

        # Detect TypeScript
        if "typescript" in deps:
            stack.frontend["language"] = "TypeScript"
            stack.frontend["typescript_version"] = deps["typescript"].lstrip("^~")
            self._add_detection("frontend_language", "TypeScript", 0.95)
        else:
            stack.frontend["language"] = "JavaScript"
            self._add_detection("frontend_language", "JavaScript", 0.8)

        # Detect build tool
        build_tools = {
            "vite": "Vite",
            "webpack": "Webpack",
            "parcel": "Parcel",
            "esbuild": "esbuild",
            "rollup": "Rollup",
        }

        for tool, name in build_tools.items():
            if tool in deps:
                stack.frontend["build_tool"] = name
                self._add_detection("build_tool", name, 0.9)
                break

        # Detect state management
        state_libs = {
            "@reduxjs/toolkit": "Redux Toolkit",
            "redux": "Redux",
            "zustand": "Zustand",
            "recoil": "Recoil",
            "mobx": "MobX",
            "pinia": "Pinia",
            "vuex": "Vuex",
        }

        for lib, name in state_libs.items():
            if lib in deps:
                stack.frontend["state_management"] = name
                self._add_detection("state_management", name, 0.85)
                break

        # Detect testing
        test_libs = {
            "vitest": "Vitest",
            "jest": "Jest",
            "@testing-library/react": "Testing Library",
            "playwright": "Playwright",
            "cypress": "Cypress",
        }

        for lib, name in test_libs.items():
            if lib in deps:
                if "testing" not in stack.testing:
                    stack.testing["frontend"] = []
                stack.testing.setdefault("frontend", []).append(name)
                self._add_detection("frontend_testing", name, 0.9)

        # Detect backend if it's a Node backend
        backend_frameworks = {
            "express": "Express",
            "fastify": "Fastify",
            "@nestjs/core": "NestJS",
            "koa": "Koa",
            "hapi": "Hapi",
        }

        for dep, name in backend_frameworks.items():
            if dep in deps:
                stack.backend["framework"] = name
                stack.backend["language"] = (
                    "TypeScript" if "typescript" in deps else "JavaScript"
                )
                stack.backend["runtime"] = "Node.js"
                self._add_detection("backend_framework", name, 0.9)
                break

    def _detect_python_project(self, stack: DetectedStack) -> None:
        """Detect Python technologies."""
        # Check multiple possible locations
        pyproject = self.project_path / "pyproject.toml"
        requirements = self.project_path / "requirements.txt"

        # Also check backend subdirectory
        if not pyproject.exists() and not requirements.exists():
            pyproject = self.project_path / "backend" / "pyproject.toml"
            requirements = self.project_path / "backend" / "requirements.txt"

        deps_content = ""

        if pyproject.exists():
            try:
                content = pyproject.read_text()
                deps_content = content

                # Extract Python version
                python_match = re.search(r'python\s*=\s*"([^"]+)"', content)
                if python_match:
                    stack.backend["python_version"] = python_match.group(1)
                    self._add_detection("python_version", python_match.group(1), 0.95)
            except IOError:
                pass

        if requirements.exists():
            try:
                deps_content += "\n" + requirements.read_text()
            except IOError:
                pass

        if not deps_content:
            return

        # Detect framework
        frameworks = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "starlette": "Starlette",
            "aiohttp": "aiohttp",
        }

        for pkg, name in frameworks.items():
            if pkg in deps_content.lower():
                stack.backend["framework"] = name
                stack.backend["language"] = "Python"
                self._add_detection("backend_framework", name, 0.9)
                break

        # Detect ORM
        orms = {
            "sqlalchemy": "SQLAlchemy",
            "tortoise-orm": "Tortoise ORM",
            "peewee": "Peewee",
            "django": "Django ORM",
        }

        for pkg, name in orms.items():
            if pkg in deps_content.lower():
                stack.backend["orm"] = name
                self._add_detection("orm", name, 0.85)
                break

        # Detect testing
        test_libs = {"pytest": "pytest", "unittest": "unittest", "nose": "nose"}

        for pkg, name in test_libs.items():
            if pkg in deps_content.lower():
                stack.testing.setdefault("backend", []).append(name)
                self._add_detection("backend_testing", name, 0.9)

    def _detect_go_project(self, stack: DetectedStack) -> None:
        """Detect Go technologies."""
        go_mod = self.project_path / "go.mod"

        if not go_mod.exists():
            return

        try:
            content = go_mod.read_text()
        except IOError:
            return

        stack.backend["language"] = "Go"
        self._add_detection("backend_language", "Go", 0.95)

        # Detect framework
        frameworks = {
            "github.com/gin-gonic/gin": "Gin",
            "github.com/labstack/echo": "Echo",
            "github.com/gofiber/fiber": "Fiber",
            "github.com/gorilla/mux": "Gorilla Mux",
        }

        for pkg, name in frameworks.items():
            if pkg in content:
                stack.backend["framework"] = name
                self._add_detection("backend_framework", name, 0.9)
                break

    def _detect_rust_project(self, stack: DetectedStack) -> None:
        """Detect Rust technologies."""
        cargo_toml = self.project_path / "Cargo.toml"

        if not cargo_toml.exists():
            return

        try:
            content = cargo_toml.read_text()
        except IOError:
            return

        stack.backend["language"] = "Rust"
        self._add_detection("backend_language", "Rust", 0.95)

        # Detect framework
        frameworks = {
            "axum": "Axum",
            "actix-web": "Actix Web",
            "rocket": "Rocket",
            "warp": "Warp",
        }

        for pkg, name in frameworks.items():
            if pkg in content:
                stack.backend["framework"] = name
                self._add_detection("backend_framework", name, 0.9)
                break

    def _detect_docker(self, stack: DetectedStack) -> None:
        """Detect Docker configuration."""
        dockerfile = self.project_path / "Dockerfile"
        compose = self.project_path / "docker-compose.yml"
        compose_alt = self.project_path / "docker-compose.yaml"

        if dockerfile.exists():
            stack.infrastructure["containerization"] = "Docker"
            self._add_detection("containerization", "Docker", 0.95)

        compose_file = compose if compose.exists() else compose_alt
        if compose_file.exists():
            stack.infrastructure["orchestration"] = "Docker Compose"
            self._add_detection("orchestration", "Docker Compose", 0.9)

            # Try to detect services from compose
            try:
                content = compose_file.read_text()

                # Detect databases
                if "postgres" in content.lower():
                    stack.database["type"] = "PostgreSQL"
                    self._add_detection("database", "PostgreSQL", 0.85)
                elif "mysql" in content.lower():
                    stack.database["type"] = "MySQL"
                    self._add_detection("database", "MySQL", 0.85)
                elif "mongo" in content.lower():
                    stack.database["type"] = "MongoDB"
                    self._add_detection("database", "MongoDB", 0.85)

                # Detect Redis
                if "redis" in content.lower():
                    stack.infrastructure["cache"] = "Redis"
                    self._add_detection("cache", "Redis", 0.85)
            except IOError:
                pass

    def _detect_ci_cd(self, stack: DetectedStack) -> None:
        """Detect CI/CD configuration."""
        github_workflows = self.project_path / ".github" / "workflows"
        gitlab_ci = self.project_path / ".gitlab-ci.yml"
        circleci = self.project_path / ".circleci" / "config.yml"
        jenkins = self.project_path / "Jenkinsfile"

        if github_workflows.exists() and any(github_workflows.iterdir()):
            stack.ci_cd["platform"] = "GitHub Actions"
            self._add_detection("ci_cd", "GitHub Actions", 0.95)
        elif gitlab_ci.exists():
            stack.ci_cd["platform"] = "GitLab CI"
            self._add_detection("ci_cd", "GitLab CI", 0.95)
        elif circleci.exists():
            stack.ci_cd["platform"] = "CircleCI"
            self._add_detection("ci_cd", "CircleCI", 0.95)
        elif jenkins.exists():
            stack.ci_cd["platform"] = "Jenkins"
            self._add_detection("ci_cd", "Jenkins", 0.95)

    def _detect_database(self, stack: DetectedStack) -> None:
        """Detect database from various sources."""
        # Check for Prisma
        prisma_schema = self.project_path / "prisma" / "schema.prisma"
        if prisma_schema.exists():
            try:
                content = prisma_schema.read_text()
                if "postgresql" in content.lower():
                    stack.database["type"] = "PostgreSQL"
                elif "mysql" in content.lower():
                    stack.database["type"] = "MySQL"
                elif "sqlite" in content.lower():
                    stack.database["type"] = "SQLite"
                elif "mongodb" in content.lower():
                    stack.database["type"] = "MongoDB"

                stack.backend["orm"] = "Prisma"
                self._add_detection("orm", "Prisma", 0.95)
            except IOError:
                pass

        # Check for Alembic (SQLAlchemy migrations)
        alembic_ini = self.project_path / "alembic.ini"
        if alembic_ini.exists():
            stack.backend["migrations"] = "Alembic"
            self._add_detection("migrations", "Alembic", 0.9)

    def _add_detection(self, category: str, value: str, confidence: float) -> None:
        """Record a detection with confidence score."""
        self.detections.append(
            {"category": category, "value": value, "confidence": confidence}
        )

    def _calculate_confidence(self) -> float:
        """Calculate overall confidence score."""
        if not self.detections:
            return 0.0
        return sum(d["confidence"] for d in self.detections) / len(self.detections)


def format_detection_report(stack: DetectedStack) -> str:
    """Format detection results as a readable report."""
    lines = []
    lines.append("Detected Configuration:")
    lines.append("=" * 50)

    if stack.frontend:
        lines.append("\nFrontend:")
        for key, value in stack.frontend.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if stack.backend:
        lines.append("\nBackend:")
        for key, value in stack.backend.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if stack.database:
        lines.append("\nDatabase:")
        for key, value in stack.database.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if stack.infrastructure:
        lines.append("\nInfrastructure:")
        for key, value in stack.infrastructure.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if stack.ci_cd:
        lines.append("\nCI/CD:")
        for key, value in stack.ci_cd.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    if stack.testing:
        lines.append("\nTesting:")
        for key, value in stack.testing.items():
            if isinstance(value, list):
                lines.append(f"  {key.replace('_', ' ').title()}: {', '.join(value)}")
            else:
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")

    lines.append(f"\nDetection Confidence: {stack.confidence:.0%}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    detector = TechStackDetector(path)
    stack = detector.detect()
    print(format_detection_report(stack))
