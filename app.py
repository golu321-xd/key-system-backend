from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)

DB_FILE = "keys.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    return json.load(open(DB_FILE))

def save_db(data):
    json.dump(data, open(DB_FILE, "w"))

@app.route("/")
def home():
    return "Backend running"

@app.route("/create_key", methods=["POST"])
def create_key():
    user = request.json.get("user")
    key = request.json.get("key")
    
    db = load_db()

    # Only 1 key per user
    if user in db:
        return jsonify({"error": "already_has_key"}), 400

    db[user] = {
        "key": key,
        "hwid": None,
        "expire": time.time() + 86400  # valid 24 hours
    }
    save_db(db)
    return {"status": "ok"}

@app.route("/lock_key", methods=["POST"])
def lock_key():
    key = request.json.get("key")
    hwid = request.json.get("hwid")

    db = load_db()

    for user, info in db.items():
        if info["key"] == key:
            if info["hwid"] is None:
                info["hwid"] = hwid
                save_db(db)
                return {"status": "locked"}
            else:
                return {"error": "already_locked"}, 400

    return {"error": "invalid_key"}, 400

@app.route("/check_key", methods=["POST"])
def check_key():
    key = request.json.get("key")
    hwid = request.json.get("hwid")

    db = load_db()

    for user, info in db.items():
        if info["key"] == key:
            if time.time() > info["expire"]:
                return {"error": "expired"}, 400

            if info["hwid"] is None:
                return {"error": "not_locked"}, 400

            if info["hwid"] != hwid:
                return {"error": "hwid_mismatch"}, 400

            return {"status": "ok"}

    return {"error": "invalid_key"}, 400
