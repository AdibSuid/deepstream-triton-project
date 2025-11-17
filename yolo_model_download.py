from ultralytics import YOLO

# Load model
model = YOLO('yolo11n.pt')

# Export to ONNX
model.export(format='onnx', dynamic=False, simplify=True)