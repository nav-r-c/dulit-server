from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import base64
import requests
from docxtpl import DocxTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS

# Paths
TEMPLATE_PATH = os.path.join(os.getcwd(), "templates", "Dulit-pass.docx")
TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Google Apps Script Web API URL (set this in your .env file)
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

def generate_unique_id():
    """Generate a unique 9-character alphanumeric ID."""
    return uuid.uuid4().hex[:9]

def modify_docx(first_name, day_number, output_path):
    """Modify the DOCX template using Jinja2 placeholders."""
    doc = DocxTemplate(TEMPLATE_PATH)
    context = {"FirstName": first_name, "DayNumber": day_number}
    doc.render(context)
    doc.save(output_path)

def upload_to_google_drive(docx_path):
    """Encode the DOCX file to base64 and send it to the Google Apps Script endpoint."""
    try:
        file_name = os.path.basename(docx_path)
        with open(docx_path, "rb") as f:
            file_data = f.read()
        # Encode file data as a base64 string
        file_data_base64 = base64.b64encode(file_data).decode("utf-8")
        
        payload = {
            "fileName": file_name,
            "fileData": file_data_base64
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(APPS_SCRIPT_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()  # Expected to contain the pdfUrl key
    except Exception as e:
        print("Upload error:", e)
        return None

@app.route("/generate-doc", methods=["POST"])
def generate_doc():
    """Generate a custom DOCX file, upload it to Google Drive for conversion, and return the PDF URL."""
    try:
        data = request.json
        first_name = data.get('firstName')
        day_number = data.get('dayNumber')
        if not first_name or not day_number:
            return jsonify({"error": "Missing firstName or dayNumber"}), 400

        unique_id = generate_unique_id()
        docx_filename = f"Dulit-pass-{first_name}-{day_number}-{unique_id}.docx"
        docx_path = os.path.join(TEMP_DIR, docx_filename)

        # Create a DOCX file using your template and Jinja2 placeholders
        modify_docx(first_name, day_number, docx_path)

        # Upload the DOCX file to Google Drive (via Apps Script) and convert it to PDF
        result = upload_to_google_drive(docx_path)
        
        # Clean up the temporary DOCX file
        os.remove(docx_path)
        
        if not result:
            return jsonify({"error": "Failed to upload and convert document"}), 500
        return jsonify(result)
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)
