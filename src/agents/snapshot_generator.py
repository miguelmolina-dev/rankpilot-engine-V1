from langchain_openai import ChatOpenAI
from src.chains.snapshot_chain import snapshot_chain
from src.utils.llm_manager import get_llm
from src.graph.state import RankPilotState

def snapshot_generator_node(state: RankPilotState):
    print("--- [NODE] Generating Final Snapshot ---")
    
    try:

        input_data = {
            "raw_text": state.get("raw_text", ""),
            "history": state.get("history", []),
            "practice_area": state.get("metadata", {}).get("practice_area", "General Law"),
            "gaps": state.get("gaps", "No specific gaps identified yet.")
        }

        # ... invoke logic remains the same ...
        # 2. Invoke the Auditor Chain (Low temperature for accuracy)
        result = snapshot_chain.invoke(input_data)
        
        # Flatten the result so it matches your RankPilotState keys
        return {
            "positioning_core": result.positioning_core.model_dump(),
            "positioning_tier": result.positioning_tier.model_dump(),
            "blind_spots": [bs.model_dump() for bs in result.blind_spots],
            "competitive_advantage": result.competitive_advantage,
            "status": "completed",
            "next_node": "end" # Update this to tell the test the flow finished
        }
    except Exception as e:
        print(f"!!! Error en Snapshot: {e}")
        # Retornamos algo mínimo para evitar el AttributeError: 'NoneType' en el test
        return {"status": "error", "final_report": {}, "positioning_tier": {"label": "Error"}}