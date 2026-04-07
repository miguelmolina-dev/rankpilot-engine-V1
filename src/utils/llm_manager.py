from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

class MockChatOpenAI(RunnableLambda):
    def __init__(self, *args, **kwargs):
        super().__init__(self._invoke)

    def _invoke(self, prompt, **kwargs):
        import json
        prompt_text = str(prompt)

        if "ExtractedStructure" in prompt_text or "file_type" in prompt_text or "Initial Structural Analysis" in prompt_text:
             return AIMessage(content=json.dumps({
                 "file_type": "document",
                 "detected_band": "Band 2",
                 "target_band": "Band 1",
                 "key_lawyers": ["John Doe"],
                 "practice_area": "Corporate M&A",
                 "practice_model": {"model": "test_model"},
                 "definition": "test",
                 "confidence_score": 1.0,
                 "initial_signals": ["test"],
                 "gaps": ["test"]
             }))
        elif "InterrogationQuestion" in prompt_text or "next_question" in prompt_text or "You are the Interrogation Agent" in prompt_text:
             return AIMessage(content=json.dumps({
                 "id": "q1",
                 "text": "Can you provide an example of a recent M&A deal?"
             }))
        elif "FinalSnapshot" in prompt_text or "positioning_core" in prompt_text or "Snapshot Generation Agent" in prompt_text:
             return AIMessage(content=json.dumps({
                 "submission_id": "test_submission_123",
                 "positioning_core": {"practice_model": {"model": "test"}, "practice_definition": "test", "confidence_score": 1.0, "signals": []},
                 "positioning_tier": {"label": "test", "explanation": "test"},
                 "blind_spots": [{"issue": "test", "description": "test"}],
                 "competitive_advantage": ["test"],
                 "evolution_path": [{"action": "test", "impact": "test", "instruction": "test"}]
             }))

        return AIMessage(content=json.dumps({
                 "id": "q1",
                 "text": "Fallback Mock Question"
        }))
    
    def with_structured_output(self, schema, *args, **kwargs):
        class MockStructuredOutput(RunnableLambda):
            def __init__(self):
                super().__init__(self._invoke)

            def _invoke(self, prompt, **kwargs):
                if schema.__name__ == 'ExtractedStructure':
                    return schema(
                        file_type="document",
                        detected_band="Band 2",
                        target_band="Band 1",
                        key_lawyers=["John Doe"],
                        practice_area="Corporate M&A"
                    )
                elif schema.__name__ == 'InterrogationQuestion':
                    return schema(text="Can you provide an example of a recent M&A deal?")
                elif schema.__name__ == 'FinalSnapshot':
                    from src.graph.state import PositioningCore, PositioningTier
                    return schema(
                        submission_id="test_submission_123",
                        positioning_core={"practice_model": {"model": "test"}, "practice_definition": "test", "confidence_score": 1.0, "signals": []},
                        positioning_tier={"label": "test", "explanation": "test"},
                        blind_spots=[{"issue": "test", "description": "test"}],
                        competitive_advantage=["test"],
                        evolution_path=[{"action": "test", "impact": "test", "instruction": "test"}]
                    )
                return schema()
        return MockStructuredOutput()
    
    def bind_tools(self, *args, **kwargs):
        return self

def get_llm(temperature=0):
    return MockChatOpenAI()
