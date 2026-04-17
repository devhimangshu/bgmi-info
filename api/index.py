import requests
import json
import time
from urllib.parse import unquote
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================
# TOKEN CACHE
# ============================

token_cache = {
    "token": None,
    "time": 0
}

# ============================
# GET TOKEN (WITH CACHE)
# ============================

def get_cached_token(session):
    global token_cache

    # reuse token for 10 minutes
    if token_cache["token"] and (time.time() - token_cache["time"] < 600):
        return token_cache["token"]

    url = "https://www.rooter.gg/"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }

    response = session.get(url, headers=headers, timeout=5)

    user_auth = session.cookies.get("user_auth")
    if not user_auth:
        return None

    try:
        access_token_json = unquote(user_auth)
        access_token_data = json.loads(access_token_json)

        token = access_token_data.get("accessToken")

        token_cache["token"] = token
        token_cache["time"] = time.time()

        return token
    except:
        return None


# ============================
# BGMI FETCH
# ============================

def get_bgmi_username(user_id):
    session = requests.Session()

    access_token = get_cached_token(session)

    if not access_token:
        return {"error": "Token fetch failed"}

    url = f"https://bazaar.rooter.io/order/getUnipinUsername?gameCode=BGMI_IN&id={user_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()

        if data.get("transaction") == "SUCCESS":
            return {
                "username": data['unipinRes']['username'],
                "uid": user_id
            }
        else:
            return {"error": data.get("message", "Unknown error")}

    except:
        return {"error": "Request failed"}


# ============================
# ROUTES
# ============================

@app.route("/")
def home():
    return "BGMI API Running"

@app.route("/api")
def api():
    uid = request.args.get("uid")

    if not uid:
        return jsonify({"error": "UID is required"}), 400

    result = get_bgmi_username(uid)
    return jsonify(result)
