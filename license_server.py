from flask import Flask, request, send_file, jsonify
from openpyxl import load_workbook
import os
import json
from datetime import datetime

app = Flask(__name__)

# Constants for file paths
TEMPLATE_FILE = "template.xlsm"
OUTPUT_DIR = "generated"
USED_IDS_FILE = "used_ids.json"

# -------------------------------
# Functions to track used machine IDs
# -------------------------------
def load_used_ids():
    if not os.path.exists(USED_IDS_FILE):
        return []
    with open(USED_IDS_FILE, "r") as f:
        return json.load(f)

def save_used_id(machine_id):
    used_ids = load_used_ids()
    used_ids.append(machine_id)
    with open(USED_IDS_FILE, "w") as f:
        json.dump(used_ids, f)

# -------------------------------
# Updated password generation function:
# This exactly mimics your VBA function:
#   Seed = 12345, and then for each character in machineID, add Asc(character)
#   Finally, Password = "PWD" & Seed
# -------------------------------
def generate_password(machine_id):
    seed = 12345
    for c in machine_id:
        seed += ord(c)
    return "PWD" + str(seed)

# -------------------------------
# License generation endpoint
# -------------------------------
@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()

    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    # For our fully automatic system, allow the download regardless,
    # but store the ID so that the same machine can re-download if needed.
    used_ids = load_used_ids()
    if machine_id not in used_ids:
        save_used_id(machine_id)

    if not os.path.exists(TEMPLATE_FILE):
        return jsonify({"error": "Template file not found."}), 500

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"QTY_Network_2025_{timestamp}.xlsm")

    # Load the template with macros, fill in A1 and A2 on sheet "LicenseData"
    wb = load_workbook(TEMPLATE_FILE, keep_vba=True)
    ws = wb["LicenseData"]  # This sheet must exist in template.xlsm
    ws["A1"] = machine_id
    ws["A2"] = generate_password(machine_id)
    wb.save(output_file)

    return send_file(output_file, as_attachment=True)

# -------------------------------
# Run the server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
