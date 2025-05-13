import os
import base64
import requests
import json
from urllib.parse import parse_qs
from typing import Dict
from http.server import BaseHTTPRequestHandler, HTTPServer

# Original Lambda handler function
def handler(request) -> Dict:
    try:
        # Handle preflight CORS request
        if request.get("method") == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
                },
                "body": ""
            }

        # Parse query parameters
        query_params = parse_qs(request.get("query", ""))
        query = query_params.get("query", ["city"])[0]
        num_images = int(query_params.get("numImages", ["10"])[0])
        title_length = int(query_params.get("titleLength", ["30"])[0])

        # Get API credentials
        client_id = os.environ.get('SHUTTERSTOCK_CLIENT_ID')
        client_secret = os.environ.get('SHUTTERSTOCK_CLIENT_SECRET')
        if not client_id or not client_secret:
            return error_response("API credentials not configured")

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
            return error_response(f"Failed to get access token: {token_response.text}", token_response.status_code)

        access_token = token_response.json().get('access_token')
        if not access_token:
            return error_response("No access token received")

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
            return error_response(f"Failed to fetch images: {search_response.text}", search_response.status_code)

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

        # Check for Brotli support
        accept_encoding = request.get("headers", {}).get("accept-encoding", "")
        use_brotli = "br" in accept_encoding
        response_body = json.dumps(formatted_images)

        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
        }

        if use_brotli:
            try:
                import brotli
                compressed = brotli.compress(response_body.encode("utf-8"))
                headers["Content-Encoding"] = "br"
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": base64.b64encode(compressed).decode("utf-8"),
                    "isBase64Encoded": True
                }
            except ImportError:
                pass  # Fallback to uncompressed

        return {
            "statusCode": 200,
            "headers": headers,
            "body": response_body
        }

    except Exception as e:
        return error_response(str(e))

# Utility function for consistent error responses
def error_response(message, status=500):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept-Encoding"
        },
        "body": json.dumps({"error": message})
    }

# HTTP Server implementation that uses the handler function
class ShutterstockRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract query string
        query = ""
        if '?' in self.path:
            query = self.path.split('?', 1)[1]
        
        # Build request object compatible with Lambda handler
        request = {
            "method": "GET",
            "path": self.path,
            "query": query,
            "headers": {k.lower(): v for k, v in self.headers.items()}
        }
        
        # Call the original handler
        response = handler(request)
        
        # Send response
        self.send_response(response.get("statusCode", 200))
        for header, value in response.get("headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        
        body = response.get("body", "")
        if response.get("isBase64Encoded", False):
            body = base64.b64decode(body)
        elif isinstance(body, str):
            body = body.encode('utf-8')
            
        self.wfile.write(body)

    def do_OPTIONS(self):
        # Handle OPTIONS requests
        request = {"method": "OPTIONS"}
        response = handler(request)
        
        self.send_response(response.get("statusCode", 204))
        for header, value in response.get("headers", {}).items():
            self.send_header(header, value)
        self.end_headers()

# Entry point for standalone HTTP server
def run_server(host='localhost', port=8000):
    server = HTTPServer((host, port), ShutterstockRequestHandler)
    print(f"Starting HTTP server on http://{host}:{port}")
    server.serve_forever()

# This will be the entry point when running as a script
if __name__ == "__main__":
    # Set environment variables if not already set (for local testing)
    if not os.environ.get('SHUTTERSTOCK_CLIENT_ID'):
        os.environ['SHUTTERSTOCK_CLIENT_ID'] = 'your_client_id_here'
    if not os.environ.get('SHUTTERSTOCK_CLIENT_SECRET'):
        os.environ['SHUTTERSTOCK_CLIENT_SECRET'] = 'your_client_secret_here'
    
    run_server()

# Entry point for AWS Lambda
def lambda_handler(event, context):
    # Convert Lambda event to format expected by our handler
    request = {
        "method": event.get("httpMethod", "GET"),
        "path": event.get("path", "/"),
        "query": event.get("queryStringParameters", {}),
        "headers": {k.lower(): v for k, v in event.get("headers", {}).items()}
    }
    
    # If query is a dict (AWS API Gateway format), convert to query string
    if isinstance(request["query"], dict):
        request["query"] = "&".join([f"{k}={v}" for k, v in request["query"].items()])
    
    return handler(request)