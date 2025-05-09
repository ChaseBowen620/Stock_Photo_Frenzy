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

    # Debug: log environment and request
    print("Handler called")
    print("Request method:", request.method)
    print("Client ID:", os.environ.get('SHUTTERSTOCK_CLIENT_ID'))
    print("Client Secret:", os.environ.get('SHUTTERSTOCK_CLIENT_SECRET'))

    if request.method == "OPTIONS":
        return ("", 204, cors_headers)

    query = request.args.get('query', '')
    num_images = int(request.args.get('numImages', '10'))
    title_length = int(request.args.get('titleLength', '30'))

    client_id = os.environ.get('SHUTTERSTOCK_CLIENT_ID')
    client_secret = os.environ.get('SHUTTERSTOCK_CLIENT_SECRET')
    if not client_id or not client_secret:
        print("Missing API credentials!")
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
        print("Error during token request:", str(e))
        return (json.dumps({"error": str(e)}), 500, cors_headers)
    if token_response.status_code != 200:
        print("Failed to get access token:", token_response.text)
        return (json.dumps({"error": f"Failed to get access token: {token_response.text}"}), token_response.status_code, cors_headers)

    access_token = token_response.json().get('access_token')
    if not access_token:
        print("No access token received!")
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
        print("Error during image search:", str(e))
        return (json.dumps({"error": str(e)}), 500, cors_headers)
    if search_response.status_code != 200:
        print("Failed to fetch images:", search_response.text)
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

    print(f"Returning {len(formatted_images)} images.")
    return (json.dumps(formatted_images), 200, cors_headers) 