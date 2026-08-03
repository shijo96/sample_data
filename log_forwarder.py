import sys
import requests
import os

def main():
    # URL provided by Ngrok or localtunnel that points to your Django server
    base_url = os.environ.get('SAFEOPS_URL') 
    workflow_id = os.environ.get('GITHUB_RUN_ID', 'local-run-123')
    
    if not base_url:
        print("SAFEOPS_URL not set. Skipping log forwarding.")
        # We still need to print the stdin to stdout so the pipeline continues normally
        for line in sys.stdin:
            print(line, end='')
        return

    print(f"SafeOps Log Forwarder Initialized. Sending to {base_url}/api/log/")
    
    # Read pipeline execution logs line by line in real-time
    for line in sys.stdin:
        # 1. Print the line so it still appears in GitHub Actions console
        print(line, end='')
        
        # 2. Forward the line to the SafeOps Desktop App
        try:
            payload = {
                'workflow': workflow_id,
                'log': line.strip()
            }
            response = requests.post(f"{base_url}/api/log/", json=payload, timeout=2)
            
            # 3. If SafeOps returns "Block" (Critical Vulnerability), fail the pipeline!
            data = response.json()
            if data.get('action') == 'Block':
                print("\n\n[SAFEOPS ALERT]: Critical vulnerability detected in logs!")
                print(f"[SAFEOPS ALERT]: {line.strip()}")
                print("[SAFEOPS ALERT]: Pipeline execution blocked.")
                sys.exit(1) # This fails the GitHub Action pipeline
                
        except requests.exceptions.RequestException:
            pass # Ignore connection errors to keep pipeline running if SafeOps is down

if __name__ == "__main__":
    main()
