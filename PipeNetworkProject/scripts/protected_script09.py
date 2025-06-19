
# protected_script09.py

import json
import os
import sys

# License validation
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
base = os.path.dirname(sys.argv[0])
group_path = os.path.join(base, "input", "structure_name_groups.json")
count_path = os.path.join(base, "input", "structure_counts.json")
output_path = os.path.join(base, "output", "valid_connections.json")

# Load inputs
with open(group_path, "r") as f:
    structure_groups = json.load(f)
with open(count_path, "r") as f:
    structure_counts = json.load(f)

# Flatten structures and isolate singles
all_names = []
single_names = []

for i, group in enumerate(structure_groups):
    if not isinstance(group, list):
        group = [group]
    all_names.extend(group)
    if structure_counts[i] == 1:
        single_names.append(group[0])

# Parent-finding logic
def is_valid_connection(child, parent):
    child_parts = child.split('-')
    parent_parts = parent.split('-')
    if len(parent_parts) != len(child_parts) - 1:
        return False
    return all(parent_parts[i] == child_parts[i] for i in range(len(parent_parts)))

connections = []
for child in single_names:
    if '-' not in child:
        continue
    parent_pattern = '-'.join(child.split('-')[:-1])
    for candidate in all_names:
        if candidate == parent_pattern and is_valid_connection(child, candidate):
            connections.append({
                "child": child,
                "parent": candidate,
                "relationship": f"{child} → {candidate}"
            })
            break

# Save output
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w") as f:
    json.dump(connections, f, indent=2)
