import argparse
import sys
import yaml
import os
import json
import logging
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.inference.model_exporter import ModelExporter
from src.inference.onnx_inference import ONNXInferenceWrapper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_tensorrt_availability() -> bool:
    try:
        import tensorrt
        return True
    except ImportError:
        return False

def verify_numerical_equivalence(pt_model_path: str, onnx_model_path: str, test_img_path: str) -> bool:
    logger.info("Starting numerical equivalence verification...")
    
    # 1. Run PyTorch
    pt_model = YOLO(pt_model_path)
    # Using float32 for deterministic comparison
    pt_results = pt_model.predict(source=test_img_path, verbose=False)[0]
    
    pt_boxes = []
    if pt_results.boxes is not None:
        pt_boxes = pt_results.boxes.xyxy.cpu().numpy()
        
    # 2. Run ONNX Native via Ultralytics (which wraps ORT and handles post-processing equivalently)
    onnx_model = YOLO(onnx_model_path)
    onnx_results = onnx_model.predict(source=test_img_path, verbose=False)[0]
    
    onnx_boxes = []
    if onnx_results.boxes is not None:
        onnx_boxes = onnx_results.boxes.xyxy.cpu().numpy()
        
    # 3. Compare shapes
    if len(pt_boxes) != len(onnx_boxes):
        logger.warning(f"Detection count mismatch! PT: {len(pt_boxes)}, ONNX: {len(onnx_boxes)}")
        return False
        
    if len(pt_boxes) == 0:
        logger.info("No detections found in either model. Skipping bounding box value comparison.")
        return True

    # 4. Compare box coordinates with tolerance
    # Float32 can have minor precision differences, use np.allclose with atol=1.0 pixel
    is_close = np.allclose(pt_boxes, onnx_boxes, atol=1.0)
    if is_close:
        logger.info("Numerical equivalence verified successfully!")
        return True
    else:
        logger.warning("Bounding boxes are not numerically equivalent!")
        # Print differences
        diff = np.abs(pt_boxes - onnx_boxes)
        logger.warning(f"Max difference: {np.max(diff)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX.")
    parser.add_argument("--config", type=str, default="configs/inference/export.yaml",
                        help="Path to export config file")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    model_path = config['model_path']
    onnx_output_dir = config['onnx_output_dir']
    
    # Export
    exporter = ModelExporter(model_path)
    onnx_path = exporter.export_onnx(
        output_dir=onnx_output_dir,
        imgsz=tuple(config.get('image_size', (200, 200))),
        opset=config.get('opset', 12),
        dynamic=config.get('dynamic', False),
        simplify=config.get('simplify', True)
    )
    
    export_success = onnx_path is not None and os.path.exists(onnx_path)
    
    trt_available = check_tensorrt_availability()
    if not trt_available:
        logger.warning("TensorRT is unavailable in current environment.")
        
    numerical_valid = False
    
    if export_success:
        # Find a test image
        img_dir = config.get('benchmark', {}).get('test_image', 'data/processed/yolo/test/images/')
        test_img = None
        if os.path.exists(img_dir) and os.path.isdir(img_dir):
            for f in os.listdir(img_dir):
                if f.endswith(('.jpg', '.png', '.jpeg')):
                    test_img = os.path.join(img_dir, f)
                    break
                    
        if test_img:
            numerical_valid = verify_numerical_equivalence(model_path, onnx_path, test_img)
        else:
            logger.warning("No test image found for numerical verification.")
    
    # Save export report
    report_dir = "reports/benchmarks"
    os.makedirs(report_dir, exist_ok=True)
    
    report = {
        "pytorch_model": model_path,
        "onnx_model": onnx_path if export_success else None,
        "tensorrt_model": None, # Future module/when supported
        "export_status": "Success" if export_success else "Failed",
        "tensorrt_available": trt_available,
        "numerical_equivalence": numerical_valid,
        "configuration": config
    }
    
    with open(os.path.join(report_dir, "export_report.json"), "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Export report saved to {report_dir}/export_report.json")

if __name__ == "__main__":
    main()
