import argparse
import sys
import yaml
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.vision.realtime_pipeline import RealTimePipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Real-Time Defect Detection Pipeline.")
    parser.add_argument("--config", type=str, default="configs/inference/realtime.yaml",
                        help="Path to realtime config file")
    parser.add_argument("--headless", action="store_true", help="Force headless mode")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    if args.headless:
        if 'display' not in config:
            config['display'] = {}
        config['display']['headless'] = True

    pipeline = RealTimePipeline(config)
    pipeline.run()
    
    # After pipeline finishes (e.g. video ends or user quits)
    # Generate performance report
    perf = pipeline.performance
    
    # Handle source type accurately for images
    src_type = "image" if pipeline.camera._is_image else config.get('source', {}).get('type')
    
    report = {
        "source_type": src_type,
        "source": config.get('source', {}).get('id') if src_type == 'camera' else config.get('source', {}).get('path'),
        "resolution": [pipeline.orig_w, pipeline.orig_h],
        "model": pipeline.inference_engine.model_path,
        "runtime": pipeline.inference_engine.providers,
        "image_size": pipeline.imgsz,
        "confidence_threshold": config.get('inference', {}).get('confidence_threshold'),
        "iou_threshold": config.get('inference', {}).get('iou_threshold'),
        "source_image_count": 1 if pipeline.camera._is_image else perf.frame_count,
        "benchmark_inference_iterations": max(0, perf.frame_count - perf.warmup_frames),
        "warmup_frames": perf.warmup_frames,
        "frames_processed": perf.frame_count,
        "average_inference_latency_ms": perf.get_avg_inference_latency(),
        "average_e2e_latency_ms": perf.get_avg_e2e_latency(),
        "average_fps": perf.get_fps()
    }
    
    report_dir = "reports/benchmarks"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "realtime_pipeline.json")
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Performance report saved to {report_path}")

if __name__ == "__main__":
    main()
