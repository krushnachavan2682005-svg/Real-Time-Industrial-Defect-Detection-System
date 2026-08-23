import os
import glob
import logging
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from src.augmentation.pipeline import AugmentationPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_yolo_labels(label_path: str):
    bboxes = []
    class_labels = []
    if os.path.exists(label_path):
        with open(label_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_labels.append(int(parts[0]))
                    bboxes.append([float(x) for x in parts[1:5]])
    return bboxes, class_labels

def draw_yolo_boxes(image: np.ndarray, bboxes: list, class_labels: list, names: dict = None):
    img = image.copy()
    h, w = img.shape[:2]
    
    for bbox, label in zip(bboxes, class_labels):
        x_c, y_c, bw, bh = bbox
        
        # Convert YOLO to pixel coordinates
        x_c_p, y_c_p = int(x_c * w), int(y_c * h)
        bw_p, bh_p = int(bw * w), int(bh * h)
        
        x_min = int(x_c_p - bw_p / 2.0)
        y_min = int(y_c_p - bh_p / 2.0)
        x_max = int(x_c_p + bw_p / 2.0)
        y_max = int(y_c_p + bh_p / 2.0)
        
        # Clamp to image size just in case
        x_min = max(0, min(w, x_min))
        y_min = max(0, min(h, y_min))
        x_max = max(0, min(w, x_max))
        y_max = max(0, min(h, y_max))
        
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        
        # Class label text
        name = names.get(label, str(label)) if names else str(label)
        cv2.putText(img, name, (x_min, max(0, y_min - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
    return img

def main():
    config_path = "configs/augmentation/train.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Config not found at {config_path}")
        return

    # Use classes config to map names
    import yaml
    classes_path = "configs/data/classes.yaml"
    names = {}
    if os.path.exists(classes_path):
        with open(classes_path, "r") as f:
            classes_config = yaml.safe_load(f)
            names = {v: k for k, v in classes_config.items()}

    pipeline = AugmentationPipeline(config_path)

    image_dir = "data/processed/yolo/train/images"
    label_dir = "data/processed/yolo/train/labels"
    output_dir = "reports/dataset_validation/augmentation"
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    image_files = glob.glob(os.path.join(image_dir, "*.jpg"))
    if not image_files:
        logger.warning(f"No images found in {image_dir}")
        return
        
    # Sample a few images deterministically
    image_files = sorted(image_files)[:5]
    
    for img_path in image_files:
        base_name = os.path.basename(img_path)
        name_no_ext = os.path.splitext(base_name)[0]
        label_path = os.path.join(label_dir, name_no_ext + ".txt")
        
        img = cv2.imread(img_path)
        if img is None:
            logger.warning(f"Could not read {img_path}")
            continue
            
        # Convert BGR to RGB for matplotlib
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        bboxes, class_labels = load_yolo_labels(label_path)
        
        # Apply augmentation
        aug_img, aug_bboxes, aug_labels = pipeline(img_rgb, bboxes, class_labels)
        
        # Draw boxes
        orig_drawn = draw_yolo_boxes(img_rgb, bboxes, class_labels, names)
        aug_drawn = draw_yolo_boxes(aug_img, aug_bboxes, aug_labels, names)
        
        # Plot side by side
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        axes[0].imshow(orig_drawn)
        axes[0].set_title(f"Original: {base_name}")
        axes[0].axis('off')
        
        axes[1].imshow(aug_drawn)
        axes[1].set_title(f"Augmented: {base_name}")
        axes[1].axis('off')
        
        out_path = os.path.join(output_dir, f"aug_cmp_{base_name}")
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close(fig)
        logger.info(f"Saved visualization to {out_path}")

if __name__ == "__main__":
    main()
