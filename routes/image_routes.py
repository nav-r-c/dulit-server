from flask import Blueprint, request
from controllers.image_controller import upload_image

# Create a Blueprint for the image routes
image_routes = Blueprint('image_routes', __name__)

# Define the route for uploading images
@image_routes.route('/upload-image', methods=['POST'])
def upload_image_route():
    file = request.files.get('image')
    return upload_image(file)
