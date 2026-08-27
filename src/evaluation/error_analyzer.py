from typing import List, Dict, Any, Tuple
import numpy as np

def calculate_iou(box1: List[float], box2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    Boxes are expected in [x_min, y_min, x_max, y_max] format.
    """
    # Determine the coordinates of the intersection rectangle
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union_area = box1_area + box2_area - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area

def match_predictions_to_ground_truths(
    predictions: List[Dict[str, Any]], 
    ground_truths: List[Dict[str, Any]], 
    iou_threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Match predictions to ground truths to identify TP, FP, FN and error categories.
    
    predictions: List of dicts with 'bbox' [x1,y1,x2,y2], 'class_id', 'confidence'
    ground_truths: List of dicts with 'bbox' [x1,y1,x2,y2], 'class_id'
    
    Returns a dictionary summarizing true positives, false positives, false negatives,
    and specific error types (wrong class, localization error, duplicate).
    """
    
    # Sort predictions by confidence descending
    predictions = sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)
    
    matched_gt_indices = set()
    
    true_positives = []
    false_positives = [] # list of dicts with error_type
    
    for pred_idx, pred in enumerate(predictions):
        pred_box = pred['bbox']
        pred_class = pred['class_id']
        
        best_iou = 0.0
        best_gt_idx = -1
        best_gt_class = -1
        
        # Find best matching GT
        for gt_idx, gt in enumerate(ground_truths):
            gt_box = gt['bbox']
            iou = calculate_iou(pred_box, gt_box)
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = gt_idx
                best_gt_class = gt['class_id']
                
        # Categorize the prediction
        pred_result = pred.copy()
        pred_result['matched_gt_idx'] = best_gt_idx
        pred_result['iou'] = best_iou
        
        if best_gt_idx != -1:
            if best_gt_idx in matched_gt_indices:
                if best_iou >= iou_threshold:
                    # Duplicate detection (another prediction already claimed this GT)
                    pred_result['error_type'] = 'duplicate_fp'
                    false_positives.append(pred_result)
                else:
                    # Background FP since it doesn't overlap enough with ANY gt
                    pred_result['error_type'] = 'background_fp'
                    false_positives.append(pred_result)
            else:
                if best_iou >= iou_threshold:
                    if pred_class == best_gt_class:
                        # True Positive
                        true_positives.append(pred_result)
                        matched_gt_indices.add(best_gt_idx)
                    else:
                        # Misclassification (Wrong Class)
                        pred_result['error_type'] = 'wrong_class_fp'
                        pred_result['true_class_id'] = best_gt_class
                        false_positives.append(pred_result)
                else:
                    if pred_class == best_gt_class:
                        # Poor localization (IoU < threshold but correct class)
                        pred_result['error_type'] = 'localization_fp'
                        false_positives.append(pred_result)
                    else:
                        # Background FP
                        pred_result['error_type'] = 'background_fp'
                        false_positives.append(pred_result)
        else:
            # No GT matched at all
            pred_result['error_type'] = 'background_fp'
            false_positives.append(pred_result)

    # False negatives are GTs that were not matched by a TP
    false_negatives = []
    for gt_idx, gt in enumerate(ground_truths):
        if gt_idx not in matched_gt_indices:
            fn_result = gt.copy()
            # Try to find if there was a wrong_class or localization error for this GT
            related_fp = next((fp for fp in false_positives if fp.get('matched_gt_idx') == gt_idx), None)
            if related_fp:
                fn_result['related_fp_type'] = related_fp.get('error_type')
                fn_result['related_fp_conf'] = related_fp.get('confidence')
            else:
                fn_result['related_fp_type'] = 'none'
            
            false_negatives.append(fn_result)
            
    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }

class ErrorAnalyzer:
    def __init__(self, iou_threshold: float = 0.5):
        self.iou_threshold = iou_threshold
        
    def analyze_image(self, predictions: List[Dict[str, Any]], ground_truths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze errors for a single image.
        """
        return match_predictions_to_ground_truths(predictions, ground_truths, self.iou_threshold)
