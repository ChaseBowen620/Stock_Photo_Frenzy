from flask import Flask, request, jsonify
from os import environ
import requests
import json
from dotenv import load_dotenv
from flask_cors import CORS
import base64
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/get-random-images', methods=['GET'])
def get_random_images():
    try:
        query = request.args.get('query', '')
        num_images = int(request.args.get('numImages', '10'))
        title_length = int(request.args.get('titleLength', '30'))

        logger.info(f"Received request - Query: {query}, Num Images: {num_images}, Title Length: {title_length}")

        # Shutterstock API credentials
        client_id = environ.get('SHUTTERSTOCK_CLIENT_ID')
        client_secret = environ.get('SHUTTERSTOCK_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("API credentials not configured")
            return jsonify({"error": "API credentials not configured"}), 500

        # First, get an access token
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
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

        logger.info("Requesting access token...")
        token_response = requests.post(token_url, headers=token_headers, data=token_data)
        logger.info(f"Token response status: {token_response.status_code}")
        logger.info(f"Token response body: {token_response.text}")

        if token_response.status_code != 200:
            logger.error(f"Failed to get access token: {token_response.text}")
            return jsonify({"error": f"Failed to get access token: {token_response.text}"}), token_response.status_code

        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.error("No access token received")
            return jsonify({"error": "No access token received"}), 500

        # Now use the access token to search for images
        search_url = "https://api.shutterstock.com/v2/images/search"
        search_headers = {
            "Authorization": f"Bearer {access_token}"
        }
        search_params = {
            "query": query,
            "per_page": num_images,
            "view": "full"
        }

        logger.info("Searching for images...")
        response = requests.get(search_url, headers=search_headers, params=search_params)
        logger.info(f"Search response status: {response.status_code}")
        logger.info(f"Search response body: {response.text}")

        if response.status_code != 200:
            logger.error(f"Failed to fetch images: {response.text}")
            return jsonify({"error": f"Failed to fetch images: {response.text}"}), response.status_code

        data = response.json()
        formatted_images = []
        
        for image in data.get('data', []):
            preview_url = image.get('assets', {}).get('preview', {}).get('url', '')
            description = image.get('description', '')
            
            # Handle title length
            truncated_description = description
            if len(description) > title_length:
                truncated_description = description[:title_length] + "..."
                
            formatted_images.append({
                "url": preview_url,
                "title": description,
                "truncated_title": truncated_description
            })

        logger.info(f"Successfully formatted {len(formatted_images)} images")
        return jsonify(formatted_images)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# For local development
if __name__ == '__main__':
    app.run() 