import sys
import base64
import httpx
import json
import argparse
import os

def send_file(filepath, url="http://localhost:8001/process"):
    if not os.path.isfile(filepath):
        print(f"Error: File not found at {filepath}")
        return None

    try:
        with open(filepath, "rb") as f:
            file_bytes = f.read()

        base64_str = base64.b64encode(file_bytes).decode("utf-8")

        # Determine mime type
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            mime_type = "application/pdf"
        elif ext in ['.doc', '.docx']:
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            mime_type = "application/octet-stream"

        base64_payload = f"data:{mime_type};base64,{base64_str}"

        payload = {
            "submission_id": "test_submission_123",
            "metadata": {
                "file_base64": base64_payload,
                "region": "Test Region",
                "practice_area": "Test Practice Area",
                "location": "Test Location",
                "firm_name": "Test Firm"
            }
        }

        print(f"Sending file {filepath} to {url}...")

        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)

        print(f"Status Code: {response.status_code}")
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Response was not JSON:")
            print(response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a file to base64 and send it to the local system.")
    parser.add_argument("filepath", help="Path to the file to convert and send")
    parser.add_argument("--url", default="http://localhost:8001/process", help="URL of the process endpoint")

    args = parser.parse_args()

    result = send_file(args.filepath, args.url)
    if result:
        print("Response:")
        print(json.dumps(result, indent=2))
