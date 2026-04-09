import base64
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_dummy_pdf_base64():
    # A tiny valid PDF structure to avoid PyMuPDF parsing errors
    minimal_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources <<>> /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 21 >>\nstream\nBT\n/F1 12 Tf\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n283\n%%EOF"
    base64_str = base64.b64encode(minimal_pdf).decode("utf-8")
    return f"data:application/pdf;base64,{base64_str}"

def test_process_endpoint(monkeypatch):
    # Mock the LLM call or any downstream graph execution
    # For now, let's just make sure the API accepts the payload correctly
    # Since the full LangGraph workflow needs an API key and performs actual calls,
    # we'll mock app_workflow.invoke to just return a dummy state

    from src.graph.workflow import app_workflow

    class DummyWorkflow:
        def invoke(self, request):
            return request

    monkeypatch.setattr("main.app_workflow", DummyWorkflow())

    base64_payload = create_dummy_pdf_base64()

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

    response = client.post("/process", json=payload)

    assert response.status_code == 200
    assert response.json()["submission_id"] == "test_submission_123"
    assert response.json()["metadata"]["region"] == "Test Region"
