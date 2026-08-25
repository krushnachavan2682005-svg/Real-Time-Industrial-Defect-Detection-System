import os
import shutil
from pathlib import Path

from src.training.trainer import (
    get_device,
    load_yaml,
    save_yaml,
    setup_experiment_dir,
)


def test_get_device_explicit():
    assert get_device("cpu") == "cpu"
    assert get_device("cuda:0") == "cuda:0"


def test_get_device_auto(monkeypatch):
    import torch
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    assert get_device("") == "0"
    
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert get_device("") == "cpu"


def test_setup_experiment_dir(tmp_path):
    project_dir = str(tmp_path / "experiments")
    exp_name = "test_exp"
    
    exp_dir = setup_experiment_dir(project_dir, exp_name)
    assert exp_dir.exists()
    assert exp_dir.is_dir()
    assert exp_dir.name == "test_exp"


def test_yaml_load_save(tmp_path):
    test_data = {"epochs": 10, "model": "yolov8n.pt"}
    filepath = tmp_path / "test.yaml"
    
    save_yaml(test_data, filepath)
    assert filepath.exists()
    
    loaded_data = load_yaml(str(filepath))
    assert loaded_data == test_data
