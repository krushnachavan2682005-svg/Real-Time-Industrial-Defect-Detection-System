import os
import shutil
import logging
from typing import Optional, Tuple
from pathlib import Path
from ultralytics import YOLO
import onnx

logger = logging.getLogger(__name__)

class ModelExporter:
    """Handles exporting PyTorch models to optimized formats (ONNX/TensorRT)."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Source model not found at {model_path}")
        self.model = YOLO(self.model_path)

    def export_onnx(self, output_dir: str, imgsz: Tuple[int, int] = (200, 200), opset: int = 12, 
                    dynamic: bool = False, simplify: bool = True) -> Optional[str]:
        """
        Exports the YOLO model to ONNX format and validates the graph structure.
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.model_path))[0]
        
        logger.info(f"Starting ONNX export for {self.model_path}")
        
        try:
            # YOLO export saves the model next to the original by default or in a specified directory.
            # Using Ultralytics export
            export_path = self.model.export(
                format="onnx",
                imgsz=imgsz,
                opset=opset,
                dynamic=dynamic,
                simplify=simplify
            )
            
            # The exported file is normally created where the original model is. We should move it.
            if not os.path.exists(export_path):
                raise FileNotFoundError(f"Expected exported file not found at {export_path}")
                
            target_path = os.path.join(output_dir, f"{base_name}.onnx")
            
            # Use shutil to move it so we have it cleanly in models/onnx
            if os.path.abspath(export_path) != os.path.abspath(target_path):
                shutil.move(export_path, target_path)
            
            logger.info(f"ONNX export completed: {target_path}")
            
            # Structural validation
            if not self._validate_onnx_structure(target_path):
                raise RuntimeError("ONNX structural validation failed.")
                
            return target_path
            
        except Exception as e:
            logger.error(f"ONNX export failed: {str(e)}")
            return None
            
    def _validate_onnx_structure(self, onnx_path: str) -> bool:
        """Validates the structural integrity of the ONNX graph."""
        logger.info(f"Validating ONNX structure for {onnx_path}")
        try:
            onnx_model = onnx.load(onnx_path)
            onnx.checker.check_model(onnx_model)
            
            # Log some useful info
            logger.info(f"ONNX Graph: opset {onnx_model.opset_import[0].version}")
            logger.info(f"Inputs: {[i.name for i in onnx_model.graph.input]}")
            logger.info(f"Outputs: {[o.name for o in onnx_model.graph.output]}")
            return True
        except onnx.checker.ValidationError as e:
            logger.error(f"ONNX validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load ONNX model for validation: {e}")
            return False
