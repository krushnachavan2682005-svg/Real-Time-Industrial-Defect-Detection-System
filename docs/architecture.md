# System Architecture

## High-Level Architecture (Current Status)

The overall goal of this project is a real-time industrial defect detection system for manufacturing quality control. 

```text
Industrial Camera
  ↓
OpenCV Frame Capture
  ↓
Preprocessing
  ↓
Optimized YOLO Model (ONNX Runtime / TensorRT)
  ↓
Defect Detection
  ↓
Decision Engine
  ↓
Coordinate Mapping
  ↓
PLC
  ↓
Automated Sorting
```

## Model Deployment Flow (Module 9 Update)

To achieve low-latency edge deployment, the system uses the following execution pipeline:

```text
PyTorch Model (.pt)
  ↓
ONNX Export (.onnx)
  ↓
ONNX Runtime (CPU/CUDA) 
   -- OR --
TensorRT Engine (.engine) (when deployed on NVIDIA Edge hardware)
  ↓
Edge Inference
```

### Portability and Hardware Fallbacks
- **Why ONNX?** ONNX provides a portable model graph representation. It is completely independent of the PyTorch runtime, providing significant CPU speedups and forming the bridge to hardware-specific optimizers like TensorRT.
- **Why TensorRT?** TensorRT is NVIDIA's inference optimizer that delivers maximum throughput and minimum latency on NVIDIA edge hardware (e.g., Jetson Nano, Orin).
- **Runtime Fallbacks:** The inference wrapper gracefully degrades. If TensorRT/CUDA is unavailable, the pipeline automatically relies on ONNX Runtime's `CPUExecutionProvider` to ensure the system is fully functional across diverse development environments.

### Model Artifact Locations
- **PyTorch Models**: `models/pytorch/`
- **ONNX Models**: `models/onnx/`
- **TensorRT Engines**: `models/tensorrt/` (Generated on target hardware)
- **Benchmark Reports**: `reports/benchmarks/`

### Accuracy and Benchmarking
All exported models must pass a **numerical equivalence** check against the original PyTorch model to ensure no accuracy degradation occurs during the graph export. Latency benchmarking explicitly measures steady-state inference using a monotonic high-resolution timer (discounting warmup iterations).

## Decision Engine Flow (Module 11 Update)

```text
ONNX Detection Output
        ↓
Decision Engine
        ├── Detection Filtering
        ├── Defect Aggregation
        ├── Severity Assessment
        └── Decision Policy
                ↓
        PASS / REVIEW / REJECT
```

The **Decision Engine** is deterministic and strictly separated from model inference.
with a human-readable reason.

## Defect Mapping and Visualization (Module 12 Update)

```text
ONNX Detection Output
        ↓
Coordinate Transformation
        ↓
Decision Engine
        ↓
Defect Mapper
        ├── Spatial Position
        ├── Region
        ├── Area
        └── Frame Coverage
        ↓
Inspection Result
        ├── Structured Data
        └── Visualization
        ↓
Annotated Inspection Frame
```

The **Defect Mapping** module is responsible for providing spatial context to raw bounding boxes and rendering the results into a human-readable form. It transforms standard detections into `MappedDefect` objects (containing region, area, area ratio, and normalized coordinates). An overarching `ResultBuilder` combines this mapped data with the `DecisionResult` and frame metadata into a single `InspectionResult`. Finally, the `DefectVisualizer` generates an annotated inspection frame based on a standardized color policy, completely independent from core mapping logic.

## Monitoring and Observability (Module 15 Update)

```text
FastAPI Request
        ↓
API Metrics Middleware (HTTP request latency/counters)
        ↓
Inspection Service
        ├── inference timing
        ├── pipeline timing
        ├── decision counters
        ├── defect counters
        └── PLC command counters
        ↓
Prometheus Metrics Registry
        ↓
GET /metrics
        ↓
Prometheus
        ↓
Grafana Dashboard
        ↓
Alerts
```

The **Monitoring** architecture is completely decoupled from business logic. It relies on a central `MetricsService` that acts as a safe facade over the `prometheus_client`. The `/metrics` endpoint exposes real-time operational data for Prometheus scraping.

### Metric Ownership
- **API middleware** → HTTP request count and latency
- **Inspection service** → Inspection counts and pipeline latency
- **Inference layer** → Inference timing (measured carefully by the Inspection Service)
- **Decision result** → Decision metrics (PASS/REVIEW/REJECT)
- **PLC result** → PLC metrics (success/failure per command)
- **Errors** → Pipeline error metrics (grouped by component)

## Persistence Layer (Module 18 Update)

```text
Inspection Pipeline
        ↓
InspectionResult
        ↓
Inspection Repository
        ↓
Database
        ↓
Historical Inspection API
```

The system uses SQLAlchemy ORM to persist inspection metadata and mapped defects to a relational database. This serves as an immutable audit log of manufacturing events. 

- The Core Domain (`InspectionResult`, `DecisionResult`, etc.) remains strictly separated from SQLAlchemy via a repository interface.
- Historical data is exposed through dedicated REST endpoints (`/api/v1/inspections`) allowing paginated reads and filtering, keeping the primary pipeline unaffected.

## Authentication and Authorization (Module 20 Update)

```text
User Request
        ↓
OAuth2 Password Bearer / JWT Token
        ↓
FastAPI Dependency Injection (`get_current_user`)
        ↓
Role-Based Access Control (`require_roles`)
        ↓
Endpoint / Business Logic
```

The system employs a JWT-based authentication layer tightly integrated with FastAPI's dependency injection system, ensuring standard OAuth2 compliance and secure role-based access control (RBAC).

- **Authentication**: Uses `passlib` (bcrypt) for secure password hashing and `PyJWT` for generating state-less access tokens.
- **Authorization (RBAC)**: Centralized authorization decorators limit access to endpoints based on defined roles (`ADMIN`, `ENGINEER`, `OPERATOR`, `VIEWER`). The core business routers are unaltered; they simply consume the DI wrapper.
- **Security**: Hardcoded secrets are removed. Configuration is driven via `security.yaml` and `.env` to enforce production-grade security and password policies.
- **Bootstrap Admin**: The API safely initializes an admin user on a fresh database to prevent lockout, configurable via the `BOOTSTRAP_ADMIN_ENABLED` environment variable.
