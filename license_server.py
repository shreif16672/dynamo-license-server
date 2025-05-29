from flask import Flask, request, send_file, jsonify
import json
import time
import os
from datetime import datetime

app = Flask(__name__)

TEMPLATE_FILE = "protected_template.dyn"
OUTPUT_FOLDER = "generated_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/generate", methods=["POST"])
def generate_dynamo():
    try:
        data = request.get_json()
        mac = data["machine_id"]
        start_time = data["start_timestamp"]
        duration = data["duration_seconds"]

        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            dyn_data = json.load(f)

        # Replace placeholders in script
        for node in dyn_data.get("Nodes", []):
            if "Code" in node and isinstance(node["Code"], str) and "TO_BE_REPLACED" in node["Code"]:
                node["Code"] = node["Code"].replace("TO_BE_REPLACED", mac, 1)
                node["Code"] = node["Code"].replace("TO_BE_REPLACED", str(start_time), 1)
                node["Code"] = node["Code"].replace("TO_BE_REPLACED", str(duration), 1)
                break

        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(OUTPUT_FOLDER, f"license_{mac}_{timestamp_str}.dyn")

        with open(output_path, "w", encoding="utf-8") as out_file:
            json.dump(dyn_data, out_file, indent=2)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
