import logging
from typing import Any, Dict

import cv2

from src.inference.onnx_inference import ONNXInferenceWrapper
from src.vision.camera import Camera, CameraReadError
from src.vision.coordinate_transform import CoordinateTransformer
from src.vision.performance import PerformanceMonitor
from src.vision.postprocess import Postprocessor
from src.vision.visualizer import Visualizer

logger = logging.getLogger(__name__)


class RealTimePipeline:
    """Orchestrates the entire real-time vision inference pipeline."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 1. Setup Camera
        source_type = config.get("source", {}).get("type", "camera")
        if source_type == "camera":
            source = config.get("source", {}).get("id", 0)
        else:
            source = config.get("source", {}).get("path", "")

        self.camera = Camera(source)
        self.camera.open()
        self.orig_w, self.orig_h = self.camera.get_resolution()

        # 2. Setup Inference
        model_path = config.get("inference", {}).get("model_path", "")
        self.inference_engine = ONNXInferenceWrapper(model_path)
        # Assuming inference_engine uses the same image size for both width and height from config
        self.imgsz = tuple(config.get("inference", {}).get("image_size", [224, 224]))

        # Override inference engine target size for safe direct resizing matching training
        self.inference_engine.imgsz = self.imgsz

        # 3. Setup Coordinate Transformer
        self.coord_transformer = CoordinateTransformer(
            (self.orig_w, self.orig_h), self.imgsz
        )

        # 4. Setup Postprocessor
        classes = config.get("classes", {})
        # Ensure keys are ints
        class_map = {int(k): str(v) for k, v in classes.items()}
        conf_thresh = config.get("inference", {}).get("confidence_threshold", 0.25)
        iou_thresh = config.get("inference", {}).get("iou_threshold", 0.50)
        self.postprocessor = Postprocessor(class_map, conf_thresh, iou_thresh)

        # 5. Setup Visualization
        self.headless = config.get("display", {}).get("headless", False)
        self.visualizer = Visualizer(display_metrics=True)

        # 6. Setup Performance Tracking
        warmup = config.get("display", {}).get("warmup_frames", 20)
        self.performance = PerformanceMonitor(warmup_frames=warmup)

        # Setup Headless Image Benchmark repetitions
        if self.headless and self.camera._is_image:
            # Default to 100 measured iterations if not specified
            benchmark_iters = config.get("inference", {}).get(
                "benchmark_iterations", 100
            )
            self.camera.repeat_count = warmup + benchmark_iters

        # Target FPS for video playback pacing
        self.target_fps = config.get("display", {}).get("target_fps", 30)
        self.delay_ms = int(1000 / self.target_fps) if self.target_fps > 0 else 1

    def process_frame(self) -> bool:
        """
        Processes a single frame.
        Returns True if successful, False if the stream ended or failed.
        """
        try:
            self.performance.start_frame()

            # 1. Capture
            frame = self.camera.read()
            if frame is None:
                return False

            # 2. Preprocess & Inference
            self.performance.start_inference()
            raw_output = self.inference_engine.predict(frame)
            self.performance.end_inference()

            # 3. Postprocess
            detections_model_space = self.postprocessor.process(raw_output)

            # 4. Map Coordinates
            detections_orig_space = []
            for det in detections_model_space:
                x1, y1, x2, y2 = self.coord_transformer.transform(
                    det.x1, det.y1, det.x2, det.y2
                )
                det.x1, det.y1, det.x2, det.y2 = x1, y1, x2, y2
                detections_orig_space.append(det)

            # 5. Visualize
            if not self.headless:
                fps = self.performance.get_fps()
                inf_ms = self.performance.get_avg_inference_latency()
                e2e_ms = self.performance.get_avg_e2e_latency()

                annotated_frame = self.visualizer.draw_detections(
                    frame, detections_orig_space
                )
                annotated_frame = self.visualizer.draw_metrics(
                    annotated_frame, inf_ms, e2e_ms, fps
                )

                cv2.imshow("Real-Time Defect Detection", annotated_frame)

                # Check for exit (q key)
                if cv2.waitKey(self.delay_ms) & 0xFF == ord("q"):
                    return False

            self.performance.end_frame()
            return True

        except CameraReadError as e:
            logger.error(f"Camera read error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in pipeline: {e}")
            return False

    def run(self):
        """Runs the continuous loop until interrupted or stream ends."""
        logger.info("Starting real-time pipeline...")
        try:
            while True:
                if not self.process_frame():
                    break
        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Releases resources."""
        self.camera.release()
        if not self.headless:
            cv2.destroyAllWindows()
        logger.info("Real-time pipeline shut down cleanly.")
