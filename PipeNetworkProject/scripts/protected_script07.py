
# protected_script07.py

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
input_path = os.path.join(base_path, "input", "structure_groups.json")
start_path = os.path.join(base_path, "output", "start_structures.json")
end_path = os.path.join(base_path, "output", "end_structures.json")

# Load structure_groups
with open(input_path, "r") as f:
    structure_groups = json.load(f)

start_structures = []
end_structures = []

for group in structure_groups:
    if len(group) > 1:
        start_structures.append(group[:-1])
        end_structures.append(group[1:])
    else:
        start_structures.append([])
        end_structures.append([])

# Save outputs
os.makedirs(os.path.dirname(start_path), exist_ok=True)
with open(start_path, "w") as f:
    json.dump(start_structures, f, indent=2)
with open(end_path, "w") as f:
    json.dump(end_structures, f, indent=2)
