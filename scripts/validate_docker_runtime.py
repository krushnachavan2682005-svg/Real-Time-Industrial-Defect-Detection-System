import subprocess
import json
import time
import requests
import sys

def check_docker_available():
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def validate_docker_runtime():
    if not check_docker_available():
        print(json.dumps({"status": "SKIPPED", "reason": "Docker daemon unavailable"}))
        return "SKIPPED"
    
    print("Docker is available. Testing runtime...", file=sys.stderr)
    
    # Normally we would do `docker compose up -d` and test the endpoints,
    # but that might be heavy or complex depending on the docker setup.
    # For a minimal runtime smoke test:
    try:
        # Start only the API to keep it light
        subprocess.run(["docker", "compose", "-f", "deployment/docker/docker-compose.yml", "up", "-d", "api"], 
                       check=True, capture_output=True)
        
        # Wait for health
        api_url = "http://localhost:8000"
        healthy = False
        for _ in range(15): # wait up to 15s
            try:
                resp = requests.get(f"{api_url}/health", timeout=1)
                if resp.status_code == 200:
                    healthy = True
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
            
        # Stop container
        subprocess.run(["docker", "compose", "-f", "deployment/docker/docker-compose.yml", "down"], 
                       capture_output=True)
                       
        if healthy:
            print(json.dumps({"status": "PASS", "reason": "Container started and responded to health check"}))
            return "PASS"
        else:
            print(json.dumps({"status": "FAIL", "reason": "Container did not become healthy in time"}))
            return "FAIL"
            
    except subprocess.CalledProcessError as e:
        print(json.dumps({"status": "FAIL", "reason": f"Docker compose command failed: {e}"}))
        return "FAIL"

if __name__ == "__main__":
    validate_docker_runtime()
