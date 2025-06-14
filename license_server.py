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
PENDING_IDS_FILE = "pending_ids.json"
USED_IDS_FILE = "used_ids.json"

# Ensure necessary JSON files exist
def ensure_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)

for f in [ALLOWED_IDS_FILE, PENDING_IDS_FILE, USED_IDS_FILE]:
    ensure_json(f)

def load_ids(file):
    with open(file, 'r') as f:
        return json.load(f)

def save_ids(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# Password generation (must match VBA)
def generate_password(machine_id):
    seed = 12345
    for c in machine_id:
        seed += ord(c)
    return "PWD" + str(seed)

@app.route("/request", methods=["POST"])
def handle_request():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()
    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    pending = load_ids(PENDING_IDS_FILE)
    if machine_id not in pending:
        pending.append(machine_id)
        save_ids(PENDING_IDS_FILE, pending)

    return jsonify({"status": "Request received. Waiting for approval."}), 200

@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()
    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    allowed = load_ids(ALLOWED_IDS_FILE)
    if machine_id not in allowed:
        return jsonify({"error": "Machine ID not approved."}), 403

    used = load_ids(USED_IDS_FILE)
    if machine_id not in used:
        used.append(machine_id)
        save_ids(USED_IDS_FILE, used)

    if not os.path.exists(TEMPLATE_FILE):
        return jsonify({"error": "Template file not found."}), 500

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"QTY_Network_2025_{timestamp}.xlsm")

    wb = load_workbook(TEMPLATE_FILE, keep_vba=True)
    ws = wb["LicenseData"]
    ws["A1"] = machine_id
    ws["A2"] = generate_password(machine_id)
    wb.save(output_file)

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
