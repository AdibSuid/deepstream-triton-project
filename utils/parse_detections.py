#!/usr/bin/env python3
"""Parse YOLO and DETR detection outputs"""

import numpy as np
from typing import List, Tuple, Dict

def parse_yolo_output(output: np.ndarray, 
                     conf_threshold: float = 0.25,
                     iou_threshold: float = 0.45,
                     input_shape: Tuple[int, int] = (640, 640),
                     original_shape: Tuple[int, int] = None) -> List[Dict]:
    """
    Parse YOLO11 output format [1, 84, 8400]
    
    Returns:
        List of detection dicts with keys: x1, y1, x2, y2, confidence, class_id
    """
    
    # Transpose to [8400, 84]
    output = output[0].transpose()
    
    # Split into boxes and scores
    boxes = output[:, :4]  # [8400, 4] - x_center, y_center, w, h
    scores = output[:, 4:]  # [8400, 80] - class scores
    
    # Get max score and class for each detection
    class_ids = np.argmax(scores, axis=1)
    confidences = np.max(scores, axis=1)
    
    # Filter by confidence
    mask = confidences > conf_threshold
    boxes = boxes[mask]
    confidences = confidences[mask]
    class_ids = class_ids[mask]
    
    if len(boxes) == 0:
        return []
    
    # Convert from center format (x_c, y_c, w, h) to corner format (x1, y1, x2, y2)
    x_center, y_center, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    x1 = x_center - w / 2
    y1 = y_center - h / 2
    x2 = x_center + w / 2
    y2 = y_center + h / 2
    
    boxes = np.stack([x1, y1, x2, y2], axis=1)
    
    # Apply NMS
    indices = nms(boxes, confidences, iou_threshold)
    
    # Scale boxes to original image size if provided
    if original_shape is not None:
        scale_x = original_shape[1] / input_shape[1]
        scale_y = original_shape[0] / input_shape[0]
        boxes[:, [0, 2]] *= scale_x
        boxes[:, [1, 3]] *= scale_y
    
    # Create detection list
    detections = []
    for idx in indices:
        detections.append({
            'x1': float(boxes[idx, 0]),
            'y1': float(boxes[idx, 1]),
            'x2': float(boxes[idx, 2]),
            'y2': float(boxes[idx, 3]),
            'confidence': float(confidences[idx]),
            'class_id': int(class_ids[idx])
        })
    
    return detections

def parse_detr_output(output: np.ndarray,
                     conf_threshold: float = 0.25,
                     input_shape: Tuple[int, int] = (640, 640),
                     original_shape: Tuple[int, int] = None) -> List[Dict]:
    """
    Parse RF-DETR output format [1, 300, 6]
    Output format: [x1, y1, x2, y2, confidence, class_id]
    
    Returns:
        List of detection dicts
    """
    
    detections = []
    output = output[0]  # [300, 6]
    
    for det in output:
        confidence = det[4]
        
        if confidence < conf_threshold:
            continue
        
        x1, y1, x2, y2 = det[:4]
        class_id = int(det[5])
        
        # Scale boxes to original image size if provided
        if original_shape is not None:
            scale_x = original_shape[1] / input_shape[1]
            scale_y = original_shape[0] / input_shape[0]
            x1 *= scale_x
            x2 *= scale_x
            y1 *= scale_y
            y2 *= scale_y
        
        detections.append({
            'x1': float(x1),
            'y1': float(y1),
            'x2': float(x2),
            'y2': float(y2),
            'confidence': float(confidence),
            'class_id': class_id
        })
    
    return detections

def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> List[int]:
    """
    Non-Maximum Suppression
    
    Args:
        boxes: Array of shape [N, 4] with format [x1, y1, x2, y2]
        scores: Array of shape [N] with confidence scores
        iou_threshold: IoU threshold for suppression
    
    Returns:
        List of indices to keep
    """
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        
        # Compute IoU with remaining boxes
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        iou = inter / (areas[i] + areas[order[1:]] - inter)
        
        # Keep boxes with IoU less than threshold
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
    
    return keep

def draw_detections(image: np.ndarray, 
                   detections: List[Dict],
                   labels: List[str] = None,
                   color: Tuple[int, int, int] = (0, 255, 0),
                   thickness: int = 2) -> np.ndarray:
    """
    Draw bounding boxes on image
    
    Args:
        image: Input image (BGR format)
        detections: List of detection dicts
        labels: List of class labels
        color: BGR color tuple
        thickness: Line thickness
    
    Returns:
        Image with drawn boxes
    """
    import cv2
    
    result = image.copy()
    
    for det in detections:
        x1 = int(det['x1'])
        y1 = int(det['y1'])
        x2 = int(det['x2'])
        y2 = int(det['y2'])
        conf = det['confidence']
        class_id = det['class_id']
        
        # Draw box
        cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label
        label = f"{labels[class_id] if labels else class_id}: {conf:.2f}"
        
        # Calculate text size for background
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        
        # Draw background rectangle
        cv2.rectangle(
            result,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            result,
            label,
            (x1, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
    
    return result