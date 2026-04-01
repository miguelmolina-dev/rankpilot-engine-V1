from langchain_openai import ChatOpenAI
from src.chains.snapshot_chain import snapshot_chain
from src.utils.llm_manager import get_llm
from src.graph.state import RankPilotState

def snapshot_generator_node(state: RankPilotState):
    print("--- [NODE] Generating Final Snapshot ---")
    
    try:
        # ... invoke logic remains the same ...
        result = snapshot_chain.invoke({
            "raw_text": state.get("raw_text", ""),
            "history": state.get("history", []),
            "practice_model": state.get("positioning_core", {}).get("practice_model", "Unknown Model"),
            "submission_id": state.get("submission_id", "Default-ID"),
            "gaps": state.get("gaps", "No specific gaps identified yet.")
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