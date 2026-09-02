import logging

from prometheus_client import Counter, Histogram, Info

logger = logging.getLogger(__name__)

# Single initialization flag to prevent duplicate registration
_INITIALIZED = False

# Application Information
application_info: Info | None = None

# API Metrics
http_requests_total: Counter | None = None
http_request_duration_seconds: Histogram | None = None

# Inspection Metrics
inspections_total: Counter | None = None
inspection_decisions_total: Counter | None = None
model_inference_duration_seconds: Histogram | None = None
inspection_pipeline_duration_seconds: Histogram | None = None
defects_detected_total: Counter | None = None

# PLC Metrics
plc_commands_total: Counter | None = None

# Error Metrics
pipeline_errors_total: Counter | None = None

# Database Metrics
database_operations_total: Counter | None = None
database_operation_duration_seconds: Histogram | None = None
database_errors_total: Counter | None = None


def init_metrics(namespace: str, buckets: list[float]) -> None:
    """Initialize all Prometheus metrics safely."""
    global _INITIALIZED, application_info
    global http_requests_total, http_request_duration_seconds
    global inspections_total, inspection_decisions_total
    global model_inference_duration_seconds, inspection_pipeline_duration_seconds
    global defects_detected_total, plc_commands_total, pipeline_errors_total
    global database_operations_total, database_operation_duration_seconds, database_errors_total

    if _INITIALIZED:
        logger.warning("Metrics already initialized, skipping.")
        return

    application_info = Info(
        "application",
        "Application information",
        namespace=namespace,
    )

    http_requests_total = Counter(
        "http_requests_total",
        "Total number of HTTP requests",
        ["method", "endpoint", "status_code"],
        namespace=namespace,
    )

    http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
        buckets=buckets,
        namespace=namespace,
    )

    inspections_total = Counter(
        "inspections_total",
        "Total number of inspections processed",
        ["status"],
        namespace=namespace,
    )

    inspection_decisions_total = Counter(
        "inspection_decisions_total",
        "Total number of inspection decisions",
        ["decision"],
        namespace=namespace,
    )

    model_inference_duration_seconds = Histogram(
        "model_inference_duration_seconds",
        "Model inference duration in seconds",
        buckets=buckets,
        namespace=namespace,
    )

    inspection_pipeline_duration_seconds = Histogram(
        "inspection_pipeline_duration_seconds",
        "End-to-end inspection pipeline duration in seconds",
        buckets=buckets,
        namespace=namespace,
    )

    defects_detected_total = Counter(
        "defects_detected_total",
        "Total number of detected defects by class",
        ["class_name"],
        namespace=namespace,
    )

    plc_commands_total = Counter(
        "plc_commands_total",
        "Total number of PLC commands dispatched",
        ["command", "status"],
        namespace=namespace,
    )

    pipeline_errors_total = Counter(
        "pipeline_errors_total",
        "Total number of pipeline errors by component",
        ["component"],
        namespace=namespace,
    )

    database_operations_total = Counter(
        "database_operations_total",
        "Total number of database operations",
        ["operation", "status"],
        namespace=namespace,
    )

    database_operation_duration_seconds = Histogram(
        "database_operation_duration_seconds",
        "Database operation duration in seconds",
        ["operation"],
        buckets=buckets,
        namespace=namespace,
    )

    database_errors_total = Counter(
        "database_errors_total",
        "Total number of database errors",
        ["operation"],
        namespace=namespace,
    )

    _INITIALIZED = True
    logger.info(f"Prometheus metrics initialized with namespace: {namespace}")
