import logging
from pathlib import Path
from typing import Any

import yaml

from src.core.exceptions import ConfigurationError
from src.monitoring import metrics

logger = logging.getLogger(__name__)


class MetricsService:
    """Facade for recording Prometheus metrics safely and cleanly."""

    def __init__(self, config_path: str | Path = "configs/monitoring/monitoring.yaml"):
        self.config_path = str(config_path)
        self.config = self._load_config()
        self.enabled = self.config.get("monitoring", {}).get("enabled", False)

        if self.enabled:
            self._init_metrics()

    def _load_config(self) -> dict[str, Any]:
        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    return {}
                return dict(data)
        except Exception as e:
            logger.error(f"Failed to load monitoring config: {e}")
            raise ConfigurationError(f"Failed to load monitoring config: {e}") from e

    def _init_metrics(self) -> None:
        try:
            monitoring_cfg = self.config.get("monitoring", {})
            namespace = monitoring_cfg.get("metrics", {}).get(
                "namespace", "industrial_defect"
            )
            buckets = monitoring_cfg.get("latency", {}).get(
                "histogram_buckets",
                [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            )

            metrics.init_metrics(namespace, buckets)

            app_name = monitoring_cfg.get("service", {}).get(
                "name", "industrial-defect-detection"
            )
            if metrics.application_info:
                metrics.application_info.info({"name": app_name, "version": "1.0.0"})

        except Exception as e:
            logger.error(f"Failed to initialize metrics: {e}")
            self.enabled = False

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration_seconds: float
    ) -> None:
        if not self.enabled:
            return
        try:
            if metrics.http_requests_total:
                metrics.http_requests_total.labels(
                    method=method, endpoint=endpoint, status_code=str(status_code)
                ).inc()
            if metrics.http_request_duration_seconds:
                metrics.http_request_duration_seconds.labels(
                    method=method, endpoint=endpoint
                ).observe(duration_seconds)
        except Exception as e:
            logger.warning(f"Failed to record HTTP request metrics: {e}")

    def record_inspection(self, success: bool) -> None:
        if not self.enabled:
            return
        try:
            status = "success" if success else "failure"
            if metrics.inspections_total:
                metrics.inspections_total.labels(status=status).inc()
        except Exception as e:
            logger.warning(f"Failed to record inspection metric: {e}")

    def record_decision(self, decision: str) -> None:
        if not self.enabled:
            return
        try:
            if metrics.inspection_decisions_total:
                metrics.inspection_decisions_total.labels(decision=decision).inc()
        except Exception as e:
            logger.warning(f"Failed to record decision metric: {e}")

    def record_inference_latency(self, duration_seconds: float) -> None:
        if not self.enabled:
            return
        try:
            if metrics.model_inference_duration_seconds:
                metrics.model_inference_duration_seconds.observe(duration_seconds)
        except Exception as e:
            logger.warning(f"Failed to record inference latency metric: {e}")

    def record_pipeline_latency(self, duration_seconds: float) -> None:
        if not self.enabled:
            return
        try:
            if metrics.inspection_pipeline_duration_seconds:
                metrics.inspection_pipeline_duration_seconds.observe(duration_seconds)
        except Exception as e:
            logger.warning(f"Failed to record pipeline latency metric: {e}")

    def record_defect(self, class_name: str) -> None:
        if not self.enabled:
            return
        try:
            if metrics.defects_detected_total:
                metrics.defects_detected_total.labels(class_name=class_name).inc()
        except Exception as e:
            logger.warning(f"Failed to record defect metric: {e}")

    def record_plc_command(self, command: str, success: bool) -> None:
        if not self.enabled:
            return
        try:
            status = "success" if success else "failure"
            if metrics.plc_commands_total:
                metrics.plc_commands_total.labels(command=command, status=status).inc()
        except Exception as e:
            logger.warning(f"Failed to record PLC command metric: {e}")

    def record_pipeline_error(self, component: str) -> None:
        if not self.enabled:
            return
        try:
            if metrics.pipeline_errors_total:
                metrics.pipeline_errors_total.labels(component=component).inc()
        except Exception as e:
            logger.warning(f"Failed to record pipeline error metric: {e}")
