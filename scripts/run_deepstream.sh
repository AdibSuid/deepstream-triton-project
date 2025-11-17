#!/bin/bash

echo "Starting DeepStream pipeline with YOLO11n..."

docker run --gpus all -it --rm \
  --network host \
  -v $(pwd)/configs:/configs \
  -v $(pwd)/model_repository:/models \
  nvcr.io/nvidia/deepstream:8.0-triton-multiarch \
  deepstream-app -c /configs/deepstream_yolo11n.txt