import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict

import torch
import yaml
from ultralytics import YOLO

logger = logging.getLogger(__name__)


def setup_experiment_dir(project_dir: str, experiment_name: str) -> Path:
    """Creates the experiment directory under reports/experiments."""
    exp_dir = Path(project_dir) / experiment_name
    if exp_dir.exists():
        logger.warning(f"Experiment directory {exp_dir} already exists. Removing it to start fresh.")
        shutil.rmtree(exp_dir)
    exp_dir.mkdir(parents=True, exist_ok=True)
    return exp_dir


def get_device(requested_device: str = "") -> str:
    """Returns 'cuda' or 'cuda:X' or 'cpu'."""
    if requested_device:
        return requested_device
    if torch.cuda.is_available():
        return "0"  # default to first GPU
    return "cpu"


def load_yaml(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], filepath: Path) -> None:
    with open(filepath, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def save_experiment_report(
    config: Dict[str, Any],
    hyp: Dict[str, Any],
    results: Any,
    exp_dir: Path,
    model_dir: str,
) -> None:
    """Parses training results and saves a summary report."""
    
    # Extract metrics from Ultralytics Results object (it varies by version, usually model.metrics)
    metrics_dict = {}
    class_metrics = {}
    
    try:
        if hasattr(results, "results_dict"):
            metrics_dict = results.results_dict
        elif hasattr(results, "metrics"):
             if hasattr(results.metrics, "results_dict"):
                 metrics_dict = results.metrics.results_dict
    except Exception as e:
         logger.warning(f"Could not parse top-level metrics: {e}")

    try:
        # Extract class-wise metrics if available
        if hasattr(results, "metrics") and hasattr(results.metrics, "keys"):
            for i, c in enumerate(results.metrics.keys):
                 class_metrics[c] = {
                     "mAP50": float(results.metrics.box.map50[i]) if hasattr(results.metrics, "box") else 0.0,
                     "mAP50-95": float(results.metrics.box.map[i]) if hasattr(results.metrics, "box") else 0.0
                 }
    except Exception as e:
         logger.warning(f"Could not parse class-wise metrics: {e}")

    summary = {
        "experiment_name": config.get("experiment_name"),
        "model": config.get("model"),
        "dataset": config.get("dataset_config"),
        "device": config.get("device"),
        "epochs": config.get("epochs"),
        "batch_size": config.get("batch_size"),
        "image_size": config.get("image_size"),
        "seed": config.get("seed"),
        "metrics": metrics_dict,
        "class_metrics": class_metrics,
        "best_checkpoint": os.path.join(model_dir, config.get("experiment_name", "exp"), "best.pt"),
        "pytorch_version": torch.__version__,
    }

    with open(exp_dir / "training_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    logger.info(f"Experiment summary saved to {exp_dir / 'training_summary.json'}")


def move_checkpoints(ultralytics_project: Path, ultralytics_name: str, target_dir: str, experiment_name: str) -> None:
    """Moves best.pt and last.pt from ultralytics runs/ to our models/ directory."""
    src_dir = ultralytics_project / ultralytics_name / "weights"
    dst_dir = Path(target_dir) / experiment_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    best_src = src_dir / "best.pt"
    last_src = src_dir / "last.pt"
    
    if best_src.exists():
        shutil.copy(best_src, dst_dir / "best.pt")
        logger.info(f"Saved best checkpoint to {dst_dir / 'best.pt'}")
        
    if last_src.exists():
        shutil.copy(last_src, dst_dir / "last.pt")
        logger.info(f"Saved last checkpoint to {dst_dir / 'last.pt'}")
