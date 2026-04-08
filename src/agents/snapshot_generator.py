from langchain_openai import ChatOpenAI
from src.chains.snapshot_chain import snapshot_chain
from src.utils.llm_manager import get_llm
from src.graph.state import RankPilotState

def snapshot_generator_node(state: RankPilotState):
    print("--- [NODE] Generating Final Snapshot ---")
    
    try:
        # ... invoke logic remains the same ...
        result = snapshot_chain.invoke({
            "raw_text": state.raw_text,
            "history": state.history,
            "practice_model": state.positioning_core.practice_model if state.positioning_core else "Unknown Model",
            "submission_id": state.submission_id,
            "gaps": state.gaps if state.gaps else "No specific gaps identified yet."
        })
        
        # Flatten the result so it matches your RankPilotState keys
        return {
            "positioning_core": result.positioning_core.model_dump(),
            "positioning_tier": result.positioning_tier.model_dump(),
            "blind_spots": [bs.model_dump() for bs in result.blind_spots],
            "competitive_advantage": result.competitive_advantage,
            "evolution_path": [ep.model_dump() for ep in result.evolution_path],
            "final_report": result.model_dump(), # Keep this for Laravel if needed
            "status": "completed",
            "next_node": "end" # Update this to tell the test the flow finished
        }
    except Exception as e:
        print(f"!!! Error en Snapshot: {e}")
        # Retornamos algo mínimo para evitar el AttributeError: 'NoneType' en el test
        return {"status": "error", "final_report": {}, "positioning_tier": {"label": "Error"}}