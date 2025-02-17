import os
import requests
from flask import jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the imgBB API key from the environment variables
IMGBB_API_KEY = os.getenv("IMGBB_KEY")

def upload_image(file):
    """Handle image upload to imgBB and return the URL."""
    if not file:
        return jsonify({"error": "No image file provided"}), 400

    try:
        files = {'image': (file.filename, file.stream, file.content_type)}
        params = {'key': IMGBB_API_KEY}
        
        # Send the image to imgBB API
        response = requests.post('https://api.imgbb.com/1/upload', files=files, params=params)
        
        if response.status_code == 200:
            img_url = response.json()['data']['url']
            return jsonify({"url": img_url}), 200
        else:
            return jsonify({"error": "Failed to upload image to imgBB"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
