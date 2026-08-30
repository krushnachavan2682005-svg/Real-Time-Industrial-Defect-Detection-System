from pathlib import Path

import yaml


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def test_deployment_files_exist():
    """Test that all essential deployment configuration files exist."""
    root = get_project_root()

    assert (root / "deployment" / "docker" / "Dockerfile").is_file()
    assert (root / "deployment" / "docker" / "docker-compose.yml").is_file()
    assert (root / "deployment" / "docker" / ".env.example").is_file()
    assert (root / "deployment" / "docker" / "README.md").is_file()
    assert (root / "deployment" / "edge" / "README.md").is_file()


def test_docker_compose_structure():
    """Test that the docker-compose.yml file is structurally valid."""
    root = get_project_root()
    compose_path = root / "deployment" / "docker" / "docker-compose.yml"

    with open(compose_path, "r") as f:
        compose_data = yaml.safe_load(f)

    assert "services" in compose_data
    services = compose_data["services"]

    # Check for expected services
    assert "industrial-defect-api" in services
    assert "prometheus" in services
    assert "grafana" in services

    # Check API service structure
    api = services["industrial-defect-api"]
    assert "build" in api
    assert "ports" in api
    assert "8000:8000" in api["ports"]
    assert "healthcheck" in api

    # Check Prometheus service target configuration matches API
    prometheus = services["prometheus"]
    assert "depends_on" in prometheus
    assert "industrial-defect-api" in prometheus["depends_on"]

    # Check Grafana service
    grafana = services["grafana"]
    assert "depends_on" in grafana
    assert "prometheus" in grafana["depends_on"]
    assert "ports" in grafana
    assert "3000:3000" in grafana["ports"]


def test_env_example_variables():
    """Test that .env.example contains expected non-secret configurations."""
    root = get_project_root()
    env_path = root / "deployment" / "docker" / ".env.example"

    with open(env_path, "r") as f:
        env_content = f.read()

    expected_vars = [
        "APP_ENV=",
        "LOG_LEVEL=",
        "MODEL_PATH=",
        "API_HOST=",
        "API_PORT=",
        "PLC_ENABLED=",
        "PROMETHEUS_ENABLED=",
        "GRAFANA_ADMIN_USER=",
        "GRAFANA_ADMIN_PASSWORD=",
    ]

    for var in expected_vars:
        assert var in env_content, f"Expected {var} in .env.example"
