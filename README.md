# Real-Time Industrial Defect Detection System

## Project Description
A Real-Time Industrial Defect Detection System using YOLOv8, OpenCV, PyTorch, ONNX/TensorRT, FastAPI, Prometheus, and Grafana. The system will detect industrial surface defects from live camera feeds and eventually communicate defect information to industrial PLCs.

## Problem Statement
Detecting surface defects in real-time during the manufacturing process is critical for quality control. Manual inspection is slow and error-prone. This project aims to automate the inspection process using state-of-the-art computer vision models, ensuring high throughput and accuracy, and integrating seamlessly into existing industrial automation systems (PLCs).

## Expected System Architecture
```text
Camera -> OpenCV -> Preprocessing -> Inference Engine -> Decision Engine -> Coordinate Mapping -> FastAPI -> PLC
```

## Planned Technology Stack
- **Languages:** Python 3.11+
- **Deep Learning:** PyTorch, Ultralytics YOLO
- **Computer Vision:** OpenCV, Albumentations
- **Inference & Optimization:** ONNX, TensorRT
- **Backend & APIs:** FastAPI, Uvicorn, Pydantic
- **Monitoring:** Prometheus, Grafana
- **Testing & Formatting:** Pytest, Ruff, Black, MyPy

## Repository Structure
- `configs/`: Configuration files (data, model, training, etc.)
- `data/`: Datasets (raw, interim, processed, external)
- `models/`: Model binaries (pytorch, onnx, tensorrt)
- `src/`: Source code modules (core, data, training, inference, api, plc, etc.)
- `tests/`: Unit, integration, e2e, and performance tests
- `monitoring/`: Grafana dashboards and alerts
- `deployment/`: Docker and edge deployment scripts
- `reports/`: Experiment and evaluation reports
- `docs/`: System documentation

## Current Development Status
**Module 1 — Project Foundation**

*(Dataset preparation and model development are planned for future modules.)*

## Local Setup
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Environment Setup
Copy `.env.example` to `.env` and adjust the variables as needed:
```bash
cp .env.example .env
```

## Testing Commands
Run the test suite:
```bash
pytest
```

## Code-Quality Commands
Run linters and formatters:
```bash
ruff check .
black --check .
mypy src
```

## Future Modules
- Module 2: Dataset Acquisition & Initial Dataset Validation
- Module 3: Annotation Preparation & Augmentation
- Module 4: YOLOv8 Training & Evaluation
- Module 5: ONNX/TensorRT Export & Inference
- Module 6: FastAPI & PLC Integration
- Module 7: Monitoring & Deployment
