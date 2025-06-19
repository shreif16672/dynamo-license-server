
# protected_script03.py

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
structures_path = os.path.join(base_path, "input", "structures.json")
cogo_names_path = os.path.join(base_path, "input", "cogo_names.json")
output_path = os.path.join(base_path, "output", "structure_name_result.json")

# Read input
with open(structures_path, "r") as f:
    structures = json.load(f)
with open(cogo_names_path, "r") as f:
    cogoNames = json.load(f)

# Logic
flat_structures = [item for sublist in structures for item in sublist] if isinstance(structures[0], list) else structures
flat_names = [item for sublist in cogoNames for item in sublist] if isinstance(cogoNames[0], list) else cogoNames

result_names = []
for i, structure in enumerate(flat_structures):
    if i < len(flat_names):
        result_names.append(flat_names[i])
    else:
        result_names.append("Structure-{}".format(i+1))

# Save result
with open(output_path, "w") as f:
    json.dump({
        "structures": flat_structures,
        "names": result_names
    }, f, indent=2)
