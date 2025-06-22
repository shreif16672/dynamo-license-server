import os
import json
import uuid
import hashlib
import requests

# === SETTINGS ===
program_id = "pipe_network"
SERVER_URL = "https://dynamo-license-server.onrender.com/validate"

# === Detect Machine ID ===
def get_machine_id():
    return hex(uuid.getnode()).replace("0x", "").upper()

machine_id = get_machine_id()

# === Send to server ===
payload = {
    "machine_id": machine_id,
    "program_id": program_id
}

try:
    response = requests.post(SERVER_URL, json=payload)
    if response.status_code == 200:
        license_data = response.json()

        # === Write license file to standard location ===
        license_dir = os.path.join(os.environ["APPDATA"], "DynamoLicense")
        os.makedirs(license_dir, exist_ok=True)
        license_path = os.path.join(license_dir, "license.txt")

        with open(license_path, "w") as f:
            json.dump(license_data, f, indent=2)

        print(f"✅ License saved to: {license_path}")
    else:
        print(f"❌ License request rejected: {response.text}")
except Exception as e:
    print(f"❌ License server unreachable: {e}")