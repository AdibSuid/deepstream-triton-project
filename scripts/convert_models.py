#!/usr/bin/env python3
"""
Convert ONNX models to TensorRT engines using Docker.
"""

import os
import subprocess
import sys
from pathlib import Path


def convert_models():
    """Convert all ONNX models in model_repository to TensorRT engines."""
    print("Converting ONNX models to TensorRT engines...")
    
    # Get the project root directory (parent of scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    model_repo = project_root / "docker" / "model_repository"
    
    # Check if model_repository exists
    if not model_repo.exists():
        print(f"Error: Model repository not found at {model_repo}")
        sys.exit(1)
    
    # Build docker command
    cmd = [
        "docker", "run",
        "--gpus", "all",
        "-it", "--rm",
        "-v", f"{model_repo.absolute()}:/model_repository",
        "nvcr.io/nvidia/tensorrt:25.04-py3",
        "bash", "-c",
        (
            "cd /model_repository && "
            "for d in */1; do "
            "onnx=\"$d/model.onnx\"; "
            "plan=\"$d/model.plan\"; "
            "echo \"Converting $onnx → $plan\"; "
            "trtexec --onnx=\"$onnx\" --saveEngine=\"$plan\" --fp16; "
            "done"
        )
    ]
    
    try:
        # Run the docker command
        result = subprocess.run(cmd, check=True)
        print("\n✓ Model conversion complete!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during model conversion: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Error: Docker is not installed or not in PATH")
        sys.exit(1)


if __name__ == "__main__":
    convert_models()
