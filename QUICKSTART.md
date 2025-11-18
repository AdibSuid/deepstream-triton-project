# Quick Start Guide - DeepStream Triton Project

## The Error You Encountered

**Issue**: `plugin-type=1` was incorrect for Triton backend
**Fix**: Changed to `plugin-type=0` in `configs/deepstream_triton.txt`

## Before Running DeepStream

### 1. Start Backend Services
```powershell
cd docker
docker compose up -d
```

This starts:
- **Triton Server** (port 8000) - AI inference engine
- **MediaMTX** (port 8554) - RTSP/RTMP streaming server

### 2. Verify Services Are Ready
```powershell
python scripts/check_services.py
```

This checks:
- ✓ Docker containers running
- ✓ Triton server ready
- ✓ Models loaded in Triton
- ✓ MediaMTX ready (optional)

### 3. Configure Your RTSP Stream
Edit `configs/deepstream_triton.txt`:
```ini
[source0]
uri=rtsp://your-camera-ip:554/stream1
```

Or use the test stream publisher:
```powershell
python scripts/stream_publisher.py path/to/video.mp4 --loop
```

### 4. Run DeepStream
```powershell
python scripts/run_deepstream.py
```

Or with a different config:
```powershell
python scripts/run_deepstream.py deepstream_rfdetr.txt
```

## Common Issues

### "Triton server is not running"
```powershell
docker compose -f docker/docker-compose.yml up -d triton
docker logs triton  # Check for errors
```

### "No models loaded in Triton"
1. Check models exist:
   ```powershell
   ls docker/model_repository/yolo11n/1/
   ls docker/model_repository/rf-detr-nano/1/
   ```

2. Convert ONNX to TensorRT:
   ```powershell
   python scripts/convert_models.py
   ```

3. Restart Triton:
   ```powershell
   docker compose -f docker/docker-compose.yml restart triton
   ```

### "RTSP Connection Failed"
- Verify your camera/stream is accessible
- Check network connectivity
- Test with: `ffplay rtsp://your-stream-url`

## Full Workflow

```powershell
# 1. Initial setup (once)
python scripts/setup.py

# 2. Add your models
# Copy ONNX models to docker/model_repository/*/1/

# 3. Convert models
python scripts/convert_models.py

# 4. Start services
cd docker
docker compose up -d

# 5. Check everything is ready
python scripts/check_services.py

# 6. Start video stream (if testing)
python scripts/stream_publisher.py test_video.mp4 --loop

# 7. Run DeepStream
python scripts/run_deepstream.py
```

## Service Ports

- **8000** - Triton HTTP inference
- **8001** - Triton gRPC inference  
- **8002** - Triton metrics (Prometheus)
- **8554** - RTSP streaming (MediaMTX)
- **8555** - DeepStream RTSP output
- **8889** - WebRTC (MediaMTX)

## Monitoring

```powershell
# Check Triton health
curl http://localhost:8000/v2/health/ready

# View Triton metrics
curl http://localhost:8002/metrics

# List available streams
curl http://localhost:8889/v3/paths/list

# Watch container logs
docker logs -f triton
docker logs -f mediamtx
```
