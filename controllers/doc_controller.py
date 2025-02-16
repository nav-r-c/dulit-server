# controllers/doc_controller.py
import os
import uuid
import base64
import requests
from docxtpl import DocxTemplate

# Define paths
TEMPLATE_PATH = os.path.join(os.getcwd(), "templates", "Dulit-pass.docx")
TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Get the Google Apps Script URL from environment variables
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

def generate_document(first_name, day_number):
    """
    Create a DOCX file from the template, upload it for conversion, and return the result.
    """
    unique_id = generate_unique_id()
    docx_filename = f"Dulit-pass-{first_name}-{day_number}-{unique_id}.docx"
    docx_path = os.path.join(TEMP_DIR, docx_filename)

    # Generate the DOCX file
    modify_docx(first_name, day_number, docx_path)

    # Upload and convert the DOCX file
    result = upload_to_google_drive(docx_path)
    
    # Clean up the temporary file
    os.remove(docx_path)
    
    return result
