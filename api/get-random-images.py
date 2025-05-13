import os
import base64
import requests
import json
from urllib.parse import parse_qs
from typing import Dict

def handler(request) -> Dict:
    try:
        # Parse query parameters
        query_params = parse_qs(request.get("query", ""))
        query = query_params.get("query", ["city"])[0]
        num_images = int(query_params.get("numImages", ["10"])[0])
        title_length = int(query_params.get("titleLength", ["30"])[0])

        # Get API credentials
        client_id = os.environ.get('SHUTTERSTOCK_CLIENT_ID')
        client_secret = os.environ.get('SHUTTERSTOCK_CLIENT_SECRET')
        if not client_id or not client_secret:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
                },
                "body": json.dumps({"error": "API credentials not configured"})
            }

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
            return {
                "statusCode": token_response.status_code,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
                },
                "body": json.dumps({"error": f"Failed to get access token: {token_response.text}"})
            }

        access_token = token_response.json().get('access_token')
        if not access_token:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
                },
                "body": json.dumps({"error": "No access token received"})
            }

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
            return {
                "statusCode": search_response.status_code,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
                },
                "body": json.dumps({"error": f"Failed to fetch images: {search_response.text}"})
            }

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

        # Check if client accepts Brotli compression
        accept_encoding = request.get("headers", {}).get("accept-encoding", "")
        use_brotli = "br" in accept_encoding

        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
        }

        if use_brotli:
            try:
                import brotli
                response_body = brotli.compress(json.dumps(formatted_images).encode('utf-8'))
                headers["Content-Encoding"] = "br"
            except ImportError:
                response_body = json.dumps(formatted_images)
        else:
            response_body = json.dumps(formatted_images)

        return {
            "statusCode": 200,
            "headers": headers,
            "body": response_body
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
            },
            "body": json.dumps({"error": str(e)})
        } 