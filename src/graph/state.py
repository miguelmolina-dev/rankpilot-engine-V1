from typing import TypedDict, List, Optional, Any
from pydantic import BaseModel
# --- 1. SUB-ESTRUCTURAS (TypedDict) ---
# Definimos los componentes internos solo como TypedDict. 
# Esto los hace compatibles con .get() en tus nodos.

class PositioningCore(TypedDict, total=False):
    practice_model: str  
    practice_definition: str  
    confidence_score: float
    signals: List[str]

class PositioningTier(TypedDict, total=False):
    label: str
    explanation: str

class BlindSpot(TypedDict, total=False):
    issue: str
    description: str

class EvolutionAction(TypedDict, total=False):
    action: str
    impact: str
    instruction: str

class NewAnswer(TypedDict, total=False):
    question_text: str
    answer: str

class MetaData(TypedDict, total=False):
    file_base64: str
    directory: Optional[str]
    current_band: Optional[str]
    target_band: Optional[str]

# --- 2. EL ESTADO DEL GRAFO (LangGraph) ---
# IMPORTANTE: No pongas "= []" o "= 0" aquí. TypedDict solo acepta tipos.
class RankPilotState(TypedDict):
    submission_id: str
    metadata: Optional[MetaData]
    raw_text: str  
    new_answer: Optional[NewAnswer]
    history: List[str]
    current_step: int
    gaps: Optional[List[str]]
    positioning_core: Optional[PositioningCore]
    positioning_tier: Optional[PositioningTier]
    blind_spots: List[BlindSpot]
    competitive_advantage: List[str]
    evolution_path: List[EvolutionAction]
    next_node: str

# --- 3. EL ESQUEMA DE PETICIÓN (FastAPI / Pydantic) ---
# Aquí SÍ usamos valores por defecto para que Laravel pueda enviar JSONs incompletos.
class RankPilotRequest(BaseModel):
    submission_id: str
    metadata: Optional[MetaData] = None
    raw_text: str = ""
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