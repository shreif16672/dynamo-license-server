import os
import json
import sys

# License check
def get_license_path():
    return os.path.join(os.getenv("APPDATA"), "DynamoLicense", "license.txt")

def is_license_valid():
    expected = "LICENSE-VALID-1234567890"
    lp = get_license_path()
    if not os.path.exists(lp):
        print("❌ License file not found.")
        return False
    return open(lp).read().strip() == expected

if not is_license_valid():
    print("⛔ Invalid or missing license.")
    exit(1)

# --- Resolve dynamic project path ---
current_dir = os.path.dirname(sys.argv[0])  # Folder where the EXE is located
input_folder = os.path.join(current_dir, "input")
config_file = os.path.join(input_folder, "project_path.txt")

# Create input folder and project_path.txt if not found
os.makedirs(input_folder, exist_ok=True)
if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        f.write(current_dir)
    print(f"ℹ️ Created project_path.txt with: {current_dir}")

# Read the path from config
with open(config_file, "r") as f:
    project_path = f.read().strip()

# --- Load mtext_data.json ---
mtext_path = os.path.join(project_path, "input", "mtext_data.json")
grouped_path = os.path.join(project_path, "input", "grouped_data.json")

if not os.path.exists(mtext_path):
    print("❌ mtext_data.json not found.")
    exit(1)

with open(mtext_path, "r") as f:
    data = json.load(f)

# Example processing: convert each entry to grouped structure
grouped = []
for entry in data:
    grouped.append({
        "Name": entry.get("Contents", ""),
        "E": entry["Location"]["X"],
        "N": entry["Location"]["Y"]
    })

with open(grouped_path, "w") as f:
    json.dump(grouped, f, indent=2)

print("✅ grouped_data.json created successfully.")