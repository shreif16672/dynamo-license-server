from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import os, json, hashlib
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "secret-signature-key"  # must match client

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def create_signature(data: dict) -> str:
    msg = f"{data['machine_id']}{data['program_id']}{data['expiry']}"
    return hashlib.sha256((msg + SECRET_KEY).encode()).hexdigest()

@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id")
    program_id = data.get("program_id", "default")
    if not machine_id or not program_id:
        return "Invalid request", 400

    allowed_file = get_file_path(f"PipeNetworkProject/allowed_ids_{program_id}.json")
    pending_file = get_file_path(f"PipeNetworkProject/pending_ids_{program_id}.json")

    allowed = load_json(allowed_file)
    if machine_id in allowed:
        expiry = allowed[machine_id]
        payload = {
            "machine_id": machine_id,
            "program_id": program_id,
            "expiry": expiry,
        }
        payload["signature"] = create_signature(payload)
        return jsonify(payload)

    # Not allowed yet → add to pending
    pending = load_json(pending_file)
    if machine_id not in pending:
        pending[machine_id] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        save_json(pending_file, pending)

    return "Machine ID pending approval", 403

@app.route("/validate_pipe_network", methods=["POST"])
def validate_pipe_network():
    data = request.get_json()
    machine_id = data.get("machine_id")
    program_id = "pipe_network"
    signature = data.get("signature")
    expiry = data.get("expiry")

    expected = {
        "machine_id": machine_id,
        "program_id": program_id,
        "expiry": expiry
    }
    expected_signature = create_signature(expected)

    if signature != expected_signature:
        return "Invalid license", 403

    # Optional: check expiry
    if expiry is not None and expiry < datetime.utcnow().isoformat():
        return "License expired", 403

    return "VALID", 200

@app.route("/admin/pipe_network")
def admin_pipe_network():
    pending_file = get_file_path("PipeNetworkProject/pending_ids_pipe_network.json")
    allowed_file = get_file_path("PipeNetworkProject/allowed_ids_pipe_network.json")

    pending = load_json(pending_file)
    allowed = load_json(allowed_file)

    html = "<h1>Pipe Network License Requests</h1><h2>Pending</h2><ul>"
    for mid, time in pending.items():
        html += f"<li>{mid} — {time}</li>"
    html += "</ul><h2>Approved</h2><ul>"
    for mid, exp in allowed.items():
        html += f"<li>{mid} — {exp}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
