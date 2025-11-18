#!/usr/bin/env python3
"""
Check if required services are running before starting DeepStream.
"""

import subprocess
import sys
import requests
from pathlib import Path


def check_triton():
    """Check if Triton server is running and ready."""
    print("Checking Triton Inference Server...")
    try:
        response = requests.get("http://localhost:8000/v2/health/ready", timeout=2)
        if response.status_code == 200:
            print("✓ Triton server is running and ready")
            return True
        else:
            print(f"✗ Triton server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Triton server is not running")
        print("  Start it with: docker compose -f docker/docker-compose.yml up -d triton")
        return False
    except Exception as e:
        print(f"✗ Error checking Triton: {e}")
        return False


def check_triton_models():
    """Check if models are loaded in Triton."""
    print("\nChecking Triton models...")
    try:
        # Try to get yolo11n model specifically (Triton v2 API)
        response = requests.get("http://localhost:8000/v2/models/yolo11n", timeout=2)
        if response.status_code == 200:
            model_info = response.json()
            print(f"✓ Model '{model_info['name']}' is loaded and ready")
            print(f"  Platform: {model_info.get('platform', 'N/A')}")
            print(f"  Versions: {', '.join(model_info.get('versions', []))}")
            return True
        else:
            print(f"✗ Model yolo11n not found (status {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Triton server")
        return False
    except Exception as e:
        print(f"✗ Error checking models: {e}")
        return False


def check_mediamtx():
    """Check if MediaMTX is running."""
    print("\nChecking MediaMTX...")
    try:
        response = requests.get("http://localhost:8889/v3/config/global/get", timeout=2)
        if response.status_code == 200:
            print("✓ MediaMTX is running")
            return True
        else:
            print(f"⚠ MediaMTX responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠ MediaMTX is not running (optional)")
        print("  Start it with: docker compose -f docker/docker-compose.yml up -d mediamtx")
        return False
    except Exception as e:
        print(f"⚠ Error checking MediaMTX: {e}")
        return False


def check_rtsp_stream():
    """Check if RTSP stream is available."""
    print("\nChecking RTSP stream...")
    # This would require ffmpeg/gstreamer to properly check
    # For now, just inform the user - this is NOT a blocker
    print("ℹ RTSP stream configuration:")
    print("  DeepStream will pull the stream from your camera")
    print("  Make sure your camera is accessible at the configured URI")
    print("  (This is just informational, not a requirement check)")
    return True  # Don't block on RTSP check


def check_docker_containers():
    """Check running Docker containers."""
    print("\nChecking Docker containers...")
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        containers = result.stdout.strip().split('\n')
        containers = [c for c in containers if c]  # Remove empty strings
        
        if containers:
            print(f"✓ Found {len(containers)} running container(s):")
            for container in containers:
                print(f"  - {container}")
            return True
        else:
            print("✗ No Docker containers running")
            print("  Start services with: docker compose -f docker/docker-compose.yml up -d")
            return False
    except Exception as e:
        print(f"✗ Error checking containers: {e}")
        return False


def main():
    """Main check function."""
    print("=" * 60)
    print("DeepStream-Triton Service Check")
    print("=" * 60 + "\n")
    
    checks = {
        "Docker Containers": check_docker_containers(),
        "Triton Server": check_triton(),
        "Triton Models": check_triton_models(),
        "MediaMTX": check_mediamtx(),
        "RTSP Stream": check_rtsp_stream(),
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    required_checks = ["Docker Containers", "Triton Server", "Triton Models"]
    all_required_passed = all(checks[check] for check in required_checks)
    
    if all_required_passed:
        print("✓ All required services are ready!")
        print("\nYou can now run: python scripts/run_deepstream.py")
        return 0
    else:
        print("✗ Some required services are not ready")
        print("\nPlease fix the issues above before running DeepStream")
        return 1


if __name__ == "__main__":
    sys.exit(main())
