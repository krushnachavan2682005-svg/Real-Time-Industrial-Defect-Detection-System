#!/usr/bin/env python3
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ultralytics import YOLO

from src.training.trainer import (
    get_device,
    load_yaml,
    move_checkpoints,
    save_experiment_report,
    setup_experiment_dir,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    # 1. Load Configurations
    config_path = "configs/training/train.yaml"
    hyp_path = "configs/training/hyp.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"Missing training config: {config_path}")
        sys.exit(1)
        
    config = load_yaml(config_path)
    hyp = load_yaml(hyp_path) if os.path.exists(hyp_path) else {}
    
    # 2. Extract configuration
    model_name = config.get("model", "yolov8n.pt")
    dataset_cfg = config.get("dataset_config", "configs/data/dataset.yaml")
    exp_name = config.get("experiment_name", "baseline_yolov8n")
    epochs = config.get("epochs", 50)
    batch = config.get("batch_size", 16)
    imgsz = config.get("image_size", 200)
    patience = config.get("patience", 10)
    workers = config.get("workers", 4)
    project_dir = config.get("project_dir", "reports/experiments")
    model_dir = config.get("model_dir", "models/pytorch")
    
    # 3. Setup Device and Experiment Directory
    device = get_device(config.get("device", ""))
    config["device"] = device  # Update config with actual device
    logger.info(f"Using device: {device}")
    
    exp_dir = setup_experiment_dir(project_dir, exp_name)
    logger.info(f"Experiment directory created at: {exp_dir}")
    
    # 4. Load YOLO Model
    logger.info(f"Loading YOLO model: {model_name}")
    try:
        model = YOLO(model_name)
    except Exception as e:
        logger.error(f"Failed to load YOLO model {model_name}: {e}")
        sys.exit(1)
        
    # 5. Execute Training
    logger.info("Starting training...")
    try:
        # We pass hyp as kwargs. Ultralytics takes augmentation parameters as kwargs to train()
        results = model.train(
            data=dataset_cfg,
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            device=device,
            patience=patience,
            workers=workers,
            project=str(exp_dir),
            name="run",
            exist_ok=True,
            **hyp  # Unpack our module 5 intended augmentations
        )
        logger.info("Training completed successfully.")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)
        
    # 6. Save Experiment Information
    logger.info("Saving experiment report and moving checkpoints...")
    try:
        # YOLO saves to project/name/weights (e.g., reports/experiments/baseline_yolov8n/run/weights)
        move_checkpoints(
            ultralytics_project=exp_dir,
            ultralytics_name="run",
            target_dir=model_dir,
            experiment_name=exp_name
        )
        save_experiment_report(config, hyp, results, exp_dir, model_dir)
    except Exception as e:
        logger.error(f"Failed to save artifacts: {e}")
        sys.exit(1)
        
    logger.info(f"Experiment {exp_name} finished. Best model at {os.path.join(model_dir, exp_name, 'best.pt')}")


if __name__ == "__main__":
    main()
