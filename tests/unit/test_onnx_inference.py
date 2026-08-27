import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.inference.onnx_inference import ONNXInferenceWrapper

@patch("src.inference.onnx_inference.os.path.exists")
@patch("src.inference.onnx_inference.ort.InferenceSession")
def test_onnx_wrapper_init(mock_session, mock_exists):
    mock_exists.return_value = True
    
    # Mock session outputs
    mock_session_instance = MagicMock()
    
    mock_input = MagicMock()
    mock_input.name = "images"
    mock_input.shape = ["batch", 3, 224, 224]
    
    mock_output = MagicMock()
    mock_output.name = "output0"
    
    mock_session_instance.get_inputs.return_value = [mock_input]
    mock_session_instance.get_outputs.return_value = [mock_output]
    mock_session.return_value = mock_session_instance
    
    wrapper = ONNXInferenceWrapper("fake.onnx")
    
    assert wrapper.input_name == "images"
    assert wrapper.output_name == "output0"
    assert wrapper.imgsz == (224, 224)

@patch("src.inference.onnx_inference.os.path.exists")
@patch("src.inference.onnx_inference.ort.InferenceSession")
def test_onnx_wrapper_preprocess(mock_session, mock_exists):
    mock_exists.return_value = True
    
    mock_session_instance = MagicMock()
    mock_input = MagicMock()
    mock_input.name = "images"
    mock_input.shape = ["batch", 3, 200, 200]
    mock_output = MagicMock()
    mock_output.name = "output0"
    
    mock_session_instance.get_inputs.return_value = [mock_input]
    mock_session_instance.get_outputs.return_value = [mock_output]
    mock_session.return_value = mock_session_instance
    
    wrapper = ONNXInferenceWrapper("fake.onnx")
    
    # Dummy BGR image 300x300
    img = np.ones((300, 300, 3), dtype=np.uint8) * 255
    
    tensor = wrapper.preprocess(img)
    
    assert tensor.shape == (1, 3, 200, 200)
    assert tensor.dtype == np.float32
    assert np.max(tensor) <= 1.0 # Normalized
