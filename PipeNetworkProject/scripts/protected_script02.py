
# protected_script02.py

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
input_path = os.path.join(base_path, "input", "grouped_data.json")
output_path = os.path.join(base_path, "output", "first_names.json")

# Load input
with open(input_path, "r") as f:
    grouped_data = json.load(f)

# Process
first_names = [group["Name"][0] for group in grouped_data if group["Name"]]

# Save output
with open(output_path, "w") as f:
    json.dump(first_names, f, indent=2)
