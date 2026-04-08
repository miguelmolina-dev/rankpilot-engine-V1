from typing import TypedDict, List, Optional, Any
from pydantic import BaseModel

# --- 1. DEFINICIONES DE TIPOS (TypedDict) ---
# Usamos TypedDict para que tus nodos de LangGraph puedan usar .get() sin problemas.
# Pydantic V2 es capaz de validar estos diccionarios dentro de un BaseModel

# --- 1. SUB-ESTRUCTURAS (BaseModel) ---
# Estas clases permiten que FastAPI genere el esquema JSON sin crashear.
class PositioningCore(BaseModel):
    practice_model: str  
    practice_definition: str  
    confidence_score: float
    signals: List[str]

class PositioningTier(BaseModel):
    label: str
    explanation: str

class BlindSpot(BaseModel):
    issue: str
    description: str

class EvolutionAction(BaseModel):
    action: str
    impact: str
    instruction: str

class NewAnswer(BaseModel):
    question_text: str
    answer: str

class MetaData(BaseModel):
    file_base64: str
    directory: Optional[str] = None
    current_band: Optional[str] = None
    target_band: Optional[str] = None

# --- 2. ESQUEMA DE ENTRADA PARA FASTAPI (BaseModel) ---
# Este es el "Escudo" que recibe los datos de Laravel.
class RankPilotRequest(BaseModel):
    submission_id: str
    metadata: Optional[MetaData] = None
    raw_text: str  
    new_answer: Optional[NewAnswer] = None
    history: List[str] = []
    current_step: int = 0
    gaps: Optional[List[str]] = None
    positioning_core: Optional[PositioningCore] = None
    positioning_tier: Optional[PositioningTier] = None
    blind_spots: List[BlindSpot] = []
    competitive_advantage: List[str] = []
    evolution_path: List[EvolutionAction] = []
    next_node: str = ""

# --- 3. ESTADO DEL GRAFO PARA LANGGRAPH (TypedDict) ---
# Usa esta clase exclusivamente para definir tu Grafo: StateGraph(RankPilotState).
# Al usar Any/dict en los campos anidados, evitamos que Pydantic intente validarlos aquí.
class RankPilotState(TypedDict):
    submission_id: str
    metadata: Optional[dict]
    raw_text: str  
    new_answer: Optional[dict]
    history: List[str]
    current_step: int
    gaps: Optional[List[str]]
    positioning_core: Optional[dict]
    positioning_tier: Optional[dict]
    blind_spots: List[dict]
    competitive_advantage: List[str]
    evolution_path: List[dict]
    next_node: str