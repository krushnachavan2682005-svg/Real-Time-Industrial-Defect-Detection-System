# Real-Time Industrial Defect Detection System

## 1. Executive Summary

This project is an automated visual inspection system for manufacturing lines. In simple terms, it acts as a "smart camera" that watches products moving on a conveyor belt and automatically identifies if a product is damaged or defective.

In manufacturing, detecting defects is extremely important because sending a damaged product to a customer damages the brand and creates waste. Our system uses advanced computer vision to take pictures of the products, instantly detect any defects like scratches or cracks, and make an automated decision to pass or reject the item. The final outcome is a fully functional web dashboard where factory operators can see the live inspections, combined with a simulated industrial controller (PLC) that can physically separate the bad products from the good ones.

---

## 2. Problem Statement

In traditional manufacturing, quality control relies heavily on manual inspection. Human workers look at products as they move down the line. However, manual inspection has several major limitations:
- **Human fatigue:** People get tired and lose focus over time.
- **Slow inspection:** Humans can only inspect so many items per minute, slowing down production.
- **Inconsistent decisions:** What one person considers a "pass," another might consider a "reject."
- **Manufacturing waste:** If defects are not caught early, defective products might reach customers or require expensive rework.

Computer vision helps solve this problem by using a trained AI model to inspect products consistently at high speeds without ever getting tired, ensuring that only high-quality products leave the factory.

---

## 3. Project Objectives

The main objectives of this project are:
- Detect surface defects automatically using a machine learning model.
- Classify the specific types of defects on the surface.
- Process images very quickly (in real-time).
- Make automated PASS / REVIEW / REJECT business decisions.
- Provide spatial defect information (where exactly the defect is located).
- Expose the entire inspection pipeline through a fast web API.
- Store the history of inspections in a database.
- Monitor system performance and health.
- Provide a secure frontend dashboard for operators.
- Prepare the system for deployment in an industrial environment using Docker.

---

## 4. Dataset

The system is trained to recognize defects from a specialized industrial surface defect dataset. The dataset focuses on detecting various anomalies that happen during manufacturing.

The dataset includes 6 distinct defect classes:
1. **Crazing:** Fine, hairline cracks on the surface.
2. **Inclusion:** Foreign materials or impurities pressed into the surface.
3. **Patches:** Irregular, localized discolored areas or raised spots.
4. **Pitted Surface:** Small holes or craters in the material.
5. **Rolled-in Scale:** Scale or oxides that have been rolled into the metal surface.
6. **Scratches:** Linear marks or cuts on the surface.

Before any training could occur, the dataset went through a validation process. Dataset validation is performed to ensure that images are not corrupted, that bounding box annotations match the image sizes, and that class distributions are understood. This guarantees the model learns from high-quality data.

---

## 5. Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core backend programming language |
| PyTorch | Deep learning framework for original model |
| Ultralytics YOLOv8 | Object detection model architecture |
| OpenCV | Image processing and frame capture |
| ONNX | Portable model representation |
| ONNX Runtime | High-speed model inference engine |
| FastAPI | High-performance backend API framework |
| SQLAlchemy | Database persistence and Object-Relational Mapping (ORM) |
| React | Frontend UI library |
| TypeScript | Strongly typed language for frontend |
| Vite | Fast frontend build tool |
| Zustand | Frontend global state management |
| TanStack Query | Frontend server state and API data fetching |
| Axios | HTTP client for the frontend |
| Prometheus | Metrics and performance monitoring |
| Grafana | Dashboard visualization for metrics |
| Docker | Containerization for deployment |
| PyTest | Automated testing framework |
| Ruff / Black / MyPy | Code quality, linting, formatting, and typing |

---

## 6. Complete System Architecture

```text
User
  ↓
React Frontend (Dashboard)
  ↓
FastAPI Backend (API Layer)
  ↓
Authentication / RBAC (Security Layer)
  ↓
Inspection Service (Core Logic)
  ↓
ONNX Inference (YOLO Model Execution)
  ↓
Postprocessing (NMS, Confidence Filtering)
  ↓
Coordinate Transformation (Bounding Box to Image Scale)
  ↓
Decision Engine (Pass/Review/Reject Logic)
  ↓
Defect Mapping (Spatial Location)
  ↓
PLC Integration (Simulated Conveyor Control)
  ↓
Database Persistence (Save History)
  ↓
Analytics / Monitoring (Prometheus & Grafana)
```

