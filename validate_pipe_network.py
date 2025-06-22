from flask import Flask, request, jsonify, abort

app = Flask(__name__)

@app.route("/validate", methods=["POST"])
def validate_license():
    data = request.get_json()
    mid = data.get("machine_id")
    pid = data.get("program_id")

    with open("allowed_ids_pipe_network.json") as f:
        allowed = json.load(f)

    if mid in allowed and allowed[mid] == pid:
        # Return a secure license payload
        license_json = {...}
        return jsonify(license_json), 200
    else:
        return abort(403, "Unauthorized")

# Other routes...

if __name__ == "__main__":
    app.run()