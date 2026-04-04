from typing import Dict, Any
from src.graph.state import RankPilotState
from src.chains.scheduler_chain import scheduler_chain

def scheduler_node(state: RankPilotState) -> Dict[str, Any]:
    """
    Strategic Scheduler Agent:
    Translates technical gaps into a 5-step roadmap based on the deadline.
    """
    print("--- [NODE] Executing Strategic Scheduler ---")

    # 1. Extract Metadata and Context
    # We use .get() to ensure the system doesn't crash if Laravel misses a key
    metadata = state.get("metadata", {})
    submission_deadline = metadata.get("submission_deadline", "No deadline provided")
    location = metadata.get("location", "Global")
    practice_area = metadata.get("practice_area", "General Law")
    
    # 2. Get Analysis Data from previous nodes
    # 'positioning_core' should already be populated by the Snapshot Generator
    raw_blind_spots = state.get("blind_spots", [])
    raw_gaps = state.get("gaps", [])

    formatted_blind_spots = ""
    if isinstance(raw_blind_spots, list):
        for bs in raw_blind_spots:
            # Handle dictionary objects from Snapshot
            issue = bs.get('issue', 'Unknown Issue')
            desc = bs.get('description', '')
            formatted_blind_spots += f"- {issue}: {desc}\n"
    else:
        formatted_blind_spots = str(raw_blind_spots)

    formatted_gaps = "\n".join([f"- {g}" for g in raw_gaps]) if isinstance(raw_gaps, list) else str(raw_gaps)

    

    # 3. Prepare Input for the Chain
    # We truncate raw_text to keep the context window efficient
    input_data = {
        "submission_deadline": submission_deadline,
        "location": location,
        "practice_area": practice_area,
        "gaps": formatted_gaps,
        "blind_spots": formatted_blind_spots,
        # Truncate to 4000 for safety on free models
        "raw_text": state.get("raw_text", "") 
    }

    try:
        # The parser will now turn the LLM's raw string into your object

        print(f"--- [DEBUG] calling LLM ---")

        response = scheduler_chain.invoke(input_data)
        
        # Use .model_dump() instead of .dict() for Pydantic v2
        return {
            "evolution_path": [m.model_dump() for m in response.evolution_path],
            "current_step": state.get("current_step", 0) + 1
        }
    except Exception as e:
        print(f"!!! Scheduler Parser Failure: {e}")
        # Return a fallback to prevent the graph from dying
        return {"evolution_path": [], "status": "scheduler_error"}