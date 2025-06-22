from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import os
import json
import hashlib
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

# (Keep /admin/<program_id> and /admin-panel as-is)
# ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
