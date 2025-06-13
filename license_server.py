# license_server.py
from flask import Flask, request, send_file, jsonify
from openpyxl import load_workbook
import os
import json
from datetime import datetime

app = Flask(__name__)

# Constants
TEMPLATE_FILE = "template.xlsm"
OUTPUT_DIR = "generated"
ALLOWED_IDS_FILE = "allowed_ids.json"
USED_IDS_FILE = "used_ids.json"

# ---------------------- Helpers ----------------------
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def generate_password(machine_id):
    seed = 12345
    for c in machine_id:
        seed += ord(c)
    return "PWD" + str(seed)

# ---------------------- License Endpoint ----------------------
@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()

    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    allowed_ids = load_json(ALLOWED_IDS_FILE)
    used_ids = load_json(USED_IDS_FILE)

    # Automatically allow new machine IDs
    if machine_id not in allowed_ids:
        allowed_ids.append(machine_id)
        save_json(ALLOWED_IDS_FILE, allowed_ids)

    # Save usage (for tracking)
    if machine_id not in used_ids:
        used_ids.append(machine_id)
        save_json(USED_IDS_FILE, used_ids)

    if not os.path.exists(TEMPLATE_FILE):
        return jsonify({"error": "Template file not found."}), 500

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"QTY_Network_2025_{timestamp}.xlsm")

    # Inject license data
    wb = load_workbook(TEMPLATE_FILE, keep_vba=True)
    ws = wb["LicenseData"]
    ws["A1"] = machine_id
    ws["A2"] = generate_password(machine_id)
    wb.save(output_file)

    return send_file(output_file, as_attachment=True)

# ---------------------- Run Flask ----------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
