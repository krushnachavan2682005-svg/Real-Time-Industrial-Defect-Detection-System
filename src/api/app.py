import logging
import yaml
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import app_state
from src.api.exceptions import industrial_exception_handler, general_exception_handler
from src.core.exceptions import ApplicationError
from src.inference.onnx_inference import ONNXInferenceWrapper
from src.decision.decision_engine import DecisionEngine
from src.vision.coordinate_transform import CoordinateTransformer
from src.vision.postprocess import Postprocessor
from src.mapping.result_builder import ResultBuilder
from src.plc.service import PLCService
from src.plc.command_mapper import PLCCommandMapper
from src.plc.simulator import SimulationPLCClient
from src.plc.models import PLCConfig, PLCCommandConfig, PLCCommandType

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load configuration
    try:
        with open("configs/api/api.yaml", "r") as f:
            api_config = yaml.safe_load(f)
        with open("configs/inference/realtime.yaml", "r") as f:
            inference_config = yaml.safe_load(f)

        app_state.config = {"api": api_config, "inference": inference_config}
    except Exception as e:
        logger.error(f"Failed to load configurations: {e}")
        raise

    # Initialize components
    try:
        model_path = inference_config.get("inference", {}).get(
            "model_path", "models/onnx/best.onnx"
        )
        app_state.inference_engine = ONNXInferenceWrapper(model_path)

        imgsz = tuple(
            inference_config.get("inference", {}).get("image_size", [224, 224])
        )
        app_state.inference_engine.imgsz = imgsz

        # Determine max upload size and original image sizes dynamically, here we just initialize coordinate transformer
        # We will re-instantiate CoordinateTransformer per request in service since it depends on original image size.

        classes = inference_config.get("classes", {})
        class_map = {int(k): str(v) for k, v in classes.items()}
        conf_thresh = inference_config.get("inference", {}).get(
            "confidence_threshold", 0.25
        )
        iou_thresh = inference_config.get("inference", {}).get("iou_threshold", 0.50)

        app_state.postprocessor = Postprocessor(class_map, conf_thresh, iou_thresh)

        decision_config_path = "configs/decision/decision_rules.yaml"
        app_state.decision_engine = DecisionEngine(decision_config_path)

        app_state.result_builder = ResultBuilder()

        if api_config.get("inspection", {}).get("enable_plc_dispatch", False):
            client = SimulationPLCClient()
            plc_config = PLCConfig(
                enabled=True,
                mode="simulation",
                commands={
                    "pass": PLCCommandConfig(action=PLCCommandType.CONTINUE_CONVEYOR),
                    "review": PLCCommandConfig(
                        action=PLCCommandType.FLAG_FOR_MANUAL_INSPECTION
                    ),
                    "reject": PLCCommandConfig(action=PLCCommandType.REJECT_PRODUCT),
                },
            )
            mapper = PLCCommandMapper(config=plc_config)
            app_state.plc_service = PLCService(client, mapper)
            app_state.plc_service.start()
            logger.info("PLC Service started in simulation mode.")
        else:
            app_state.plc_service = None
            logger.info("PLC dispatch is disabled via config.")

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

    logger.info("Application lifespan started.")
    yield
    # Shutdown
    if app_state.plc_service:
        app_state.plc_service.stop()
        logger.info("PLC Service stopped.")
    logger.info("Application lifespan ended.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Industrial Defect Detection API",
        version="1.0.0",
        description="FastAPI Inference & Inspection API for manufacturing quality control.",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(ApplicationError, industrial_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Register Routers (will import them locally to avoid circular dependencies if needed, or normal import)
    from src.api.routers import health, inspection

    app.include_router(health.router)
    app.include_router(inspection.router, prefix="/api/v1")

    return app
