import os
import base64
import requests
import json

def handler(request, response):
    # CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    if request.method == "OPTIONS":
        response.status_code = 204
        return ""

    query = request.args.get('query', '')
    num_images = int(request.args.get('numImages', '10'))
    title_length = int(request.args.get('titleLength', '30'))

    client_id = os.environ.get('SHUTTERSTOCK_CLIENT_ID')
    client_secret = os.environ.get('SHUTTERSTOCK_CLIENT_SECRET')
    if not client_id or not client_secret:
        response.status_code = 500
        return json.dumps({"error": "API credentials not configured"})

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
        response.status_code = token_response.status_code
        return json.dumps({"error": f"Failed to get access token: {token_response.text}"})

    access_token = token_response.json().get('access_token')
    if not access_token:
        response.status_code = 500
        return json.dumps({"error": "No access token received"})

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
        response.status_code = search_response.status_code
        return json.dumps({"error": f"Failed to fetch images: {search_response.text}"})

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

    response.headers["Content-Type"] = "application/json"
    return json.dumps(formatted_images) 