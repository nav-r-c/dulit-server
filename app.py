from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import base64
import requests
from docxtpl import DocxTemplate
from docx2pdf import convert

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configurations
GOOGLE_APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
TEMPLATE_PATH = os.path.join(os.getcwd(), "templates", "Dulit-pass.docx")
TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("templates", exist_ok=True)

def generate_unique_id():
    """Generate a unique 9-character alphanumeric ID."""
    return uuid.uuid4().hex[:9]

def modify_docx(first_name, day_number, output_path):
    """
    Modify the DOCX template using DocxTemplate and Jinja2 templating.
    
    Your DOCX template should include Jinja2 placeholders like:
      {{ FirstName }} and {{ DayNumber }}
    """
    doc = DocxTemplate(TEMPLATE_PATH)
    context = {
        "FirstName": first_name,
        "DayNumber": day_number,
    }
    doc.render(context)
    doc.save(output_path)

def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert .docx to .pdf using docx2pdf."""
    convert(docx_path, pdf_path)

def upload_to_google_apps_script(file_path, file_name):
    """Upload PDF to Google Drive using Apps Script."""
    try:
        with open(file_path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode("utf-8")

        response = requests.post(
            GOOGLE_APPS_SCRIPT_URL,
            json={"fileName": file_name, "fileData": file_data}
        )
        return response.json().get("url", None)
    except Exception as e:
        print(f"Upload Error: {e}")
        raise

@app.route("/generate-doc", methods=["POST"])
def generate_doc():
    """Generate a custom document and convert it to PDF."""
    try:
        data = request.json
        first_name = data.get("firstName")
        day_number = data.get("dayNumber")

        if not first_name or not day_number:
            return jsonify({"error": "Missing firstName or dayNumber"}), 400

        unique_id = generate_unique_id()
        docx_filename = f"Dulit-pass-{first_name}-{day_number}-{unique_id}.docx"
        pdf_filename = f"Dulit-pass-{first_name}-{day_number}-{unique_id}.pdf"

        docx_path = os.path.join(TEMP_DIR, docx_filename)
        pdf_path = os.path.join(TEMP_DIR, pdf_filename)

        # Modify DOCX using Jinja2 templating and convert to PDF
        modify_docx(first_name, day_number, docx_path)
        convert_docx_to_pdf(docx_path, pdf_path)

        # Upload to Google Drive via Apps Script
        pdf_url = upload_to_google_apps_script(pdf_path, pdf_filename)

        # Clean up temporary files
        os.remove(docx_path)
        os.remove(pdf_path)

        return jsonify({"url": pdf_url, "uniqueId": unique_id})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/upload-template", methods=["POST"])
def upload_template():
    """Upload a new DOCX template."""
    try:
        if "template" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["template"]
        file.save(TEMPLATE_PATH)

        return jsonify({"message": "Template updated successfully"})

    except Exception as e:
        return jsonify({"error": f"Failed to update template: {e}"}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)
