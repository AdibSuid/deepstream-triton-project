#!/usr/bin/env python3
"""
Motion detection and WebRTC trigger for DeepStream pipeline.
"""
import time
import requests
from utils.parse_detections import parse_yolo_output, parse_detr_output

# Example: This function should be called after each inference frame
# detections: list of detection dicts from parse_yolo_output or parse_detr_output
# threshold: minimum number of detections to consider as motion

def is_motion_detected(detections, threshold=1):
    """Return True if motion is detected (at least threshold objects)."""
    return len(detections) >= threshold

# Example: Trigger WebRTC stream via MediaMTX API
# This is a stub; actual implementation may require MediaMTX API or config reload

def trigger_webrtc_stream(enable=True):
    """Enable or disable WebRTC stream in MediaMTX (stub)."""
    # Example: Use MediaMTX HTTP API to enable/disable stream
    # Replace with actual API endpoint and logic
    url = "http://localhost:8889/v3/paths/stream1/enable"
    try:
        if enable:
            requests.post(url, json={"enabled": True})
        else:
            requests.post(url, json={"enabled": False})
    except Exception as e:
        print(f"WebRTC trigger error: {e}")

# Example usage in DeepStream pipeline (pseudo-code):
# for each frame:
#     detections = parse_yolo_output(model_output)
#     if is_motion_detected(detections):
#         trigger_webrtc_stream(True)
#     else:
#         trigger_webrtc_stream(False)
