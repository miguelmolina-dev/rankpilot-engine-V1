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