**Major Layers Explained:**
- **Frontend Layer:** What the user sees and clicks on (React).
- **Security Layer:** Ensures only logged-in users with the right roles can access the system.
- **API Layer:** Receives the image and orchestrates the entire process (FastAPI).
- **Inference Layer:** The brain of the operation that detects the defects (ONNX Runtime).
- **Decision & Mapping Layer:** Applies business rules to the defects to decide if the product is good or bad, and figures out exactly where the defects are.
- **Hardware Integration Layer:** Tells the factory machines (PLCs) what to do.
- **Data Layer:** Saves the results to a database for future analysis.

---

## 7. Machine Learning Pipeline

The ML pipeline operates step-by-step to go from a raw image to final defects:

1. **Image Input:** The camera or API provides a raw image frame.
2. **Preprocessing:** The image is resized and formatted so the AI model can read it.
3. **YOLOv8 Model:** The image is passed into the YOLO object detection model.
4. **Object Detection:** The model predicts where defects are and what type they are.
5. **Confidence Filtering:** Predictions that the model is not very sure about (low confidence) are thrown away.
6. **Non-Maximum Suppression (NMS):** If the model predicts overlapping boxes for the same defect, it merges them into one clean box.
7. **Coordinate Transformation:** The AI's mathematical box coordinates are converted back into standard image pixels.
8. **Final Detections:** The pipeline outputs the clean list of defects.

---

## 8. Model Training

The system utilizes an Ultralytics YOLOv8 object detection model. YOLO (You Only Look Once) was chosen because it is incredibly fast and highly accurate, which is strictly required for moving conveyor belts. 

The model was trained on the 6-class dataset using standard image augmentation techniques (like flipping and brightness adjustments) to ensure the model generalizes well to different lighting conditions in the factory. 

---

## 9. Model Optimization and ONNX Conversion

Running standard PyTorch models in production is often too slow and heavy. To solve this, we used ONNX (Open Neural Network Exchange).

PyTorch Model → Export → ONNX Model → ONNX Runtime → Faster Deployment Inference

**Why ONNX?** ONNX provides a standardized, optimized format. By running the `.onnx` file using ONNX Runtime, we decouple the model from the heavy PyTorch library, resulting in massive CPU speedups.

Currently, the system uses ONNX Runtime. For future NVIDIA edge devices, TensorRT is available as a hardware-specific optimization option. If TensorRT fails to load, the system has a built-in safety net that falls back to the ONNX CPU Execution Provider.

---

## 10. Real-Time Vision Pipeline

Camera/Image → Frame Capture → Preprocessing → ONNX Inference → Postprocessing → Coordinate Transformation

In the real-time pipeline, performance is everything. The system uses a **headless mode**, which means it processes the images entirely in memory without opening visible graphical windows, saving compute power. 

When benchmarking the real-time pipeline, the system performs **warmup iterations** (running the model a few times without measuring) to wake up the CPU/GPU cache, followed by **benchmark iterations** to accurately measure the steady-state performance.

---

## 11. Decision Engine

The model only finds defects. The Decision Engine is the business layer that decides what to do about them.

Detections → Detection Filtering → Defect Aggregation → Severity Assessment → Decision Policy → PASS / REVIEW / REJECT

- **Confidence Thresholds:** Minimum confidence required to trust a defect.
- **Severity & Critical Defects:** A small scratch might just trigger a REVIEW, but a large Crazing defect will instantly trigger a REJECT.
- **Multiple Defect Escalation:** If a product has too many minor defects, it is automatically escalated to a REJECT.

Separating the ML detection from business decisions is critical because factory managers change their quality standards (e.g., "allow small scratches today") without us needing to retrain the AI model.

---

