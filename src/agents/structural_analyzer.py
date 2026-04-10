from src.graph.state import RankPilotState
from src.chains.extractor_chain import extraction_chain
from src.utils.document_loader import extract_text_from_base64, clean_extracted_text
from src.graph.state import RankPilotState, PositioningCore, MetaData
def structural_analyzer_node(state: RankPilotState) -> RankPilotState:
    """
    Node 1: Parses the document and identifies initial structural gaps.
    """
    print("--- [NODE] Starting Structural Analysis ---")
    
    # 1. Get the text (This only happens in the very first hit)
    if not state.raw_text:
        if not state.metadata or not state.metadata.file_base64:
            return {"status": "error", "message": "No file_base64 in metadata for structural analysis."}
        # We assume the file_base64 is passed in metadata by Laravel
        file_base64 = state.metadata.file_base64
        raw_data = extract_text_from_base64(file_base64)
        state.raw_text = clean_extracted_text(raw_data)
        print("--- DEBUG: raw_text extracted ---")

    try: 
        print("--- DEBUG: Invoking Extraction Chain ---")
        # 2. Call the LCEL Chain (The LLM logic)
        # We pass the raw text to the chain to get the first "Diagnosis"
        analysis_result = extraction_chain.invoke({"text": state.raw_text})

        print(f"--- DEBUG: LLM Response Received: {analysis_result.firm_name} ---")

        # 1. Inject the dynamically extracted firm_name from the LLM result
        # This ensures metadata is enriched with the firm name found in the PDF
        if state.metadata:
            state.metadata.firm_name = analysis_result.firm_name

        core_data = PositioningCore(
            practice_model=analysis_result.practice_model,
            practice_definition=analysis_result.definition,
            confidence_score=analysis_result.confidence_score,
            signals=analysis_result.initial_signals
        )

        # 2. Update the State
        # Note: We don't fill 'positioning_tier' yet, just the core model and gaps
        return {
            "metadata": state.metadata,
            "raw_text": state.raw_text,
            "history": state.history,
            "gaps": analysis_result.gaps, # Add the identified gaps to the state
            # Fill the new standardized PositioningCore
            "positioning_core": core_data,
            "current_step": 1,
            "next_node": "interrogate" # This MUST match workflow.add_node("interrogator", ...)
        }
    except Exception as e:
        print(f"!!! Error in Extraction Chain: {e}")
        return {"next_node": "end", "gaps": [f"Analysis Error: {e}"]}

    # 3. Retorno de Actualizaciones
    # En LangGraph, solo devolvemos lo que cambia. El resto se mantiene.
    return {
        "raw_text": raw_text,
        "gaps": analysis_result.get("gaps", []),
        "positioning_core": PositioningCore(
            practice_model=analysis_result.get("practice_model", ""),
            practice_definition=analysis_result.get("practice_definition") or analysis_result.get("definition", ""),
            confidence_score=analysis_result.get("confidence_score", 0.0),
            signals=analysis_result.get("initial_signals", [])
        ),
        "current_step": 1,
        "next_node": "interrogate" 
    }