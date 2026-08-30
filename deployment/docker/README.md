# Docker Deployment

This directory contains the production-oriented Docker configuration for the Real-Time Industrial Defect Detection System.

## Architecture

The deployment consists of three core services managed via Docker Compose:

1. **industrial-defect-api**: The core FastAPI application that serves the inference and inspection endpoints.
2. **prometheus**: Scrapes metrics from the API service for observability.
3. **grafana**: Visualizes the Prometheus metrics via pre-configured dashboards.

## Environment Variables

Before starting, copy the example environment file and adjust it as needed:

```bash
cp .env.example .env
```

Key variables:
- `APP_ENV`: Deployment environment (e.g., `production`).
- `MODEL_PATH`: Path to the ONNX model (default: `models/onnx/best.onnx`).
- `GRAFANA_ADMIN_PASSWORD`: Admin password for Grafana.

## Model Artifact Strategy

By default, the `docker-compose.yml` mounts the local `models` directory as a volume (`../../models:/app/models`). This allows you to update models without rebuilding the Docker image. For true standalone edge deployments, you can remove the volume mount and allow the `Dockerfile` to copy the model directly into the image by ensuring it's not excluded in `.dockerignore`.

## Commands

### Build the Image
```bash
docker compose build
```

### Start the System (Foreground)
```bash
docker compose up
```

### Start the System (Background / Daemon)
```bash
docker compose up -d
```

### Stop the System
```bash
docker compose down
```

## Endpoints

- **API Health**: `GET http://localhost:8000/health`
- **API Metrics**: `GET http://localhost:8000/metrics`
- **Inspection API**: `POST http://localhost:8000/api/v1/inspect`
- **Prometheus UI**: `http://localhost:9090`
- **Grafana UI**: `http://localhost:3000`

## Production Considerations
- **Volumes**: Prometheus and Grafana use Docker named volumes (`prometheus_data`, `grafana_data`) to persist monitoring data across restarts.
- **Security**: The API runs as a non-root user (`appuser`).
- **CPU Deployment**: The current deployment targets CPU execution using ONNX Runtime. For NVIDIA edge deployments, refer to the edge deployment docs.
