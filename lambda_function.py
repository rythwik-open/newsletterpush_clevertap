import json
import os
import requests
import hashlib
import time

CLEVERTAP_ACCOUNT_ID = os.environ['CLEVERTAP_ACCOUNT_ID']
CLEVERTAP_PASSCODE = os.environ['CLEVERTAP_PASSCODE']
CLEVERTAP_REGION = os.environ['CLEVERTAP_REGION']  # e.g., in1, us1

BASE_URL = f"https://{CLEVERTAP_REGION}.api.clevertap.com"

HEADERS = {
    "X-CleverTap-Account-Id": CLEVERTAP_ACCOUNT_ID,
    "X-CleverTap-Passcode": CLEVERTAP_PASSCODE,
    "Content-Type": "application/json"
}

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')

        if not email:
            return {"statusCode": 400, "body": json.dumps({"message": "Email is required."})}

        # Step 1: Try fetching the profile
        profile_url = f"{BASE_URL}/1/profile.json"
        res = requests.get(profile_url, headers=HEADERS, params={"identity": email})
        
        if res.status_code == 200:
            profile = res.json().get("profile", {})
            properties = profile.get("props", {})
            
            if properties.get("Zwitch Newsletter") == "yes":
                return {"statusCode": 200, "body": json.dumps({"message": "Already registered"})}
            else:
                # Update the user profile with the Zwitch Newsletter field
                update_res = update_user_profile(email)
                if update_res.status_code == 200:
                    return {"statusCode": 200, "body": json.dumps({"message": "Successfully subscribed"})}
                else:
                    return {"statusCode": 500, "body": json.dumps({"message": "Failed to update profile"})}
        else:
            # Profile doesn't exist — create one with the newsletter flag
            create_res = create_user_profile(email)
            if create_res.status_code == 200:
                return {"statusCode": 200, "body": json.dumps({"message": "Successfully subscribed"})}
            else:
                return {"statusCode": 500, "body": json.dumps({"message": "Failed to create profile"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": "Server error", "error": str(e)})}


def update_user_profile(email):
    url = f"{BASE_URL}/1/upload"
    payload = {
        "d": [
            {
                "identity": email,
                "type": "profile",
                "ts": int(time.time()),
                "profileData": {
                    "Zwitch Newsletter": "yes"
                }
            }
        ]
    }
    return requests.post(url, headers=HEADERS, data=json.dumps(payload))


def create_user_profile(email):
    url = f"{BASE_URL}/1/upload"
    payload = {
        "d": [
            {
                "identity": email,
                "type": "profile",
                "ts": int(time.time()),
                "profileData": {
                    "Email": email,
                    "Zwitch Newsletter": "yes"
                }
            }
        ]
    }
    return requests.post(url, headers=HEADERS, data=json.dumps(payload))
