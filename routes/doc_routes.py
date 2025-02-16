# routes/doc_routes.py
from flask import Blueprint, request, jsonify
from controllers.doc_controller import generate_document

doc_bp = Blueprint('doc_bp', __name__)

@doc_bp.route("/generate-doc", methods=["POST"])
def generate_doc():
    """Endpoint to generate a custom DOCX, upload it, and return the PDF URL."""
    data = request.json
    first_name = data.get('firstName')
    day_number = data.get('dayNumber')

    if not first_name or not day_number:
        return jsonify({"error": "Missing firstName or dayNumber"}), 400

    try:
        result = generate_document(first_name, day_number)
        if not result:
            return jsonify({"error": "Failed to upload and convert document"}), 500
        return jsonify(result)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500
