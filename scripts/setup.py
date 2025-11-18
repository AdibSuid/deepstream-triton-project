#!/usr/bin/env python3
"""
Setup script for DeepStream-Triton project.
Creates necessary directories and performs initial setup.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"✓ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed: {e}")
        return False


def create_directories():
    """Create necessary project directories."""
    print("\n=== Creating Project Directories ===")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    directories = [
        "docker/model_repository/yolo11n/1",
        "docker/model_repository/rf-detr-nano/1",
        "logs",
        "recordings",
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")


def pull_docker_images():
    """Pull required Docker images."""
    print("\n=== Pulling Docker Images ===")
    
    images = [
        "nvcr.io/nvidia/tritonserver:25.03-py3",
        "nvcr.io/nvidia/deepstream:8.0-triton-multiarch",
        "bluenviron/mediamtx:latest",
        "nvcr.io/nvidia/tensorrt:25.04-py3",
    ]
    
    for image in images:
        if not run_command(f"docker pull {image}", f"Pulling {image}"):
            print(f"Warning: Failed to pull {image}")


def install_python_deps():
    """Install Python dependencies."""
    print("\n=== Installing Python Dependencies ===")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    requirements_file = project_root / "requirements.txt"
    
    if requirements_file.exists():
        run_command(
            f"pip install -r {requirements_file}",
            "Installing Python packages"
        )
    else:
        print("Warning: requirements.txt not found")


def check_docker():
    """Check if Docker is installed and running."""
    print("\n=== Checking Docker ===")
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✓ Docker is installed")
        
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        print("✓ Docker daemon is running")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Docker is not installed or not running")
        return False


def check_nvidia_docker():
    """Check if NVIDIA Docker runtime is available."""
    print("\n=== Checking NVIDIA Docker Runtime ===")
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:12.0-base", "nvidia-smi"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ NVIDIA Docker runtime is working")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ NVIDIA Docker runtime not available")
        print("  Make sure NVIDIA Container Toolkit is installed")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("DeepStream-Triton Project Setup")
    print("=" * 60)
    
    # Check prerequisites
    if not check_docker():
        print("\n⚠ Please install Docker and try again")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install Python dependencies
    install_python_deps()
    
    # Check NVIDIA Docker (warning only)
    check_nvidia_docker()
    
    # Pull Docker images
    pull_choice = input("\n\nPull Docker images now? (y/n): ").lower()
    if pull_choice == 'y':
        pull_docker_images()
    
    print("\n" + "=" * 60)
    print("✓ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Place your ONNX models in docker/model_repository/*/1/")
    print("2. Run: python scripts/convert_models.py")
    print("3. Run: docker compose -f docker/docker-compose.yml up -d")
    print("4. Run: python scripts/stream_publisher.py <video_file>")
    print("5. Run: python scripts/run_deepstream.py")


if __name__ == "__main__":
    main()
