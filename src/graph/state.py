from typing import List, Optional, Any
from pydantic import BaseModel

# --- 1. SUB-ESTRUCTURAS (Pydantic Models) ---
class PositioningCore(BaseModel):
    practice_model: str = ""
    practice_definition: str = ""
    confidence_score: float = 0.0
    signals: List[str] = []

class PositioningTier(BaseModel):
    label: str = ""
    explanation: str = ""

class BlindSpot(BaseModel):
    issue: str = ""
    description: str = ""

class EvolutionAction(BaseModel):
    action: str = ""
    impact: str = ""
    instruction: str = ""

class NewAnswer(BaseModel):
    question_text: str = ""
    answer: str = ""

class MetaData(BaseModel):
    file_base64: str = ""
    directory: Optional[str] = None
    current_band: Optional[str] = None
    target_band: Optional[str] = None

# --- 2. EL ESTADO DEL GRAFO Y PETICIÓN (LangGraph / FastAPI) ---
class RankPilotState(BaseModel):
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

# Since RankPilotRequest is the same as the RankPilotState, we can just alias it
RankPilotRequest = RankPilotState