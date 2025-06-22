from flask import Flask, request, jsonify, render_template_string
import json
import os
import hashlib

app = Flask(__name__)

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "PipeNetworkProject")
ALLOWED_FILE = os.path.join(DATA_FOLDER, "allowed_ids_pipe_network.json")
PENDING_FILE = os.path.join(DATA_FOLDER, "pending_ids_pipe_network.json")

# Make sure data folder and files exist
os.makedirs(DATA_FOLDER, exist_ok=True)
for file_path in [ALLOWED_FILE, PENDING_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("{}")

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def hash_machine_id(machine_id):
    return hashlib.sha256(machine_id.encode()).hexdigest()

@app.route("/validate_pipe_network", methods=["POST"])
def validate_pipe_network():
    data = request.json
    machine_id = data.get("machine_id")
    program_id = data.get("program_id")
    expiry = data.get("expiry")

    if not machine_id or not program_id:
        return jsonify({"status": "error", "message": "Missing machine_id or program_id"}), 400

    hashed = hash_machine_id(machine_id)

    allowed = load_json(ALLOWED_FILE)
    if hashed in allowed:
        license_info = {
            "machine_id": machine_id,
            "program_id": program_id,
            "expiry": allowed[hashed].get("expiry"),
            "signature": allowed[hashed].get("signature", "")
        }
        return jsonify({"status": "approved", "license": license_info})

    # Add to pending if not already requested
    pending = load_json(PENDING_FILE)
    if hashed not in pending:
        pending[hashed] = {"machine_id": machine_id, "program_id": program_id, "expiry": expiry}
        save_json(PENDING_FILE, pending)

    return jsonify({"status": "pending"})

@app.route("/admin/pipe_network")
def admin_pipe_network():
    pending = load_json(PENDING_FILE)
    allowed = load_json(ALLOWED_FILE)

    html = """
    <h1>Pipe Network License Requests</h1>
    <h2>Pending</h2>
    <ul>
    {% for k, v in pending.items() %}
        <li><b>{{ v.machine_id }}</b> (Hash: {{ k }}) — Program: {{ v.program_id }}</li>
    {% else %}
        <li>No pending requests.</li>
    {% endfor %}
    </ul>
    <h2>Approved</h2>
    <ul>
    {% for k, v in allowed.items() %}
        <li><b>{{ v.machine_id }}</b> (Hash: {{ k }}) — Program: pipe_network</li>
    {% else %}
        <li>No approved machines.</li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, pending=pending, allowed=allowed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
