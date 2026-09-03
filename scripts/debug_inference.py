import sys
import yaml
import cv2
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.inference.onnx_inference import ONNXInferenceWrapper
from src.vision.postprocess import Postprocessor
from src.vision.coordinate_transform import CoordinateTransformer
from src.decision.decision_engine import DecisionEngine

def test_api_pipeline(image_path: str):
    print("=== API Pipeline Test ===")
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image")
        return
        
    orig_h, orig_w = img.shape[:2]
    print(f"Original image shape: {img.shape}")
    
    with open("configs/inference/realtime.yaml", "r") as f:
        inference_config = yaml.safe_load(f)
        
    model_path = inference_config.get("inference", {}).get("model_path", "models/onnx/best.onnx")
    imgsz = tuple(inference_config.get("inference", {}).get("image_size", [224, 224]))
    
    inference_engine = ONNXInferenceWrapper(model_path)
    inference_engine.imgsz = imgsz
    print(f"ONNX Input Size (W, H): {inference_engine.imgsz}")
    
    classes = inference_config.get("classes", {})
    class_map = {int(k): str(v) for k, v in classes.items()}
    conf_thresh = inference_config.get("inference", {}).get("confidence_threshold", 0.25)
    iou_thresh = inference_config.get("inference", {}).get("iou_threshold", 0.50)
    
    postprocessor = Postprocessor(class_map, conf_thresh, iou_thresh)
    decision_engine = DecisionEngine("configs/decision/decision_rules.yaml")
    
    # 1. Inference
    raw_output = inference_engine.predict(img)
    print(f"Raw ONNX output shape: {raw_output.shape}")
    
    # 2. Postprocess
    detections_model_space = postprocessor.process(raw_output)
    print(f"Detections after NMS (Model Space): {len(detections_model_space)}")
    
    # 3. Transform
    coord_transformer = CoordinateTransformer((orig_w, orig_h), inference_engine.imgsz)
    detections_orig_space = []
    for det in detections_model_space:
        x1, y1, x2, y2 = coord_transformer.transform(det.x1, det.y1, det.x2, det.y2)
        det.x1, det.y1, det.x2, det.y2 = x1, y1, x2, y2
        detections_orig_space.append(det)
        
    print(f"Detections after Transform (Original Space): {len(detections_orig_space)}")
    if detections_orig_space:
        print(f"Sample detection: {detections_orig_space[0]}")
    
    # 4. Decision Engine
    decision_result = decision_engine.evaluate(detections_orig_space)
    print(f"Final Decision: {decision_result.decision.name}")
    print(f"Final Defects Count: {decision_result.total_defects}")

def test_standalone_pipeline(image_path: str):
    print("\n=== Standalone Predict Script Equivalent ===")
    from ultralytics import YOLO
    model = YOLO("models/pytorch/baseline_yolov8n/best.pt")
    results = model.predict(source=image_path, conf=0.25, verbose=False)
    for result in results:
        boxes = result.boxes
        print(f"Standalone Detections found: {len(boxes)}")
        for box in boxes:
            conf = box.conf[0].item()
            cls_name = model.names[int(box.cls[0].item())]
            print(f"Standalone found: {cls_name} ({conf:.2f})")

if __name__ == "__main__":
    test_api_pipeline("test_image.jpg")
    test_standalone_pipeline("test_image.jpg")
