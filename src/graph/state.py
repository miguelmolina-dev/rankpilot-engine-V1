from typing import TypedDict, List, Optional, Any
from pydantic import BaseModel

# --- 1. VALIDATION MODELS (BaseModel) ---
# These are used EXCLUSIVELY for FastAPI validation. 
# We append 'Model' to the names to avoid namespace collisions.

class PositioningCore(TypedDict):
    practice_model: str  
    practice_definition: str  
    confidence_score: float
    signals: List[str]

class PositioningTier(TypedDict):
    label: str
    explanation: str

class BlindSpot(TypedDict):
    issue: str
    description: str

class EvolutionAction(TypedDict):
    action: str
    impact: str
    instruction: str

class NewAnswer(TypedDict):
    question_text: str
    answer: str

class MetaData(TypedDict):
    file_base64: str
    directory: Optional[str]
    current_band: Optional[str]
    target_band: Optional[str]

# --- 2. THE GRAPH STATE (LangGraph) ---
# Use this class for: workflow = StateGraph(RankPilotState)
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

# --- 3. THE REQUEST WRAPPER (FastAPI / Pydantic) ---
# Use this class in your endpoint: async def process(request: RankPilotRequest)
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