# DeepStream + Triton Inference Server

Production-ready video analytics pipeline for real-time object detection on RTSP streams.

## Features

- Real-time multi-stream processing with DeepStream
- TensorRT-optimized inference with Triton Server
- RTSP/RTMP/WebRTC streaming with MediaMTX
- Object tracking with NvMultiObjectTracker
- Prometheus metrics and monitoring
- Docker-based deployment

## Quick Start

### 1. Prerequisites
```bash
# Install system dependencies
sudo apt update && sudo apt install -y \
    libssl3 libssl-dev libgles2-mesa-dev \
    libgstreamer1.0-0 gstreamer1.0-tools \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    libgstreamer-plugins-base1.0-dev libgstrtspserver-1.0-0 \
    libjansson4 libyaml-cpp-dev libjsoncpp-dev \
    protobuf-compiler libmosquitto1 gcc make git python3

# Pull Docker images
docker pull nvcr.io/nvidia/tritonserver:25.03-py3
docker pull nvcr.io/nvidia/deepstream:8.0-triton-multiarch
docker pull bluenviron/mediamtx:latest
docker pull nvcr.io/nvidia/tensorrt:25.04-py3
```

### 2. Setup Project
```bash
# Create directory structure
mkdir -p deepstream-triton-project/{configs,scripts,utils,model_repository,logs,recordings}
cd deepstream-triton-project

# Copy all configuration files from this repository

# Create model directories
mkdir -p model_repository/yolo11n/1
mkdir -p model_repository/rf-detr-nano/1

# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py utils/*.py
```

### 3. Add Your Models

Place your ONNX models in:
- `model_repository/yolo11n/1/model.onnx`
- `model_repository/rf-detr-nano/1/model.onnx`

### 4. Convert to TensorRT
```bash
./scripts/convert_models.sh
```

### 5. Start Services
```bash
docker compose up -d

# Verify
docker logs triton
docker logs mediamtx
curl http://localhost:8000/v2/health/ready
```

### 6. Publish Test Stream
```bash
# From video file
./scripts/stream_publisher.py test_video.mp4 --loop

# From webcam
./scripts/stream_publisher.py 0
```

### 7. Run DeepStream
```bash
./scripts/run_deepstream.sh
```

## Testing

### Test Triton Inference
```bash
python scripts/test_inference.py test_image.jpg yolo11n
```

### Monitor Metrics
```bash
# Triton metrics
curl http://localhost:8000/v2/health/ready
curl http://localhost:8002/metrics

# MediaMTX streams
curl http://localhost:8889/v3/paths/list
```

## Performance

### YOLO11n (NVIDIA L20)
- Throughput: 1145.82 QPS
- Latency: 1.18 ms (mean)
- GPU Compute: 0.87 ms

### RF-DETR-Nano (NVIDIA L20)
- Throughput: 573.19 QPS
- Latency: 1.83 ms (mean)
- GPU Compute: 1.74 ms

## Troubleshooting

### GPU Not Detected
```bash
nvidia-smi
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Triton Model Load Failed
```bash
# Check logs
docker logs triton --tail 100

# Verify model structure
tree model_repository/
```

### RTSP Connection Failed
```bash
# Test connectivity
ffplay rtsp://localhost:8554/stream1

# Check MediaMTX
docker logs mediamtx
```

## Documentation

- [NVIDIA DeepStream](https://docs.nvidia.com/metropolis/deepstream/dev-guide/)
- [Triton Inference Server](https://github.com/triton-inference-server/server)
- [MediaMTX](https://github.com/bluenviron/mediamtx)
- [TensorRT](https://docs.nvidia.com/deeplearning/tensorrt/)

## License

MIT License