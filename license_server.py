from flask import Flask, request, jsonify, render_template_string
import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), "PipeNetworkProject")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

PROGRAM_CONFIGS = {
    "pipe_network": {
        "pending_file": os.path.join(BASE_DIR, "pending_ids_pipe_network.json"),
        "allowed_file": os.path.join(BASE_DIR, "allowed_ids_pipe_network.json"),
    },
    "xlsm_tool": {
        "pending_file": "pending_ids_xlsm_tool.json",
        "allowed_file": "allowed_ids_xlsm_tool.json",
    }
}

SECRET_KEY = "MySecretKeyForHMAC"

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    machine_id = data.get("machine_id")
    program_id = data.get("program_id")
    duration = data.get("duration")

    if not all([machine_id, program_id]):
        return "Missing required fields", 400

    config = PROGRAM_CONFIGS.get(program_id)
    if not config:
        return "Invalid program_id", 400

    pending = load_json(config["pending_file"])
    allowed = load_json(config["allowed_file"])

    if machine_id in allowed:
        expiry = None
        if duration:
            expiry = (datetime.utcnow() + timedelta(hours=int(duration))).isoformat()
        payload = {
            "machine_id": machine_id,
            "program_id": program_id,
            "expiry": expiry
        }
        signature = hmac.new(SECRET_KEY.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
        payload["signature"] = signature
        return jsonify(payload)

    pending[machine_id] = {"program_id": program_id, "duration": duration}
    save_json(config["pending_file"], pending)
    return "Request submitted and pending approval.", 202

@app.route("/validate_pipe_network", methods=["POST"])
def validate_pipe_network():
    data = request.json
    machine_id = data.get("machine_id")
    program_id = "pipe_network"

    config = PROGRAM_CONFIGS[program_id]
    allowed = load_json(config["allowed_file"])

    record = allowed.get(machine_id)
    if not record:
        return jsonify({"valid": False, "reason": "Not allowed"}), 403

    expiry = record.get("expiry")
    if expiry:
        if datetime.utcnow() > datetime.fromisoformat(expiry):
            return jsonify({"valid": False, "reason": "License expired"}), 403

    return jsonify({"valid": True})

@app.route("/admin/<program_id>")
def admin_view(program_id):
    config = PROGRAM_CONFIGS.get(program_id)
    if not config:
        return f"Invalid program_id: {program_id}", 404

    pending = load_json(config["pending_file"])
    allowed = load_json(config["allowed_file"])

    html = f"<h1>{program_id.replace('_', ' ').title()} License Requests</h1>"
    html += "<h2>Pending</h2>"
    if pending:
        html += "<ul>"
        for mid in pending:
            html += f"<li>{mid}</li>"
        html += "</ul>"
    else:
        html += "<p>No pending requests.</p>"

    html += "<h2>Approved</h2>"
    if allowed:
        html += "<ul>"
        for mid in allowed:
            html += f"<li>{mid}</li>"
        html += "</ul>"
    else:
        html += "<p>No approved machines.</p>"

    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
