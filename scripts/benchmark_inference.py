import argparse
import sys
import yaml
import os
import csv
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ultralytics import YOLO
from src.inference.benchmark import BenchmarkRunner, get_torch_sync_func
from src.inference.onnx_inference import ONNXInferenceWrapper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_test_image(img_dir: str) -> str:
    if os.path.exists(img_dir) and os.path.isdir(img_dir):
        for f in os.listdir(img_dir):
            if f.endswith(('.jpg', '.png', '.jpeg')):
                return os.path.join(img_dir, f)
    raise FileNotFoundError(f"No valid test image found in {img_dir}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark Inference Engines.")
    parser.add_argument("--config", type=str, default="configs/inference/export.yaml",
                        help="Path to export config file")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        
    model_path = config['model_path']
    base_name = os.path.splitext(os.path.basename(model_path))[0]
    onnx_path = os.path.join(config['onnx_output_dir'], f"{base_name}.onnx")
    
    test_img = get_test_image(config.get('benchmark', {}).get('test_image', 'data/processed/yolo/test/images/'))
    
    warmup = config.get('benchmark', {}).get('warmup_iterations', 20)
    iters = config.get('benchmark', {}).get('iterations', 100)
    
    runner = BenchmarkRunner(warmup_iterations=warmup, iterations=iters)
    results = []
    
    # 1. PyTorch CPU
    logger.info("Setting up PyTorch benchmark...")
    pt_model = YOLO(model_path)
    # Move to CPU explicitly if we are testing CPU
    # If testing CUDA, we would use pt_model.to('cuda')
    pt_func = lambda: pt_model.predict(source=test_img, verbose=False, device='cpu')
    res_pt = runner.run_benchmark("PyTorch (CPU, FP32)", pt_func)
    results.append(res_pt)
    
    # 2. ONNX Runtime CPU
    if os.path.exists(onnx_path):
        import cv2
        logger.info("Setting up ONNX Runtime CPU benchmark...")
        ort_wrapper = ONNXInferenceWrapper(onnx_path)
        img_bgr = cv2.imread(test_img)
        # Pre-process once to only measure inference time, OR measure with preprocessing?
        # Typically we measure end-to-end or just inference. For fairness with PyTorch YOLO.predict() 
        # which includes preprocessing, we could include it, but the wrapper predict() already includes it.
        ort_func = lambda: ort_wrapper.predict(img_bgr)
        res_onnx = runner.run_benchmark("ONNX Runtime (CPU, FP32)", ort_func)
        results.append(res_onnx)
    else:
        logger.warning(f"ONNX model not found at {onnx_path}, skipping ONNX benchmark.")
        
    # Save results
    report_dir = "reports/benchmarks"
    os.makedirs(report_dir, exist_ok=True)
    
    csv_path = os.path.join(report_dir, "inference_benchmark.csv")
    json_path = os.path.join(report_dir, "inference_benchmark.json")
    
    # Save CSV
    if results:
        keys = results[0].keys()
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    # Save JSON
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    logger.info(f"Benchmark completed. Results saved to {report_dir}")

if __name__ == "__main__":
    main()
