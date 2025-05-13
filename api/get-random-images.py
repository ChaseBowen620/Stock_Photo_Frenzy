import os
import base64
import requests
import json
from urllib.parse import parse_qs

def handler(request):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding",
            "Content-Type": "application/json"
        },
        "body": json.dumps({"message": "API is reachable!"})
    }

"""
    def cors_headers():
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
        }

    try:
        # --- Parse query parameters ---
        raw_query = request.get("query", "")
        query_params = parse_qs(raw_query)
        query = query_params.get("query", ["city"])[0]
        num_images = int(query_params.get("numImages", ["5"])[0])
        title_length = int(query_params.get("titleLength", ["50"])[0])

        # --- Get API credentials ---
        client_id = os.environ.get("SHUTTERSTOCK_CLIENT_ID")
        client_secret = os.environ.get("SHUTTERSTOCK_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError("Missing Shutterstock credentials")

        # --- Get access token ---
        auth_string = f"{client_id}:{client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        token_response = requests.post(
            "https://api.shutterstock.com/v2/access_token",
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }
        )
        if token_response.status_code != 200:
            raise RuntimeError(f"Auth failed: {token_response.text}")

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise RuntimeError("No access token received")

        # --- Fetch images ---
        search_response = requests.get(
            "https://api.shutterstock.com/v2/images/search",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"query": query, "per_page": num_images, "view": "full"}
        )
        if search_response.status_code != 200:
            raise RuntimeError(f"Image fetch failed: {search_response.text}")

        # --- Format image data ---
        images = []
        for item in search_response.json().get("data", []):
            title = item.get("description", "")
            images.append({
                "url": item.get("assets", {}).get("preview", {}).get("url", ""),
                "title": title,
                "truncated_title": title if len(title) <= title_length else title[:title_length] + "..."
            })

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps(images)
        }

    except Exception as e:
        # Always include CORS headers on error
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }
"""