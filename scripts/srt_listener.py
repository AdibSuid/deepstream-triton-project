#!/usr/bin/env python3
"""
SRT Listener - Receives encrypted SRT streams from edge agents
and republishes as RTSP for DeepStream consumption.

Usage:
    python srt_listener.py --port 9000 --passphrase YOUR_SECRET_PASS
"""

import subprocess
import argparse
import signal
import sys
import time
from pathlib import Path


class SRTListener:
    """Receives SRT streams and republishes as RTSP"""
    
    def __init__(self, srt_port=9000, passphrase="", rtsp_port=8554):
        self.srt_port = srt_port
        self.passphrase = passphrase
        self.rtsp_port = rtsp_port
        self.processes = {}
        self.running = True
        
    def start_stream_relay(self, stream_id, output_path):
        """
        Start ffmpeg to receive SRT and output to MediaMTX RTSP
        
        Args:
            stream_id: Unique identifier for this stream
            output_path: RTSP path (e.g., /cam1)
        """
        # Build SRT source URL
        srt_url = f"srt://0.0.0.0:{self.srt_port}?mode=listener&passphrase={self.passphrase}"
        
        # Build RTSP output URL (MediaMTX)
        rtsp_url = f"rtsp://localhost:{self.rtsp_port}{output_path}"
        
        # FFmpeg command to relay SRT → RTSP
        cmd = [
            'ffmpeg',
            '-i', srt_url,
            '-c', 'copy',  # Copy codec (no re-encoding)
            '-f', 'rtsp',
            '-rtsp_transport', 'tcp',
            rtsp_url
        ]
        
        print(f"Starting relay for {stream_id}:")
        print(f"  SRT Input:  {srt_url}")
        print(f"  RTSP Output: {rtsp_url}")
        
        # Start process
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes[stream_id] = proc
        return proc
    
    def start_multi_stream_listener(self, num_streams=4):
        """
        Start listeners for multiple edge agent streams
        
        DeepStream will consume these RTSP streams
        """
        print(f"\n{'='*60}")
        print("SRT Multi-Stream Listener")
        print(f"{'='*60}")
        print(f"SRT Port: {self.srt_port}")
        print(f"Passphrase: {'*' * len(self.passphrase)}")
        print(f"RTSP Port: {self.rtsp_port}")
        print(f"Streams: {num_streams}")
        print(f"{'='*60}\n")
        
        # Start relay for each expected stream
        for i in range(1, num_streams + 1):
            stream_id = f"cam{i}"
            output_path = f"/stream{i}"
            
            try:
                self.start_stream_relay(stream_id, output_path)
                print(f"✓ Stream {i} relay started")
                time.sleep(1)  # Stagger starts
            except Exception as e:
                print(f"✗ Failed to start stream {i}: {e}")
        
        print(f"\n{'='*60}")
        print("All relays started. DeepStream can now connect to:")
        for i in range(1, num_streams + 1):
            print(f"  rtsp://localhost:{self.rtsp_port}/stream{i}")
        print(f"{'='*60}\n")
        
        print("Press Ctrl+C to stop...")
        
        # Monitor processes
        try:
            while self.running:
                time.sleep(5)
                
                # Check if any process died
                for stream_id, proc in list(self.processes.items()):
                    if proc.poll() is not None:
                        print(f"⚠ Stream {stream_id} died, restarting...")
                        output_path = f"/stream{stream_id[-1]}"
                        self.start_stream_relay(stream_id, output_path)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop_all()
    
    def stop_all(self):
        """Stop all relay processes"""
        self.running = False
        
        for stream_id, proc in self.processes.items():
            print(f"Stopping {stream_id}...")
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except:
                proc.kill()
        
        print("All streams stopped")


def main():
    parser = argparse.ArgumentParser(description='SRT Listener for Edge Agents')
    parser.add_argument('--port', type=int, default=9000, 
                       help='SRT listening port (default: 9000)')
    parser.add_argument('--passphrase', type=str, required=True,
                       help='SRT encryption passphrase (REQUIRED)')
    parser.add_argument('--rtsp-port', type=int, default=8554,
                       help='RTSP output port (default: 8554)')
    parser.add_argument('--streams', type=int, default=4,
                       help='Number of streams to expect (default: 4)')
    
    args = parser.parse_args()
    
    # Validate passphrase
    if len(args.passphrase) < 10:
        print("Error: Passphrase must be at least 10 characters")
        sys.exit(1)
    
    # Create listener
    listener = SRTListener(
        srt_port=args.port,
        passphrase=args.passphrase,
        rtsp_port=args.rtsp_port
    )
    
    # Start multi-stream listener
    listener.start_multi_stream_listener(num_streams=args.streams)


if __name__ == '__main__':
    main()