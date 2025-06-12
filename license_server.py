from flask import Flask, request, send_file, jsonify
from openpyxl import load_workbook
import os, shutil
from datetime import datetime

app = Flask(__name__)

TEMPLATE_PATH = "template.xlsm"
OUTPUT_DIR = "output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_password(machine_id):
    seed = 12345
    for char in machine_id:
        seed += ord(char)
    return "PWD" + str(seed)

@app.route('/generate', methods=['POST'])
def generate_license():
    data = request.get_json()
    machine_id = data.get("machine_id")

    if not machine_id:
        return jsonify({"error": "Missing machine_id"}), 400

    password = generate_password(machine_id)

    # Create timestamped file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"licensed_{timestamp}.xlsm")

    shutil.copyfile(TEMPLATE_PATH, output_file)

    try:
        wb = load_workbook(output_file, keep_vba=True)

        if "LicenseData" not in wb.sheetnames:
            ws = wb.create_sheet("LicenseData")
        else:
            ws = wb["LicenseData"]

        ws["A1"] = machine_id
        ws["A2"] = password

        wb.save(output_file)
        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
