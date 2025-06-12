from flask import Flask, request, send_file, jsonify
from openpyxl import load_workbook
import os
import json
from datetime import datetime

app = Flask(__name__)

TEMPLATE_FILE = "template.xlsm"
OUTPUT_DIR = "generated"
USED_IDS_FILE = "used_ids.json"

# -------------------------------
# Machine ID usage tracking
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
# Simple password logic
# Must match your VBA logic
# -------------------------------
def generate_password(machine_id):
    return str(sum(ord(c) for c in machine_id) * 7 % 100000)

# -------------------------------
# License generation endpoint
# -------------------------------
@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()

    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    used_ids = load_used_ids()
    if machine_id in used_ids:
        return jsonify({"error": "License already generated for this machine."}), 403

    # Prepare new file path
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"QTY_Network_2025_{timestamp}.xlsm")

    # Load template
    wb = load_workbook(TEMPLATE_FILE, keep_vba=True)
    ws = wb["LicenseData"]
    ws["A1"] = machine_id
    ws["A2"] = generate_password(machine_id)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    wb.save(output_file)

    save_used_id(machine_id)

    return send_file(output_file, as_attachment=True)

# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
