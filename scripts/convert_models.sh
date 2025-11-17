#!/bin/bash

echo "Converting ONNX models to TensorRT engines..."

docker run --gpus all -it --rm \
  -v $(pwd)/model_repository:/model_repository \
  nvcr.io/nvidia/tensorrt:25.04-py3 \
  bash -c "cd /model_repository && \
  for d in */1; do \
    onnx=\"\$d/model.onnx\"; \
    plan=\"\$d/model.plan\"; \
    echo \"Converting \$onnx → \$plan\"; \
    trtexec --onnx=\"\$onnx\" --saveEngine=\"\$plan\" --fp16; \
  done"

echo "Model conversion complete!"