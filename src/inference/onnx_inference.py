import os
import cv2
import numpy as np
import logging
import onnxruntime as ort
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ONNXInferenceWrapper:
    """Wrapper for running inference using ONNX Runtime with proper preprocessing."""

    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX model not found at {model_path}")
            
        self.model_path = model_path
        
        # Detect and set providers gracefully
        available_providers = ort.get_available_providers()
        self.providers = []
        
        if 'CUDAExecutionProvider' in available_providers:
            self.providers.append('CUDAExecutionProvider')
        if 'CPUExecutionProvider' in available_providers:
            self.providers.append('CPUExecutionProvider')
            
        if not self.providers:
            # Fallback to defaults
            self.providers = ['CPUExecutionProvider']
            
        logger.info(f"Loading ONNX model {model_path} with providers: {self.providers}")
        self.session = ort.InferenceSession(self.model_path, providers=self.providers)
        
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        # typically [batch, channels, height, width]
        self.input_shape = self.session.get_inputs()[0].shape 
        
        # Extract required height/width from model input shape if static
        # Assuming shape is ['batch', 3, H, W]
        if isinstance(self.input_shape[2], int):
            self.imgsz = (self.input_shape[3], self.input_shape[2]) # (W, H)
        else:
            self.imgsz = (200, 200) # Fallback

    def preprocess(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Preprocesses a BGR image for YOLOv8 ONNX inference.
        Resizes without letterboxing to match direct tensor comparison.
        """
        # Resize to match expected input size
        img = cv2.resize(img_bgr, self.imgsz)
        
        # BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalize to 0-1
        img = img.astype(np.float32) / 255.0
        
        # HWC to CHW
        img = img.transpose((2, 0, 1))
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        
        return img

    def predict(self, img_bgr: np.ndarray) -> np.ndarray:
        """Runs inference and returns raw ONNX outputs."""
        input_tensor = self.preprocess(img_bgr)
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
        return outputs[0]
        
    def predict_tensor(self, input_tensor: np.ndarray) -> np.ndarray:
        """Runs inference on an already preprocessed tensor."""
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
        return outputs[0]

    def get_runtime_info(self) -> Dict[str, Any]:
        """Returns details about the active execution provider."""
        active_providers = self.session.get_providers()
        return {
            "model_path": self.model_path,
            "active_providers": active_providers,
            "input_shape": self.input_shape,
            "input_name": self.input_name,
            "output_name": self.output_name
        }
