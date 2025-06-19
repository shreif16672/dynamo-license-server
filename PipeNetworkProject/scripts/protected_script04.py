
# protected_script04.py

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

# Paths
base_path = os.path.dirname(sys.argv[0])
input_path = os.path.join(base_path, "input", "group_items.json")
output_path = os.path.join(base_path, "output", "count_results.json")

# Read input
with open(input_path, "r") as f:
    input_data = json.load(f)

# Process
counts = []
for item in input_data:
    if isinstance(item, list):
        counts.append(len(item))
    else:
        counts.append(1 if item is not None else 0)

# Save output
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(counts, f, indent=2)
