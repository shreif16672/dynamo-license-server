from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMIN_PASSWORD = "admin123"

def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

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
        return "VALID"

    pending = load_json(pending_file)
    pending[machine_id] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    save_json(pending_file, pending)
    return "Machine ID pending approval", 403

@app.route("/admin-panel", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password != ADMIN_PASSWORD:
            return "<h3>Access denied</h3>"

        action = request.form.get("action")
        machine_id = request.form.get("machine_id")
        program_id = request.form.get("program_id")

        pending_path = get_file_path(f"PipeNetworkProject/pending_ids_{program_id}.json")
        allowed_path = get_file_path(f"PipeNetworkProject/allowed_ids_{program_id}.json")

        pending = load_json(pending_path)
        allowed = load_json(allowed_path)

        if action == "approve":
            allowed[machine_id] = datetime.utcnow().strftime("%Y-%m-%d")
            pending.pop(machine_id, None)
            save_json(pending_path, pending)
            save_json(allowed_path, allowed)
        elif action == "reject":
            pending.pop(machine_id, None)
            save_json(pending_path, pending)

        return redirect(url_for('admin_panel'))

    table_html = ""
    for fname in os.listdir(get_file_path("PipeNetworkProject")):
        if fname.startswith("pending_ids_") and fname.endswith(".json"):
            program = fname.replace("pending_ids_", "").replace(".json", "")
            fpath = get_file_path(f"PipeNetworkProject/{fname}")
            pending = load_json(fpath)
            if pending:
                table_html += f"<h3>{program}</h3><ul>"
                for mid, timestamp in pending.items():
                    table_html += f"""
<li>
    {mid} -> {timestamp}
    <form method="POST" style="display:inline;">
        <input type="hidden" name="password" value="{ADMIN_PASSWORD}">
        <input type="hidden" name="machine_id" value="{mid}">
        <input type="hidden" name="program_id" value="{program}">
        <button name="action" value="approve">Approve</button>
        <button name="action" value="reject">Reject</button>
    </form>
</li>
"""
                table_html += "</ul>"

    if not table_html:
        table_html = "<p>No pending requests.</p>"

    return f"<h1>License Admin Panel</h1>{table_html}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
