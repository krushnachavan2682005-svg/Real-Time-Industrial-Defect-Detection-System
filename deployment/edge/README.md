# Edge Deployment Strategy

This document outlines the deployment strategy for edge devices in industrial environments.

## Current Deployment: CPU Edge

The current containerization strategy targets standard CPU-based edge devices using **ONNX Runtime CPUExecutionProvider**.

**Deployment Path:**
1. Train model on Development Machine.
2. Export to optimized ONNX artifact (`best.onnx`).
3. Deploy ONNX artifact alongside the Docker image to the Edge Device.
4. Run via Docker Compose (using standard x86 or ARM CPU).

This provides a highly portable, easy-to-manage deployment suitable for most initial production rollouts where latency requirements are met by standard CPUs.

## Future Deployment: NVIDIA Edge (Jetson / TensorRT)

For higher frame rates and lower latency, future deployments will target NVIDIA Edge devices (e.g., Jetson Orin) using TensorRT.

**Important Considerations for TensorRT:**
- **Target Device Build**: TensorRT engines (`.engine` or `.trt` files) should generally be built *on the target device* (or a device with the exact same GPU architecture). Building a TensorRT engine on a development machine and copying it to a Jetson device often fails due to architecture mismatches.
- **Model Artifact Portability**: The ONNX model (`best.onnx`) serves as the universal intermediate format. You copy the ONNX model to the edge device, and the edge device (or its initialization script) converts it to a TensorRT engine on first run.

## Hardware & Mounting Considerations

- **Camera Device Mounting**: When deploying the Docker container, ensure the camera device (e.g., `/dev/video0`) is correctly passed through to the container using the `devices` configuration in `docker-compose.yml`.
- **USB Passthrough**: For industrial USB cameras, ensure udev rules on the host allow the Docker daemon to access the hardware.
