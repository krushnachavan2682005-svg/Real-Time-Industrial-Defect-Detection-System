import os
import yaml
import logging
import json
import hashlib
import shutil
from pathlib import Path
from tqdm import tqdm
from src.data.dataset_splitter import DatasetSplitter
from src.data.leakage_checker import LeakageChecker

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def compute_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def main():
    project_root = Path(__file__).resolve().parent.parent
    
    # Load config
    split_config_path = project_root / "configs" / "data" / "split.yaml"
    with open(split_config_path, "r") as f:
        config = yaml.safe_load(f)
        
    seed = config.get("seed", 42)
    train_ratio = config.get("train_ratio", 0.7)
    val_ratio = config.get("val_ratio", 0.15)
    test_ratio = config.get("test_ratio", 0.15)
    
    raw_dir = project_root / "data" / "raw" / "neu_dataset" / "NEU-DET"
    yolo_dir = project_root / "data" / "processed" / "yolo"
    yolo_split_dir = project_root / "data" / "processed" / "yolo_split"
    
    logger.info(f"Gathering samples from {raw_dir} and {yolo_dir}...")
    samples = []
    
    label_dir = yolo_dir / "labels"
    
    if not raw_dir.exists() or not label_dir.exists():
        logger.error("Raw directory or label directory not found. Ensure previous modules were run.")
        return

    for split in ["train", "validation"]:
        split_img_dir = raw_dir / split / "images"
        split_lbl_dir = label_dir / split
        
        if not split_img_dir.exists():
            continue
            
        for class_dir in split_img_dir.iterdir():
            if not class_dir.is_dir():
                continue
                
            for img_path in class_dir.glob("*.jpg"):
                class_name = class_dir.name
                
                label_path = split_lbl_dir / (img_path.stem + ".txt")
                if not label_path.exists():
                    logger.warning(f"Label not found for {img_path}")
                    continue
                    
                samples.append({
                    "image_path": img_path,
                    "label_path": label_path,
                    "class_name": class_name,
                    "hash": compute_hash(img_path)
                })
            
    logger.info(f"Found {len(samples)} valid image-label pairs.")
    
    splitter = DatasetSplitter(seed=seed)
    logger.info(f"Splitting with ratios Train:{train_ratio}, Val:{val_ratio}, Test:{test_ratio}")
    splits = splitter.split(samples, train_ratio, val_ratio, test_ratio)
    
    logger.info("Verifying leakage before copying...")
    leakage_result = LeakageChecker.check_leakage(splits["train"], splits["val"], splits["test"])
    if not leakage_result["passed"]:
        logger.error("Leakage detected! Aborting.")
        return
        
    logger.info(f"Copying files to temporary {yolo_split_dir}...")
    if yolo_split_dir.exists():
        shutil.rmtree(yolo_split_dir)
        
    split_stats = {
        "total_images": len(samples),
        "seed": seed,
        "leakage_check": {"passed": True},
    }
    
    for split_name, split_samples in splits.items():
        out_img_dir = yolo_split_dir / split_name / "images"
        out_lbl_dir = yolo_split_dir / split_name / "labels"
        
        out_img_dir.mkdir(parents=True, exist_ok=True)
        out_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        class_dist = {}
        for s in tqdm(split_samples, desc=f"Copying {split_name}"):
            shutil.copy2(s["image_path"], out_img_dir / s["image_path"].name)
            shutil.copy2(s["label_path"], out_lbl_dir / s["label_path"].name)
            
            c = s["class_name"]
            class_dist[c] = class_dist.get(c, 0) + 1
            
        split_stats[split_name] = {
            "count": len(split_samples),
            "percentage": round(len(split_samples) / len(samples) * 100, 2) if samples else 0,
            "class_distribution": class_dist
        }
        
    logger.info(f"Replacing {yolo_dir} with new split structure...")
    shutil.rmtree(yolo_dir)
    yolo_split_dir.rename(yolo_dir)
    
    report_dir = project_root / "reports" / "dataset_validation"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "split_report.json"
    with open(report_path, "w") as f:
        json.dump(split_stats, f, indent=4)
        
    logger.info(f"Split complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
