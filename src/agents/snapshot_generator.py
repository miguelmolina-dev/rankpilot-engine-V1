from langchain_openai import ChatOpenAI
from src.chains.snapshot_chain import snapshot_chain
from src.utils.llm_manager import get_llm
from src.graph.state import RankPilotState

from src.graph.state import PositioningTier

def snapshot_generator_node(state: RankPilotState):
    print("--- [NODE] Generating Final Snapshot ---")
    
    # 1. Ingestión Segura (Evitamos AttributeError si el core es None)
    pos_core = state.positioning_core
    
    try:
        # 2. Invocación de la cadena
        # Usamos los datos crudos y el historial para la síntesis final
        result = snapshot_chain.invoke({
            "raw_text": state.raw_text,
            "history": state.history,
            "practice_model": state.positioning_core.practice_model if state.positioning_core else "Unknown Model",
            "submission_id": state.submission_id,
            "gaps": state.gaps if state.gaps else "No specific gaps identified yet."
        })
        
        # 3. Mapeo al Estado
        # We can just return the pydantic models since the state is a BaseModel now
        return {
            "positioning_core": {
                "practice_model": result.positioning_core.practice_model.label,
                "practice_definition": result.positioning_core.practice_model.definition,
                "confidence_score": result.positioning_core.confidence_score,
                "signals": result.positioning_core.signals
            },
            "positioning_tier": result.positioning_tier.model_dump(),
            "blind_spots": [bs.model_dump() for bs in result.blind_spots],
            "competitive_advantage": result.competitive_advantage,
            "status": "completed",
            "next_node": "__end__" # En LangGraph, esto indica el final absoluto
        }

    except Exception as e:
        print(f"!!! Error Crítico en Generación de Snapshot: {e}")
        # Retorno de seguridad para que Laravel no reciba un vacío
        return {
            "status": "error",
            "next_node": "__end__",
            "positioning_tier": PositioningTier(label="Error", explanation=str(e))
        }