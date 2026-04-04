from src.graph.state import RankPilotState
from src.chains.extractor_chain import extraction_chain
from src.utils.pdf_loader import extract_text_from_pdf, clean_extracted_text

def structural_analyzer_node(state: RankPilotState) -> RankPilotState:
    """
    Node 1: Parses the PDF (if not already parsed) and identifies 
    the initial structural gaps and practice model.
    """
    print("--- [NODE] Starting Structural Analysis ---")
    
    # 1. Get the text (This only happens in the very first hit)
    if not state.get("raw_text"):
        if not state.get("metadata", {}).get("file_path"):
            return {"status": "error", "message": "No file_path in metadata for structural analysis."}
        # We assume the file_path is passed in metadata by Laravel
        file_path = state["metadata"].get("file_path")
        raw_data = extract_text_from_pdf(file_path)
        state["raw_text"] = clean_extracted_text(raw_data)
        print("--- DEBUG: raw_text extracted ---")

    try: 
        print("--- DEBUG: Invoking Extraction Chain ---")
        # 2. Call the LCEL Chain (The LLM logic)
        # We pass the raw text to the chain to get the first "Diagnosis"
        analysis_result_obj = extraction_chain.invoke({"text": state["raw_text"]})
        analysis_result = analysis_result_obj.dict() # Convert object to dictionary
        print(f"--- DEBUG: LLM Response Received: {analysis_result.get('practice_model')} ---")

        # 1. Get the current metadata from state
        updated_metadata = state.get("metadata", {}).copy()

        # 2. Inject the dynamically extracted firm_name from the LLM result
        # This ensures metadata is enriched with the firm name found in the PDF
        updated_metadata["firm_name"] = analysis_result.get("firm_name", "Unknown Firm")

        # 3. Update the State
        # Note: We don't fill 'positioning_tier' yet, just the core model and gaps
        return {
            # We must include the existing state keys
            "submission_id": state.get("submission_id"),
            "metadata": updated_metadata,
            "raw_text": state.get("raw_text"),
            "history": state.get("history", []),
            "gaps": analysis_result.get("gaps", []), # Add the identified gaps to the state
            # Fill the new standardized PositioningCore
            "positioning_core": {
                "practice_model": analysis_result.get("practice_model"),
                "practice_definition": analysis_result.get("practice_definition") or analysis_result.get("definition"),
                "confidence_score": analysis_result.get("confidence_score", 0.0),
                "signals": analysis_result.get("initial_signals", [])
            },
            
            "current_step": 1,
            "total_steps_estimated": 6,
            "next_node": "interrogate" # This MUST match workflow.add_node("interrogator", ...)
        }
    except Exception as e:
        print(f"Error in Structural Analysis: {e}")
        return {"status": "error", "message": str(e)}