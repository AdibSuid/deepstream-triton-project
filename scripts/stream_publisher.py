#!/usr/bin/env python3
"""Publish video stream to RTSP server"""

import cv2
import subprocess
import sys
import argparse

def publish_rtsp_stream(video_source, rtsp_url="rtsp://localhost:8554/stream1", loop=False):
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"ERROR: Could not open video source: {video_source}")
        return False
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    
    print(f"Video properties: {width}x{height} @ {fps}fps")
    print(f"Publishing to: {rtsp_url}")
    print(f"Loop: {loop}")
    
    command = [
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24', '-s', f'{width}x{height}', '-r', str(fps),
        '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast', '-tune', 'zerolatency',
        '-f', 'rtsp', rtsp_url
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                if loop:
                    print("Restarting video...")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("End of video")
                    break
            
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"Published {frame_count} frames...")
            
            try:
                process.stdin.write(frame.tobytes())
            except BrokenPipeError:
                print("ERROR: FFmpeg process terminated")
                break
            
            cv2.imshow('Publishing Stream (Press Q to quit)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested quit")
                break
                
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        process.stdin.close()
        process.wait()
        print(f"Total frames published: {frame_count}")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish video to RTSP server')
    parser.add_argument('source', help='Video file path or camera index (0 for webcam)')
    parser.add_argument('--url', default='rtsp://localhost:8554/stream1', 
                       help='RTSP URL to publish to')
    parser.add_argument('--loop', action='store_true', 
                       help='Loop video indefinitely')
    
    args = parser.parse_args()
    
    # Try to convert to int for camera index
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    success = publish_rtsp_stream(video_source, args.url, args.loop)
    sys.exit(0 if success else 1)