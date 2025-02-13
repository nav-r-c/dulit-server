from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
from docxtpl import DocxTemplate
import time


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configurations
GOOGLE_APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

TEMPLATE_PATH = os.path.join(os.getcwd(), "templates", "Dulit-pass.docx")
TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("templates", exist_ok=True)

def generate_unique_id():
    """Generate a unique 9-character alphanumeric ID."""
    return uuid.uuid4().hex[:9]

def modify_docx(first_name, day_number, output_path):
    """Modify the DOCX template using Jinja2 placeholders."""
    doc = DocxTemplate(TEMPLATE_PATH)
    context = {"FirstName": first_name, "DayNumber": day_number}
    doc.render(context)
    doc.save(output_path)


def convert_docx_to_pdf_cloudconvert(docx_path):
    """Convert DOCX to PDF using CloudConvert jobs (import, convert, export)."""
    try:
        # Step 1: Create a job with import, convert, and export tasks.
        job_url = "https://api.cloudconvert.com/v2/jobs"
        headers = {
            "Authorization": f"Bearer {CLOUDCONVERT_API_KEY}",
            "Content-Type": "application/json"
        }
        job_payload = {
            "tasks": {
                "import_task": {
                    "operation": "import/upload",
                    "redirect": None  # no redirection needed
                },
                "convert_task": {
                    "operation": "convert",
                    "input": ["import_task"],
                    "input_format": "docx",
                    "output_format": "pdf",
                    "filename": os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
                },
                "export_task": {
                    "operation": "export/url",
                    "input": ["convert_task"]
                }
            }
        }
        job_resp = requests.post(job_url, json=job_payload, headers=headers)
        job_resp.raise_for_status()
        job_data = job_resp.json()["data"]

        # Step 2: Get the upload URL from the import task.
        import_task = next(
            (task for task in job_data["tasks"] if task["name"] == "import_task"),
            None
        )
        if not import_task or "result" not in import_task or "form" not in import_task["result"]:
            raise Exception("Import task data missing required upload form info.")

        form = import_task["result"]["form"]
        upload_url = form["url"]
        upload_params = form.get("parameters", {})

        # Step 3: Upload the DOCX file using the provided URL and parameters.
        with open(docx_path, "rb") as f:
            files = {"file": (os.path.basename(docx_path), f)}
            upload_resp = requests.post(upload_url, data=upload_params, files=files)
            upload_resp.raise_for_status()

        # Step 4: Poll the job status until it is finished.
        job_id = job_data["id"]
        status_url = f"https://api.cloudconvert.com/v2/jobs/{job_id}"
        while True:
            status_resp = requests.get(status_url, headers=headers)
            status_resp.raise_for_status()
            status_data = status_resp.json()["data"]
            if status_data["status"] == "finished":
                # Look for the export task.
                export_task = next(
                    (t for t in status_data["tasks"] 
                     if t["operation"] == "export/url" and t["status"] == "finished"),
                    None
                )
                if export_task and export_task.get("result") and export_task["result"].get("files"):
                    download_info = export_task["result"]["files"][0]
                    if "url" in download_info:
                        return download_info["url"]
                    else:
                        raise Exception("Export task finished but 'url' key is missing in result.")
                else:
                    raise Exception("Job finished but export task did not return a download URL.")
            elif status_data["status"] in ["error", "failed"]:
                raise Exception("Job failed during processing.")
            time.sleep(3)  # wait before polling again

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError as e:
        print(f"Unexpected response format: Missing key {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None



@app.route("/generate-doc", methods=["POST"])
def generate_doc():
    """Generate a custom document and convert it to PDF."""
    try:
        data = request.json
        first_name = data['firstName']
        day_number = data['dayNumber']

        if not first_name or not day_number:
            return jsonify({"error": "Missing firstName or dayNumber"}), 400
        
        unique_id = generate_unique_id()
        docx_filename = f"Dulit-pass-{first_name}-{day_number}-{unique_id}.docx"
        docx_path = os.path.join(TEMP_DIR, docx_filename)

        # Modify DOCX using Jinja2 templating
        modify_docx(first_name, day_number, docx_path)

        # Convert DOCX to PDF via CloudConvert
        pdf_url = convert_docx_to_pdf_cloudconvert(docx_path)

        # Clean up temporary file
        os.remove(docx_path)

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