## 12. Defect Mapping and Visualization

Once defects are found, we need to know exactly where they are on the product.

The system calculates the area of the bounding box and maps its coordinates to a 3x3 spatial grid:

| TOP_LEFT | TOP_CENTER | TOP_RIGHT |
|---|---|---|
| **CENTER_LEFT** | **CENTER** | **CENTER_RIGHT** |
| **BOTTOM_LEFT** | **BOTTOM_CENTER** | **BOTTOM_RIGHT** |

Spatial information is highly useful in manufacturing. If defects consistently appear in the `TOP_LEFT`, it tells the mechanical engineers that a specific machine part is probably scraping the product on that side. The system then creates annotated images outlining the defects for operators to see.

---

## 13. PLC / Industrial Integration

A PLC (Programmable Logic Controller) is the industrial computer that controls factory machines, like conveyor belts and robotic arms.

Inspection Result → PLC Service → Command Mapper → PLC Command → Base PLC Client → Simulation PLC Client

The system translates the decision into a physical action:
- **PASS** → Command the conveyor to continue.
- **REVIEW** → Command the system to route the product to a manual inspection station.
- **REJECT** → Command the pneumatic kicker arm to reject the product off the line.

The current implementation utilizes a safe **Simulation PLC Client** for testing. Because of the clean abstraction architecture, real Modbus or OPC-UA integration can be added later without changing any of the higher-level application logic.

---

## 14. FastAPI Backend

The FastAPI backend serves as the high-speed bridge between the user interface and the AI model.

**Important Endpoints:**
- `GET /health` (System health check)
- `POST /api/v1/inspect` (Upload image and get inspection result)
- `GET /api/v1/inspections` (Historical data)
- `/metrics` (Prometheus monitoring)

**Inspection Request Flow:**
Frontend Image Upload → FastAPI → Image Validation → ONNX Inference → Decision Engine → Defect Mapping → PLC Command → Database Persistence → JSON Response

---

## 15. Monitoring and Observability

A machine learning system in production must be monitored to ensure it doesn't slow down or fail silently. 
The system exposes metrics for **Prometheus**, which are visualized in **Grafana**.

We track:
- HTTP request counts and API latency.
- Model inference latency (how fast the AI is).
- Pipeline latency (how fast the whole backend is).
- Defect distributions (how many of each defect type).
- PLC success/failure rates.

Monitoring is vital because if the AI inference latency suddenly spikes from 20ms to 500ms, the conveyor belt might drop products.

---

## 16. Database Persistence and Audit Trail

Inspection results are persisted using SQLAlchemy ORM to create an immutable audit log.

Inspection Record (Timestamp, Decision, Latency, PLC Status)
  ↓
Defect Records (Type, Severity, Bounding Box coordinates, Spatial Region)

This persistence is transaction-safe. We store this data so that if a customer complains about a defective product they received, the factory can look up the exact timestamp and image to prove the product was in good condition when it passed the camera.

---

## 17. Analytics and Inspection Intelligence

Because we persist data in the database, we can provide valuable analytics to the manufacturing team.

This includes calculating the pass rate, reject rate, and defect distribution over time. Historical data helps the factory identify negative trends (e.g., a sudden spike in Scratches) and triggers quality alerts so mechanical engineers can fix the factory machinery before more products are ruined.

---

## 18. Authentication and RBAC Security

Industrial systems require strict security. The backend uses JWT (JSON Web Tokens) Authentication.

User Login → Verify Credentials → Issue JWT Token → Access Protected API endpoints

**Role-Based Access Control (RBAC):**
- **ADMIN:** Full system control.
- **ENGINEER:** Can configure model settings and view detailed analytics.
- **OPERATOR:** Can run inspections on the floor.
- **VIEWER:** Read-only access to dashboards.

Different users require different permissions to prevent an untrained operator from accidentally deleting historical data or changing critical quality thresholds.

---

## 19. Frontend Dashboard

The user interacts with a modern React (Vite) frontend application. 

