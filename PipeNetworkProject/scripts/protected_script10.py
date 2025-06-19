
# protected_script10.py

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
names_path = os.path.join(base_path, "input", "network_names.json")
counts_path = os.path.join(base_path, "input", "structure_counts.json")
output_path = os.path.join(base_path, "output", "filtered_names_small_groups.json")

# Read input
with open(names_path, "r") as f:
    network_names = json.load(f)
with open(counts_path, "r") as f:
    structure_counts = json.load(f)

# Filter names with structure count < 2
filtered_names = [name for name, count in zip(network_names, structure_counts) if count < 2]

# Save output
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(filtered_names, f, indent=2)
