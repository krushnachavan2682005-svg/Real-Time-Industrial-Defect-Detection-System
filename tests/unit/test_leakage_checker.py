from src.data.leakage_checker import LeakageChecker


def test_no_leakage():
    train = [{"hash": "h1"}, {"hash": "h2"}]
    val = [{"hash": "h3"}]
    test = [{"hash": "h4"}]

    result = LeakageChecker.check_leakage(train, val, test)
    assert result["passed"] is True
    assert result["overlap_count"] == 0
    assert len(result["overlaps"]["train_val"]) == 0
    assert len(result["overlaps"]["train_test"]) == 0
    assert len(result["overlaps"]["val_test"]) == 0


def test_leakage_detected_train_val():
    train = [{"hash": "h1"}, {"hash": "h2"}]
    val = [{"hash": "h1"}]
    test = [{"hash": "h3"}]

    result = LeakageChecker.check_leakage(train, val, test)
    assert result["passed"] is False
    assert result["overlap_count"] == 1
    assert "h1" in result["overlaps"]["train_val"]


def test_leakage_detected_multiple():
    train = [{"hash": "h1"}, {"hash": "h2"}]
    val = [{"hash": "h2"}, {"hash": "h3"}]
    test = [{"hash": "h1"}, {"hash": "h3"}]

    result = LeakageChecker.check_leakage(train, val, test)
    assert result["passed"] is False
    assert result["overlap_count"] == 3
    assert "h2" in result["overlaps"]["train_val"]
    assert "h1" in result["overlaps"]["train_test"]
    assert "h3" in result["overlaps"]["val_test"]


def test_empty_splits():
    train = [{"hash": "h1"}]
    result = LeakageChecker.check_leakage(train, [], [])
    assert result["passed"] is True
    assert result["overlap_count"] == 0
