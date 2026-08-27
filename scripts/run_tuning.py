#!/usr/bin/env python3
import argparse
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.training.experiment_runner import ExperimentRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Hyperparameter Tuning Experiments")
    parser.add_argument("--experiment", type=str, help="Specific experiment ID to run (e.g., exp_01_lr)")
    parser.add_argument("--all", action="store_true", help="Run all experiments in tuning config")

    args = parser.parse_args()

    if not args.experiment and not args.all:
        logger.error("Must specify either --experiment <id> or --all")
        sys.exit(1)

    try:
        runner = ExperimentRunner(
            base_config_path="configs/training/train.yaml",
            tuning_config_path="configs/tuning/experiments.yaml",
            base_hyp_path="configs/training/hyp.yaml",
            project_dir="reports/experiments",
            model_dir="models/pytorch"
        )

        if args.experiment:
            runner.run_single(args.experiment)
        elif args.all:
            runner.run_all()

    except Exception as e:
        logger.error(f"Tuning script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
