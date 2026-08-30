import yaml
import os
import json
import datetime
import sys

def check_file_exists(path):
    if not os.path.exists(path):
        return "FAIL", f"File {path} does not exist."
    return "PASS", f"File {path} exists."

def check_file_non_empty(path):
    if not os.path.exists(path):
        return "FAIL", f"File {path} does not exist."
    if os.path.getsize(path) == 0:
        return "FAIL", f"File {path} is empty."
    return "PASS", f"File {path} is not empty."

def check_dir_exists(path):
    if not os.path.isdir(path):
        return "FAIL", f"Directory {path} does not exist."
    return "PASS", f"Directory {path} exists."

def check_config_value(file, key_path, allowed_values):
    if not os.path.exists(file):
        return "FAIL", f"Config file {file} does not exist."
    try:
        with open(file, 'r') as f:
            data = yaml.safe_load(f)
        
        keys = key_path.split('.')
        val = data
        for k in keys:
            val = val.get(k)
            if val is None:
                break
        
        if val in allowed_values or str(val).lower() in [str(v).lower() for v in allowed_values]:
            return "PASS", f"Config {key_path} has valid value: {val}."
        return "FAIL", f"Config {key_path} has invalid value: {val}. Allowed: {allowed_values}."
    except Exception as e:
        return "FAIL", f"Error reading config: {str(e)}"

def run_checks(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    results = []
    passed = 0
    failed = 0
    warnings = 0
    
    for category, checks in config.get("checks", {}).items():
        for check_name, check_data in checks.items():
            check_type = check_data["type"]
            status = "FAIL"
            message = "Unknown check type."
            
            if check_type == "file_exists":
                status, message = check_file_exists(check_data["path"])
            elif check_type == "file_non_empty":
                status, message = check_file_non_empty(check_data["path"])
            elif check_type == "dir_exists":
                status, message = check_dir_exists(check_data["path"])
            elif check_type == "config_value_check":
                status, message = check_config_value(check_data["file"], check_data["key"], check_data["allowed_values"])
            
            if status == "FAIL" and check_data.get("warning_only", False):
                status = "WARN"
                warnings += 1
            elif status == "PASS":
                passed += 1
            else:
                failed += 1
                
            results.append({
                "name": check_name,
                "category": category,
                "status": status,
                "message": message
            })
            
    overall_status = "READY"
    if failed > 0:
        overall_status = "NOT_READY"
    elif warnings > 0:
        overall_status = "READY_WITH_WARNINGS"
        
    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "overall_status": overall_status,
        "checks": results,
        "summary": {
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }
    }

def main():
    config_path = "configs/validation/production_readiness.yaml"
    output_path = "reports/production/production_readiness_report.json"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs("reports/benchmarks", exist_ok=True) # Ensure required dirs
    
    report = run_checks(config_path)
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(json.dumps(report, indent=2))
    print(f"\nProduction Readiness: {report['overall_status']}")
    
    if report['overall_status'] == "NOT_READY":
        sys.exit(1)

if __name__ == "__main__":
    main()
