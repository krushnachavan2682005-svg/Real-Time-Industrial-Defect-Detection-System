import pytest
from src.data.dataset_splitter import DatasetSplitter


def test_split_ratios():
    splitter = DatasetSplitter(seed=42)
    # Create 100 dummy samples across 2 classes
    samples = []
    for i in range(100):
        cls_name = "A" if i < 50 else "B"
        samples.append({"hash": f"h{i}", "class_name": cls_name, "data": i})

    splits = splitter.split(samples, 0.7, 0.15, 0.15)

    assert len(splits["train"]) == 70
    assert len(splits["val"]) == 15
    assert len(splits["test"]) == 15


def test_duplicate_grouping():
    splitter = DatasetSplitter(seed=42)
    # Duplicate samples with the same hash
    samples = [
        {"hash": "h1", "class_name": "A", "id": 1},
        {"hash": "h1", "class_name": "A", "id": 2},
        {"hash": "h2", "class_name": "B", "id": 3},
        {"hash": "h3", "class_name": "B", "id": 4},
        {"hash": "h4", "class_name": "A", "id": 5},
    ]

    splits = splitter.split(samples, 0.6, 0.4, 0.0)

    # Ensure both h1 items are in the same split
    h1_in_train = sum(1 for s in splits["train"] if s["hash"] == "h1")
    h1_in_val = sum(1 for s in splits["val"] if s["hash"] == "h1")
    h1_in_test = sum(1 for s in splits["test"] if s["hash"] == "h1")

    assert (h1_in_train == 2 and h1_in_val == 0 and h1_in_test == 0) or \
           (h1_in_train == 0 and h1_in_val == 2 and h1_in_test == 0)


def test_invalid_ratios():
    splitter = DatasetSplitter()
    samples = [{"hash": "h1", "class_name": "A"}]
    with pytest.raises(ValueError):
        splitter.split(samples, 0.5, 0.5, 0.5)


def test_empty_samples():
    splitter = DatasetSplitter()
    with pytest.raises(ValueError):
        splitter.split([], 0.7, 0.15, 0.15)
