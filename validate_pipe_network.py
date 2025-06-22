
import json
import hashlib
import hmac

SECRET_KEY = b"super_secret_key_used_for_signing"

def is_license_valid(license_path):
    try:
        with open(license_path, "r") as f:
            data = json.load(f)

        payload = f"{data['machine_id']}|{data['program_id']}|{data['expiry']}"
        signature = hmac.new(SECRET_KEY, payload.encode(), hashlib.sha256).hexdigest()

        return signature == data.get("signature")
    except Exception as e:
        print("❌ License validation error:", str(e))
        return False
