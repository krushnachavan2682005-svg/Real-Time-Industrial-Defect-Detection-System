import csv
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ultralytics import YOLO

from src.training.trainer import (
    get_device,
    load_yaml,
    move_checkpoints,
    save_experiment_report,
    setup_experiment_dir,
)

logger = logging.getLogger(__name__)

class ExperimentRunner:
    def __init__(
        self,
        base_config_path: str = "configs/training/train.yaml",
        tuning_config_path: str = "configs/tuning/experiments.yaml",
        base_hyp_path: str = "configs/training/hyp.yaml",
        project_dir: str = "reports/experiments",
        model_dir: str = "models/pytorch"
    ):
        self.base_config = load_yaml(base_config_path)
        self.tuning_config = load_yaml(tuning_config_path)
        self.base_hyp = load_yaml(base_hyp_path) if os.path.exists(base_hyp_path) else {}
        self.project_dir = Path(project_dir)
        self.model_dir = Path(model_dir)
        self.registry_path = self.project_dir / "experiment_registry.csv"
        self.comparison_path = self.project_dir / "tuning_comparison.csv"

        self._init_registry()

    def _init_registry(self):
        self.project_dir.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            with open(self.registry_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "experiment_id", "date", "hypothesis", "model", "changed_parameters",
                    "seed", "epochs", "image_size", "batch_size",
                    "mAP50", "mAP50_95", "precision", "recall", "status", "training_time_s"
                ])

    def validate_test_set_isolation(self, dataset_config_path: str):
        if not os.path.exists(dataset_config_path):
            raise FileNotFoundError(f"Dataset config {dataset_config_path} not found.")
        dataset = load_yaml(dataset_config_path)
        val_path = str(dataset.get("val", "")).lower()
        if "test" in val_path:
            raise ValueError(f"Test set leakage detected! Validation set is pointing to test path: {val_path}")

    def run_all(self):
        experiments = self.tuning_config.get("experiments", [])
        for exp in experiments:
            self.run_experiment(exp)
        self.generate_comparison_report()

    def run_single(self, experiment_id: str):
        experiments = self.tuning_config.get("experiments", [])
        exp = next((e for e in experiments if e["id"] == experiment_id), None)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found in tuning config.")
        self.run_experiment(exp)
        self.generate_comparison_report()

    def run_experiment(self, exp: Dict[str, Any]):
        exp_id = exp["id"]
        logger.info(f"=== Starting Experiment: {exp_id} ===")

        # Merge configs
        config = self.base_config.copy()
        hyp = self.base_hyp.copy()
        changed_params = {}

        for k, v in exp.items():
            if k in ["id", "hypothesis"]:
                continue
            # Some params go to config, some to hyp (kwargs for YOLO)
            if k in config or k in ["epochs", "batch_size", "image_size"]:
                config[k] = v
            else:
                hyp[k] = v
            changed_params[k] = v

        config["experiment_name"] = exp_id

        # Validate isolation
        try:
            self.validate_test_set_isolation(config.get("dataset_config", ""))
        except ValueError as e:
            logger.error(str(e))
            self._record_failure(exp, str(e))
            return

        device = get_device(config.get("device", ""))
        config["device"] = device

        exp_dir = setup_experiment_dir(str(self.project_dir), exp_id)

        model_name = config.get("model", "yolov8n.pt")
        try:
            model = YOLO(model_name)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            self._record_failure(exp, str(e))
            return

        start_time = time.time()
        try:
            results = model.train(
                data=config.get("dataset_config"),
                epochs=config.get("epochs"),
                batch=config.get("batch_size"),
                imgsz=config.get("image_size"),
                device=device,
                project=str(exp_dir),
                name="run",
                exist_ok=True,
                **hyp
            )
            training_time = time.time() - start_time

            # Save artifacts
            move_checkpoints(
                ultralytics_project=exp_dir,
                ultralytics_name="run",
                target_dir=str(self.model_dir),
                experiment_name=exp_id
            )
            save_experiment_report(config, hyp, results, exp_dir, str(self.model_dir))

            self._record_success(exp, config, results, training_time)
            logger.info(f"Experiment {exp_id} completed successfully.")

        except Exception as e:
            logger.error(f"Experiment {exp_id} failed: {e}")
            self._record_failure(exp, str(e))

    def _record_success(self, exp: Dict[str, Any], config: Dict[str, Any], results: Any, training_time: float):
        metrics_dict = {}
        try:
            if hasattr(results, "results_dict"):
                metrics_dict = results.results_dict
            elif hasattr(results, "metrics") and hasattr(results.metrics, "results_dict"):
                metrics_dict = results.metrics.results_dict
        except Exception:
            pass

        # Extract values
        mAP50 = metrics_dict.get("metrics/mAP50(B)", 0.0)
        mAP50_95 = metrics_dict.get("metrics/mAP50-95(B)", 0.0)
        precision = metrics_dict.get("metrics/precision(B)", 0.0)
        recall = metrics_dict.get("metrics/recall(B)", 0.0)

        changed = {k: v for k, v in exp.items() if k not in ["id", "hypothesis"]}

        with open(self.registry_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                exp["id"],
                datetime.now().isoformat(),
                exp.get("hypothesis", ""),
                config.get("model", ""),
                json.dumps(changed),
                config.get("seed", 42),
                config.get("epochs", 50),
                config.get("image_size", 200),
                config.get("batch_size", 16),
                mAP50,
                mAP50_95,
                precision,
                recall,
                "success",
                training_time
            ])

    def _record_failure(self, exp: Dict[str, Any], error_msg: str):
        changed = {k: v for k, v in exp.items() if k not in ["id", "hypothesis"]}
        with open(self.registry_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                exp["id"],
                datetime.now().isoformat(),
                exp.get("hypothesis", ""),
                "",
                json.dumps(changed),
                "", "", "", "",
                "", "", "", "",
                f"failed: {error_msg}",
                0.0
            ])

    def generate_comparison_report(self):
        if not self.registry_path.exists():
            return

        # Also read baseline metrics
        baseline_summary_path = self.project_dir / "baseline_yolov8n" / "training_summary.json"
        rows = []

        if baseline_summary_path.exists():
            with open(baseline_summary_path, "r") as f:
                bs = json.load(f)
                metrics = bs.get("metrics", {})
                rows.append({
                    "Experiment": "baseline_yolov8n",
                    "Change": "None",
                    "mAP50": metrics.get("metrics/mAP50(B)", 0.0),
                    "mAP50-95": metrics.get("metrics/mAP50-95(B)", 0.0),
                    "Precision": metrics.get("metrics/precision(B)", 0.0),
                    "Recall": metrics.get("metrics/recall(B)", 0.0),
                    "Training Time": "N/A"
                })

        with open(self.registry_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "success" in row["status"].lower():
                    rows.append({
                        "Experiment": row["experiment_id"],
                        "Change": row["changed_parameters"],
                        "mAP50": row["mAP50"],
                        "mAP50-95": row["mAP50_95"],
                        "Precision": row["precision"],
                        "Recall": row["recall"],
                        "Training Time": row["training_time_s"]
                    })

        if rows:
            with open(self.comparison_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Experiment", "Change", "mAP50", "mAP50-95", "Precision", "Recall", "Training Time"])
                writer.writeheader()
                writer.writerows(rows)
            logger.info(f"Comparison report generated at {self.comparison_path}")
