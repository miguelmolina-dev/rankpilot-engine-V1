import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

valid_payload = {
    "submission_id": "123",
    "metadata": None,
    "raw_text": "Sample raw text",
    "new_answer": None,
    "history": [],
    "current_step": 1,
    "gaps": None,
    "positioning_core": None,
    "positioning_tier": None,
    "blind_spots": [],
    "competitive_advantage": [],
    "evolution_path": [],
    "next_node": "extract_text"
}

def test_process_error_handling():
    from unittest.mock import patch

    with patch("main.app_workflow.invoke", side_effect=Exception("Test error")):
        response = client.post("/process", json=valid_payload)
        assert response.status_code == 500
        assert response.json()["detail"] == "Test error"

def test_process_success():
    from unittest.mock import patch

    with patch("main.app_workflow.invoke", return_value={"status": "success"}):
        response = client.post("/process", json=valid_payload)
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

def test_process_minimal_payload():
    from unittest.mock import patch

    # Send a minimal payload to ensure the API works without complete JSON state mapping
    minimal_payload = {
        "submission_id": "test_minimal",
        "raw_text": "Minimal content"
    }

    with patch("main.app_workflow.invoke") as mock_invoke:
        mock_invoke.return_value = {"status": "success"}
        response = client.post("/process", json=minimal_payload)

        # It should succeed
        assert response.status_code == 200

        # Verify the incomplete JSON is mapped correctly to default values
        called_args = mock_invoke.call_args[0][0]
        assert called_args.submission_id == "test_minimal"
        assert called_args.raw_text == "Minimal content"
        assert called_args.history == []
        assert called_args.current_step == 0
        assert called_args.metadata is None
        assert called_args.new_answer is None
