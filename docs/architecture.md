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
It processes standard `Detection` objects, applies configurable rules (confidence thresholds, class-specific policies, severity escalations) from `configs/decision/decision_rules.yaml`, and outputs a strongly-typed `DecisionResult` mapping defects to an industrial outcome (PASS / REVIEW / REJECT) with a human-readable reason.
