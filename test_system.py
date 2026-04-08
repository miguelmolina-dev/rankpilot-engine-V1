import pytest
from unittest.mock import patch
from src.graph.state import RankPilotRequest, MetaData
from src.chains.extractor_chain import ExtractionResult
from src.chains.snapshot_chain import FinalSnapshot, PositioningTier, BlindSpot, EvolutionAction, CorePositioning, PracticeModel
from src.chains.question_chain import question_chain

class MockQuestionResponse:
    def __init__(self, text):
        self.text = text

@pytest.fixture
def mock_chains():
    # We patch the object attributes correctly for RunnableSequence
    with patch("src.agents.structural_analyzer.extraction_chain") as mock_extract_chain, \
         patch("src.agents.interrogator.question_chain") as mock_question_chain, \
         patch("src.agents.snapshot_generator.snapshot_chain") as mock_snapshot_chain:

        # Mock Extractor output
        mock_extract_chain.invoke.return_value = ExtractionResult(
            practice_model="Test Model",
            definition="Test Definition",
            confidence_score=0.9,
            initial_signals=["Signal 1", "Signal 2", "Signal 3"],
            gaps=["Gap 1", "Gap 2"]
        )

        # Mock Interrogator output
        mock_question_chain.invoke.return_value = MockQuestionResponse("Test question?")

        # Mock Snapshot output
        mock_snapshot_chain.invoke.return_value = FinalSnapshot(
            submission_id="test_id",
            positioning_core=CorePositioning(
                practice_model=PracticeModel(label="Test Label", definition="Test Definition"),
                confidence_score=0.9,
                signals=["Signal 1", "Signal 2", "Signal 3"]
            ),
            positioning_tier=PositioningTier(label="Band 1", explanation="Excellent"),
            blind_spots=[BlindSpot(issue="Issue 1", description="Description 1")],
            competitive_advantage=["Advantage 1"],
            evolution_path=[EvolutionAction(action="Action 1", impact="Impact 1", instruction="Instruction 1")]
        )

        yield mock_extract_chain, mock_question_chain, mock_snapshot_chain

def test_full_system_flow(mock_chains):
    from src.graph.workflow import app_workflow

    # Initial state
    request = RankPilotRequest(
        submission_id="test_id",
        metadata=MetaData(file_base64="dummy_base64"),
        raw_text="Test raw text"
    )

    # Step 1: Analyze Structure -> Interrogate (first pass)
    state = app_workflow.invoke(request)

    # Since structural_analyzer sets step=1 and interrogator increments it, it should be 2
    assert state["current_step"] == 2
    assert state["next_node"] == "interrogate"
    assert state["positioning_core"].practice_model == "Test Model"
    assert state["new_answer"].question_text == "Test question?"

    # Update state for next step (Simulate user answering)
    request2 = RankPilotRequest(**state)
    request2.new_answer.answer = "Test answer"
    request2.current_step = 6 # Fast-forward to trigger snapshot

    # Step 2: Interrogate -> Generate Snapshot -> END
    state2 = app_workflow.invoke(request2)

    assert state2["next_node"] == "__end__"
    assert state2["positioning_tier"].label == "Band 1"
    assert len(state2["blind_spots"]) == 1

if __name__ == "__main__":
    pytest.main(["-v", "test_system.py"])
