
import os
import json
import hashlib
import requests
import validate_pipe_network

LICENSE_DIR = os.path.join(os.path.expanduser("~"), "C_Dynamo_Protect", "PipeNetworkProject")
LICENSE_PATH = os.path.join(LICENSE_DIR, "license.txt")
SERVER_URL = "https://dynamo-license-server.onrender.com/validate"
PROGRAM_ID = "pipe_network"

def get_machine_id():
    return hashlib.sha256(os.environ.get('COMPUTERNAME', 'UNKNOWN').encode()).hexdigest()

def request_license():
    machine_id = get_machine_id()
    data = {
        "machine_id": machine_id,
        "program_id": PROGRAM_ID
    }
    try:
        response = requests.post(SERVER_URL, json=data)
        print("📡 License request sent to server.")
        if response.status_code == 200:
            with open(LICENSE_PATH, "w") as f:
                f.write(response.text)
            print("✅ License file saved.")
        else:
            print("❌ Server rejected the request:", response.text)
    except Exception as e:
        print("❌ Failed to contact server:", str(e))

def main():
    os.makedirs(LICENSE_DIR, exist_ok=True)
    if not os.path.exists(LICENSE_PATH):
        print("🔒 No license file found. Sending request...")
        request_license()
        return

    if not validate_pipe_network.is_license_valid(LICENSE_PATH):
        print("🔒 Invalid license. Re-requesting...")
        request_license()
        return

    print("✅ License valid. Running protected script...")
    # (Here you can place the call to your protected logic or EXE)

if __name__ == "__main__":
    main()
