
# protected_script06.py

import json
import os
import sys

# License check
license_path = os.path.join(os.environ["APPDATA"], "DynamoLicense", "license.txt")
expected_license = "LICENSE-VALID-1234567890"

if not os.path.exists(license_path):
    print("License file not found.")
    sys.exit(1)

with open(license_path, "r") as f:
    if f.read().strip() != expected_license:
        print("Invalid license.")
        sys.exit(2)

# File paths
base_path = os.path.dirname(sys.argv[0])
networks_path = os.path.join(base_path, "input", "networks.json")
counts_path = os.path.join(base_path, "input", "structure_counts.json")
output_path = os.path.join(base_path, "output", "filtered_networks.json")

# Read inputs
with open(networks_path, "r") as f:
    networks = json.load(f)
with open(counts_path, "r") as f:
    counts = json.load(f)

# Filter
valid_indexes = [i for i, count in enumerate(counts) if count > 1]
valid_names = [networks[i] for i in valid_indexes]

# Write output
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump({
        "indexes": valid_indexes,
        "names": valid_names
    }, f, indent=2)
