#!/usr/bin/env python3
"""
Project Initialization CLI

Main entry point for project initialization tools.

Usage:
    python main.py init [--template TEMPLATE] [--wizard] [PATH]
    python main.py detect [PATH]
    python main.py validate [PATH]
    python main.py list-templates
"""

import argparse
import sys
from pathlib import Path

from detector import TechStackDetector, format_detection_report
from generator import ProjectGenerator, generate_project
from validator import format_validation_report, validate_project


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a project for orchestration."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        return 1

    print(f"Initializing project: {project_path.name}")
    print()

    if args.template:
        # Template-based initialization
        print(f"Using template: {args.template}")
        variables = {"project_name": project_path.name}

        try:
            files = generate_project(
                str(project_path), template=args.template, variables=variables
            )
        except ValueError as e:
            print(f"Error: {e}")
            return 1

    else:
        # Auto-detect mode
        print("Scanning project for technologies...")
        detector = TechStackDetector(project_path)
        stack = detector.detect()

        print()
        print(format_detection_report(stack))
        print()

        if stack.confidence < 0.3:
            print("Warning: Low confidence detection.")
            print("Consider using a template with: --template <template-name>")
            print()

        # Confirm with user (in CLI mode)
        if not args.yes:
            response = input("Generate configuration with detected stack? [Y/n]: ")
            if response.lower() == "n":
                print("Aborted.")
                return 0

        print()
        print("Generating configuration...")
        files = generate_project(str(project_path), stack=stack)

    print()
    print("Created files:")
    for f in files:
        # Show relative path
        try:
            rel_path = Path(f).relative_to(project_path)
            print(f"  - {rel_path}")
        except ValueError:
            print(f"  - {f}")

    print()
    print("Project initialized for orchestration!")
    print()
    print("Next steps:")
    print("  1. Review generated files in .claude/agents/project-context/")
    print("  2. Customize agent roles if needed")
    print('  3. Start orchestrating: "orchestrate feature: <your feature>"')

    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """Detect tech stack without generating files."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        return 1

    detector = TechStackDetector(project_path)
    stack = detector.detect()

    print(format_detection_report(stack))

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate project setup."""
    project_path = Path(args.path).resolve()

    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        return 1

    report = validate_project(str(project_path))
    print(format_validation_report(report))

    return 0 if report.is_ready else 1


def cmd_list_templates(args: argparse.Namespace) -> int:
    """List available templates."""
    templates = [
        ("fullstack-web", "Full-stack web app with frontend SPA and backend API"),
        ("api-service", "Backend API service (REST/GraphQL)"),
        ("frontend-spa", "Single page application (frontend only)"),
        ("cli-tool", "Command line tool"),
        ("library", "Shared library/package"),
    ]

    print("Available Project Templates")
    print("=" * 50)
    print()

    for name, description in templates:
        print(f"  {name}")
        print(f"    {description}")
        print()

    print("Usage: python main.py init --template <name> [path]")

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Project initialization for multi-agent orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init                    # Auto-detect and initialize current directory
  %(prog)s init /path/to/project   # Initialize specific project
  %(prog)s init --template api-service  # Use template
  %(prog)s detect                  # Show detected stack without generating
  %(prog)s validate                # Check if setup is ready
  %(prog)s list-templates          # Show available templates
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize project for orchestration"
    )
    init_parser.add_argument(
        "path", nargs="?", default=".", help="Project path (default: current directory)"
    )
    init_parser.add_argument(
        "--template", "-t", help="Use specific template instead of auto-detect"
    )
    init_parser.add_argument(
        "--wizard", "-w", action="store_true", help="Use interactive wizard"
    )
    init_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )
    init_parser.set_defaults(func=cmd_init)

    # detect command
    detect_parser = subparsers.add_parser(
        "detect", help="Detect tech stack (no file generation)"
    )
    detect_parser.add_argument(
        "path", nargs="?", default=".", help="Project path (default: current directory)"
    )
    detect_parser.set_defaults(func=cmd_detect)

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate project setup"
    )
    validate_parser.add_argument(
        "path", nargs="?", default=".", help="Project path (default: current directory)"
    )
    validate_parser.set_defaults(func=cmd_validate)

    # list-templates command
    list_parser = subparsers.add_parser(
        "list-templates", help="List available templates"
    )
    list_parser.set_defaults(func=cmd_list_templates)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
