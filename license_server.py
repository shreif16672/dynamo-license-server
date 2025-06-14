# license_server.py

from flask import Flask, request, send_file, jsonify, render_template_string, redirect
from openpyxl import load_workbook
import os
import json
from datetime import datetime

app = Flask(__name__)

TEMPLATE_FILE = "template.xlsm"
OUTPUT_DIR = "generated"
ALLOWED_IDS_FILE = "allowed_ids.json"
PENDING_IDS_FILE = "pending_ids.json"

# Load machine IDs from a JSON file
def load_ids(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

# Save machine IDs to a JSON file
def save_ids(file_path, ids):
    with open(file_path, "w") as f:
        json.dump(ids, f)

# Generate password based on same VBA logic
def generate_password(machine_id):
    seed = 12345
    for c in machine_id:
        seed += ord(c)
    return f"PWD{seed}"

@app.route("/request", methods=["POST"])
def request_access():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()

    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    pending_ids = load_ids(PENDING_IDS_FILE)
    if machine_id not in pending_ids:
        pending_ids.append(machine_id)
        save_ids(PENDING_IDS_FILE, pending_ids)

    return jsonify({"status": "Request received. Waiting for approval."})

@app.route("/admin")
def admin():
    pending = load_ids(PENDING_IDS_FILE)
    allowed = load_ids(ALLOWED_IDS_FILE)

    html = """
    <html>
    <head><title>License Requests</title></head>
    <body style='font-family:Arial;'>
        <h2>Pending Machine ID Requests</h2>
        {% if pending %}
            <ul>
            {% for mid in pending %}
                <li>{{ mid }} <a href='/approve/{{ mid }}'>✅ Approve</a></li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No pending requests.</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, pending=pending)

@app.route("/approve/<machine_id>")
def approve(machine_id):
    machine_id = machine_id.strip()
    if not machine_id:
        return "Invalid ID", 400

    pending_ids = load_ids(PENDING_IDS_FILE)
    allowed_ids = load_ids(ALLOWED_IDS_FILE)

    if machine_id in pending_ids:
        pending_ids.remove(machine_id)
        save_ids(PENDING_IDS_FILE, pending_ids)

    if machine_id not in allowed_ids:
        allowed_ids.append(machine_id)
        save_ids(ALLOWED_IDS_FILE, allowed_ids)

    return redirect("/admin")

@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id", "").strip()

    if not machine_id:
        return jsonify({"error": "Missing machine ID"}), 400

    allowed_ids = load_ids(ALLOWED_IDS_FILE)
    if machine_id not in allowed_ids:
        return jsonify({"error": "Machine ID not approved."}), 403

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
    app.run(debug=True, host="0.0.0.0", port=10000)
