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
from src.monitoring.service import MetricsService
from prometheus_client import make_asgi_app
from src.persistence.database import db
from src.persistence.repositories.sqlalchemy_inspection_repository import SQLAlchemyInspectionRepository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load configuration
    try:
        with open("configs/api/api.yaml", "r") as f:
            api_config = yaml.safe_load(f)
        with open("configs/inference/realtime.yaml", "r") as f:
            inference_config = yaml.safe_load(f)
        with open("configs/persistence/database.yaml", "r") as f:
            db_config = yaml.safe_load(f)

        app_state.config = {"api": api_config, "inference": inference_config, "database": db_config}
    except Exception as e:
        logger.error(f"Failed to load configurations: {e}")
        raise


    # Initialize Monitoring
    try:
        app_state.metrics_service = MetricsService()
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")
        raise
        
    # Initialize Database
    try:
        persistence_cfg = db_config.get("persistence", {})
        if persistence_cfg.get("enabled", False):
            db_url = db_config.get("database", {}).get("url")
            echo = db_config.get("database", {}).get("echo", False)
            pool_cfg = db_config.get("pool", {})
            pool_enabled = pool_cfg.get("enabled", False)
            pool_size = pool_cfg.get("pool_size", 5)
            max_overflow = pool_cfg.get("max_overflow", 10)
            
            db.initialize(db_url=db_url, echo=echo, pool_enabled=pool_enabled, pool_size=pool_size, max_overflow=max_overflow)
            app_state.inspection_repository = SQLAlchemyInspectionRepository(db.get_session)
            logger.info("Persistence layer initialized.")
        else:
            logger.info("Persistence layer is disabled via config.")
            
        # Bootstrap Admin
        from src.auth.config import auth_settings
        if auth_settings.BOOTSTRAP_ADMIN_ENABLED and persistence_cfg.get("enabled", False):
            from src.auth.service import AuthService
            from src.persistence.repositories.user_repository import SQLAlchemyUserRepository
            from src.auth.models import Role
            
            user_repo = SQLAlchemyUserRepository(db.get_session)
            auth_service = AuthService(user_repo)
            
            admin_username = auth_settings.BOOTSTRAP_ADMIN_USERNAME
            admin_password = auth_settings.BOOTSTRAP_ADMIN_PASSWORD
            
            existing_admin = user_repo.get_by_username(admin_username)
            if not existing_admin:
                try:
                    auth_service.create_user(admin_username, admin_password, Role.ADMIN)
                    logger.info(f"Bootstrap admin user '{admin_username}' created successfully.")
                except Exception as e:
                    logger.error(f"Failed to create bootstrap admin: {e}")
            else:
                logger.info(f"Bootstrap admin user '{admin_username}' already exists.")
                
    except Exception as e:
        logger.error(f"Failed to initialize persistence: {e}")
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
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Must import here to avoid dependency issues if state is not ready, but we use app_state directly.
    from src.api.middleware.monitoring import PrometheusMiddleware
    # Re-initialize MetricsService here if necessary, or pass the singleton from state.
    # Since lifespan runs on startup, app_state.metrics_service might not be populated during create_app().
    # We instantiate it once here for middleware and endpoint.
    metrics_svc = MetricsService()
    app.add_middleware(PrometheusMiddleware, metrics_service=metrics_svc)
    
    # Metrics Endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Exception Handlers
    app.add_exception_handler(ApplicationError, industrial_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Register Routers (will import them locally to avoid circular dependencies if needed, or normal import)
    from src.api.routers import health, inspection, history, analytics, auth

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(inspection.router, prefix="/api/v1")
    app.include_router(history.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1/analytics")


    return app
