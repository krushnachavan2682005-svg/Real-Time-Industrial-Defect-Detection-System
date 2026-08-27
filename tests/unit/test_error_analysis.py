import pytest
from src.evaluation.error_analyzer import calculate_iou, match_predictions_to_ground_truths, ErrorAnalyzer

def test_calculate_iou_exact_match():
    box1 = [0, 0, 10, 10]
    box2 = [0, 0, 10, 10]
    assert calculate_iou(box1, box2) == 1.0

def test_calculate_iou_no_overlap():
    box1 = [0, 0, 10, 10]
    box2 = [20, 20, 30, 30]
    assert calculate_iou(box1, box2) == 0.0

def test_calculate_iou_partial_overlap():
    box1 = [0, 0, 10, 10]
    box2 = [5, 5, 15, 15]
    # box1 area = 100
    # box2 area = 100
    # intersection = 25 (from 5,5 to 10,10)
    # union = 100 + 100 - 25 = 175
    # iou = 25 / 175 = 1 / 7 = 0.142857...
    assert pytest.approx(calculate_iou(box1, box2), 0.01) == 0.1428

def test_match_true_positive():
    preds = [{'bbox': [10, 10, 20, 20], 'class_id': 0, 'confidence': 0.9}]
    gts = [{'bbox': [10, 10, 20, 20], 'class_id': 0}]
    
    result = match_predictions_to_ground_truths(preds, gts, iou_threshold=0.5)
    assert len(result['true_positives']) == 1
    assert len(result['false_positives']) == 0
    assert len(result['false_negatives']) == 0

def test_match_false_positive_background():
    preds = [{'bbox': [50, 50, 60, 60], 'class_id': 0, 'confidence': 0.9}]
    gts = [{'bbox': [10, 10, 20, 20], 'class_id': 0}]
    
    result = match_predictions_to_ground_truths(preds, gts, iou_threshold=0.5)
    assert len(result['true_positives']) == 0
    assert len(result['false_positives']) == 1
    assert result['false_positives'][0]['error_type'] == 'background_fp'
    assert len(result['false_negatives']) == 1

def test_match_false_positive_wrong_class():
    preds = [{'bbox': [10, 10, 20, 20], 'class_id': 1, 'confidence': 0.9}]
    gts = [{'bbox': [10, 10, 20, 20], 'class_id': 0}]
    
    result = match_predictions_to_ground_truths(preds, gts, iou_threshold=0.5)
    assert len(result['true_positives']) == 0
    assert len(result['false_positives']) == 1
    assert result['false_positives'][0]['error_type'] == 'wrong_class_fp'
    assert len(result['false_negatives']) == 1

def test_match_false_positive_localization():
    preds = [{'bbox': [15, 15, 25, 25], 'class_id': 0, 'confidence': 0.9}] # IoU is < 0.5
    gts = [{'bbox': [10, 10, 20, 20], 'class_id': 0}]
    
    result = match_predictions_to_ground_truths(preds, gts, iou_threshold=0.5)
    assert len(result['true_positives']) == 0
    assert len(result['false_positives']) == 1
    assert result['false_positives'][0]['error_type'] == 'localization_fp'
    assert len(result['false_negatives']) == 1

def test_match_duplicate_predictions():
    preds = [
        {'bbox': [10, 10, 20, 20], 'class_id': 0, 'confidence': 0.9},
        {'bbox': [11, 11, 21, 21], 'class_id': 0, 'confidence': 0.8}
    ]
    gts = [{'bbox': [10, 10, 20, 20], 'class_id': 0}]
    
    result = match_predictions_to_ground_truths(preds, gts, iou_threshold=0.5)
    assert len(result['true_positives']) == 1
    assert len(result['false_positives']) == 1
    assert result['false_positives'][0]['error_type'] == 'duplicate_fp'
    assert len(result['false_negatives']) == 0
