import logging
import json
import hashlib
from pathlib import Path
from src.data.leakage_checker import LeakageChecker

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def compute_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def load_samples(split_dir: Path):
    samples = []
    if not split_dir.exists():
        return samples
        
    img_dir = split_dir / "images"
    if not img_dir.exists():
        return samples
        
    for img_path in img_dir.glob("*.jpg"):
        samples.append({
            "image_path": str(img_path),
            "hash": compute_hash(img_path)
        })
    return samples

def main():
    project_root = Path(__file__).resolve().parent.parent
    yolo_dir = project_root / "data" / "processed" / "yolo"
    
    logger.info("Loading train samples...")
    train_samples = load_samples(yolo_dir / "train")
    
    logger.info("Loading val samples...")
    val_samples = load_samples(yolo_dir / "val")
    
    logger.info("Loading test samples...")
    test_samples = load_samples(yolo_dir / "test")
    
    logger.info("Running leakage check...")
    result = LeakageChecker.check_leakage(train_samples, val_samples, test_samples)
    
    report_path = project_root / "reports" / "dataset_validation" / "leakage_report.json"
    with open(report_path, "w") as f:
        json.dump(result, f, indent=4)
        
    if result["passed"]:
        logger.info("Leakage check PASSED. No overlaps found.")
    else:
        logger.error(f"Leakage check FAILED. Overlaps found: {result['overlap_count']}")
    
    logger.info(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
