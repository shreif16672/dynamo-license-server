
# protected_script08.py

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
networks_path = os.path.join(base_path, "input", "network_names.json")
structure_groups_path = os.path.join(base_path, "input", "structure_groups.json")
counts_path = os.path.join(base_path, "input", "structure_counts.json")
output_path = os.path.join(base_path, "output", "filtered_small_groups.json")

# Read inputs
with open(networks_path, "r") as f:
    networks = json.load(f)
with open(structure_groups_path, "r") as f:
    structure_groups = json.load(f)
with open(counts_path, "r") as f:
    structure_counts = json.load(f)

# Filter indexes where count < 2
valid_indexes = [i for i, count in enumerate(structure_counts) if count < 2]

# Get filtered groups
filtered_structure_groups = [structure_groups[i] for i in valid_indexes]

# Output
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(filtered_structure_groups, f, indent=2)
