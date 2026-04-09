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
    metadata = getattr(state, "metadata", {})

    # Handle both BaseModel and dict formats
    submission_deadline = getattr(metadata, "submission_deadline", metadata.get("submission_deadline", "No deadline provided") if isinstance(metadata, dict) else "No deadline provided")
    location = getattr(metadata, "location", metadata.get("location", "Global") if isinstance(metadata, dict) else "Global")
    practice_area = getattr(metadata, "practice_area", metadata.get("practice_area", "General Law") if isinstance(metadata, dict) else "General Law")
    
    # 2. Get Analysis Data from previous nodes
    raw_blind_spots = getattr(state, "blind_spots", [])
    raw_gaps = getattr(state, "gaps", [])

    formatted_blind_spots = ""
    if isinstance(raw_blind_spots, list):
        for bs in raw_blind_spots:
            # Handle dictionary objects and BaseModel objects
            issue = getattr(bs, 'issue', bs.get('issue', 'Unknown Issue') if isinstance(bs, dict) else 'Unknown Issue')
            desc = getattr(bs, 'description', bs.get('description', '') if isinstance(bs, dict) else '')
            formatted_blind_spots += f"- {issue}: {desc}\n"
    else:
        formatted_blind_spots = str(raw_blind_spots)

    formatted_gaps = "\n".join([f"- {g}" for g in raw_gaps]) if isinstance(raw_gaps, list) else str(raw_gaps)

    # 3. Prepare Input for the Chain
    input_data = {
        "submission_deadline": submission_deadline,
        "location": location,
        "practice_area": practice_area,
        "gaps": formatted_gaps,
        "blind_spots": formatted_blind_spots,
        "raw_text": getattr(state, "raw_text", "")
    }

    try:
        print(f"--- [DEBUG] calling LLM ---")

        response = scheduler_chain.invoke(input_data)
        
        # Use .model_dump() instead of .dict() for Pydantic v2
        return {
            "evolution_path": [m.model_dump() for m in response.evolution_path],
            "current_step": getattr(state, "current_step", 0) + 1
        }
    except Exception as e:
        print(f"!!! Scheduler Parser Failure: {e}")
        return {"evolution_path": [], "status": "scheduler_error"}