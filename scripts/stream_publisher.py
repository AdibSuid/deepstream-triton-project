#!/usr/bin/env python3
"""Improved RTSP stream publisher"""

import cv2
import subprocess
import sys
import argparse
import time

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
    
    # More robust FFmpeg command
    command = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', f'{width}x{height}',
        '-r', str(fps),
        '-i', '-',  # Input from stdin
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-b:v', '2M',  # Bitrate
        '-bufsize', '2M',
        '-maxrate', '2M',
        '-g', str(fps * 2),  # GOP size
        '-f', 'rtsp',
        '-rtsp_transport', 'tcp',  # Use TCP instead of UDP
        rtsp_url
    ]
    
    print("\nStarting FFmpeg...")
    print(f"Command: {' '.join(command[:15])}...")
    
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8
    )
    
    frame_count = 0
    error_count = 0
    max_errors = 10
    
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
                process.stdin.flush()
                error_count = 0  # Reset error counter on success
            except (BrokenPipeError, OSError) as e:
                error_count += 1
                print(f"ERROR writing frame {frame_count}: {e}")
                
                if error_count >= max_errors:
                    print("Too many errors, stopping...")
                    break
                
                # Check if FFmpeg is still running
                if process.poll() is not None:
                    print("ERROR: FFmpeg process terminated")
                    print("\nFFmpeg stderr:")
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    print(stderr[-1000:])  # Last 1000 chars
                    break
                
                time.sleep(0.1)
                continue
            
            # Display local preview
            cv2.imshow('Publishing Stream (Press Q to quit)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested quit")
                break
                
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        if process.poll() is None:
            process.stdin.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print(f"\nTotal frames published: {frame_count}")
        
        # Print any errors
        if process.stderr:
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            if stderr:
                print("\nFFmpeg output:")
                print(stderr[-500:])  # Last 500 chars
    
    return frame_count > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish video to RTSP server')
    parser.add_argument('source', help='Video file path or camera index (0 for webcam)')
    parser.add_argument('--url', default='rtsp://localhost:8554/stream1', 
                       help='RTSP URL to publish to')
    parser.add_argument('--loop', action='store_true', 
                       help='Loop video indefinitely')
    
    args = parser.parse_args()
    
    # Validate RTSP URL format
    if not args.url.startswith('rtsp://'):
        print("ERROR: URL must start with rtsp://")
        sys.exit(1)
    
    # Check for common URL format mistakes
    if '/' in args.url.split('@')[0] and '@' not in args.url:
        print("WARNING: RTSP URL format might be incorrect")
        print("Correct format: rtsp://username:password@host:port/path")
        print(f"Your URL: {args.url}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Try to convert to int for camera index
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    success = publish_rtsp_stream(video_source, args.url, args.loop)
    sys.exit(0 if success else 1)