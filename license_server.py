from flask import Flask, request, jsonify, render_template_string, send_file
import os
import json
from datetime import datetime, timedelta
import hashlib
import hmac
import shutil

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = "xlsm-secret"

PROGRAM_CONFIGS = {
    "xlsm_tool": {
        "pending_file": os.path.join(BASE_DIR, "pending_ids_xlsm_tool.json"),
        "allowed_file": os.path.join(BASE_DIR, "allowed_ids_xlsm_tool.json"),
        "template_file": os.path.join(BASE_DIR, "template.xlsm"),
    }
}

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

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
        # Only for xlsm_tool, return .xlsm file
        if program_id == "xlsm_tool":
            template = config["template_file"]
            output = os.path.join(BASE_DIR, f"QTY_Network_2025_{machine_id}.xlsm")
            if not os.path.exists(template):
                return "Template file not found", 500
            shutil.copy(template, output)
            return send_file(output, as_attachment=True)

        # If other program, return JSON payload
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

    # Not approved, save to pending
    pending[machine_id] = {"program_id": program_id, "duration": duration}
    save_json(config["pending_file"], pending)
    return "Request submitted and pending approval.", 202

@app.route("/admin/<program_id>", methods=["GET", "POST"])
def admin_panel(program_id):
    config = PROGRAM_CONFIGS.get(program_id)
    if not config:
        return "Invalid program_id", 404

    pending = load_json(config["pending_file"])
    allowed = load_json(config["allowed_file"])

    if request.method == "POST":
        action = request.form.get("action")
        machine_id = request.form.get("machine_id")
        if action == "approve" and machine_id in pending:
            allowed[machine_id] = pending.pop(machine_id)
            save_json(config["allowed_file"], allowed)
            save_json(config["pending_file"], pending)
        elif action == "reject" and machine_id in pending:
            pending.pop(machine_id)
            save_json(config["pending_file"], pending)

    html = """
    <h1>{{ program_id }} License Admin</h1>
    <h2>Pending Requests</h2>
    {% if pending %}
        <ul>
        {% for machine_id in pending %}
            <li>
                <strong>{{ machine_id }}</strong>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="machine_id" value="{{ machine_id }}">
                    <button type="submit" name="action" value="approve">✅ Approve</button>
                    <button type="submit" name="action" value="reject">❌ Reject</button>
                </form>
            </li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No pending requests.</p>
    {% endif %}

    <h2>Approved Machines</h2>
    {% if allowed %}
        <ul>
        {% for machine_id in allowed %}
            <li>{{ machine_id }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No approved machines.</p>
    {% endif %}
    """
    return render_template_string(html, program_id=program_id, pending=pending, allowed=allowed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
