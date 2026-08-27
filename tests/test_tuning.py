import os
import tempfile

import pytest
import yaml

from src.training.experiment_runner import ExperimentRunner


@pytest.fixture
def dummy_project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.fixture
def dummy_configs(dummy_project_dir):
    base_config = {"experiment_name": "base", "epochs": 5, "dataset_config": os.path.join(dummy_project_dir, "dataset.yaml")}
    tuning_config = {
        "experiments": [
            {"id": "exp_01", "epochs": 10},
            {"id": "exp_02", "lr0": 0.001}
        ]
    }
    base_hyp = {"lr0": 0.01}

    # Write dataset config safe
    dataset_safe = {"train": "train/images", "val": "val/images", "test": "test/images"}
    dataset_unsafe = {"train": "train/images", "val": "test/images"}

    base_path = os.path.join(dummy_project_dir, "train.yaml")
    tuning_path = os.path.join(dummy_project_dir, "experiments.yaml")
    hyp_path = os.path.join(dummy_project_dir, "hyp.yaml")
    dataset_safe_path = os.path.join(dummy_project_dir, "dataset.yaml")
    dataset_unsafe_path = os.path.join(dummy_project_dir, "dataset_unsafe.yaml")

    with open(base_path, "w") as f: yaml.dump(base_config, f)
    with open(tuning_path, "w") as f: yaml.dump(tuning_config, f)
    with open(hyp_path, "w") as f: yaml.dump(base_hyp, f)
    with open(dataset_safe_path, "w") as f: yaml.dump(dataset_safe, f)
    with open(dataset_unsafe_path, "w") as f: yaml.dump(dataset_unsafe, f)

    return {
        "base": base_path,
        "tuning": tuning_path,
        "hyp": hyp_path,
        "dataset_safe": dataset_safe_path,
        "dataset_unsafe": dataset_unsafe_path
    }

def test_experiment_registry_init(dummy_project_dir, dummy_configs):
    runner = ExperimentRunner(
        dummy_configs["base"],
        dummy_configs["tuning"],
        dummy_configs["hyp"],
        dummy_project_dir,
        os.path.join(dummy_project_dir, "models")
    )
    assert os.path.exists(runner.registry_path)
    with open(runner.registry_path, "r") as f:
        header = f.readline().strip().split(",")
        assert "experiment_id" in header
        assert "mAP50" in header

def test_test_set_isolation_safe(dummy_project_dir, dummy_configs):
    runner = ExperimentRunner(
        dummy_configs["base"],
        dummy_configs["tuning"],
        dummy_configs["hyp"],
        dummy_project_dir,
        os.path.join(dummy_project_dir, "models")
    )
    # Should not raise exception
    runner.validate_test_set_isolation(dummy_configs["dataset_safe"])

def test_test_set_isolation_unsafe(dummy_project_dir, dummy_configs):
    runner = ExperimentRunner(
        dummy_configs["base"],
        dummy_configs["tuning"],
        dummy_configs["hyp"],
        dummy_project_dir,
        os.path.join(dummy_project_dir, "models")
    )
    with pytest.raises(ValueError, match="Test set leakage detected"):
        runner.validate_test_set_isolation(dummy_configs["dataset_unsafe"])
