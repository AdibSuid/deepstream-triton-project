#!/usr/bin/env python3
"""
Monitor DeepStream detections via MQTT and trigger WebRTC stream during motion.
"""
import paho.mqtt.client as mqtt
import json
import time
from utils.motion_webrtc_trigger import is_motion_detected, trigger_webrtc_stream

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "deepstream-detections"
MOTION_THRESHOLD = 1  # Minimum detections to consider as motion
MOTION_TIMEOUT = 5    # Seconds to keep WebRTC enabled after last motion

last_motion_time = 0
webrtc_enabled = False

def on_message(client, userdata, msg):
    global last_motion_time, webrtc_enabled
    try:
        payload = json.loads(msg.payload.decode())
        # Assume payload contains a 'detections' list
        detections = payload.get('detections', [])
        if is_motion_detected(detections, threshold=MOTION_THRESHOLD):
            last_motion_time = time.time()
            if not webrtc_enabled:
                trigger_webrtc_stream(True)
                webrtc_enabled = True
        else:
            # If no motion, check if timeout expired
            if webrtc_enabled and (time.time() - last_motion_time > MOTION_TIMEOUT):
                trigger_webrtc_stream(False)
                webrtc_enabled = False
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting motion monitor...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
