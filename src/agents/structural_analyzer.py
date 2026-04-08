from src.graph.state import RankPilotState
from src.chains.extractor_chain import extraction_chain
from src.utils.document_loader import extract_text_from_base64, clean_extracted_text

from src.graph.state import PositioningCore

def structural_analyzer_node(state: RankPilotState) -> dict:
    """
    Node 1: Parses the document and identifies initial structural gaps.
    """
    print("--- [NODE] Starting Structural Analysis ---")
    
    # 1. Obtención del texto (Solo en la primera ejecución)
    raw_text = state.raw_text
    metadata = state.metadata

    if not raw_text:
        file_base64 = metadata.file_base64 if metadata else None
        if not file_base64:
            print("!!! ERROR: No file_base64 found in metadata.")
            return {"next_node": "end", "gaps": ["Missing file_base64"]}
        
        try:
            # Extraemos y limpiamos el texto
            extracted_data = extract_text_from_base64(file_base64)
            raw_text = clean_extracted_text(extracted_data)
            print("--- DEBUG: raw_text extracted and cleaned ---")
        except Exception as e:
            print(f"!!! Error during text extraction: {e}")
            return {"next_node": "end", "gaps": [f"Extraction Error: {e}"]}

    try: 
        print("--- DEBUG: Invoking Extraction Chain ---")
        # 2. Invocación de la cadena LCEL
        analysis_result_obj = extraction_chain.invoke({"text": raw_text})
        print(f"--- DEBUG: LLM Identified Model: {analysis_result_obj.practice_model} ---")

    except Exception as e:
        print(f"!!! Error in Extraction Chain: {e}")
        return {"next_node": "end", "gaps": [f"Analysis Error: {e}"]}

    # 3. Retorno de Actualizaciones
    # En LangGraph, solo devolvemos lo que cambia. El resto se mantiene.
    return {
        "raw_text": raw_text,
        "gaps": analysis_result_obj.gaps if analysis_result_obj.gaps else [],
        "positioning_core": PositioningCore(
            practice_model=analysis_result_obj.practice_model if analysis_result_obj.practice_model else "",
            practice_definition=analysis_result_obj.definition if analysis_result_obj.definition else "",
            confidence_score=analysis_result_obj.confidence_score if analysis_result_obj.confidence_score else 0.0,
            signals=analysis_result_obj.initial_signals if analysis_result_obj.initial_signals else []
        ),
        "current_step": 1,
        "next_node": "interrogate" 
    }