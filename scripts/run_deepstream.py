#!/usr/bin/env python3
"""
Run DeepStream pipeline with YOLO11n model.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_deepstream(config_file="deepstream_triton.txt"):
    """Run DeepStream pipeline with specified configuration."""
    print(f"Starting DeepStream pipeline with {config_file}...")
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    configs_dir = project_root / "configs"
    model_repo = project_root / "docker" / "model_repository"
    
    # Check if directories exist
    if not configs_dir.exists():
        print(f"✗ Error: Configs directory not found at {configs_dir}")
        sys.exit(1)
    
    config_path = configs_dir / config_file
    if not config_path.exists():
        print(f"✗ Error: Config file not found at {config_path}")
        sys.exit(1)
    
    # Build docker command
    cmd = [
        "docker", "run",
        "--gpus", "all",
        "-it", "--rm",
        "--network", "host",
        "-v", f"{configs_dir.absolute()}:/configs",
        "-v", f"{model_repo.absolute()}:/models",
        "nvcr.io/nvidia/deepstream:8.0-triton-multiarch",
        "deepstream-app", "-c", f"/configs/{config_file}"
    ]
    
    try:
        # Run the docker command
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running DeepStream: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Error: Docker is not installed or not in PATH")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✓ DeepStream pipeline stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    # Allow specifying config file as argument
    config = sys.argv[1] if len(sys.argv) > 1 else "deepstream_triton.txt"
    run_deepstream(config)
