import logging
import time
import cv2
import numpy as np
from fastapi import UploadFile

from src.core.exceptions import ApplicationError
from src.api.dependencies import (
    get_config,
    get_inference_engine,
    get_postprocessor,
    get_decision_engine,
    get_result_builder,
    get_plc_service,
    get_metrics_service,
)
from src.vision.coordinate_transform import CoordinateTransformer
from src.api.schemas import (
    InspectionResponse,
    InspectionSummary,
    DefectSchema,
    BBox,
    PLCDispatchInfo,
)
from src.mapping.models import InspectionResult

logger = logging.getLogger(__name__)


class InvalidImageError(ApplicationError):
    pass


def process_inspection(file: UploadFile, inspection_id: str) -> InspectionResponse:
    start_time = time.perf_counter()

    # 1. Read and decode image
    try:
        contents = file.file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        logger.error(f"Error reading upload file: {e}")
        raise InvalidImageError("Could not read image file.") from e

    if img is None:
        raise InvalidImageError(
            "Failed to decode image. Possibly corrupted or unsupported format."
        )

    orig_h, orig_w = img.shape[:2]

    if orig_h == 0 or orig_w == 0:
        raise InvalidImageError("Invalid image dimensions.")

    # 2. Get dependencies
    config = get_config()
    inference_engine = get_inference_engine()
    postprocessor = get_postprocessor()
    decision_engine = get_decision_engine()
    result_builder = get_result_builder()
    plc_service = get_plc_service()
    metrics_service = get_metrics_service()

    # 3. Vision Pipeline
    # Inference
    try:
        inf_start = time.perf_counter()
        raw_output = inference_engine.predict(img)
        inf_end = time.perf_counter()
        metrics_service.record_inference_latency(inf_end - inf_start)
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        metrics_service.record_pipeline_error("inference")
        metrics_service.record_inspection(success=False)
        raise ApplicationError(f"Inference failed: {e}") from e

    # Postprocess
    detections_model_space = postprocessor.process(raw_output)

    # Transform coordinates
    coord_transformer = CoordinateTransformer((orig_w, orig_h), inference_engine.imgsz)
    detections_orig_space = []
    for det in detections_model_space:
        x1, y1, x2, y2 = coord_transformer.transform(det.x1, det.y1, det.x2, det.y2)
        det.x1, det.y1, det.x2, det.y2 = x1, y1, x2, y2
        detections_orig_space.append(det)

    # 4. Decision Engine
    try:
        decision_result = decision_engine.evaluate(detections_orig_space)
        metrics_service.record_decision(decision_result.decision.name)
    except Exception as e:
        metrics_service.record_pipeline_error("decision")
        metrics_service.record_inspection(success=False)
        raise
        
    # 5. Defect Mapping
    try:
        inspection_result = result_builder.build(
            frame=img,
            detections=detections_orig_space,
            decision_result=decision_result,
            source_id="api_upload",
        )
        for defect in inspection_result.defects:
            metrics_service.record_defect(defect.original_detection.get("class_name", "unknown"))
    except Exception as e:
        metrics_service.record_pipeline_error("mapping")
        metrics_service.record_inspection(success=False)
        raise

    # 6. PLC Dispatch
    plc_dispatch_info = PLCDispatchInfo(enabled=False, dispatched=False)
    if plc_service is not None:
        plc_dispatch_info.enabled = True
        try:
            plc_response = plc_service.process_inspection(inspection_result)
            plc_dispatch_info.dispatched = True
            plc_status = (
                plc_response.status.name
                if hasattr(plc_response.status, "name")
                else str(plc_response.status)
            )
            plc_dispatch_info.status = plc_status
            plc_dispatch_info.message = plc_response.message
            metrics_service.record_plc_command(
                command=plc_response.command_id or "unknown", 
                success=plc_response.success
            )
        except Exception as e:
            logger.error(f"PLC dispatch failed: {e}")
            plc_dispatch_info.status = "ERROR"
            plc_dispatch_info.message = str(e)
            metrics_service.record_pipeline_error("plc")
            metrics_service.record_plc_command(command="unknown", success=False)

    # Calculate Latency
    end_time = time.perf_counter()
    duration_s = end_time - start_time
    latency_ms = duration_s * 1000.0
    
    metrics_service.record_pipeline_latency(duration_s)
    metrics_service.record_inspection(success=True)

    # Build response
    defects_resp = []
    for d in inspection_result.defects:
        defects_resp.append(
            DefectSchema(
                class_name=d.original_detection.get("class_name", "unknown"),
                confidence=d.original_detection.get("confidence", 0.0),
                bbox=BBox(
                    x1=d.original_detection["bbox"][0],
                    y1=d.original_detection["bbox"][1],
                    x2=d.original_detection["bbox"][2],
                    y2=d.original_detection["bbox"][3],
                ),
                region=(
                    d.spatial_region.name
                    if hasattr(d.spatial_region, "name")
                    else str(d.spatial_region)
                ),
            )
        )

    response = InspectionResponse(
        inspection_id=inspection_id,
        decision=decision_result.decision.name,
        severity=decision_result.severity.name,
        summary=InspectionSummary(
            total_defects=decision_result.total_defects,
            affected_classes=decision_result.affected_classes,
        ),
        defects=defects_resp,
        latency_ms=latency_ms,
        plc=plc_dispatch_info,
    )

    return response
