import os
import base64
import requests
import json
from urllib.parse import parse_qs

def handler(request):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }

    method = request.get("method", "GET")
    query_string = request.get("query", "")
    params = parse_qs(query_string)
    query = params.get("query", [""])[0]
    num_images = int(params.get("numImages", ["10"])[0])
    title_length = int(params.get("titleLength", ["30"])[0])

    if method == "OPTIONS":
        return ("", 204, cors_headers)

    client_id = os.environ.get('SHUTTERSTOCK_CLIENT_ID')
    client_secret = os.environ.get('SHUTTERSTOCK_CLIENT_SECRET')
    if not client_id or not client_secret:
        return (json.dumps({"error": "API credentials not configured"}), 500, cors_headers)

    # Get access token
    auth_string = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    token_url = "https://api.shutterstock.com/v2/access_token"
    token_headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        token_response = requests.post(token_url, headers=token_headers, data=token_data)
    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, cors_headers)
    if token_response.status_code != 200:
        return (json.dumps({"error": f"Failed to get access token: {token_response.text}"}), token_response.status_code, cors_headers)

    access_token = token_response.json().get('access_token')
    if not access_token:
        return (json.dumps({"error": "No access token received"}), 500, cors_headers)

    # Search for images
    search_url = "https://api.shutterstock.com/v2/images/search"
    search_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    search_params = {
        "query": query,
        "per_page": num_images,
        "view": "full"
    }
    try:
        search_response = requests.get(search_url, headers=search_headers, params=search_params)
    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, cors_headers)
    if search_response.status_code != 200:
        return (json.dumps({"error": f"Failed to fetch images: {search_response.text}"}), search_response.status_code, cors_headers)

    data = search_response.json()
    formatted_images = []
    for image in data.get('data', []):
        preview_url = image.get('assets', {}).get('preview', {}).get('url', '')
        description = image.get('description', '')
        truncated_description = description if len(description) <= title_length else description[:title_length] + "..."
        formatted_images.append({
            "url": preview_url,
            "title": description,
            "truncated_title": truncated_description
        })

    return (json.dumps(formatted_images), 200, cors_headers) 