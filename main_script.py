import json
import hashlib
import os

# === CONFIGURATION ===
machine_id = "BUYER_ID_HERE"  # Replace with actual buyer machine ID
program_id = "pipe_network"
expiry = None  # Use None for lifetime license

# === SIGNATURE GENERATION ===
def generate_signature(machine_id, program_id, expiry):
    raw = f"{machine_id}|{program_id}|{expiry if expiry else 'lifetime'}"
    return hashlib.sha256(raw.encode()).hexdigest()

signature = generate_signature(machine_id, program_id, expiry)

# === LICENSE DATA STRUCTURE ===
license_data = {
    "machine_id": machine_id,
    "program_id": program_id,
    "expiry": expiry,
    "signature": signature
}

# === OUTPUT FILE LOCATION ===
license_dir = os.path.join(os.environ["APPDATA"], "DynamoLicense")
os.makedirs(license_dir, exist_ok=True)
license_path = os.path.join(license_dir, "license.txt")

# === WRITE TO FILE ===
with open(license_path, "w") as f:
    json.dump(license_data, f, indent=2)

print(f"✅ License written to: {license_path}")