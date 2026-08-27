import os
import json
import csv
from typing import Dict, Any
from ultralytics import YOLO
import shutil

class ModelEvaluator:
    def __init__(self, model_path: str, dataset_yaml: str):
        self.model_path = model_path
        self.dataset_yaml = dataset_yaml
        self.model = YOLO(self.model_path)
        
    def evaluate(self, split: str, output_dir: str, conf_threshold: float = 0.25, iou_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate the model on a specific split (val or test).
        Returns a dictionary of metrics and saves reports to output_dir.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Run YOLO validation
        # Ultralytics val() uses the 'val' split by default. 
        # To evaluate on test, we pass split='test'.
        # We set save_json=True to get detailed predictions if needed, and plots=True for confusion matrix.
        metrics = self.model.val(
            data=self.dataset_yaml,
            split=split,
            conf=conf_threshold,
            iou=iou_threshold,
            plots=True,
            save_json=True,
            project=output_dir,
            name=split, # Creates a subdirectory named 'val' or 'test'
            exist_ok=True
        )
        
        run_dir = os.path.join(output_dir, split)
        
        # Extract global metrics
        global_metrics = {
            "model": self.model_path,
            "split": split,
            "mAP50": float(metrics.box.map50),
            "mAP50-95": float(metrics.box.map),
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
            "fitness": float(metrics.box.fitness()),
            "conf_threshold": conf_threshold,
            "iou_threshold": iou_threshold
        }
        
        # Save evaluation summary
        summary_path = os.path.join(output_dir, f"{split}_evaluation_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(global_metrics, f, indent=4)
            
        # Extract class-wise metrics
        class_names = self.model.names
        class_metrics = []
        
        # metric.box gives arrays for class-wise precision, recall, map50, map
        # But we need to make sure we map the correct class index
        ap_class_index = metrics.box.ap_class_index
        for i, class_idx in enumerate(ap_class_index):
            class_name = class_names[class_idx]
            class_metrics.append({
                "class_id": int(class_idx),
                "class_name": class_name,
                "precision": float(metrics.box.p[i]),
                "recall": float(metrics.box.r[i]),
                "mAP50": float(metrics.box.ap50[i]),
                "mAP50-95": float(metrics.box.ap[i])
            })
            
        # Save class metrics to CSV
        csv_path = os.path.join(output_dir, f"{split}_class_metrics.csv")
        if class_metrics:
            keys = class_metrics[0].keys()
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(class_metrics)
                
        # Copy confusion matrix to root output dir for easier access
        cm_src = os.path.join(run_dir, "confusion_matrix.png")
        if os.path.exists(cm_src):
            shutil.copy(cm_src, os.path.join(output_dir, f"{split}_confusion_matrix.png"))
            
        return {
            "global_metrics": global_metrics,
            "class_metrics": class_metrics,
            "run_dir": run_dir
        }
