import sys
import base64
import httpx
import json
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Convert a file to base64 and send it to the local system.")
    parser.add_argument("filepath", help="Path to the file to convert and send")
    parser.add_argument("--url", default="http://localhost:8001/process", help="URL of the process endpoint")

    args = parser.parse_args()

    if not os.path.isfile(args.filepath):
        print(f"Error: File not found at {args.filepath}")
        sys.exit(1)

    try:
        with open(args.filepath, "rb") as f:
            file_bytes = f.read()

        base64_str = base64.b64encode(file_bytes).decode("utf-8")
        # Add the base64 prefix as it is handled by the document_loader.py
        base64_payload = f"data:application/pdf;base64,{base64_str}"

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

        print(f"Sending file {args.filepath} to {args.url}...")

        with httpx.Client(timeout=120.0) as client:
            response = client.post(args.url, json=payload)

        print(f"Status Code: {response.status_code}")
        try:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print("Response was not JSON:")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
