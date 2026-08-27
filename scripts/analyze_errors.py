import argparse
import sys
import yaml
import os
import json
import cv2
from pathlib import Path
from typing import List, Dict, Any
from ultralytics import YOLO

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.evaluation.error_analyzer import ErrorAnalyzer

def load_ground_truths(label_path: str, img_width: int, img_height: int) -> List[Dict[str, Any]]:
    """Load YOLO format labels and convert to [x1, y1, x2, y2]."""
    gts = []
    if not os.path.exists(label_path):
        return gts
        
    with open(label_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])
            
            # Convert normalized xywh to absolute xyxy
            x1 = (x_center - w / 2) * img_width
            y1 = (y_center - h / 2) * img_height
            x2 = (x_center + w / 2) * img_width
            y2 = (y_center + h / 2) * img_height
            
            gts.append({
                'class_id': class_id,
                'bbox': [x1, y1, x2, y2]
            })
            
    return gts

def draw_error_sample(img_path: str, predictions: List[Dict], ground_truths: List[Dict], 
                      class_names: Dict[int, str], save_path: str):
    """Draw GT and Pred boxes and save the image."""
    img = cv2.imread(img_path)
    if img is None:
        return
        
    # Draw GTs in green
    for gt in ground_truths:
        box = [int(v) for v in gt['bbox']]
        cls_name = class_names[gt['class_id']]
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        cv2.putText(img, f"GT: {cls_name}", (box[0], box[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    # Draw Predictions in red
    for pred in predictions:
        box = [int(v) for v in pred['bbox']]
        cls_name = class_names[pred['class_id']]
        conf = pred.get('confidence', 0.0)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
        cv2.putText(img, f"Pred: {cls_name} {conf:.2f}", (box[0], max(0, box[3]+15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
    cv2.imwrite(save_path, img)

def main():
    parser = argparse.ArgumentParser(description="Run error analysis on a specific split.")
    parser.add_argument("--split", type=str, choices=["val", "test"], required=True, 
                        help="Dataset split to evaluate on (val or test)")
    parser.add_argument("--config", type=str, default="configs/evaluation/evaluation.yaml",
                        help="Path to evaluation config file")
    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    print(f"Starting error analysis on '{args.split}' split using model '{config['model_path']}'")
    
    model = YOLO(config['model_path'])
    class_names = model.names
    
    analyzer = ErrorAnalyzer(iou_threshold=config.get('iou_threshold', 0.50))
    conf_threshold = config.get('confidence_threshold', 0.25)
    
    # Setup directories
    images_dir = f"data/processed/yolo/{args.split}/images"
    labels_dir = f"data/processed/yolo/{args.split}/labels"
    out_dir = os.path.join(config['error_analysis_dir'], args.split)
    
    categories = ['background_fp', 'wrong_class_fp', 'localization_fp', 'duplicate_fp', 'false_negatives']
    for cat in categories:
        os.makedirs(os.path.join(out_dir, cat), exist_ok=True)
        
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    summary = {
        "model": config['model_path'],
        "split": args.split,
        "iou_threshold": config.get('iou_threshold', 0.50),
        "confidence_threshold": conf_threshold,
        "total_images": len(image_files),
        "total_ground_truths": 0,
        "total_predictions": 0,
        "true_positives": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "error_categories": {cat: 0 for cat in categories}
    }
    
    max_samples = config.get('max_visual_samples_per_class', 10)
    samples_saved = {cat: 0 for cat in categories}
    
    print(f"Analyzing {len(image_files)} images...")
    
    for img_file in image_files:
        img_path = os.path.join(images_dir, img_file)
        label_path = os.path.join(labels_dir, img_file.rsplit('.', 1)[0] + '.txt')
        
        # Inference
        results = model.predict(source=img_path, conf=conf_threshold, verbose=False)[0]
        
        img_height, img_width = results.orig_shape
        
        # Load predictions
        predictions = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                predictions.append({
                    'class_id': cls,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })
                
        # Load GT
        gts = load_ground_truths(label_path, img_width, img_height)
        
        summary["total_predictions"] += len(predictions)
        summary["total_ground_truths"] += len(gts)
        
        # Analyze
        analysis = analyzer.analyze_image(predictions, gts)
        
        summary["true_positives"] += len(analysis['true_positives'])
        summary["false_positives"] += len(analysis['false_positives'])
        summary["false_negatives"] += len(analysis['false_negatives'])
        
        # Save samples
        saved_for_this_img = False
        
        for fp in analysis['false_positives']:
            cat = fp['error_type']
            summary["error_categories"][cat] += 1
            if samples_saved[cat] < max_samples and not saved_for_this_img:
                save_path = os.path.join(out_dir, cat, img_file)
                draw_error_sample(img_path, predictions, gts, class_names, save_path)
                samples_saved[cat] += 1
                saved_for_this_img = True
                
        if len(analysis['false_negatives']) > 0 and not saved_for_this_img:
            summary["error_categories"]["false_negatives"] += len(analysis['false_negatives'])
            if samples_saved["false_negatives"] < max_samples:
                save_path = os.path.join(out_dir, "false_negatives", img_file)
                draw_error_sample(img_path, predictions, gts, class_names, save_path)
                samples_saved["false_negatives"] += 1
                saved_for_this_img = True

    # Save summary
    summary_path = os.path.join(config['error_analysis_dir'], f"{args.split}_error_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
        
    print(f"\nError Analysis Summary:")
    print(f"  TP: {summary['true_positives']}")
    print(f"  FP: {summary['false_positives']}")
    print(f"  FN: {summary['false_negatives']}")
    print(f"Categories:")
    for cat, count in summary["error_categories"].items():
        print(f"  {cat}: {count}")
    print(f"\nDetailed summary saved to {summary_path}")

if __name__ == "__main__":
    main()
