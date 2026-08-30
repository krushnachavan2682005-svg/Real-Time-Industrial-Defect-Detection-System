import os
from typing import Dict, Any, Optional

import yaml

from src.inference.onnx_inference import ONNXInferenceWrapper
from src.decision.decision_engine import DecisionEngine
from src.vision.coordinate_transform import CoordinateTransformer
from src.vision.postprocess import Postprocessor
from src.mapping.result_builder import ResultBuilder
from src.plc.service import PLCService
from src.plc.simulator import SimulationPLCClient
from src.plc.command_mapper import PLCCommandMapper


# Global state to hold our singleton instances
class AppState:
    config: Dict[str, Any] = {}
    inference_engine: Optional[ONNXInferenceWrapper] = None
    coord_transformer: Optional[CoordinateTransformer] = None
    postprocessor: Optional[Postprocessor] = None
    decision_engine: Optional[DecisionEngine] = None
    result_builder: Optional[ResultBuilder] = None
    plc_service: Optional[PLCService] = None
    metrics_service: Optional['MetricsService'] = None


app_state = AppState()


def get_config() -> Dict[str, Any]:
    return app_state.config


def get_inference_engine() -> ONNXInferenceWrapper:
    if app_state.inference_engine is None:
        raise RuntimeError("Inference engine is not initialized.")
    return app_state.inference_engine


def get_coord_transformer() -> CoordinateTransformer:
    if app_state.coord_transformer is None:
        raise RuntimeError("Coordinate transformer is not initialized.")
    return app_state.coord_transformer


def get_postprocessor() -> Postprocessor:
    if app_state.postprocessor is None:
        raise RuntimeError("Postprocessor is not initialized.")
    return app_state.postprocessor


def get_decision_engine() -> DecisionEngine:
    if app_state.decision_engine is None:
        raise RuntimeError("Decision engine is not initialized.")
    return app_state.decision_engine


def get_result_builder() -> ResultBuilder:
    if app_state.result_builder is None:
        raise RuntimeError("Result builder is not initialized.")
    return app_state.result_builder


def get_plc_service() -> Optional[PLCService]:
    return app_state.plc_service


def get_metrics_service():
    from src.monitoring.service import MetricsService
    if app_state.metrics_service is None:
        # Fallback if not initialized (e.g. testing)
        app_state.metrics_service = MetricsService()
    return app_state.metrics_service