**User Workflow:**
1. User opens the web application.
2. User logs in with secure credentials.
3. A JWT token is stored securely for authentication.
4. User navigates to the Inspection Dashboard.
5. User uploads a product image.
6. User clicks "Run Inspection".
7. The image is sent to the FastAPI backend via Axios.
8. The ONNX model processes the image rapidly.
9. The Decision Engine generates a PASS/REJECT result.
10. The result and JSON payload return to the frontend.
11. The dashboard visually overlays the bounding boxes, spatial regions, and decision on the image.

---

## 20. End-to-End System Flow

The complete journey of the project:

Dataset → Training → YOLOv8 Model → ONNX Conversion → FastAPI Inference → Decision Engine → Defect Mapping → PLC Integration → Database → Analytics → React Dashboard → Monitoring

**The Journey:** We took raw images of industrial defects, trained a YOLOv8 computer vision model, and optimized it using ONNX for speed. We wrapped that fast model in a FastAPI backend, added a business logic Decision Engine, and mapped spatial coordinates. We then integrated a simulated PLC to control factory machines, saved the audit trail to a Database, and exposed it all securely to a React Dashboard while monitoring system health with Prometheus.

---

## 21. Testing Strategy

The system is rigorously tested across multiple levels to guarantee reliability:
- **Unit Testing:** Tests individual functions (like coordinate mapping math).
- **Integration Testing:** Tests that the database, API, and model work together.
- **API Testing:** Ensures all endpoints return correct status codes.
- **Performance Testing:** Evaluates the speed of the ONNX inference.

Multiple levels of testing ensure that a small code change doesn't break the mission-critical real-time pipeline.

---

## 22. Performance Results

Performance is strictly benchmarked using a monotonic high-resolution timer across 100 iterations (with 10 warmup iterations).

| Metric | PyTorch (Original) | ONNX Runtime (Optimized) | System End-to-End API |
|---|---|---|---|
| **Mean Latency** | 134.2 ms | 22.4 ms | 22.85 ms |
| **Median Latency**| 111.8 ms | 20.2 ms | 22.80 ms |
| **p95 Latency** | 240.1 ms | 33.4 ms | 26.02 ms |
| **p99 Latency** | 511.5 ms | 49.6 ms | 27.62 ms |
| **FPS / Throughput** | 7.4 FPS | 44.6 FPS | 43.7 requests/sec |

*Note: The ONNX Optimization resulted in a massive speedup (from 7 FPS to 44 FPS on CPU), proving the effectiveness of removing the PyTorch overhead.*

---

## 23. Production Readiness

The system is designed with production-grade patterns:
- **Docker configuration** for portable, isolated deployments.
- **Health checks** and API contracts.
- **Prometheus Monitoring** to track real-time stability.
- **Decoupled Architecture** where the model, database, and PLC can all be swapped without breaking the rest of the app.
- **RBAC Security** so unauthorized personnel cannot trigger factory commands.

While the software architecture is production-ready, it requires real industrial hardware validation before actual factory deployment.

---

## 24. Challenges and Solutions

| Problem | Root Cause | Solution |
|---|---|---|
| High PyTorch Latency | Loading the massive PyTorch library and graph at inference time was too slow for a real-time conveyor belt. | Exported the model to ONNX and used the lightweight ONNX Runtime C++ backend. |
| Inconsistent Decisions | A model might detect a defect with 60% confidence, confusing operators. | Created a deterministic Decision Engine to separate ML probability from hard business rules. |
| Hardware Dependency | Hardcoding CUDA/GPU logic would crash the system on CPU-only edge devices. | Built graceful degradation fallbacks into the Inference module to default to CPUExecutionProvider when needed. |

---

## 25. Current Limitations

- **Simulated PLC:** The current PLC client is a software simulation. Real physical actuators are not yet connected.
- **Hardware Validation:** While tested on CPU, physical deployment on an edge device (like an NVIDIA Jetson) has not yet been physically performed.
- **Live Camera Streaming:** The frontend currently accepts single image uploads rather than a continuous RTSP/WebSocket live video stream.

---

## 26. Future Improvements

