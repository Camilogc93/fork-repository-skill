"""
Project Initialization Tools

This package provides tools for initializing projects for multi-agent orchestration:

- detector.py: Auto-detect tech stack from project files
- generator.py: Generate configuration files
- validator.py: Validate project setup
"""

from detector import DetectedStack, TechStackDetector, format_detection_report
from generator import ProjectConfig, ProjectGenerator, generate_project
from validator import (
    ProjectValidator,
    ValidationReport,
    format_validation_report,
    validate_project,
)

__all__ = [
    # Detector
    "TechStackDetector",
    "DetectedStack",
    "format_detection_report",
    # Generator
    "ProjectGenerator",
    "ProjectConfig",
    "generate_project",
    # Validator
    "ProjectValidator",
    "ValidationReport",
    "format_validation_report",
    "validate_project",
]
