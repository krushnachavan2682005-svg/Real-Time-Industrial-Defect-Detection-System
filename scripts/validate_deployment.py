#!/usr/bin/env python3
"""
Deployment Validation Script

This script statically validates the deployment readiness of the
Real-Time Industrial Defect Detection System repository.
It ensures that all required deployment files, configurations, and artifacts
are present before attempting to build or run the Docker containers.
"""

import sys
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent.parent

    # Required files and directories
    requirements = [
        ("Dockerfile", project_root / "deployment" / "docker" / "Dockerfile"),
        (
            "Docker Compose",
            project_root / "deployment" / "docker" / "docker-compose.yml",
        ),
        ("ONNX Model", project_root / "models" / "onnx" / "best.onnx"),
        (
            "Prometheus Config",
            project_root / "monitoring" / "prometheus" / "prometheus.yml",
        ),
        (
            "Grafana Provisioning",
            project_root / "monitoring" / "grafana" / "provisioning",
        ),
        ("Grafana Dashboards", project_root / "monitoring" / "grafana" / "dashboards"),
        ("API Config", project_root / "configs" / "api" / "api.yaml"),
        ("Inference Config", project_root / "configs" / "inference" / "realtime.yaml"),
        (
            "Decision Config",
            project_root / "configs" / "decision" / "decision_rules.yaml",
        ),
    ]

    print("========================================")
    print("Deployment Readiness Validation")
    print("========================================")

    all_passed = True

    for name, path in requirements:
        if path.exists():
            print(
                f"[\033[92mPASS\033[0m] {name} exists at {path.relative_to(project_root)}"  # noqa: E501
            )
        else:
            print(
                f"[\033[91mFAIL\033[0m] {name} is missing at {path.relative_to(project_root)}"  # noqa: E501
            )
            all_passed = False

    print("========================================")

    if all_passed:
        print("\033[92mAll deployment requirements validated successfully.\033[0m")
        sys.exit(0)
    else:
        print(
            "\033[91mValidation failed. Please ensure all required files are present.\033[0m"  # noqa: E501
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
