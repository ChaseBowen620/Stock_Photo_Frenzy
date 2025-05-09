import os
import base64
import requests
import json

def handler(request):
    # CORS headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json"
    }

    if request.method == "OPTIONS":
        return ("", 204, cors_headers)

    query = request.args.get('query', '')
    num_images = int(request.args.get('numImages', '10'))
    title_length = int(request.args.get('titleLength', '30'))

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
    token_response = requests.post(token_url, headers=token_headers, data=token_data)
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
    search_response = requests.get(search_url, headers=search_headers, params=search_params)
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