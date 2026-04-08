from langchain_openai import ChatOpenAI
from src.chains.snapshot_chain import snapshot_chain
from src.utils.llm_manager import get_llm
from src.graph.state import RankPilotState

def snapshot_generator_node(state: RankPilotState):
    print("--- [NODE] Generating Final Snapshot ---")
    
    # 1. Ingestión Segura (Evitamos AttributeError si el core es None)
    # Como posicioning_core es Optional[dict], usamos .get() con precaución
    pos_core = state.get("positioning_core") or {}
    
    try:
        # 2. Invocación de la cadena
        # Usamos los datos crudos y el historial para la síntesis final
        result = snapshot_chain.invoke({
            "raw_text": state.get("raw_text", ""),
            "history": state.get("history", []),
            "practice_model": pos_core.get("practice_model", "Unknown Model"),
            "submission_id": state.get("submission_id", "Default-ID"),
            "gaps": state.get("gaps", "No specific gaps identified yet.")
        })
        
        # 3. Mapeo al Estado (Conversión de Pydantic a Dict)
        # Usamos model_dump() porque el resultado de la cadena suele ser un BaseModel
        # Pero lo guardamos como dict para que el TypedDict del Grafo sea feliz.
        return {
            "positioning_core": result.positioning_core.model_dump() if hasattr(result.positioning_core, 'model_dump') else result.positioning_core,
            "positioning_tier": result.positioning_tier.model_dump() if hasattr(result.positioning_tier, 'model_dump') else result.positioning_tier,
            "blind_spots": [bs.model_dump() if hasattr(bs, 'model_dump') else bs for bs in result.blind_spots],
            "competitive_advantage": result.competitive_advantage,
            "evolution_path": [ep.model_dump() if hasattr(ep, 'model_dump') else ep for ep in result.evolution_path],
            "status": "completed",
            "next_node": "__end__" # En LangGraph, esto indica el final absoluto
        }

    except Exception as e:
        print(f"!!! Error Crítico en Generación de Snapshot: {e}")
        # Retorno de seguridad para que Laravel no reciba un vacío
        return {
            "status": "error",
            "next_node": "__end__",
            "positioning_tier": {"label": "Error", "explanation": str(e)}
        }