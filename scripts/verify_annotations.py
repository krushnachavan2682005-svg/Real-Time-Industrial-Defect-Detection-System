import sys
import logging
from pathlib import Path
import random
import cv2
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def draw_yolo_boxes(image_path: Path, label_path: Path, output_path: Path, class_names: dict):
    img = cv2.imread(str(image_path))
    if img is None:
        logger.error(f"Failed to read image: {image_path}")
        return
        
    img_h, img_w = img.shape[:2]
    
    if label_path.exists():
        with open(label_path, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
                
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # Convert normalized back to absolute
            abs_width = int(width * img_w)
            abs_height = int(height * img_h)
            abs_x_center = int(x_center * img_w)
            abs_y_center = int(y_center * img_h)
            
            xmin = int(abs_x_center - abs_width / 2)
            ymin = int(abs_y_center - abs_height / 2)
            xmax = int(abs_x_center + abs_width / 2)
            ymax = int(abs_y_center + abs_height / 2)
            
            # Find class name
            class_name = "unknown"
            for name, cid in class_names.items():
                if cid == class_id:
                    class_name = name
                    break
                    
            color = (0, 255, 0) # Green box
            
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(img, class_name, (max(0, xmin), max(10, ymin - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
    cv2.imwrite(str(output_path), img)
    logger.info(f"Saved verification image to {output_path}")

def main():
    project_root = Path(__file__).resolve().parents[1]
    raw_images_dir = project_root / "data" / "raw" / "neu_dataset" / "NEU-DET" / "train" / "images"
    yolo_labels_dir = project_root / "data" / "processed" / "yolo" / "labels" / "train"
    output_dir = project_root / "reports" / "dataset_validation" / "annotations"
    classes_path = project_root / "configs" / "data" / "classes.yaml"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(classes_path, "r") as f:
        class_names = yaml.safe_load(f)
        
    images = list(raw_images_dir.rglob("*.jpg"))
    if not images:
        logger.error(f"No images found in {raw_images_dir}")
        return
        
    random.seed(42)
    sample_images = random.sample(images, min(20, len(images)))
    
    for img_path in sample_images:
        label_path = yolo_labels_dir / f"{img_path.stem}.txt"
        out_path = output_dir / f"verified_{img_path.name}"
        draw_yolo_boxes(img_path, label_path, out_path, class_names)
        
if __name__ == "__main__":
    main()
