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
            "practice_area": state.metadata.practice_area if state.metadata else "Unknown", # <-- CORRECCIÓN AQUÍ
            "gaps": state.gaps if state.gaps else "No specific gaps identified yet."
        })
        
        # 3. Mapeo al Estado
        # We can just return the pydantic models since the state is a BaseModel now
        return {
            # Solo actualizamos lo que este nodo genera. 
            # No tocamos positioning_core para no sobrescribir el del nodo 1.
            "positioning_tier": result.positioning_tier.model_dump(),
            "blind_spots": [bs.model_dump() for bs in result.blind_spots],
            "competitive_advantage": result.competitive_advantage,
            "status": "completed",
            "next_node": "__end__"
        }

    except Exception as e:
        print(f"!!! Error Crítico en Generación de Snapshot: {e}")
        return {
            "status": "error",
            "next_node": "__end__",
            "positioning_tier": {"label": "Error", "explanation": str(e)} # <-- CORRECCIÓN AQUÍ
        }