
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

@app.route("/generate", methods=["POST"])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id")
    program_id = data.get("program_id", "default")

    if not machine_id or not program_id:
        return "Invalid request", 400

    allowed_file = get_file_path(f"PipeNetworkProject/allowed_ids_{program_id}.json")
    pending_file = get_file_path(f"PipeNetworkProject/pending_ids_{program_id}.json")

    # Load allowed list
    allowed = {}
    if os.path.exists(allowed_file):
        with open(allowed_file, "r") as f:
            allowed = json.load(f)

    if machine_id in allowed:
        return "VALID"

    # Not allowed → Add to pending
    pending = {}
    if os.path.exists(pending_file):
        with open(pending_file, "r") as f:
            pending = json.load(f)

    pending[machine_id] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(pending_file, "w") as f:
        json.dump(pending, f, indent=2)

    return "Machine ID pending approval", 403

@app.route("/admin")
def view_all_pending():
    html = "<h1>Pending Machine ID Requests (All Programs)</h1><ul>"
    for fname in os.listdir(get_file_path("PipeNetworkProject")):
        if fname.startswith("pending_ids_") and fname.endswith(".json"):
            program = fname.replace("pending_ids_", "").replace(".json", "")
            fpath = get_file_path(f"PipeNetworkProject/{fname}")
            with open(fpath, "r") as f:
                data = json.load(f)
            html += f"<li><strong>{program}</strong>:<ul>"
            for mid, timestamp in data.items():
                html += f"<li>{mid} → {timestamp}</li>"
            html += "</ul></li>"
    html += "</ul>"
    return html

@app.route("/admin/<program_id>")
def view_program_pending(program_id):
    file_path = get_file_path(f"PipeNetworkProject/pending_ids_{program_id}.json")
    if not os.path.exists(file_path):
        return f"No pending requests for {program_id}", 404
    with open(file_path, "r") as f:
        data = json.load(f)
    html = f"<h1>Pending Requests for {program_id}</h1><ul>"
    for mid, timestamp in data.items():
        html += f"<li>{mid} → {timestamp}</li>"
    html += "</ul>"
    return html
