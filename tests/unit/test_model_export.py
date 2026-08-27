import pytest
from unittest.mock import patch, MagicMock
from src.inference.model_exporter import ModelExporter

@patch("src.inference.model_exporter.os.path.exists")
@patch("src.inference.model_exporter.YOLO")
def test_model_exporter_init(mock_yolo, mock_exists):
    mock_exists.return_value = True
    exporter = ModelExporter("fake_path.pt")
    assert exporter.model_path == "fake_path.pt"
    mock_yolo.assert_called_once_with("fake_path.pt")

@patch("src.inference.model_exporter.os.path.exists")
def test_model_exporter_init_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        ModelExporter("fake_path.pt")

@patch("src.inference.model_exporter.os.path.exists")
@patch("src.inference.model_exporter.YOLO")
@patch("src.inference.model_exporter.shutil.move")
def test_model_exporter_export(mock_move, mock_yolo, mock_exists):
    mock_exists.return_value = True
    
    # Mock YOLO instance
    mock_yolo_instance = MagicMock()
    mock_yolo_instance.export.return_value = "fake_path.onnx"
    mock_yolo.return_value = mock_yolo_instance
    
    exporter = ModelExporter("fake_path.pt")
    
    # Mock structural validation to pass
    exporter._validate_onnx_structure = MagicMock(return_value=True)
    
    result = exporter.export_onnx("output_dir", imgsz=(200, 200))
    
    assert result is not None
    mock_yolo_instance.export.assert_called_once_with(
        format="onnx", imgsz=(200, 200), opset=12, dynamic=False, simplify=True
    )