Realistic next steps for the project:
- Integrate real Modbus or OPC-UA protocols for physical PLC communication.
- Deploy the system onto an NVIDIA Jetson Orin device.
- Utilize TensorRT execution provider for maximum GPU acceleration on edge devices.
- Implement WebSocket streaming for the React dashboard for a live video feed.
- Implement a data drift detection module to alert engineers when the factory camera lighting changes.

---

## 27. Project Achievements

We successfully transformed a standard object detection model into a complete industrial software solution. 

This project is far more than a simple Jupyter Notebook ML experiment. It combines Computer Vision, ONNX Optimization, deterministic Decision Logic, API engineering, Relational Databases, Security (JWT/RBAC), React UI design, and Prometheus Monitoring into a cohesive, production-ready system architecture.

---

## 28. Conclusion

This project evolved from a raw dataset of factory anomalies into an optimized computer vision pipeline capable of sub-25ms inference. By wrapping the AI inside a fast API, attaching a strict business rules engine, saving history to a database, and serving it securely to a modern web dashboard, we created a complete end-to-end industrial quality control system. 

The architecture proves that AI can be safely and effectively integrated into highly constrained manufacturing environments.

---

# Presentation Cheat Sheet

### 1. Explain the project in 30 seconds
"This is an automated quality control system for factories. It uses a YOLOv8 computer vision model to look at products on a conveyor belt, instantly detects surface defects like scratches or cracks, makes an automated decision to pass or reject the item, and simulates a command to a factory machine to sort it out."

### 2. Explain the architecture in 1 minute
"A React frontend takes the image and sends it to a FastAPI backend. The backend uses ONNX Runtime to run a YOLO AI model instantly. The AI finds the defects, and a Decision Engine applies business rules to decide if it's a PASS or REJECT. Finally, the system logs this to a Database, updates Prometheus metrics, and simulates a PLC command to the factory machine."

### 3. Why YOLOv8?
"YOLO stands for 'You Only Look Once'. It is state-of-the-art for object detection and provides the perfect balance between high accuracy and extremely fast real-time processing speeds."

### 4. Why ONNX Runtime?
"Standard PyTorch is too heavy and slow for production inference. Exporting to ONNX decouples the model from Python and runs in C++, which gave us a massive speed boost from 7 FPS up to 44 FPS on CPU."

### 5. Where does the model run?
"The model currently runs locally inside the FastAPI backend process using ONNX Runtime."

### 6. How does frontend communicate with backend?
"The React frontend uses the Axios library to make HTTP REST API calls to the FastAPI backend, securing every request with a JWT authorization header."

### 7. What happens after image upload?
"The image hits the API, is preprocessed, runs through the ONNX AI model, the Decision Engine calculates if it passes or fails, the data is saved to a SQL database, and the annotated image is sent back to the user."

### 8. How is PASS / REVIEW / REJECT decided?
"By the deterministic Decision Engine. It looks at the AI detections and applies hard business rules—like defect severity, confidence thresholds, and total defect counts—to make a final decision."

### 9. How does PLC integration work?
"We built an abstraction layer. Right now, it uses a Simulated PLC client that just logs the command. But because the architecture is decoupled, we can easily swap it for a real Modbus client later without breaking the app."

### 10. Why database is required?
"To maintain an immutable audit log. If a customer complains about a defective part next month, we need historical proof of the exact timestamp and inspection image showing it was good when it left our factory."

### 11. Why Prometheus and Grafana?
"To monitor system health. If the AI model starts taking 500ms instead of 20ms to process an image, we need an alert to trigger immediately before the conveyor belt drops uninspected products."

### 12. What are the biggest challenges?
"Getting the inference latency low enough for real-time was hard, which we solved with ONNX. Also, separating ML probability (60% confidence) from strict business logic (Pass/Fail) required building a custom Decision Engine."

### 13. What is currently simulated?
"The physical PLC machine communication is currently simulated in software."

### 14. What would you improve next?
"I would connect a real industrial Modbus PLC, deploy the system onto an NVIDIA Jetson edge device using TensorRT for GPU acceleration, and implement WebSockets for a live video feed on the frontend."
