import argparse
import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.evaluation.evaluator import ModelEvaluator

def main():
    parser = argparse.ArgumentParser(description="Run model evaluation on validation or test split.")
    parser.add_argument("--split", type=str, choices=["val", "test"], required=True, 
                        help="Dataset split to evaluate on (val or test)")
    parser.add_argument("--config", type=str, default="configs/evaluation/evaluation.yaml",
                        help="Path to evaluation config file")
    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    print(f"Starting evaluation on '{args.split}' split using model '{config['model_path']}'")
    
    evaluator = ModelEvaluator(
        model_path=config['model_path'],
        dataset_yaml=config['dataset_yaml']
    )
    
    results = evaluator.evaluate(
        split=args.split,
        output_dir=config['evaluation_dir'],
        conf_threshold=config.get('confidence_threshold', 0.25),
        iou_threshold=config.get('iou_threshold', 0.50)
    )
    
    print("\nGlobal Metrics:")
    for k, v in results['global_metrics'].items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
            
    print(f"\nEvaluation complete. Results saved to {config['evaluation_dir']}")

if __name__ == "__main__":
    main()
