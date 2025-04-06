from flask import Flask, request, jsonify
from os import environ
import requests
import json
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
load_dotenv()

@app.route('/api/get-random-images', methods=['GET'])
def get_random_images():
    try:
        query = request.args.get('query', '')
        num_images = int(request.args.get('numImages', '10'))
        title_length = int(request.args.get('titleLength', '30'))

        # Shutterstock API credentials
        api_key = environ.get('SHUTTERSTOCK_API_KEY')
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500

        # Shutterstock API endpoint
        url = f"https://api.shutterstock.com/v2/images/search"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        params = {
            "query": query,
            "per_page": num_images,
            "view": "full"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch images"}), response.status_code

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

        return jsonify(formatted_images)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For local development
if __name__ == '__main__':
    app.run() 