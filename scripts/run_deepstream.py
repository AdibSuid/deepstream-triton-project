#!/usr/bin/env python3
"""
Run DeepStream pipeline with YOLO11n model.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_deepstream(config_file="deepstream_triton.txt", srt_uri=None, fps=None):
    """Run DeepStream pipeline with specified configuration, SRT URI, and FPS."""
    print(f"Starting DeepStream pipeline with {config_file}...")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    configs_dir = project_root / "configs"
    model_repo = project_root / "docker" / "model_repository"

    if not configs_dir.exists():
        print(f"✗ Error: Configs directory not found at {configs_dir}")
        sys.exit(1)

    config_path = configs_dir / config_file
    if not config_path.exists():
        print(f"✗ Error: Config file not found at {config_path}")
        sys.exit(1)

    # If SRT URI or FPS is provided, modify config file temporarily (only inside [source0])
    temp_config_path = config_path
    # Support SRT passphrase via environment variable or argument
    srt_passphrase = os.environ.get("SRT_PASSPHRASE") or getattr(sys, "srt_passphrase", None)
    if srt_uri or fps or srt_passphrase:
        import tempfile
        with open(config_path, "r", encoding="utf-8") as f:
            config_lines = f.readlines()
        new_lines = []
        in_source0 = False
        for line in config_lines:
            # Detect section headers robustly
            section_header = line.strip().lower()
            if section_header.startswith("[") and section_header.endswith("]"):
                in_source0 = section_header == "[source0]"
                new_lines.append(line)
                continue
            if in_source0:
                key = line.split("=")[0].strip().lower()
                if srt_uri and key == "uri":
                    new_lines.append(f"uri={srt_uri}\n")
                    continue
                if fps is not None and key == "drop-frame-interval":
                    new_lines.append(f"drop-frame-interval={fps}\n")
                    continue
                # Replace srt-reconnect-interval-sec or rtsp-reconnect-interval-sec with reconnect-interval-sec
                if key in ["srt-reconnect-interval-sec", "rtsp-reconnect-interval-sec"]:
                    value = line.split("=",1)[1].strip() if "=" in line else "10"
                    new_lines.append(f"reconnect-interval-sec={value}\n")
                    continue
                # Add SRT passphrase if not present
                if srt_passphrase and key == "latency":
                    new_lines.append(line)
                    new_lines.append(f"passphrase={srt_passphrase}\n")
                    continue
            new_lines.append(line)
        temp_path = configs_dir / ("deepstream_temp_override.txt")
        with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(new_lines)
        temp_config_path = temp_path

    cmd = [
        "docker", "run",
        "--gpus", "all",
        "-it", "--rm",
        "--network", "host",
        "-v", f"{configs_dir.absolute()}:/configs",
        "-v", f"{model_repo.absolute()}:/models",
        "nvcr.io/nvidia/deepstream:8.0-triton-multiarch",
        "deepstream-app", "-c", f"/configs/{temp_config_path.name}"
    ]

    try:
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
    # finally:
    #     # Clean up temp config file
    #     if (srt_uri or fps) and temp_config_path != config_path:
    #         try:
    #             os.remove(temp_config_path)
    #         except Exception:
    #             pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run DeepStream pipeline")
    parser.add_argument("config", nargs="?", default="deepstream_triton.txt", help="Config file name")
    parser.add_argument("--srt-uri", type=str, help="SRT stream URI (e.g. srt://example:9000)")
    parser.add_argument("--fps", type=int, help="FPS (frames per second) or drop-frame-interval")
    parser.add_argument("--srt-passphrase", type=str, help="SRT passphrase for encrypted stream")
    args = parser.parse_args()
    # Pass passphrase via sys module for patching logic
    sys.srt_passphrase = args.srt_passphrase
    run_deepstream(args.config, srt_uri=args.srt_uri, fps=args.fps)
