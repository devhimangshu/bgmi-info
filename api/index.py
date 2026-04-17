import requests
import json
from urllib.parse import unquote

def get_authorization_token(session):
    url = "https://www.rooter.gg/"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }

    response = session.get(url, headers=headers)

    user_auth = session.cookies.get("user_auth")
    if not user_auth:
        return None

    try:
        access_token_json = unquote(user_auth)
        access_token_data = json.loads(access_token_json)
        return access_token_data.get("accessToken")
    except:
        return None


def get_bgmi_username(user_id):
    session = requests.Session()

    access_token = get_authorization_token(session)

    if not access_token:
        return {"error": "Failed to get access token"}

    url = f"https://bazaar.rooter.io/order/getUnipinUsername?gameCode=BGMI_IN&id={user_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = session.get(url, headers=headers)

    try:
        data = response.json()

        if data.get("transaction") == "SUCCESS":
            return {
                "username": data['unipinRes']['username'],
                "uid": user_id
            }
        else:
            return {"error": data.get("message", "Unknown error")}

    except:
        return {"error": "Invalid response"}


# 🔥 IMPORTANT: Vercel expects THIS format
def handler(request, context):
    uid = request.query.get("uid")

    if not uid:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "UID is required"})
        }

    result = get_bgmi_username(uid)

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
