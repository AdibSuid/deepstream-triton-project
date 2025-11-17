#!/usr/bin/env python3
"""Test Triton inference server"""

import tritonclient.http as httpclient
import numpy as np
from PIL import Image
import sys

def test_triton_inference(model_name="yolo11n", image_path="test.jpg"):
    try:
        client = httpclient.InferenceServerClient(url="localhost:8000")
        
        if not client.is_server_live():
            print("ERROR: Triton server is not live!")
            return False
        
        if not client.is_model_ready(model_name):
            print(f"ERROR: Model {model_name} is not ready!")
            return False
        
        print(f"Loading image: {image_path}")
        img = Image.open(image_path).convert('RGB')
        img = img.resize((640, 640))
        img_array = np.array(img).astype(np.float32)
        img_array = img_array / 255.0
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        
        inputs = [httpclient.InferInput("images", img_array.shape, "FP32")]
        inputs[0].set_data_from_numpy(img_array)
        
        outputs = [httpclient.InferRequestedOutput("output0")]
        
        print("Running inference...")
        results = client.infer(model_name=model_name, inputs=inputs, outputs=outputs)
        
        output = results.as_numpy("output0")
        print(f"✓ Inference successful!")
        print(f"  Output shape: {output.shape}")
        print(f"  Output dtype: {output.dtype}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    model_name = sys.argv[2] if len(sys.argv) > 2 else "yolo11n"
    
    success = test_triton_inference(model_name, image_path)
    sys.exit(0 if success else 1)