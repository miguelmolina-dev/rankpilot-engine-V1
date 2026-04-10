import pytest
from src.graph.workflow import app_workflow
from src.graph.state import RankPilotState
from src.chains.extractor_chain import ExtractionResult
from src.chains.question_chain import InterrogationQuestion
from src.chains.snapshot_chain import FinalSnapshot, CorePositioning, PracticeModel, PositioningTier, BlindSpot
from src.chains.scheduler_chain import SchedulerResponse, MilestoneSchema as SchedulerMilestoneSchema
from src.chains.executive_writer_chain import ExecutiveWriterResponse
from src.agents.strategist import StrategistResponse, MilestoneSchema as StrategistMilestoneSchema

def test_full_pydantic_workflow(monkeypatch):
    class MockExtractionChain:
        def invoke(self, input_data):
            return ExtractionResult(
                firm_name="Test Firm",
                practice_model="Test Model",
                definition="Test Def",
                confidence_score=0.9,
                initial_signals=["signal 1"],
                gaps=["gap 1"]
            )
    monkeypatch.setattr("src.agents.structural_analyzer.extraction_chain", MockExtractionChain())

    class MockQuestionChain:
        def invoke(self, input_data):
            return InterrogationQuestion(id="q1", text="Next question?")
    monkeypatch.setattr("src.agents.interrogator.question_chain", MockQuestionChain())

    class MockSnapshotChain:
        def invoke(self, input_data):
            return FinalSnapshot(
                positioning_core=CorePositioning(
                    practice_model=PracticeModel(
                        label="Test Model",
                        definition="Test Definition"
                    ),
                    confidence_score=0.8,
                    signals=["Test Signal"]
                ),
                positioning_tier=PositioningTier(
                    label="Test Tier",
                    explanation="Test Explanation"
                ),
                blind_spots=[BlindSpot(
                    issue="Test Issue",
                    description="Test Description"
                )],
                competitive_advantage=["Test Advantage"]
            )
    monkeypatch.setattr("src.agents.snapshot_generator.snapshot_chain", MockSnapshotChain())

    class MockSchedulerChain:
        def invoke(self, input_data):
            return SchedulerResponse(
                evolution_path=[SchedulerMilestoneSchema(
                    category="Category 1",
                    action_title="Test Action",
                    why_it_matters="Test Impact",
                    technical_instruction="Test Instruction",
                    priority_level=1,
                    days_before_deadline=10
                )]
            )
    monkeypatch.setattr("src.agents.scheduler.scheduler_chain", MockSchedulerChain())

    class MockExecutiveWriterChain:
        def invoke(self, input_data):
            return ExecutiveWriterResponse(
                overall_score=85,
                risk_level="Low",
                strategic_verdict="Test Verdict",
                audit_letter_markdown="Test Markdown"
            )
    monkeypatch.setattr("src.agents.executive_writer.executive_writer_chain", MockExecutiveWriterChain())


    initial_state = RankPilotState(
        submission_id="test_sub",
        metadata={
            "file_base64": "dummy",
            "region": "Test"
        }
    )
    # The workflow routes to END if interrogate is called.
    # So we'll call app_workflow multiple times simulating the interaction loop

    # 1. First run, analyzes and goes to interrogate
    result = app_workflow.invoke(initial_state)
    assert result["current_step"] == 2
    assert result["next_node"] == "interrogate"

    # 2. Simulate providing an answer to the interrogation
    state2 = RankPilotState(**result)
    state2.new_answer = {
        "question_text": "Next question?",
        "answer": "My answer"
    }
    result2 = app_workflow.invoke(state2)

    # 3. Repeat to pass the current_step >= 6 logic in interrogator
    # Note: interrogator_node checks for current_step >= 6 before finishing
    # We started at 0. Structural analyzer bumped to 1.
    # result1 bumped to 2. result2 bumped to 3.
    # We need to simulate answering up to step 6.

    current_state_dict = result2

    for _ in range(4):
        state = RankPilotState(**current_state_dict)
        state.new_answer = {
            "question_text": "Next question?",
            "answer": "My answer"
        }
        current_state_dict = app_workflow.invoke(state)

    # Now it should go to generate_snapshot and the rest

    assert "executive_summary" in current_state_dict
    # executive_summary is an object (or dict), so let's check correctly
    exec_sum = current_state_dict["executive_summary"]
    if hasattr(exec_sum, "overall_score"):
        assert exec_sum.overall_score == 85
    else:
        assert exec_sum["overall_score"] == 85
