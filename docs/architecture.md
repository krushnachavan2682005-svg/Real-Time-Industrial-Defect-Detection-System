# System Architecture

## High-Level Architecture (Planned)

```text
Camera
  ↓
OpenCV
  ↓
Preprocessing
  ↓
Inference Engine
  ↓
Decision Engine
  ↓
Coordinate Mapping
  ↓
FastAPI
  ↓
PLC
```

## Training Pipeline (Planned)

```text
Dataset
  ↓
Cleaning
  ↓
Annotation
  ↓
Augmentation
  ↓
YOLOv8
  ↓
Evaluation
  ↓
ONNX
  ↓
TensorRT
```

*Note: Currently, only the foundational project structure (Module 1) exists. The components illustrated above will be implemented in subsequent modules.*
